import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError, CommandParser

from cataclysm.utils.google_sheets import extract_spreadsheet_id, read_sheet_data
from sheet_imports.stats import STATS_RANGE, STATS_TAB, parse_stats_rows
from sheet_imports.stats_services import apply_stats_rows, preview_stats_rows


DEFAULT_SPREADSHEET_ID = os.environ.get(
    'SPREADSHEET_ID',
    '1XRyeXDIhNE6iwTXS_zDc_eHrQFU96Z2OUCIXm_t0twE',
)


class Command(BaseCommand):
    help = 'Preview or apply character capabilities from the workbook Stats tab.'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('--spreadsheet-id', default=DEFAULT_SPREADSHEET_ID)
        parser.add_argument('--apply', action='store_true', help='Write changes; the default is read-only.')
        parser.add_argument('--report-json', help='Optional machine-readable report path.')

    def handle(self, *args, **options):
        spreadsheet_id = extract_spreadsheet_id(options['spreadsheet_id'])
        if not spreadsheet_id:
            raise CommandError('A spreadsheet ID or URL is required.')
        values = read_sheet_data(spreadsheet_id, f"'{STATS_TAB}'!{STATS_RANGE}")
        if values is None:
            raise CommandError(f'Could not read {STATS_TAB} ({STATS_RANGE}).')
        rows = parse_stats_rows(values)
        if options['apply']:
            run = apply_stats_rows(spreadsheet_id, rows)
            counts = run.counts
            run_id = run.pk
        else:
            counts = preview_stats_rows(rows).as_dict()
            run_id = None
        report = {
            'spreadsheet_id': spreadsheet_id,
            'dry_run': not options['apply'],
            'tab': STATS_TAB,
            'range': STATS_RANGE,
            'rows': len(rows),
            'warnings': sum(len(row.warnings) for row in rows),
            'counts': counts,
            'run_id': run_id,
        }
        prefix = 'APPLY' if options['apply'] else 'DRY-RUN'
        self.stdout.write(
            f'[{prefix}] Stats: rows={report["rows"]} warnings={report["warnings"]} '
            + ' '.join(f'{key}={value}' for key, value in counts.items())
        )
        if options['report_json']:
            path = Path(options['report_json']).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
            self.stdout.write(f'Wrote report to {path}')
