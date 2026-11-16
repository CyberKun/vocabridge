"""Discover vocabularies through the public Wikidata Query Service.

Wikidata content is CC0, so results can be reused freely. Please keep traffic light:
results are cached, and every request sends a descriptive User-Agent as Wikidata asks.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from collections.abc import Callable

from .. import __version__
from .base import CandidateVocabulary
from .cache import FileCache

ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = (f"vocabridge/{__version__} "
              "(https://github.com/YOUR-USERNAME/vocabridge; vocabulary discovery)")

# Wikidata classes whose instances (or instances of subclasses) count as vocabularies.
DEFAULT_CLASSES = {
    "Q324254": "ontology",
    "Q1469824": "controlled vocabulary",
}

QUERY_TEMPLATE = """
SELECT DISTINCT ?item ?itemLabel ?itemDescription ?homepage WHERE {{
  SERVICE wikibase:mwapi {{
    bd:serviceParam wikibase:endpoint "www.wikidata.org";
                    wikibase:api "EntitySearch";
                    mwapi:search "{keyword}";
                    mwapi:language "en";
                    mwapi:limit "50".
    ?item wikibase:apiOutputItem mwapi:item.
  }}
  VALUES ?vocabClass {{ {classes} }}
  ?item wdt:P31/wdt:P279* ?vocabClass .
  OPTIONAL {{ ?item wdt:P856 ?homepage . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
LIMIT {limit}
"""

Fetcher = Callable[[str], dict]


def _escape(keyword: str) -> str:
    return keyword.replace("\\", "\\\\").replace('"', '\\"').strip()


def build_query(keyword: str, limit: int = 10, classes: dict[str, str] | None = None) -> str:
    class_ids = " ".join(f"wd:{q}" for q in (classes or DEFAULT_CLASSES))
    return QUERY_TEMPLATE.format(keyword=_escape(keyword), classes=class_ids, limit=int(limit))


def http_fetch(query: str, timeout: float = 30.0) -> dict:
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/sparql-results+json",
    })
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_results(payload: dict, keyword: str) -> list[CandidateVocabulary]:
    found: dict[str, CandidateVocabulary] = {}
    for b in payload.get("results", {}).get("bindings", []):
        iri = b.get("item", {}).get("value", "")
        if not iri:
            continue
        qid = iri.rsplit("/", 1)[-1]
        cand = found.get(qid)
        if cand is None:
            found[qid] = CandidateVocabulary(
                identifier=qid,
                label=b.get("itemLabel", {}).get("value", qid),
                source=WikidataSource.name,
                description=b.get("itemDescription", {}).get("value", ""),
                homepage=b.get("homepage", {}).get("value", ""),
                matched_keywords=[keyword],
            )
        elif not cand.homepage and b.get("homepage"):
            cand.homepage = b["homepage"]["value"]
    return list(found.values())


class WikidataSource:
    name = "wikidata"

    def __init__(self, fetch: Fetcher | None = None, cache: FileCache | None = None,
                 classes: dict[str, str] | None = None):
        self._fetch = fetch or http_fetch
        self._cache = cache
        self._classes = classes or DEFAULT_CLASSES

    def search(self, keyword: str, limit: int = 10) -> list[CandidateVocabulary]:
        query = build_query(keyword, limit=limit, classes=self._classes)
        payload = self._cache.get(self.name, query) if self._cache else None
        if payload is None:
            payload = self._fetch(query)
            if self._cache:
                self._cache.set(self.name, query, payload)
        return parse_results(payload, keyword)[:limit]
