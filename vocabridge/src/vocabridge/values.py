"""Evidence from the data values themselves, not just from column names.

Column names are often misleading ("ref", "code", "partner"). Values are harder to fake:

* **Value patterns**: the shape of the values (two-letter upper-case codes, three-letter codes,
  e-mail addresses, URLs, prefixed identifiers) hints at what a field holds.
* **Value overlap with linked datasets**: if 95% of the values in ``payee_ref`` appear as
  identifiers in an already-reviewed suppliers dataset, ``payee_ref`` almost certainly refers
  to suppliers, whatever it is called.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .text import local_name

# name -> (regex every value must match, words that suggest a property is about this kind of value)
PATTERNS: dict[str, tuple[re.Pattern, set[str], str]] = {
    "email": (re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$"),
              {"email", "mail", "contact"}, "e-mail addresses"),
    "url": (re.compile(r"^https?://\S+$"),
            {"url", "homepage", "website", "page", "link", "uri", "iri"}, "URLs"),
    "upper-code-2": (re.compile(r"^[A-Z]{2}$"),
                     {"country", "code", "iso", "region", "language"},
                     "two-letter upper-case codes (e.g. ISO 3166-1 alpha-2 country codes)"),
    "upper-code-3": (re.compile(r"^[A-Z]{3}$"),
                     {"currency", "code", "iso", "country"},
                     "three-letter upper-case codes (e.g. ISO 4217 currency codes)"),
    "prefixed-identifier": (re.compile(r"^[A-Za-z]{1,6}[-_/]?[0-9][0-9A-Za-z\-_/]*$"),
                            {"id", "identifier", "number", "code", "reference", "key"},
                            "prefixed identifiers (e.g. PO-24-0001)"),
}

# Overlap thresholds for reference evidence.
STRONG_OVERLAP = 0.8
WEAK_OVERLAP = 0.2


def detect_pattern(values: list[str], min_values: int = 2) -> str | None:
    """Return the name of the first pattern that every non-empty value matches."""
    present = [v.strip() for v in values if v and v.strip()]
    if len(present) < min_values:
        return None
    for name, (regex, _hints, _desc) in PATTERNS.items():
        if all(regex.match(v) for v in present):
            return name
    return None


def pattern_hints(pattern: str | None) -> set[str]:
    return PATTERNS[pattern][1] if pattern in PATTERNS else set()


def pattern_description(pattern: str) -> str:
    return PATTERNS[pattern][2]


@dataclass
class LinkedDataset:
    """An already-reviewed dataset whose identifiers other datasets may refer to."""

    name: str
    class_iri: str
    id_field: str
    values: frozenset[str]

    @property
    def label(self) -> str:
        return f"{self.name}.{self.id_field}"

    @property
    def class_name(self) -> str:
        return local_name(self.class_iri)


def load_linked(mapping_file: str | Path) -> LinkedDataset:
    """Load identifiers from a mapping file whose subject class has been accepted."""
    # Local imports: profiling imports this module for detect_pattern.
    from .generate import dataset_path
    from .hypotheses import ACCEPTED, MappingSet
    from .profiling import read_records

    mapping = MappingSet.load(mapping_file)
    if mapping.subject.status != ACCEPTED or not mapping.subject.term:
        raise ValueError(f"{mapping_file}: accept the subject class before linking to it")
    if not mapping.id_field:
        raise ValueError(f"{mapping_file}: has no identifier field to link to")
    path = dataset_path(mapping, mapping_file)
    values = frozenset(
        (row.get(mapping.id_field) or "").strip()
        for row in read_records(path)
        if (row.get(mapping.id_field) or "").strip()
    )
    return LinkedDataset(name=Path(path).stem, class_iri=mapping.subject.term,
                         id_field=mapping.id_field, values=values)


def containment(values: list[str], linked: LinkedDataset) -> tuple[float, int, int]:
    """Share of distinct non-empty ``values`` found among the linked identifiers."""
    distinct = {v.strip() for v in values if v and v.strip()}
    if not distinct:
        return 0.0, 0, 0
    found = len(distinct & linked.values)
    return found / len(distinct), found, len(distinct)
