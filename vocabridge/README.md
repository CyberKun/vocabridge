# vocabridge

**The trust layer for semantic mappings.** vocabridge maps tabular data onto existing vocabularies, proves each mapping with evidence from the data itself, keeps a record of every human decision, and only publishes what a person accepted.

Most teams that want a knowledge graph start with spreadsheets, CSV exports or JSON APIs. The hard part is not writing RDF; it is deciding *what each column means*, which published vocabulary already describes it, and proving that the result is correct. vocabridge makes those decisions explicit, reviewable and repeatable.

```
CSV / TSV / JSON ──► profile ──► suggest ──► review ──► generate ──► RDF + SHACL ──► validate
                  │           │           │
           field types   hypotheses   accepted / rejected,
           & samples     + evidence   who decided and why
```

## The core principle

> **A machine-generated interpretation is a hypothesis, not a fact.**

vocabridge never silently decides what your data means. Every proposed mapping records:

- the vocabulary term proposed, and the alternatives it considered
- the **evidence** behind it (label match, synonym match, domain, datatype range) with a signed weight
- a **confidence** score
- the **review decision**: accepted or rejected, by whom, when, and why

Only accepted hypotheses are turned into RDF. The mapping file is plain JSON, so it can be diffed, code-reviewed and versioned like any other source file.

## Quick start

```bash
git clone https://github.com/YOUR-USERNAME/vocabridge.git
cd vocabridge
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run the complete procurement example
./examples/procurement/run.sh
```

Or step by step with your own data:

```bash
# 1. See what is in the data
vocabridge profile data.csv

# 2. Find published vocabularies that might fit (queries Wikidata; results are leads, not answers)
vocabridge discover data.csv --keyword procurement

# 3. Propose mappings against vocabulary files you choose
vocabridge suggest data.csv --vocab my-vocabulary.ttl --base-iri https://example.org/ \
    -o data.mapping.json --report data.review.md

# 4. Decide. Bulk-accept confident matches, then handle the rest one by one
vocabridge review data.mapping.json --accept-above 0.9 --reviewer "Your Name"
vocabridge review data.mapping.json --accept country --note "ISO alpha-2 codes"
vocabridge review data.mapping.json --reject notes --note "Free text"

# 5. Generate RDF and SHACL shapes from the accepted mappings, and validate
vocabridge generate data.mapping.json -o data.ttl --shapes shapes.ttl
```

## Evidence from the values, not just the names

Column names are unreliable. In `examples/procurement/data/invoices.csv`, nothing about the names `payee_ref` and `po_ref` resembles the ontology properties *billed by* and *bills order*, so a name matcher gives up:

| Field | Names only | With `--link` to reviewed datasets |
| --- | --- | --- |
| `payee_ref` | _no suggestion_ | `billed by` → Supplier |
| `po_ref` | _no suggestion_ | `bills order` → Purchase order |

```bash
vocabridge suggest data/invoices.csv --vocab ontology/procurement.ttl --base-iri https://example.org/procurement/ \
    --link output/suppliers.mapping.json --link output/purchase_orders.mapping.json -o output/invoices.mapping.json
```

The evidence recorded for `payee_ref`:

```
Evidence [value-overlap, +0.45]: 4 of 4 distinct values (100%) appear in suppliers.supplier_id, the identifiers of Supplier
```

Values that do *not* appear in the linked identifiers count against a mapping. Value shapes are used too: a column of three-letter upper-case codes supports *currency code*; two-letter codes support *country code*.

Because the reference values become the same IRIs as the linked dataset's rows, the three files join into one graph. `examples/procurement/queries/invoice-supplier-order.rq` answers "which supplier billed each invoice, for which order?" across all three.

## What the review report looks like

From the procurement example (`examples/procurement/output/purchase_orders.review.md`):

| Field | Proposed term | Value | Confidence | Status |
| --- | --- | --- | --- | --- |
| `__subject__` | `Purchase order` | IRI | 1.00 | accepted |
| `po_number` | `order number` | string | 0.94 | accepted |
| `vendor_id` | `ordered from` | IRI | 0.89 | accepted |
| `cost_centre` | `raised by` | IRI | 0.79 | accepted |
| `approved_by` | _no suggestion_ | string | 0.15 | rejected |

Each row is followed by its evidence. For example, `vendor_id` maps to `ordered from` because the ontology lists *vendor* as an alternative label, and because the field name looks like a reference, its values become links to `Supplier` resources rather than text. Where the tool has no good evidence (`approved_by`, `notes`), it says so instead of guessing.

