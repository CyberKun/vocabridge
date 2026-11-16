"""Command-line interface.

Typical flow::

    vocabridge profile   data.csv
    vocabridge discover  data.csv
    vocabridge suggest   data.csv --vocab my-ontology.ttl --base-iri https://example.org/ -o mapping.json
    vocabridge review    mapping.json --accept-above 0.7 --reviewer "Your Name"
    vocabridge generate  mapping.json -o data.ttl --shapes shapes.ttl
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from pathlib import Path

from . import __version__
from .catalog import SOURCES, discover
from .catalog.cache import FileCache
from .generate import MappingNotReadyError, build_shapes, dataset_path, generate_rdf, validate
from .hypotheses import ACCEPTED, PROPOSED, REJECTED, MappingSet
from .profiling import profile_file, profile_records, read_records
from .report import render_report
from .suggest import IDENTIFIER_TOKENS, suggest_mappings
from .text import tokens
from .values import load_linked
from .vocab import load_vocabularies

# Field-name tokens that say little about the domain, skipped when building search keywords.
GENERIC_TOKENS = IDENTIFIER_TOKENS | {"name", "date", "amount", "value", "type", "status",
                                       "description", "created", "updated", "flag", "is"}


def _write_or_print(text: str, output: str | None) -> None:
    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Wrote {output}", file=sys.stderr)
    else:
        sys.stdout.write(text)


def cmd_profile(args: argparse.Namespace) -> int:
    profile = profile_file(args.data, sample_size=args.samples)
    _write_or_print(json.dumps(profile.to_dict(), indent=2) + "\n", args.output)
    return 0


def keywords_for(profile, extra: list[str]) -> list[str]:
    words = [" ".join(tokens(profile.name))]
    for f in profile.fields:
        words.extend(t for t in tokens(f.name) if t not in GENERIC_TOKENS and len(t) > 2)
    return list(dict.fromkeys([*extra, *words]))


def cmd_discover(args: argparse.Namespace) -> int:
    profile = profile_file(args.data)
    keywords = args.keyword if args.only_keywords else keywords_for(profile, args.keyword)
    source = SOURCES[args.source](cache=None if args.no_cache else FileCache())
    try:
        candidates = discover(source, keywords, limit_per_keyword=args.limit)
    except OSError as exc:
        print(f"Could not reach the {args.source} catalog: {exc}", file=sys.stderr)
        return 2
    payload = {
        "dataset": profile.source,
        "source": args.source,
        "keywords": keywords,
        "note": "Candidates are leads to investigate, not recommendations.",
        "candidates": [c.to_dict() for c in candidates],
    }
    if args.output:
        _write_or_print(json.dumps(payload, indent=2) + "\n", args.output)
    else:
        print(f"Searched {args.source} for: {', '.join(keywords)}\n")
        for c in candidates:
            print(f"- {c.label} [{c.identifier}] matched: {', '.join(c.matched_keywords)}")
            if c.description:
                print(f"    {c.description}")
            if c.homepage:
                print(f"    {c.homepage}")
        if not candidates:
            print("No candidates found. Try --keyword with broader domain terms.")
    return 0


def cmd_suggest(args: argparse.Namespace) -> int:
    records = read_records(args.data)
    profile = profile_records(records, source=str(args.data), name=Path(args.data).stem)
    terms = load_vocabularies(args.vocab)
    try:
        links = [load_linked(m) for m in args.link]
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    mapping = suggest_mappings(profile, terms, base_iri=args.base_iri,
                               vocabularies=[str(v) for v in args.vocab],
                               records=records, links=links)
    if args.id_field:
        profile.field(args.id_field)  # raises if the field does not exist
        mapping.id_field = args.id_field
    # Store the dataset path relative to the mapping file so the pair can be moved together.
    mapping.dataset = os.path.relpath(Path(args.data).resolve(),
                                      Path(args.output).resolve().parent)
    mapping.save(args.output)
    print(f"Wrote {args.output}", file=sys.stderr)
    if args.report:
        _write_or_print(render_report(mapping), args.report)
    counts = mapping.counts()
    unmatched = sum(1 for h in mapping.all() if not h.term)
    print(f"{counts[PROPOSED]} hypotheses proposed, {unmatched} field(s) without a suggestion. "
          "Nothing is accepted until you review.", file=sys.stderr)
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    mapping = MappingSet.load(args.mapping)
    reviewer = args.reviewer or getpass.getuser()
    changed = 0
    try:
        for name in args.accept:
            mapping.hypothesis(name).set_status(ACCEPTED, reviewer, args.note)
            changed += 1
        for name in args.reject:
            mapping.hypothesis(name).set_status(REJECTED, reviewer, args.note)
            changed += 1
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.accept_above is not None:
        for h in mapping.all():
            if h.status == PROPOSED and h.term and h.confidence >= args.accept_above:
                h.set_status(ACCEPTED, reviewer,
                             args.note or f"bulk-accepted at confidence >= {args.accept_above}")
                changed += 1
    if changed:
        mapping.save(args.mapping)
        print(f"Updated {changed} hypothesis decision(s) in {args.mapping}", file=sys.stderr)
    _write_or_print(render_report(mapping), args.report)
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    mapping = MappingSet.load(args.mapping)
    try:
        data = generate_rdf(mapping, args.mapping, provenance=not args.no_provenance)
        profile = profile_file(dataset_path(mapping, args.mapping))
        shapes = build_shapes(mapping, profile)
    except MappingNotReadyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    data.serialize(destination=args.output, format="turtle")
    print(f"Wrote {args.output} ({len(data)} triples)", file=sys.stderr)
    if args.shapes:
        shapes.serialize(destination=args.shapes, format="turtle")
        print(f"Wrote {args.shapes}", file=sys.stderr)
    if args.no_validate:
        return 0
    result = validate(data, shapes)
    if result.conforms:
        print("SHACL validation: conforms", file=sys.stderr)
        return 0
    print(result.report_text, file=sys.stderr)
    return 1


def cmd_validate(args: argparse.Namespace) -> int:
    from rdflib import Graph

    data, shapes = Graph(), Graph()
    data.parse(args.data)
    shapes.parse(args.shapes)
    result = validate(data, shapes)
    print("conforms" if result.conforms else result.report_text)
    return 0 if result.conforms else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vocabridge",
        description="Map tabular data onto existing vocabularies, one reviewable hypothesis "
                    "at a time, then generate validated RDF.",
    )
    parser.add_argument("--version", action="version", version=f"vocabridge {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("profile", help="describe the fields of a CSV or JSON file")
    p.add_argument("data")
    p.add_argument("--samples", type=int, default=5)
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_profile)

    p = sub.add_parser("discover", help="search a public catalog for vocabularies to reuse")
    p.add_argument("data")
    p.add_argument("--source", choices=sorted(SOURCES), default="wikidata")
    p.add_argument("--keyword", action="append", default=[], help="extra search keyword")
    p.add_argument("--only-keywords", action="store_true",
                   help="search only the --keyword values, not words from the data")
    p.add_argument("--limit", type=int, default=5, help="results per keyword")
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_discover)

    p = sub.add_parser("suggest", help="propose mapping hypotheses against vocabulary files")
    p.add_argument("data")
    p.add_argument("--vocab", action="append", required=True,
                   help="RDF vocabulary file (repeatable)")
    p.add_argument("--base-iri", required=True, help="namespace for generated resources")
    p.add_argument("--id-field", help="field used to mint resource IRIs")
    p.add_argument("--link", action="append", default=[], metavar="MAPPING",
                   help="mapping file of a reviewed dataset whose identifiers this data may "
                        "reference; values are compared to find links (repeatable)")
    p.add_argument("-o", "--output", required=True, help="mapping file to write (JSON)")
    p.add_argument("--report", help="also write a Markdown review report")
    p.set_defaults(func=cmd_suggest)

    p = sub.add_parser("review", help="accept or reject hypotheses and print the review report")
    p.add_argument("mapping")
    p.add_argument("--accept", action="append", default=[], metavar="FIELD",
                   help="accept a field's hypothesis (use __subject__ for the row class)")
    p.add_argument("--reject", action="append", default=[], metavar="FIELD")
    p.add_argument("--accept-above", type=float, metavar="CONFIDENCE",
                   help="accept every proposed hypothesis at or above this confidence")
    p.add_argument("--reviewer", help="name recorded with each decision")
    p.add_argument("--note", default="", help="note recorded with each decision")
    p.add_argument("--report", help="write the report to a file instead of stdout")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("generate", help="generate RDF and SHACL from accepted hypotheses")
    p.add_argument("mapping")
    p.add_argument("-o", "--output", required=True, help="Turtle file for the data")
    p.add_argument("--shapes", help="Turtle file for the generated SHACL shapes")
    p.add_argument("--no-validate", action="store_true")
    p.add_argument("--no-provenance", action="store_true")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("validate", help="validate an RDF file against SHACL shapes")
    p.add_argument("data")
    p.add_argument("shapes")
    p.set_defaults(func=cmd_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
