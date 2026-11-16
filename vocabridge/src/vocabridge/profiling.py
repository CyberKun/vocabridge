"""Profile an input dataset: field names, inferred types and sample values.

The profile is the only view of the data that later stages see. It is deliberately
small and serialisable so that it can be stored next to the mapping file as evidence.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

from .values import detect_pattern

# Inferred types, from most to least specific. "string" is the fallback.
TYPE_ORDER = ("boolean", "integer", "decimal", "date", "string")

_BOOL_VALUES = {"true", "false", "yes", "no", "y", "n", "t", "f"}
_INT_RE = re.compile(r"^[+-]?\d+$")
_DEC_RE = re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?$")


@dataclass
class FieldProfile:
    name: str
    inferred_type: str
    row_count: int
    missing_count: int
    distinct_count: int
    samples: list[str] = field(default_factory=list)
    pattern: str | None = None  # shape shared by every value, see values.PATTERNS

    @property
    def is_complete(self) -> bool:
        """True when no row is missing a value for this field."""
        return self.missing_count == 0

    @property
    def is_unique(self) -> bool:
        """True when every non-missing value is distinct (a candidate identifier)."""
        present = self.row_count - self.missing_count
        return present > 0 and self.distinct_count == present


@dataclass
class DatasetProfile:
    source: str
    name: str
    row_count: int
    fields: list[FieldProfile]

    def field(self, name: str) -> FieldProfile:
        for f in self.fields:
            if f.name == name:
                return f
        raise KeyError(f"Unknown field: {name}")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> DatasetProfile:
        return cls(
            source=data["source"],
            name=data["name"],
            row_count=data["row_count"],
            fields=[FieldProfile(**f) for f in data["fields"]],
        )


def _is_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def infer_type(values: list[str]) -> str:
    """Return the most specific type that every non-empty value satisfies."""
    present = [v.strip() for v in values if v is not None and v.strip() != ""]
    if not present:
        return "string"
    checks = {
        "boolean": lambda v: v.lower() in _BOOL_VALUES,
        "integer": lambda v: bool(_INT_RE.match(v)),
        "decimal": lambda v: bool(_DEC_RE.match(v)),
        "date": _is_date,
    }
    for type_name in TYPE_ORDER[:-1]:
        if all(checks[type_name](v) for v in present):
            return type_name
    return "string"


def read_records(path: str | Path) -> list[dict[str, str]]:
    """Read a CSV file or a JSON array of flat objects into a list of string dicts."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
            raise ValueError("JSON input must be an array of flat objects")
        return [
            {k: "" if v is None else str(v).lower() if isinstance(v, bool) else str(v)
             for k, v in row.items()}
            for row in data
        ]
    raise ValueError(f"Unsupported input format: {suffix} (expected .csv or .json)")


def profile_records(records: list[dict[str, str]], source: str, name: str,
                    sample_size: int = 5) -> DatasetProfile:
    field_names: list[str] = []
    for row in records:
        for key in row:
            if key not in field_names:
                field_names.append(key)

    fields = []
    for fname in field_names:
        values = [row.get(fname) or "" for row in records]
        present = [v for v in values if v.strip() != ""]
        distinct = list(dict.fromkeys(present))
        fields.append(
            FieldProfile(
                name=fname,
                inferred_type=infer_type(values),
                row_count=len(values),
                missing_count=len(values) - len(present),
                distinct_count=len(distinct),
                samples=distinct[:sample_size],
                pattern=detect_pattern(values),
            )
        )
    return DatasetProfile(source=source, name=name, row_count=len(records), fields=fields)


def profile_file(path: str | Path, sample_size: int = 5) -> DatasetProfile:
    path = Path(path)
    return profile_records(read_records(path), source=str(path), name=path.stem,
                           sample_size=sample_size)
