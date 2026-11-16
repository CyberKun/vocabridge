"""Propose mapping hypotheses for each field using transparent lexical rules.

This is the *baseline* suggester. It is intentionally simple and explainable: every score
is built from named pieces of evidence that are written into the mapping file. Smarter
suggesters (for example an LLM) can be added later, but they must produce the same
``MappingHypothesis`` objects, so the review and generation steps never change.
"""

from __future__ import annotations

from difflib import SequenceMatcher

from .hypotheses import IRI, LITERAL, Alternative, Evidence, MappingHypothesis, MappingSet
from .profiling import DatasetProfile, FieldProfile
from .text import local_name, tokens
from .values import (
    STRONG_OVERLAP,
    WEAK_OVERLAP,
    LinkedDataset,
    containment,
    pattern_description,
    pattern_hints,
)
from .vocab import XSD_NS, Term

METHOD = "lexical-baseline"
SUBJECT_FIELD = "__subject__"

# Tokens suggesting a field holds an identifier or a reference to another resource.
IDENTIFIER_TOKENS = {"id", "identifier", "number", "no", "code", "key", "ref", "reference"}

XSD_FOR_TYPE = {
    "boolean": XSD_NS + "boolean",
    "integer": XSD_NS + "integer",
    "decimal": XSD_NS + "decimal",
    "date": XSD_NS + "date",
    "string": XSD_NS + "string",
}

# Which inferred profile types can be stored in which XSD range without loss.
_COMPATIBLE = {
    "boolean": {"boolean", "string"},
    "integer": {"integer", "int", "long", "short", "nonNegativeInteger", "positiveInteger",
                "decimal", "double", "float", "string"},
    "decimal": {"decimal", "double", "float", "string"},
    "date": {"date", "dateTime", "string"},
    "string": {"string", "normalizedString", "token", "anyURI", "language"},
}

MIN_CONFIDENCE = 0.35
ALT_LABEL_FACTOR = 0.9


def name_similarity(a: list[str], b: list[str]) -> float:
    """Blend of token overlap and character similarity, in [0, 1]."""
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    jaccard = len(sa & sb) / len(sa | sb)
    if sa == sb:
        return 1.0
    ratio = SequenceMatcher(None, " ".join(a), " ".join(b)).ratio()
    return 0.6 * jaccard + 0.4 * ratio


def _best_name_match(field_tokens: list[str], term: Term) -> tuple[float, Evidence | None]:
    best, evidence = 0.0, None
    primary = [term.label, local_name(term.iri)]
    for name in primary:
        score = name_similarity(field_tokens, tokens(name))
        if score > best:
            best = score
            evidence = Evidence("label-match", f"field tokens {field_tokens} vs {name!r}",
                                round(score, 3))
    for alt in term.alt_labels:
        score = name_similarity(field_tokens, tokens(alt)) * ALT_LABEL_FACTOR
        if score > best:
            best = score
            evidence = Evidence("alt-label-match",
                                f"field tokens {field_tokens} vs alternative label {alt!r}",
                                round(score, 3))
    return best, evidence


def _range_check(profile: FieldProfile, term: Term) -> Evidence | None:
    datatypes = [r[len(XSD_NS):] for r in term.ranges if r.startswith(XSD_NS)]
    if not datatypes:
        return None
    allowed = _COMPATIBLE.get(profile.inferred_type, set())
    if any(d in allowed for d in datatypes):
        return Evidence("range", f"values look like {profile.inferred_type}; range "
                        f"{', '.join('xsd:' + d for d in datatypes)} is compatible", 0.05)
    return Evidence("range", f"values look like {profile.inferred_type} but range is "
                    f"{', '.join('xsd:' + d for d in datatypes)}", -0.25)


def _link_evidence(values: list[str], term: Term,
                   links: list[LinkedDataset]) -> tuple[float, Evidence | None, str | None]:
    """Compare a field's values with identifiers of linked datasets the term may point to."""
    best: tuple[float, Evidence | None, str | None] = (0.0, None, None)
    best_share = -1.0
    for link in links:
        if term.ranges and link.class_iri not in term.ranges:
            continue
        share, found, total = containment(values, link)
        if total == 0 or share <= best_share:
            continue
        best_share = share
        detail = (f"{found} of {total} distinct values ({share:.0%}) appear in {link.label}, "
                  f"the identifiers of {link.class_name}")
        if share >= STRONG_OVERLAP:
            weight = round(0.45 * share, 3)
            best = (weight, Evidence("value-overlap", detail, weight), link.class_iri)
        elif share < WEAK_OVERLAP:
            best = (-0.2, Evidence("value-overlap", detail, -0.2), None)
        else:
            best = (0.0, Evidence("value-overlap", detail + " (inconclusive)", 0.0), None)
    return best


