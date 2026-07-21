import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError, CommandParser

from cataclysm.utils.google_sheets import extract_spreadsheet_id, read_sheet_data
from sheet_imports.crew import CREW_SCHEMAS, parse_crew_rows
from sheet_imports.services import apply_crew_rows, preview_crew_rows


DEFAULT_SPREADSHEET_ID = os.environ.get(
    'SPREADSHEET_ID',
    '1XRyeXDIhNE6iwTXS_zDc_eHrQFU96Z2OUCIXm_t0twE',
)


class Command(BaseCommand):
    help = 'Preview or apply schema-driven imports from the Main Crew and Other Crew tabs.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--spreadsheet-id',
            default=DEFAULT_SPREADSHEET_ID,
            help='Google spreadsheet URL or ID (defaults to SPREADSHEET_ID).',
        )
        parser.add_argument(
            '--tabs',
            nargs='+',
            choices=tuple(CREW_SCHEMAS),
            default=list(CREW_SCHEMAS),
            help='Crew tabs to process.',
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Write changes. Without this flag the command is a read-only preview.',
        )
        parser.add_argument('--report-json', help='Optional path for a machine-readable report.')

    def handle(self, *args, **options):
        spreadsheet_id = extract_spreadsheet_id(options['spreadsheet_id'])
        if not spreadsheet_id:
            raise CommandError('A spreadsheet ID or URL is required.')

        report = {'spreadsheet_id': spreadsheet_id, 'dry_run': not options['apply'], 'tabs': {}}
        for tab_name in options['tabs']:
            schema = CREW_SCHEMAS[tab_name]
            values = read_sheet_data(spreadsheet_id, f"'{schema.tab_name}'!{schema.range_name}")
            if values is None:
                raise CommandError(f'Could not read {schema.tab_name} ({schema.range_name}).')
            rows = parse_crew_rows(values, schema)
            warnings = sum(len(row.warnings) for row in rows)

            if options['apply']:
                run = apply_crew_rows(spreadsheet_id, schema, rows)
                counts = run.counts
                run_id = run.pk
            else:
                counts = preview_crew_rows(rows).as_dict()
                run_id = None

            report['tabs'][tab_name] = {
                'range': schema.range_name,
                'rows': len(rows),
                'warnings': warnings,
                'counts': counts,
                'run_id': run_id,
            }
            prefix = 'APPLY' if options['apply'] else 'DRY-RUN'
            self.stdout.write(
                f'[{prefix}] {tab_name}: rows={len(rows)} warnings={warnings} '
                + ' '.join(f'{key}={value}' for key, value in counts.items())
            )

        if options['report_json']:
            report_path = Path(options['report_json']).expanduser()
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
            self.stdout.write(f'Wrote report to {report_path}')
