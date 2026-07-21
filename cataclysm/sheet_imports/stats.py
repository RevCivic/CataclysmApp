from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Iterable

from .crew import normalize_text


STATS_TAB = 'Stats'
STATS_RANGE = 'A1:BH'


@dataclass(frozen=True)
class StatsRow:
    row_number: int
    name: str
    capabilities: dict[str, str]
    raw_values: tuple[str, ...]
    warnings: tuple[str, ...] = ()

    @property
    def row_fingerprint(self):
        identity = {'tab': STATS_TAB, 'name': normalize_text(self.name).casefold()}
        return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()

    def normalized_payload(self):
        payload = asdict(self)
        payload.pop('raw_values')
        return json.loads(json.dumps(payload, sort_keys=True))


def parse_stats_rows(rows: Iterable[list[str]]) -> list[StatsRow]:
    values = [[str(value or '') for value in row] for row in rows]
    if not values:
        return []
    headers = [normalize_text(value) for value in values[0]]
    parsed = []
    for row_number, row in enumerate(values[1:], start=2):
        name = normalize_text(row[0] if row else '')
        if not name:
            continue
        warnings = []
        capabilities = {}
        for index, marker in enumerate(row[1:], start=1):
            marker = normalize_text(marker)
            if not marker:
                continue
            heading = headers[index] if index < len(headers) else ''
            if not heading:
                warnings.append(f'Ignored marker in unnamed column {index + 1}')
                continue
            capabilities[heading] = marker
        parsed.append(
            StatsRow(
                row_number=row_number,
                name=name,
                capabilities=capabilities,
                raw_values=tuple(row),
                warnings=tuple(warnings),
            )
        )
    return parsed