def score_property(profile: FieldProfile, term: Term, subject_class: str | None,
                   class_tokens: list[str], values: list[str] | None = None,
                   links: list[LinkedDataset] | None = None,
                   ) -> tuple[float, list[Evidence], str, str | None]:
    """Score how well ``term`` fits ``profile``.

    Returns (confidence, evidence, value_kind, target_class). ``values`` and ``links`` are
    optional; when given, the field's values are compared with identifiers of linked datasets.
    """
    field_tokens = tokens(profile.name)
    looks_like_reference = bool(set(field_tokens) & IDENTIFIER_TOKENS)
    value_kind = IRI if term.kind == "object_property" else LITERAL

    # An object property is matched on the field name without its "id"-like suffix,
    # because "vendor_id" refers to a vendor rather than naming an identifier property.
    compare_tokens = field_tokens
    if value_kind == IRI:
        compare_tokens = [t for t in field_tokens if t not in IDENTIFIER_TOKENS] or field_tokens

    term_tokens = {tok for name in term.names for tok in tokens(name)}
    shares_token = bool(set(compare_tokens) & term_tokens)

    score, name_ev = _best_name_match(compare_tokens, term)
    # Short field names such as "name" often mean "<class> name" (e.g. supplierName).
    # Only try this when the field already shares a word with the term, otherwise
    # "notes" would drift towards "supplier name" just because of the class.
    if shares_token and class_tokens and not set(class_tokens) & set(compare_tokens):
        ctx_score, ctx_ev = _best_name_match(class_tokens + compare_tokens, term)
        if ctx_score > score + 0.05:
            score, name_ev = ctx_score * 0.95, ctx_ev
            if name_ev:
                name_ev.detail += " (with class context)"
                name_ev.weight = round(score, 3)

    evidence = [name_ev] if name_ev else []
    confidence = score * 0.85
    target_class = term.ranges[0] if value_kind == IRI and term.ranges else None

    link_weight, link_ev, link_class = 0.0, None, None
    if value_kind == IRI and values and links:
        link_weight, link_ev, link_class = _link_evidence(values, term, links)
    values_prove_link = link_weight > 0

    if not shares_token and not values_prove_link:
        # Character similarity alone is weak evidence; schema hints may not promote it.
        evidence.append(Evidence("no-shared-word", "field and term share no word", 0.0))
        return max(0.0, min(1.0, round(confidence, 3))), evidence, value_kind, target_class

    if link_ev:
        evidence.append(link_ev)
        confidence += link_weight
        target_class = link_class or target_class

    if value_kind == IRI and not looks_like_reference and not values_prove_link:
        evidence.append(Evidence("reference", "object property, but the field name does not "
                                 "look like an identifier or reference", -0.1))
        confidence -= 0.1

    if term.domains and subject_class:
        if subject_class in term.domains:
            evidence.append(Evidence("domain", f"domain includes {local_name(subject_class)}",
                                     0.12))
            confidence += 0.12
        else:
            evidence.append(Evidence(
                "domain", f"domain is {', '.join(local_name(d) for d in term.domains)}, "
                f"not {local_name(subject_class)}", -0.15))
            confidence -= 0.15

    if value_kind == LITERAL:
        range_ev = _range_check(profile, term)
        if range_ev:
            evidence.append(range_ev)
            confidence += range_ev.weight
        hints = pattern_hints(profile.pattern)
        described_by = term_tokens | set(tokens(term.comment))
        if hints & described_by:
            evidence.append(Evidence(
                "value-pattern", f"all values are {pattern_description(profile.pattern)}; "
                f"the term mentions {', '.join(sorted(hints & described_by))}", 0.08))
            confidence += 0.08

    if profile.missing_count:
        evidence.append(Evidence("profile", f"{profile.missing_count} of {profile.row_count} "
                                 "rows have no value", 0.0))

    return max(0.0, min(1.0, round(confidence, 3))), evidence, value_kind, target_class


