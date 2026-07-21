from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from people.models import Capability, Person, PersonCapability

from .crew import normalize_text
from .models import SheetImportRun, SheetRowBinding, SheetSource
from .services import ImportCounts
from .stats import STATS_RANGE, STATS_TAB, StatsRow


def preview_stats_rows(rows: list[StatsRow]):
    counts = ImportCounts()
    for row in rows:
        match_count = Person.objects.filter(name__iexact=row.name).count()
        if match_count == 1:
            counts.updated += 1
        else:
            counts.unresolved += 1
    return counts


@transaction.atomic
def apply_stats_rows(spreadsheet_id: str, rows: list[StatsRow]):
    source, _ = SheetSource.objects.get_or_create(
        spreadsheet_id=spreadsheet_id,
        tab_name=STATS_TAB,
        range_name=STATS_RANGE,
        defaults={'schema_version': 1},
    )
    run = SheetImportRun.objects.create(
        source=source,
        status=SheetImportRun.Status.RUNNING,
        dry_run=False,
        started_at=timezone.now(),
    )
    counts = ImportCounts()
    seen = set()
    try:
        for row in rows:
            seen.add(row.row_fingerprint)
            matches = Person.objects.filter(name__iexact=row.name)
            if matches.count() != 1:
                counts.unresolved += 1
                _save_binding(source, run, row, SheetRowBinding.Status.UNRESOLVED)
                continue
            person = matches.get()
            binding = source.row_bindings.filter(row_fingerprint=row.row_fingerprint).first()
            if binding and binding.target == person and binding.normalized_payload == row.normalized_payload():
                binding.last_run = run
                binding.source_row_number = row.row_number
                binding.raw_payload = {'values': list(row.raw_values)}
                binding.warnings = list(row.warnings)
                binding.status = SheetRowBinding.Status.IMPORTED
                binding.save()
                counts.unchanged += 1
                continue

            for name, marker in row.capabilities.items():
                normalized_name = normalize_text(name).casefold()
                capability, _ = Capability.objects.get_or_create(
                    normalized_name=normalized_name,
                    defaults={'name': name, 'category': 'Workbook Stats'},
                )
                PersonCapability.objects.update_or_create(
                    person=person,
                    capability=capability,
                    defaults={'raw_marker': marker},
                )
            _save_binding(source, run, row, SheetRowBinding.Status.IMPORTED, person)
            counts.updated += 1

        source.row_bindings.exclude(row_fingerprint__in=seen).update(status=SheetRowBinding.Status.STALE)
        run.status = SheetImportRun.Status.SUCCEEDED
    except Exception as exc:
        run.status = SheetImportRun.Status.FAILED
        run.error_message = str(exc)
        counts.errors += 1
        raise
    finally:
        run.counts = counts.as_dict()
        run.finished_at = timezone.now()
        run.save(update_fields=('status', 'counts', 'error_message', 'finished_at'))
    return run


def _save_binding(source, run, row, status, person=None):
    defaults = {
        'last_run': run,
        'source_row_number': row.row_number,
        'status': status,
        'raw_payload': {'values': list(row.raw_values)},
        'normalized_payload': row.normalized_payload(),
        'warnings': list(row.warnings),
        'content_type': ContentType.objects.get_for_model(person) if person else None,
        'object_id': person.pk if person else None,
    }
    return SheetRowBinding.objects.update_or_create(
        source=source,
        row_fingerprint=row.row_fingerprint,
        defaults=defaults,
    )[0]
