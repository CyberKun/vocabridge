"""Load the classes and properties of an RDF vocabulary so that fields can be matched to them.

Any RDFS/OWL vocabulary that rdflib can parse (Turtle, RDF/XML, JSON-LD, N-Triples) works.
Users bring their own vocabulary files; vocabridge does not bundle third-party vocabularies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from rdflib import OWL, RDF, RDFS, SKOS, Graph, Literal, URIRef

from .text import local_name

CLASS = "class"
DATATYPE_PROPERTY = "datatype_property"
OBJECT_PROPERTY = "object_property"
PROPERTY = "property"  # a property whose kind cannot be determined

_CLASS_TYPES = (OWL.Class, RDFS.Class)
_PROPERTY_TYPES = {
    OWL.DatatypeProperty: DATATYPE_PROPERTY,
    OWL.ObjectProperty: OBJECT_PROPERTY,
    RDF.Property: PROPERTY,
    OWL.AnnotationProperty: PROPERTY,
}

XSD_NS = "http://www.w3.org/2001/XMLSchema#"


@dataclass
class Term:
    iri: str
    kind: str
    label: str
    alt_labels: list[str] = field(default_factory=list)
    comment: str = ""
    domains: list[str] = field(default_factory=list)
    ranges: list[str] = field(default_factory=list)
    vocabulary: str = ""

    @property
    def is_class(self) -> bool:
        return self.kind == CLASS

    @property
    def is_property(self) -> bool:
        return not self.is_class

    @property
    def range_is_datatype(self) -> bool:
        return any(r.startswith(XSD_NS) or r == str(RDFS.Literal) for r in self.ranges)

    @property
    def names(self) -> list[str]:
        """All human-readable names for the term, used for matching."""
        return [self.label, local_name(self.iri), *self.alt_labels]


def _english(graph: Graph, subject: URIRef, predicate: URIRef) -> list[str]:
    values = []
    for obj in graph.objects(subject, predicate):
        if isinstance(obj, Literal) and (not obj.language or obj.language.startswith("en")):
            values.append(str(obj))
    return values


def terms_from_graph(graph: Graph, vocabulary: str = "") -> list[Term]:
    kinds: dict[URIRef, str] = {}
    for cls_type in _CLASS_TYPES:
        for s in graph.subjects(RDF.type, cls_type):
            if isinstance(s, URIRef):
                kinds[s] = CLASS
    for prop_type, kind in _PROPERTY_TYPES.items():
        for s in graph.subjects(RDF.type, prop_type):
            if isinstance(s, URIRef) and kinds.get(s) in (None, PROPERTY):
                kinds[s] = kind

    terms = []
    for iri, kind in kinds.items():
        labels = _english(graph, iri, RDFS.label) or _english(graph, iri, SKOS.prefLabel)
        ranges = [str(o) for o in graph.objects(iri, RDFS.range) if isinstance(o, URIRef)]
        if kind == PROPERTY and ranges:
            kind = DATATYPE_PROPERTY if all(
                r.startswith(XSD_NS) or r == str(RDFS.Literal) for r in ranges
            ) else OBJECT_PROPERTY
        comments = _english(graph, iri, RDFS.comment) or _english(graph, iri, SKOS.definition)
        terms.append(
            Term(
                iri=str(iri),
                kind=kind,
                label=labels[0] if labels else local_name(str(iri)),
                alt_labels=_english(graph, iri, SKOS.altLabel),
                comment=comments[0] if comments else "",
                domains=[str(o) for o in graph.objects(iri, RDFS.domain) if isinstance(o, URIRef)],
                ranges=ranges,
                vocabulary=vocabulary,
            )
        )
    terms.sort(key=lambda t: t.iri)
    return terms


def load_vocabulary(path: str | Path) -> list[Term]:
    path = Path(path)
    graph = Graph()
    graph.parse(str(path))
    return terms_from_graph(graph, vocabulary=path.name)


def load_vocabularies(paths: list[str | Path]) -> list[Term]:
    terms: dict[str, Term] = {}
    for p in paths:
        for term in load_vocabulary(p):
            terms.setdefault(term.iri, term)
    return list(terms.values())
