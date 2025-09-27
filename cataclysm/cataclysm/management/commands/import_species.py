from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, List, Dict

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.core.exceptions import ValidationError

from species.models import Species


def _choice_values(choices: Iterable[tuple]) -> set[str]:
    return {c[0] for c in choices}


SIZE_OK = _choice_values(Species.SIZE_CHOICES)
TYPE_OK = _choice_values(Species.TYPE_CHOICES)
AIR_OK = _choice_values(Species.AIR_CHOICES)
REPRO_OK = _choice_values(Species.REPRODUCTIVE_CHOICES)
GRAV_OK = _choice_values(Species.GRAVITY_CHOICES)
ACCORD_OK = _choice_values(Species.ACCORD_STATUS_CHOICES)
SOCIETY_OK = _choice_values(Species.SOCIETY_CHOICES)
LOCO_OK = _choice_values(Species.LOCOMOTION_CHOICES)


def _coerce_choice(val: Any, ok: set[str], default: str | None = None) -> str:
    if val is None:
        return default if default is not None else next(iter(ok))
    s = str(val).strip().lower()
    if s in ok:
        return s
    return default if default is not None else next(iter(ok))


def _coerce_int(val: Any, default: int = 0) -> int:
    try:
        return int(val)
    except Exception:
        try:
            return int(float(val))
        except Exception:
            return default


def _coerce_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    s = str(val).strip().lower()
    return s in {"1", "true", "t", "yes", "y", "x"}


def _coerce_json_list(val: Any) -> list:
    if isinstance(val, list):
        return val
    if val in (None, "", "null", "None"):
        return []
    if isinstance(val, str):
        try:
            maybe = json.loads(val)
            if isinstance(maybe, list):
                return maybe
        except Exception:
            pass
        # fallback: split lines/semicolons
        parts = [p.strip() for p in val.replace(");", ";").split(";")]
        return [p for p in parts if p]
    return []


class Command(BaseCommand):
    help = "Import species from a JSON file created from the Species Index/Stats sheets."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("json_path", type=str, help="Path to JSON file (list of species records).")
        parser.add_argument(
            "--update-only",
            action="store_true",
            help="Only update existing Species by name; do not create new rows.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate, print a summary, but do not write to the database.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        json_path = Path(options["json_path"]).expanduser().resolve()
        update_only = options["update_only"]
        dry_run = options["dry_run"]

        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {json_path}"))
            return

        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            self.stderr.write(self.style.ERROR("JSON must be an array of objects."))
            return

        created = 0
        updated = 0
        skipped = 0
        errors: list[str] = []

        for i, rec in enumerate(data, start=1):
            name = (rec.get("name") or rec.get("Name") or "").strip()
            if not name:
                skipped += 1
                errors.append(f"[{i}] Missing name; skipped.")
                continue

            # Build kwargs with coercions
            payload: Dict[str, Any] = dict(
                name=name,
                home_world=(rec.get("home_world") or "").strip(),
                society=_coerce_choice(rec.get("society"), SOCIETY_OK, "unknown"),
                accord_status=_coerce_choice(rec.get("accord_status"), ACCORD_OK, "unknown"),
                background=(rec.get("background") or "").strip(),
                sociology=(rec.get("sociology") or "").strip(),
                physiology=(rec.get("physiology") or "").strip(),
                racial_traits=_coerce_json_list(rec.get("racial_traits")),
                size=_coerce_choice(rec.get("size"), SIZE_OK, "medium"),
                type=_coerce_choice(rec.get("type"), TYPE_OK, "animal"),
                air=_coerce_choice(rec.get("air"), AIR_OK, "oxygen"),
                reproduction_method=_coerce_choice(rec.get("reproduction_method"), REPRO_OK, "standard"),
                hours_of_sleep=_coerce_int(rec.get("hours_of_sleep"), 8),
                days_without_food=_coerce_int(rec.get("days_without_food"), 14),
                days_without_water=_coerce_int(rec.get("days_without_water"), 3),
                strength_rating=_coerce_int(rec.get("strength_rating"), 3),
                toughness_rating=_coerce_int(rec.get("toughness_rating"), 3),
                speed_rating=_coerce_int(rec.get("speed_rating"), 3),
                intelligence_rating=_coerce_int(rec.get("intelligence_rating"), 3),
                natural_weapons=_coerce_bool(rec.get("natural_weapons")),
                natural_armor=_coerce_bool(rec.get("natural_armor")),
                can_fly=_coerce_bool(rec.get("can_fly")),
                aquatic=_coerce_bool(rec.get("aquatic")),
                amphibious=_coerce_bool(rec.get("amphibious")),
                telepathic=_coerce_bool(rec.get("telepathic")),
                psionic=_coerce_bool(rec.get("psionic")),
                gravity=_coerce_choice(rec.get("gravity"), GRAV_OK, "standard"),
                special_abilities=_coerce_json_list(rec.get("special_abilities")),
                locomotion_method=_coerce_choice(rec.get("locomotion_method"), LOCO_OK, "bipedal"),
                hidden=bool(rec.get("hidden", False)),
            )

            try:
                if Species.objects.filter(name=name).exists():
                    if dry_run:
                        updated += 1
                        continue
                    obj = Species.objects.get(name=name)
                    for k, v in payload.items():
                        setattr(obj, k, v)
                    obj.full_clean()
                    obj.save()
                    updated += 1
                else:
                    if update_only:
                        skipped += 1
                        continue
                    if dry_run:
                        created += 1
                        continue
                    obj = Species(**payload)
                    obj.full_clean()
                    obj.save()
                    created += 1
            except ValidationError as ve:
                skipped += 1
                errors.append(f"[{i}] {name}: validation error: {ve}")
            except Exception as e:
                skipped += 1
                errors.append(f"[{i}] {name}: {e}")

        msg = f"Processed {len(data)} records → created={created}, updated={updated}, skipped={skipped}"
        if dry_run:
            msg = "[DRY-RUN] " + msg
        self.stdout.write(self.style.SUCCESS(msg))

        if errors:
            self.stdout.write(self.style.WARNING("Some records had issues:"))
            for line in errors:
                self.stdout.write("  - " + line)