def suggest_subject_class(profile: DatasetProfile, terms: list[Term]) -> MappingHypothesis:
    name_tokens = tokens(profile.name)
    classes = [t for t in terms if t.is_class]
    properties = [t for t in terms if t.is_property]

    # Domain votes: classes that are the domain of properties resembling the fields.
    votes: dict[str, int] = {}
    for fp in profile.fields:
        best = max(properties, default=None,
                   key=lambda t: _best_name_match(tokens(fp.name), t)[0])
        if best is not None and _best_name_match(tokens(fp.name), best)[0] >= 0.6:
            for d in best.domains:
                votes[d] = votes.get(d, 0) + 1

    scored = []
    for cls in classes:
        score, name_ev = _best_name_match(name_tokens, cls)
        evidence = [name_ev] if name_ev else []
        confidence = score * 0.8
        if votes.get(cls.iri):
            bonus = min(0.3, 0.06 * votes[cls.iri])
            evidence.append(Evidence("domain-votes", f"{votes[cls.iri]} field(s) match properties "
                                     f"whose domain is {cls.label}", round(bonus, 3)))
            confidence += bonus
        scored.append((min(1.0, round(confidence, 3)), cls, evidence))
    scored.sort(key=lambda x: (-x[0], x[1].iri))

    if not scored or scored[0][0] < MIN_CONFIDENCE:
        return MappingHypothesis(field=SUBJECT_FIELD, term=None, method=METHOD,
                                 confidence=scored[0][0] if scored else 0.0,
                                 evidence=[Evidence("no-match", "no class matched the dataset "
                                                    f"name {profile.name!r}")],
                                 alternatives=[Alternative(c.iri, c.label, s)
                                               for s, c, _ in scored[:3] if s > 0.15])
    conf, cls, evidence = scored[0]
    return MappingHypothesis(
        field=SUBJECT_FIELD, term=cls.iri, term_label=cls.label, value_kind=IRI,
        confidence=conf, method=METHOD, evidence=evidence,
        alternatives=[Alternative(c.iri, c.label, s) for s, c, _ in scored[1:4] if s > 0.15],
    )


def choose_id_field(profile: DatasetProfile) -> str | None:
    """Pick the field used to mint subject IRIs: complete, unique and identifier-like."""
    candidates = [f for f in profile.fields if f.is_complete and f.is_unique]
    for f in candidates:
        if set(tokens(f.name)) & IDENTIFIER_TOKENS:
            return f.name
    return candidates[0].name if candidates else None


def suggest_field(profile: FieldProfile, terms: list[Term], subject_class: str | None,
                  class_tokens: list[str], top_k: int = 3, values: list[str] | None = None,
                  links: list[LinkedDataset] | None = None) -> MappingHypothesis:
    scored = []
    targets: dict[str, str | None] = {}
    for term in terms:
        if not term.is_property:
            continue
        conf, evidence, value_kind, target = score_property(
            profile, term, subject_class, class_tokens, values=values, links=links)
        if conf > 0:
            scored.append((conf, term, evidence, value_kind))
            targets[term.iri] = target
    scored.sort(key=lambda x: (-x[0], x[1].iri))

    alternatives = [Alternative(t.iri, t.label, c) for c, t, _, _ in scored[1:top_k + 1]
                    if c >= 0.2]
    if not scored or scored[0][0] < MIN_CONFIDENCE:
        return MappingHypothesis(
            field=profile.name, term=None, method=METHOD,
            confidence=scored[0][0] if scored else 0.0,
            datatype=XSD_FOR_TYPE[profile.inferred_type],
            evidence=[Evidence("no-match", "no property scored above "
                               f"{MIN_CONFIDENCE}; needs a human or a better suggester")],
            alternatives=[Alternative(t.iri, t.label, c) for c, t, _, _ in scored[:top_k]
                          if c >= 0.2],
        )

    conf, term, evidence, value_kind = scored[0]
    datatype = None
    target_class = None
    if value_kind == LITERAL:
        ranges = [r for r in term.ranges if r.startswith(XSD_NS)]
        datatype = ranges[0] if ranges else XSD_FOR_TYPE[profile.inferred_type]
    else:
        target_class = targets.get(term.iri)
    return MappingHypothesis(
        field=profile.name, term=term.iri, term_label=term.label, value_kind=value_kind,
        datatype=datatype, target_class=target_class, confidence=conf, method=METHOD,
        evidence=evidence, alternatives=alternatives,
    )


def suggest_mappings(profile: DatasetProfile, terms: list[Term], base_iri: str,
                     vocabularies: list[str] | None = None,
                     records: list[dict[str, str]] | None = None,
                     links: list[LinkedDataset] | None = None) -> MappingSet:
    """Propose hypotheses for every field.

    ``records`` (the full rows) and ``links`` (already-reviewed datasets) are optional; with
    both, reference fields are checked against the linked datasets' identifiers.
    """
    if not terms:
        raise ValueError("No vocabulary terms loaded; pass at least one --vocab file")
    subject = suggest_subject_class(profile, terms)
    class_tokens = []
    if subject.term:
        class_term = next(t for t in terms if t.iri == subject.term)
        class_tokens = tokens(class_term.label)
    fields = [
        suggest_field(fp, terms, subject.term, class_tokens,
                      values=[r.get(fp.name) or "" for r in records] if records else None,
                      links=links)
        for fp in profile.fields
    ]
    return MappingSet(
        dataset=profile.source,
        base_iri=base_iri if base_iri.endswith(("/", "#")) else base_iri + "/",
        id_field=choose_id_field(profile),
        subject=subject,
        fields=fields,
        vocabularies=vocabularies or [],
    )
