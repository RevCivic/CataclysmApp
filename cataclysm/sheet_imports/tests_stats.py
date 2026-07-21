import json
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from people.models import Person, PersonCapability

from .models import SheetImportRun, SheetRowBinding
from .stats import parse_stats_rows
from .stats_services import apply_stats_rows


STATS_VALUES = [
    ['Name', 'Command', 'Engineering', 'Medical'],
    ['Known Crew', 'X', 'D', ''],
    ['Unknown Crew', '', '', 'X'],
]


class StatsParserTests(TestCase):
    def test_parser_uses_headings_and_preserves_markers(self):
        rows = parse_stats_rows(STATS_VALUES)

        self.assertEqual(rows[0].row_number, 2)
        self.assertEqual(rows[0].capabilities, {'Command': 'X', 'Engineering': 'D'})
        self.assertEqual(rows[1].capabilities, {'Medical': 'X'})

    def test_parser_ignores_blank_names_and_warns_for_unnamed_columns(self):
        rows = parse_stats_rows([['Name', ''], ['', 'X'], ['Crew', 'X']])

        self.assertEqual(len(rows), 1)
        self.assertIn('unnamed column', rows[0].warnings[0])


class StatsApplyTests(TestCase):
    def setUp(self):
        self.person = Person.objects.create(name='Known Crew', age=30)

    def test_apply_links_only_exact_unique_people_and_is_idempotent(self):
        rows = parse_stats_rows(STATS_VALUES)

        first = apply_stats_rows('sheet-id', rows)
        second = apply_stats_rows('sheet-id', rows)

        self.assertEqual(PersonCapability.objects.filter(person=self.person).count(), 2)
        self.assertEqual(
            set(PersonCapability.objects.filter(person=self.person).values_list('raw_marker', flat=True)),
            {'X', 'D'},
        )
        self.assertEqual(first.counts['updated'], 1)
        self.assertEqual(first.counts['unresolved'], 1)
        self.assertEqual(second.counts['unchanged'], 1)
        self.assertEqual(second.counts['unresolved'], 1)
        self.assertEqual(SheetRowBinding.objects.count(), 2)


class ImportStatsCommandTests(TestCase):
    @patch('sheet_imports.management.commands.import_crew_stats.read_sheet_data')
    def test_command_is_dry_run_by_default(self, read_sheet_data):
        read_sheet_data.return_value = STATS_VALUES
        Person.objects.create(name='Known Crew', age=30)

        call_command('import_crew_stats', verbosity=0)

        self.assertFalse(PersonCapability.objects.exists())
        self.assertFalse(SheetImportRun.objects.exists())
        read_sheet_data.assert_called_once_with(
            '1XRyeXDIhNE6iwTXS_zDc_eHrQFU96Z2OUCIXm_t0twE',
            "'Stats'!A1:BH",
        )

    @patch('sheet_imports.management.commands.import_crew_stats.read_sheet_data')
    def test_command_writes_json_report(self, read_sheet_data):
        read_sheet_data.return_value = STATS_VALUES
        Person.objects.create(name='Known Crew', age=30)
        with TemporaryDirectory() as directory:
            path = f'{directory}/stats.json'
            call_command('import_crew_stats', '--report-json', path, verbosity=0)
            report = json.loads(open(path, encoding='utf-8').read())

        self.assertTrue(report['dry_run'])
        self.assertEqual(report['rows'], 2)
        self.assertEqual(report['counts']['updated'], 1)
        self.assertEqual(report['counts']['unresolved'], 1)
