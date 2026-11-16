# Roadmap

**Direction:** vocabridge is the trust layer for semantic mappings. Creating a mapping is the easy part; the roadmap focuses on proving it, measuring it, and keeping it correct as data and vocabularies change.

## v0.1 — Foundation (done)

1. Project setup: package layout, licence, README, contributing guide, tests, CI
2. Input profiling for CSV and JSON
3. Pluggable catalog-source interface with Wikidata as the first source, plus caching
4. Hypothesis data model with evidence, confidence, alternatives, review audit trail and report
5. SHACL shape generation from accepted mappings, RDF generation and validation
6. Value evidence: value-pattern detection and identifier overlap with reviewed datasets (`--link`)

## v0.2 — Measured trust

Drafts for every item are in [`docs/issues/`](docs/issues); open them on GitHub with `scripts/create_issues.sh`.

| Issue | Why it matters |
| --- | --- |
| 01 Evaluation harness | Every later claim of "better" needs numbers. Built first. |
| 08 Calibrated confidence from review history | Published work shows LLM confidence is often overconfident; calibration fixes much of it. |
| 09 Review prioritisation | Asking about the most informative items first cuts human effort sharply in active-learning studies. |
| 10 Change impact (`vocabridge diff`) | Propagating data and ontology changes to mappings is still mostly manual. |
| 02 LLM suggester | Better recall on cryptic names, with the same evidence and review rules. |
| 06 Interactive review, 07 Delimiter detection | Usability; good first issues. |

## v0.3 — Decisions as assets

| Issue | Why it matters |
| --- | --- |
| 11 Decision memory | Past human decisions become evidence for new datasets. |
| 12 `explain` and PROV export | Any triple can be traced to its row, field, evidence and reviewer, inside the graph. |
| 13 Competency-question tests | The graph is checked against the business questions it must answer. |
| 14 Unit detection | Numeric columns in mixed or implicit units are a known source of silent errors. |
| 03 RML export | Run accepted mappings in any RML engine. |
| 04 LOV source, 05 OKG source | More vocabulary discovery, all optional. |

## Research this roadmap draws on

- Ontology-change propagation to mappings: Conde-Herreros et al., KGCW 2024; OntoRipple.
- Mapping evolution in practice: Shafique et al., empirical study of YARRRML evolution (2026).
- LLM confidence calibration: Kamsteeg et al., UncertaiNLP 2025; uncertainty for tabular entity linking, OM 2025.
- Active learning for schema alignment: Alfa, VLDB Journal 2024.
- Vocabulary term reuse: TermPicker (ESWC 2016); Datavore (ISWC 2015 posters).
- Units in tabular data: Ceritli & Williams (2021); mixed-unit column annotation (WWW 2025).
- Competency-question testing: OE-Assist (2025); Bench4KE (2025).
