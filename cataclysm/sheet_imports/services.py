from __future__ import annotations

from dataclasses import dataclass

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from people.models import OrganizationUnit, Person, PersonAssignment, PersonProfileFact, Trait
from species.models import Species

from .crew import CrewRow, CrewTabSchema, fingerprint_rows, normalize_text
from .models import SheetImportRun, SheetRowBinding, SheetSource


@dataclass
class ImportCounts:
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    unresolved: int = 0
    errors: int = 0

    def as_dict(self):
        return vars(self).copy()


def _find_person(row: CrewRow, source: SheetSource | None = None) -> Person | None:
    if source:
        binding = source.row_bindings.filter(row_fingerprint=row.row_fingerprint).first()
        if binding and isinstance(binding.target, Person):
            return binding.target
    matches = Person.objects.filter(name__iexact=row.name)
    return matches.first() if matches.count() == 1 else None


def preview_crew_rows(rows: list[CrewRow]) -> ImportCounts:
    counts = ImportCounts()
    for row in rows:
        matches = Person.objects.filter(name__iexact=row.name)
        if matches.count() > 1:
            counts.unresolved += 1
        elif matches.exists():
            counts.updated += 1
        else:
            counts.created += 1
    return counts


@transaction.atomic
def apply_crew_rows(spreadsheet_id: str, schema: CrewTabSchema, rows: list[CrewRow]) -> SheetImportRun:
    source, _ = SheetSource.objects.get_or_create(
        spreadsheet_id=spreadsheet_id,
        tab_name=schema.tab_name,
        range_name=schema.range_name,
        defaults={'schema_version': 1},
    )
    run = SheetImportRun.objects.create(
        source=source,
        status=SheetImportRun.Status.RUNNING,
        dry_run=False,
        content_fingerprint=fingerprint_rows(rows),
        started_at=timezone.now(),
    )
    counts = ImportCounts()
    seen_fingerprints = set()

    try:
        for row in rows:
            seen_fingerprints.add(row.row_fingerprint)
            existing_binding = source.row_bindings.filter(row_fingerprint=row.row_fingerprint).first()
            person = _find_person(row, source)
            if person is None and Person.objects.filter(name__iexact=row.name).count() > 1:
                counts.unresolved += 1
                SheetRowBinding.objects.update_or_create(
                    source=source,
                    row_fingerprint=row.row_fingerprint,
                    defaults=_binding_defaults(run, row, SheetRowBinding.Status.UNRESOLVED),
                )
                continue

            if (
                existing_binding
                and isinstance(existing_binding.target, Person)
                and existing_binding.normalized_payload == row.normalized_payload()
            ):
                existing_binding.last_run = run
                existing_binding.source_row_number = row.row_number
                existing_binding.raw_payload = {'values': list(row.raw_values)}
                existing_binding.warnings = list(row.warnings)
                existing_binding.status = SheetRowBinding.Status.IMPORTED
                existing_binding.save()
                counts.unchanged += 1
                continue

            created = person is None
            if created:
                person = Person(name=row.name)
            person.age = row.age
            person.age_text = row.age_text
            person.sex = row.sex
            person.rank = row.rank
            person.position = row.role

            species_matches = Species.objects.filter(species_name__iexact=row.species_name) if row.species_name else Species.objects.none()
            if species_matches.count() == 1:
                person.species = species_matches.first()

            person.save()
            # Imported markers must not remove traits curated in the app.
            person.traits.add(*(Trait.objects.get_or_create(name=name)[0] for name in row.traits))

            if row.branch:
                normalized_branch = normalize_text(row.branch).casefold()
                unit, _ = OrganizationUnit.objects.get_or_create(
                    normalized_name=normalized_branch,
                    kind=OrganizationUnit.Kind.BRANCH,
                    defaults={'name': row.branch},
                )
                PersonAssignment.objects.update_or_create(
                    person=person,
                    unit=unit,
                    role=row.role,
                    defaults={'rank': row.rank, 'status': row.status, 'is_primary': True},
                )

            facts = dict(row.profile_facts)
            if row.status:
                facts['status'] = row.status
            for key, value in facts.items():
                PersonProfileFact.objects.update_or_create(
                    person=person,
                    key=key,
                    defaults={'value': value, 'normalized_value': normalize_text(value).casefold()},
                )

            binding_defaults = _binding_defaults(run, row, SheetRowBinding.Status.IMPORTED)
            binding_defaults.update(
                content_type=ContentType.objects.get_for_model(person),
                object_id=person.pk,
            )
            SheetRowBinding.objects.update_or_create(
                source=source,
                row_fingerprint=row.row_fingerprint,
                defaults=binding_defaults,
            )
            if created:
                counts.created += 1
            else:
                counts.updated += 1

        source.row_bindings.exclude(row_fingerprint__in=seen_fingerprints).update(status=SheetRowBinding.Status.STALE)
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


def _binding_defaults(run, row, status):
    return {
        'last_run': run,
        'source_row_number': row.row_number,
        'status': status,
        'raw_payload': {'values': list(row.raw_values)},
        'normalized_payload': row.normalized_payload(),
        'warnings': list(row.warnings),
        'content_type': None,
        'object_id': None,
    }
