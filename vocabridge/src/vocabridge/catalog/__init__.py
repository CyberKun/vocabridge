"""Pluggable catalog sources for discovering reusable vocabularies."""

from .base import CandidateVocabulary, CatalogSource, discover
from .wikidata import WikidataSource

SOURCES = {"wikidata": WikidataSource}

__all__ = ["SOURCES", "CandidateVocabulary", "CatalogSource", "WikidataSource", "discover"]
