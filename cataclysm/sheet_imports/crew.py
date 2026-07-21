from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class CrewTabSchema:
    tab_name: str
    range_name: str
    first_row_number: int
    trait_columns: dict[int, str]
    rank_column: int
    role_column: int
    branch_column: int
    status_column: int
    profile_columns: dict[int, str] = field(default_factory=dict)


MAIN_CREW_SCHEMA = CrewTabSchema(
    tab_name='Main Crew',
    range_name='A3:V',
    first_row_number=3,
    trait_columns={
        4: 'Tactician',
        5: 'Medical',
        6: 'Scientist',
        7: 'Engineer',
        8: 'Strong',
        9: 'Tough',
        10: 'Agile',
        11: 'Stealthy',
        12: 'Cybernetic',
        13: 'Leader',
        14: 'Genius',
        15: 'Psychic',
        16: 'Flier',
        17: 'Mutant',
    },
    rank_column=18,
    role_column=19,
    branch_column=20,
    status_column=21,
)

OTHER_CREW_SCHEMA = CrewTabSchema(
    tab_name='Other Crew',
    range_name='A6:AG',
    first_row_number=6,
    trait_columns={
        4: 'Tactician',
        5: 'Medical',
        6: 'Scientist',
        7: 'Engineer',
        8: 'Strong',
        9: 'Tough',
        10: 'Agile',
        11: 'Stealthy',
        12: 'Cybernetic',
        13: 'Leader',
        14: 'Genius',
        15: 'Psychic',
        16: 'Arcane',
        17: 'Divine',
        18: 'Flier',
        19: 'Mutant',
    },
    rank_column=20,
    role_column=21,
    branch_column=22,
    status_column=23,
    profile_columns={
        24: 'origin',
        25: 'headed_to',
        26: 'reason',
        27: 'height',
        28: 'weight',
        29: 'hair_color',
        30: 'eyeball_color',
        31: 'iris_color',
        32: 'pupil_color',
    },
)

CREW_SCHEMAS = {schema.tab_name: schema for schema in (MAIN_CREW_SCHEMA, OTHER_CREW_SCHEMA)}


@dataclass(frozen=True)
class CrewRow:
    tab_name: str
    row_number: int
    name: str
    species_name: str
    age: int | None
    age_text: str
    sex: str
    traits: tuple[str, ...]
    rank: str
    role: str
    branch: str
    status: str
    profile_facts: dict[str, str]
    raw_values: tuple[str, ...]
    warnings: tuple[str, ...] = ()

    @property
    def row_fingerprint(self) -> str:
        identity = {'tab': self.tab_name, 'name': normalize_text(self.name)}
        return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()

    @property
    def content_fingerprint(self) -> str:
        payload = asdict(self)
        payload.pop('raw_values')
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def normalized_payload(self) -> dict:
        payload = asdict(self)
        payload.pop('raw_values')
        # Return the same JSON-native types Django's JSONField will read back
        # (notably lists rather than tuples) so unchanged rows compare equal.
        return json.loads(json.dumps(payload, sort_keys=True))


def normalize_text(value: object) -> str:
    return ' '.join(str(value or '').strip().split())


def parse_age(value: str) -> tuple[int | None, str]:
    age_text = normalize_text(value)
    if not age_text:
        return None, ''
    try:
        numeric = float(age_text)
    except ValueError:
        return None, age_text
    if numeric.is_integer() and numeric >= 0:
        return int(numeric), age_text
    return None, age_text


def _cell(row: list[str], index: int) -> str:
    return normalize_text(row[index]) if index < len(row) else ''


def parse_crew_rows(rows: Iterable[list[str]], schema: CrewTabSchema) -> list[CrewRow]:
    parsed = []
    for offset, raw_row in enumerate(rows):
        row = [str(value or '') for value in raw_row]
        row_number = schema.first_row_number + offset
        name = _cell(row, 0)
        if not name:
            continue

        warnings = []
        age, age_text = parse_age(_cell(row, 2))
        if age is None and age_text:
            warnings.append(f'Age retained as text: {age_text}')

        traits = tuple(
            trait_name
            for index, trait_name in schema.trait_columns.items()
            if _cell(row, index)
        )
        profile_facts = {
            key: value
            for index, key in schema.profile_columns.items()
            if (value := _cell(row, index))
        }
        parsed.append(
            CrewRow(
                tab_name=schema.tab_name,
                row_number=row_number,
                name=name,
                species_name=_cell(row, 1),
                age=age,
                age_text=age_text,
                sex=_cell(row, 3),
                traits=traits,
                rank=_cell(row, schema.rank_column),
                role=_cell(row, schema.role_column),
                branch=_cell(row, schema.branch_column),
                status=_cell(row, schema.status_column),
                profile_facts=profile_facts,
                raw_values=tuple(row),
                warnings=tuple(warnings),
            )
        )
    return parsed


def fingerprint_rows(rows: Iterable[CrewRow]) -> str:
    fingerprints = [row.content_fingerprint for row in rows]
    return hashlib.sha256(json.dumps(fingerprints).encode()).hexdigest()
