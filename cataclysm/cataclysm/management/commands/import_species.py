from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from species.importing import build_species_payload
from species.models import Species


class Command(BaseCommand):
    help = 'Import species from a JSON file created from the Species Index/Stats sheets.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('json_path', type=str, help='Path to JSON file (list of species records).')
        parser.add_argument(
            '--update-only',
            action='store_true',
            help='Only update existing Species by species name; do not create new rows.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse and validate, print a summary, but do not write to the database.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        json_path = Path(options['json_path']).expanduser().resolve()
        update_only = options['update_only']
        dry_run = options['dry_run']

        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f'File not found: {json_path}'))
            return

        with json_path.open('r', encoding='utf-8') as file_handle:
            data = json.load(file_handle)

        if not isinstance(data, list):
            self.stderr.write(self.style.ERROR('JSON must be an array of objects.'))
            return

        created = 0
        updated = 0
        skipped = 0
        errors: list[str] = []

        for index, record in enumerate(data, start=1):
            payload = build_species_payload(record)
            species_name = payload.get('species_name') or payload.get('name') or ''
            species_name = species_name.strip()
            if not species_name:
                skipped += 1
                errors.append(f'[{index}] Missing species_name; skipped.')
                continue
            payload['species_name'] = species_name

            try:
                species = Species.objects.filter(species_name=species_name).first()
                if species:
                    if dry_run:
                        updated += 1
                        continue
                    for field_name, value in payload.items():
                        setattr(species, field_name, value)
                    species.full_clean()
                    species.save()
                    updated += 1
                    continue

                if update_only:
                    skipped += 1
                    continue
                if dry_run:
                    created += 1
                    continue

                species = Species(**payload)
                species.full_clean()
                species.save()
                created += 1
            except Exception as exc:
                skipped += 1
                errors.append(f'[{index}] {species_name}: {exc}')

        message = f'Processed {len(data)} records → created={created}, updated={updated}, skipped={skipped}'
        if dry_run:
            message = '[DRY-RUN] ' + message
        self.stdout.write(self.style.SUCCESS(message))

        if errors:
            self.stdout.write(self.style.WARNING('Some records had issues:'))
            for line in errors:
                self.stdout.write('  - ' + line)
