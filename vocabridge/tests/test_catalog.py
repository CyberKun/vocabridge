from vocabridge.catalog import WikidataSource, discover
from vocabridge.catalog.cache import FileCache
from vocabridge.catalog.wikidata import build_query


def binding(qid, label, homepage=None):
    b = {
        "item": {"value": f"http://www.wikidata.org/entity/{qid}"},
        "itemLabel": {"value": label},
        "itemDescription": {"value": f"{label} description"},
    }
    if homepage:
        b["homepage"] = {"value": homepage}
    return b


class FakeFetch:
    def __init__(self, responses):
        self.responses = responses
        self.queries = []

    def __call__(self, query):
        self.queries.append(query)
        for keyword, bindings in self.responses.items():
            if f'"{keyword}"' in query:
                return {"results": {"bindings": bindings}}
        return {"results": {"bindings": []}}


def test_build_query_escapes_and_uses_classes():
    q = build_query('pro"curement', limit=3)
    assert 'mwapi:search "pro\\"curement"' in q
    assert "wd:Q324254" in q and "wd:Q1469824" in q
    assert "LIMIT 3" in q


def test_search_and_merge():
    fetch = FakeFetch({
        "procurement": [binding("Q1", "Procurement Ontology", "https://example.org/po"),
                        binding("Q2", "Trade Vocabulary")],
        "supplier": [binding("Q1", "Procurement Ontology")],
    })
    source = WikidataSource(fetch=fetch)
    results = discover(source, ["procurement", "supplier", "procurement"])
    assert len(fetch.queries) == 2  # duplicate keyword searched once
    assert results[0].identifier == "Q1"
    assert results[0].matched_keywords == ["procurement", "supplier"]
    assert results[0].homepage == "https://example.org/po"
    assert results[0].source == "wikidata"


def test_cache_prevents_second_request(tmp_path):
    fetch = FakeFetch({"supplier": [binding("Q9", "Supplier Codes")]})
    source = WikidataSource(fetch=fetch, cache=FileCache(tmp_path))
    first = source.search("supplier")
    second = source.search("supplier")
    assert len(fetch.queries) == 1
    assert first == second


def test_custom_source_satisfies_protocol():
    from vocabridge.catalog import CandidateVocabulary, CatalogSource

    class LocalList:
        name = "local"

        def search(self, keyword, limit=10):
            return [CandidateVocabulary("x", "X", self.name)] if keyword == "x" else []

    assert isinstance(LocalList(), CatalogSource)
    assert [c.identifier for c in discover(LocalList(), ["x", "y"])] == ["x"]