## What vocabridge does today (v0.1)

| Capability | Status |
| --- | --- |
| Profile CSV, TSV and JSON (types, completeness, uniqueness, samples) | ✅ |
| Load any RDFS/OWL/SKOS vocabulary file (Turtle, RDF/XML, JSON-LD…) | ✅ |
| Explainable baseline suggester (labels, `skos:altLabel`, domain, range) | ✅ |
| Hypothesis model with evidence, alternatives and review audit trail | ✅ |
| Markdown review report | ✅ |
| RDF generation with stable, cross-dataset resource IRIs and provenance | ✅ |
| SHACL shape generation and validation (pySHACL) | ✅ |
| Vocabulary discovery through Wikidata, behind a pluggable catalog interface | ✅ |
| Value evidence: value patterns and identifier overlap with reviewed datasets (`--link`) | ✅ |

See [ROADMAP.md](ROADMAP.md) for what comes next. The direction is to make mappings trustworthy over time, not only at creation:

- **Measured confidence**: an evaluation harness, and confidence scores recalibrated from your own review history, so 0.9 means roughly 90% correct.
- **Smarter review**: ask people about the most uncertain, most consequential hypotheses first.
- **Change impact**: when data or vocabularies change, reopen only the decisions that are affected.
- **Decision memory and `explain`**: reuse past decisions as evidence, and trace any triple back to its row, field, evidence and reviewer.

## How vocabridge relates to other tools

Mapping data to RDF is a well-studied problem, and vocabridge builds on that work rather than replacing it.

| Tool or approach | Main focus | Where vocabridge differs |
| --- | --- | --- |
| [Karma](https://github.com/usc-isi-i2/Web-Karma) | Interactive GUI for modelling sources against an ontology, with learned semantic-type suggestions | Command-line and file-based; mapping decisions are versionable JSON with evidence and reviewer |
| [OpenRefine](https://openrefine.org/) reconciliation | Matching cell *values* to entities (e.g. Wikidata items) with human approval | Maps *columns* to vocabulary terms; uses value overlap as evidence for references |
| [RDFMap](https://pypi.org/project/semantic-rdf-mapper/) | Ontology-aligned conversion with label-based matching, confidence scores and SHACL | Hypothesis-first review model; value evidence across datasets; planned calibration and change impact |
| LLM mapping pipelines (research and vendor workflows) | Drafting mappings with language models, often with human review | Any suggester, LLM included, must emit the same evidence-carrying hypotheses; accuracy is measured, not assumed |
| [SemTab](https://sem-tab-challenge.github.io/) | Benchmark for annotating tables with knowledge-graph entities, types and properties | A practical tool, not a benchmark; SemTab datasets are a planned evaluation source |

If one of these fits your need better, use it. vocabridge aims to be the piece that makes mapping decisions explainable, measurable and maintainable.

## Design choices

- **Bring your own vocabulary.** vocabridge does not bundle third-party vocabularies. You point it at the files you want to reuse.
- **No single external dependency.** Discovery goes through a small `CatalogSource` interface. Wikidata is the default; other catalogs can be added as optional sources, and everything except `discover` works fully offline.
- **Explainable before clever.** The baseline suggester is deliberately simple so that every score can be traced to evidence. Smarter suggesters must produce the same hypothesis objects and go through the same review.
- **Standards only.** RDF, RDFS/OWL, SKOS, SHACL, PROV. No proprietary formats.

More detail: [docs/architecture.md](docs/architecture.md) and [docs/principles.md](docs/principles.md).

## Contributing

Contributions are welcome, from fixing a typo to adding a catalog source. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and look for issues labelled `good first issue`.

## Acknowledgements

Vocabulary discovery uses the public [Wikidata Query Service](https://query.wikidata.org/); Wikidata content is available under CC0. Built with [rdflib](https://github.com/RDFLib/rdflib) and [pySHACL](https://github.com/RDFLib/pySHACL).

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

### Delimited input

`.tsv` files use tabs. For `.csv`, vocabridge detects commas, semicolons,
tabs or pipes from the first 8 KiB, falling back to commas if detection fails.
Use `--delimiter ';'` with `profile`, `suggest` or `discover` to override
that choice (the value must be one character). Quoted fields are supported.

Suggested mappings save the chosen delimiter so generation and linked-dataset
loading interpret the source consistently. Older mappings without a delimiter
continue to use commas; JSON inputs are unchanged.
