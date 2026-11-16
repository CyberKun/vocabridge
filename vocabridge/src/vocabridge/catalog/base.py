"""The catalog-source interface used to discover existing vocabularies.

A catalog source answers one question: "which published vocabularies might describe data
about these keywords?" Sources are interchangeable. vocabridge works with any of them, and
works offline with none of them, so it never depends on a single external project.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class CandidateVocabulary:
    """A vocabulary a catalog suggests for reuse. This is a lead to investigate, not a fact."""

    identifier: str  # stable ID or IRI in the source catalog
    label: str
    source: str  # name of the catalog source that returned it
    description: str = ""
    homepage: str = ""
    matched_keywords: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@runtime_checkable
class CatalogSource(Protocol):
    name: str

    def search(self, keyword: str, limit: int = 10) -> list[CandidateVocabulary]:
        """Return candidate vocabularies for a single keyword."""
        ...


def discover(source: CatalogSource, keywords: list[str],
             limit_per_keyword: int = 5) -> list[CandidateVocabulary]:
    """Search each keyword and merge results, keeping track of which keywords matched."""
    merged: dict[str, CandidateVocabulary] = {}
    for keyword in dict.fromkeys(k for k in keywords if k):
        for cand in source.search(keyword, limit=limit_per_keyword):
            existing = merged.get(cand.identifier)
            if existing is None:
                cand.matched_keywords = [keyword]
                merged[cand.identifier] = cand
            elif keyword not in existing.matched_keywords:
                existing.matched_keywords.append(keyword)
    return sorted(merged.values(), key=lambda c: (-len(c.matched_keywords), c.label.lower()))
