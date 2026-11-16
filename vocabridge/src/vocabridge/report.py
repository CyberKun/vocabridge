"""Human-readable review report for a mapping file."""

from __future__ import annotations

from .hypotheses import ACCEPTED, PROPOSED, REJECTED, MappingHypothesis, MappingSet
from .text import local_name

_ICON = {ACCEPTED: "accepted", REJECTED: "rejected", PROPOSED: "**needs review**"}


def _term(h: MappingHypothesis) -> str:
    if not h.term:
        return "_no suggestion_"
    return f"`{h.term_label or local_name(h.term)}` <{h.term}>"


def _row(h: MappingHypothesis) -> str:
    kind = "IRI" if h.value_kind == "iri" else (local_name(h.datatype) if h.datatype else "")
    return (f"| `{h.field}` | {_term(h)} | {kind} | {h.confidence:.2f} | "
            f"{_ICON.get(h.status, h.status)} |")


def _details(h: MappingHypothesis) -> list[str]:
    lines = [f"### `{h.field}`", ""]
    lines.append(f"- Proposed: {_term(h)} (method `{h.method}`, confidence {h.confidence:.2f})")
    if h.target_class:
        lines.append(f"- References resources of class `{local_name(h.target_class)}`")
    for ev in h.evidence:
        sign = f"{ev.weight:+.2f}" if ev.weight else " 0.00"
        lines.append(f"- Evidence [{ev.kind}, {sign}]: {ev.detail}")
    if h.alternatives:
        alts = ", ".join(f"`{a.label}` ({a.confidence:.2f})" for a in h.alternatives)
        lines.append(f"- Alternatives: {alts}")
    review = h.review
    if review.status != PROPOSED:
        who = f" by {review.reviewer}" if review.reviewer else ""
        note = f" — {review.note}" if review.note else ""
        lines.append(f"- Decision: {review.status}{who} at {review.reviewed_at}{note}")
    lines.append("")
    return lines


def render_report(mapping: MappingSet) -> str:
    counts = mapping.counts()
    lines = [
        f"# Mapping review: `{mapping.dataset}`",
        "",
        "Every row below is a **hypothesis**. Only accepted hypotheses are used to generate RDF.",
        "",
        f"- Base IRI: `{mapping.base_iri}`",
        f"- Identifier field: `{mapping.id_field or '(none — row numbers are used)'}`",
        f"- Vocabularies: {', '.join(mapping.vocabularies) or '(not recorded)'}",
        (f"- Status: {counts[ACCEPTED]} accepted, {counts[REJECTED]} rejected, "
         f"{counts[PROPOSED]} awaiting review"),
        "",
        "| Field | Proposed term | Value | Confidence | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    lines.extend(_row(h) for h in mapping.all())
    lines += ["", "## Evidence", ""]
    for h in mapping.all():
        lines.extend(_details(h))
    return "\n".join(lines).rstrip() + "\n"
