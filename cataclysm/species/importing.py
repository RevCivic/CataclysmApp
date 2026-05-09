from __future__ import annotations

import re
from typing import Any, Mapping

SPECIES_IMPORT_FIELDS = [
    {"name": "species_name", "label": "Species Name", "kind": "text", "required": True},
    {"name": "home_world", "label": "Home World", "kind": "text"},
    {"name": "size", "label": "Size", "kind": "text"},
    {"name": "type", "label": "Type", "kind": "text"},
    {"name": "air", "label": "Air", "kind": "text"},
    {"name": "sex", "label": "Sex", "kind": "text"},
    {"name": "strength", "label": "Strength", "kind": "integer"},
    {"name": "natural_weapon", "label": "Natural Weapon", "kind": "boolean"},
    {"name": "toughness", "label": "Toughness", "kind": "integer"},
    {"name": "natural_armor", "label": "Natural Armor", "kind": "boolean"},
    {"name": "speed", "label": "Speed", "kind": "integer"},
    {"name": "intelligence", "label": "Intelligence", "kind": "integer"},
    {"name": "flier", "label": "Flier", "kind": "boolean"},
    {"name": "aquatic", "label": "Aquatic", "kind": "boolean"},
    {"name": "amphibious", "label": "Amphibious", "kind": "boolean"},
    {"name": "tech_level", "label": "Tech Level", "kind": "text"},
    {"name": "telepathic", "label": "Telepathic", "kind": "boolean"},
    {"name": "psionic", "label": "Psionic", "kind": "boolean"},
    {"name": "light_grav", "label": "Light Grav", "kind": "boolean"},
    {"name": "heavy_grav", "label": "Heavy Grav", "kind": "boolean"},
    {"name": "status", "label": "Status", "kind": "text"},
    {"name": "locomotion", "label": "Locomotion", "kind": "text"},
    {"name": "society", "label": "Society", "kind": "text"},
    {"name": "attributes", "label": "Attributes", "kind": "list"},
    {"name": "hours_of_sleep", "label": "Hours of Sleep", "kind": "integer"},
    {"name": "days_without_food", "label": "Days Without Food", "kind": "integer"},
    {"name": "days_without_water", "label": "Days Without Water", "kind": "integer"},
    {"name": "background", "label": "Background", "kind": "text"},
    {"name": "sociology", "label": "Sociology", "kind": "text"},
    {"name": "physiology", "label": "Physiology", "kind": "text"},
    {"name": "special_abilities", "label": "Special Abilities", "kind": "list"},
    {"name": "match_status", "label": "Match Status", "kind": "text"},
]

SPECIES_FIELD_NAMES = [field["name"] for field in SPECIES_IMPORT_FIELDS]
SPECIES_FIELD_MAP = {field["name"]: field for field in SPECIES_IMPORT_FIELDS}

_FIELD_ALIASES = {
    "name": "species_name",
    "species": "species_name",
    "strength_rating": "strength",
    "toughness_rating": "toughness",
    "speed_rating": "speed",
    "intelligence_rating": "intelligence",
    "natural_weapons": "natural_weapon",
    "can_fly": "flier",
    "accord_status": "status",
    "locomotion_method": "locomotion",
    "racial_traits": "attributes",
}


def normalize_header(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower())
    return normalized.strip("_")


def guess_field_mapping(headers: list[str]) -> dict[str, str]:
    normalized_headers = {normalize_header(header): header for header in headers}
    mapping: dict[str, str] = {}
    for field in SPECIES_IMPORT_FIELDS:
        field_name = field["name"]
        candidates = {
            normalize_header(field_name),
            normalize_header(field["label"]),
        }
        alias = _FIELD_ALIASES.get(field_name)
        if alias:
            candidates.add(normalize_header(alias))
        for source_name, target_name in _FIELD_ALIASES.items():
            if target_name == field_name:
                candidates.add(normalize_header(source_name))
        for candidate in candidates:
            if candidate in normalized_headers:
                mapping[field_name] = normalized_headers[candidate]
                break
    return mapping


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in {"1", "true", "t", "yes", "y", "x", "on"}


def parse_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        try:
            return int(float(str(value).strip()))
        except (TypeError, ValueError):
            return None


def parse_list(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).replace("\r", "\n")
    for separator in (";", "|", "\n"):
        if separator in text:
            parts = [part.strip() for part in text.split(separator)]
            return [part for part in parts if part]
    if ',' in text:
        parts = [part.strip() for part in text.split(',')]
        return [part for part in parts if part]
    return [text.strip()] if text.strip() else []


def serialize_list(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    return str(value)


def build_species_payload(source: Mapping[str, Any], field_mapping: Mapping[str, str] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for field in SPECIES_IMPORT_FIELDS:
        field_name = field["name"]
        source_key = field_mapping[field_name] if field_mapping is not None else field_name
        if not source_key:
            continue
        if source_key not in source:
            continue
        raw_value = source.get(source_key)
        kind = field["kind"]
        if kind == "boolean":
            payload[field_name] = parse_bool(raw_value)
        elif kind == "integer":
            payload[field_name] = parse_int(raw_value)
        elif kind == "list":
            payload[field_name] = parse_list(raw_value)
        else:
            payload[field_name] = str(raw_value).strip() if raw_value is not None else ""
    return payload
