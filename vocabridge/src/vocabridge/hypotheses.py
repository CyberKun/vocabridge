"""The core data model: every proposed mapping is a hypothesis until a person accepts it.

A mapping file records, for each field, which vocabulary term was proposed, by which
method, with what evidence and confidence, and what a reviewer decided. Nothing is
published as RDF unless its hypothesis has status ``accepted``.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PROPOSED = "proposed"
ACCEPTED = "accepted"
REJECTED = "rejected"
STATUSES = (PROPOSED, ACCEPTED, REJECTED)

LITERAL = "literal"
IRI = "iri"

FORMAT_VERSION = 1


@dataclass
class Evidence:
    """One reason supporting (or weakening) a hypothesis."""

    kind: str  # e.g. "label-match", "alt-label-match", "domain", "range", "profile"
    detail: str
    weight: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Alternative:
    term: str
    label: str
    confidence: float


@dataclass
class Review:
    status: str = PROPOSED
    reviewer: str = ""
    reviewed_at: str = ""
    note: str = ""


@dataclass
class MappingHypothesis:
    field: str
    term: str | None
    term_label: str = ""
    value_kind: str = LITERAL
    datatype: str | None = None
    target_class: str | None = None  # for IRI values: class of the referenced resource
    confidence: float = 0.0
    method: str = ""
    evidence: list[Evidence] = field(default_factory=list)
    alternatives: list[Alternative] = field(default_factory=list)
    review: Review = field(default_factory=Review)

    @property
    def status(self) -> str:
        return self.review.status

    def set_status(self, status: str, reviewer: str = "", note: str = "") -> None:
        if status not in STATUSES:
            raise ValueError(f"Unknown status {status!r}; expected one of {STATUSES}")
        if status == ACCEPTED and not self.term:
            raise ValueError(f"Cannot accept field {self.field!r}: no term was proposed")
        self.review = Review(
            status=status,
            reviewer=reviewer,
            reviewed_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            note=note,
        )

    @classmethod
    def from_dict(cls, data: dict) -> MappingHypothesis:
        data = dict(data)
        data["evidence"] = [Evidence(**e) for e in data.get("evidence", [])]
        data["alternatives"] = [Alternative(**a) for a in data.get("alternatives", [])]
        data["review"] = Review(**data.get("review", {}))
        return cls(**data)


@dataclass
class MappingSet:
    """All hypotheses for one dataset, plus how subjects are identified and typed."""

    dataset: str
    base_iri: str
    id_field: str | None
    subject: MappingHypothesis  # field="__subject__", term = the class of each row
    fields: list[MappingHypothesis]
    vocabularies: list[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    generator: str = "vocabridge"
    format_version: int = FORMAT_VERSION
    delimiter: str | None = ","

    def hypothesis(self, field_name: str) -> MappingHypothesis:
        if field_name == self.subject.field:
            return self.subject
        for h in self.fields:
            if h.field == field_name:
                return h
        raise KeyError(f"No hypothesis for field {field_name!r}")

    def all(self) -> list[MappingHypothesis]:
        return [self.subject, *self.fields]

    def accepted_fields(self) -> list[MappingHypothesis]:
        return [h for h in self.fields if h.status == ACCEPTED]

    def counts(self) -> dict[str, int]:
        counts = {s: 0 for s in STATUSES}
        for h in self.all():
            counts[h.status] += 1
        return counts

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def from_dict(cls, data: dict) -> MappingSet:
        version = data.get("format_version", FORMAT_VERSION)
        if version > FORMAT_VERSION:
            raise ValueError(f"Mapping file format {version} is newer than this vocabridge")
        return cls(
            dataset=data["dataset"],
            base_iri=data["base_iri"],
            id_field=data.get("id_field"),
            subject=MappingHypothesis.from_dict(data["subject"]),
            fields=[MappingHypothesis.from_dict(h) for h in data["fields"]],
            vocabularies=data.get("vocabularies", []),
            created_at=data.get("created_at", ""),
            generator=data.get("generator", "vocabridge"),
            format_version=version,
            delimiter=data.get("delimiter", ","),
        )

    @classmethod
    def load(cls, path: str | Path) -> MappingSet:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
