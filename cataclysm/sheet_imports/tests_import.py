import json
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from cataclysm.utils.google_sheets import read_sheet_data
from people.models import Person

from .crew import MAIN_CREW_SCHEMA, OTHER_CREW_SCHEMA, parse_age, parse_crew_rows
from .models import SheetImportRun, SheetRowBinding, SheetSource


def _row(width, values):
    row = [''] * width
    for index, value in values.items():
        row[index] = value
    return row


class CrewParserTests(TestCase):
    def test_parse_age_preserves_qualified_values(self):
        self.assertEqual(parse_age('29.0'), (29, '29.0'))
        self.assertEqual(parse_age('44 KIA'), (None, '44 KIA'))
        self.assertEqual(parse_age('?'), (None, '?'))

    def test_main_and_other_schemas_use_their_own_trait_offsets(self):
        main = parse_crew_rows(
            [_row(22, {0: 'Main Person', 2: '29', 16: 'M', 17: 'N', 18: 'LT', 20: 'Navy'})],
            MAIN_CREW_SCHEMA,
        )[0]
        other = parse_crew_rows(
            [_row(33, {0: 'Other Person', 2: '?', 16: 'M', 17: 'N', 18: 'O', 19: 'P', 22: 'Civilian'})],
            OTHER_CREW_SCHEMA,
        )[0]

        self.assertEqual(main.traits, ('Flier', 'Mutant'))
        self.assertEqual(other.traits, ('Arcane', 'Divine', 'Flier', 'Mutant'))
        self.assertEqual(other.age_text, '?')
        self.assertTrue(other.warnings)

    def test_parser_skips_blank_names_and_tracks_source_rows(self):
        parsed = parse_crew_rows([[], ['Crew Member', '', '30']], MAIN_CREW_SCHEMA)

        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].row_number, 4)


class SheetTransportTests(TestCase):
    @patch('cataclysm.utils.google_sheets.requests.get')
    def test_named_tab_uses_gviz_parameters(self, get):
        get.return_value.text = 'Name,Age\nA Person,30\n'
        get.return_value.raise_for_status.return_value = None

        rows = read_sheet_data('sheet-id', "'Other Crew'!A6:AG")

        self.assertEqual(rows[1], ['A Person', '30'])
        url = get.call_args.args[0]
        params = get.call_args.kwargs['params']
        self.assertTrue(url.endswith('/sheet-id/gviz/tq'))
        self.assertEqual(params, {'tqx': 'out:csv', 'sheet': 'Other Crew', 'range': 'A6:AG'})


class ImportCrewCommandTests(TestCase):
    def setUp(self):
        self.values = [
            _row(
                22,
                {
                    0: 'Import Person',
                    1: 'Unknown Species',
                    2: '>100',
                    3: 'F',
                    7: 'D',
                    18: 'LT',
                    19: 'Engineer',
                    20: 'Navy',
                    21: 'Good',
                },
            )
        ]

    @patch('sheet_imports.management.commands.import_crew_workbook.read_sheet_data')
    def test_dry_run_is_default_and_does_not_write(self, read_sheet_data):
        read_sheet_data.return_value = self.values

        call_command('import_crew_workbook', '--tabs', 'Main Crew', verbosity=0)

        self.assertFalse(Person.objects.exists())
        self.assertFalse(SheetImportRun.objects.exists())
        read_sheet_data.assert_called_once_with(
            '1XRyeXDIhNE6iwTXS_zDc_eHrQFU96Z2OUCIXm_t0twE',
            "'Main Crew'!A3:V",
        )

    @patch('sheet_imports.management.commands.import_crew_workbook.read_sheet_data')
    def test_apply_is_idempotent_and_preserves_provenance(self, read_sheet_data):
        read_sheet_data.return_value = self.values

        call_command('import_crew_workbook', '--tabs', 'Main Crew', '--apply', verbosity=0)
        call_command('import_crew_workbook', '--tabs', 'Main Crew', '--apply', verbosity=0)

        person = Person.objects.get()
        self.assertIsNone(person.age)
        self.assertEqual(person.age_text, '>100')
        self.assertEqual(person.assignments.get().unit.name, 'Navy')
        self.assertEqual(set(person.traits.values_list('name', flat=True)), {'Engineer'})
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(SheetSource.objects.count(), 1)
        self.assertEqual(SheetRowBinding.objects.count(), 1)
        self.assertEqual(SheetImportRun.objects.count(), 2)
        self.assertEqual(SheetImportRun.objects.first().counts['unchanged'], 1)

    @patch('sheet_imports.management.commands.import_crew_workbook.read_sheet_data')
    def test_json_report_contains_preview_counts(self, read_sheet_data):
        read_sheet_data.return_value = self.values
        with TemporaryDirectory() as directory:
            path = f'{directory}/report.json'
            call_command(
                'import_crew_workbook',
                '--tabs',
                'Main Crew',
                '--report-json',
                path,
                verbosity=0,
            )
            report = json.loads(open(path, encoding='utf-8').read())

        self.assertTrue(report['dry_run'])
        self.assertEqual(report['tabs']['Main Crew']['counts']['created'], 1)
        self.assertEqual(report['tabs']['Main Crew']['rows'], 1)
