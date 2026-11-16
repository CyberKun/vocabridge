"""Small text utilities used for lexical matching of field names and vocabulary terms."""

from __future__ import annotations

import re

_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_SPLIT_RE = re.compile(r"[^A-Za-z0-9]+")

# Tokens that carry little meaning on their own when comparing names.
STOPWORDS = {"the", "a", "an", "of", "has", "is", "to", "for", "in", "on", "by", "at"}


def tokens(text: str) -> list[str]:
    """Split snake_case, kebab-case, camelCase and plain text into lower-case tokens."""
    parts = []
    for chunk in _SPLIT_RE.split(text):
        if chunk:
            parts.extend(_CAMEL_RE.split(chunk))
    return [singular(p.lower()) for p in parts if p and p.lower() not in STOPWORDS]


def singular(word: str) -> str:
    """Very small English singulariser, good enough for column and file names."""
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 4 and word.endswith(("ses", "xes", "ches", "shes")):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def local_name(iri: str) -> str:
    """Return the part of an IRI after the last '#' or '/'."""
    for sep in ("#", "/"):
        if sep in iri:
            iri = iri.rsplit(sep, 1)[1]
    return iri
