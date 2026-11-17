# VocaBridge

**The trust layer for semantic mappings.**

VocaBridge is an open-source, evidence-driven semantic mapping toolkit that maps tabular data to existing vocabularies. It proposes mappings with evidence from the data, records human review decisions, and generates RDF only from accepted mappings.

Most teams that want to build a knowledge graph start with spreadsheets, CSV exports, or JSON APIs. The difficult part is not writing RDF. It is deciding what each column means, identifying which existing vocabulary describes it, and establishing whether the proposed mapping is reasonable.

VocaBridge makes these decisions explicit, reviewable, and repeatable.

```text
CSV / JSON
    |
    v
  PROFILE       Understand fields, types, completeness and values
    |
    v
  SUGGEST       Propose vocabulary mappings with supporting evidence
    |
    v
  REVIEW        Accept or reject hypotheses; record human decisions
    |
    v
  GENERATE      Generate RDF and SHACL shapes from accepted mappings
    |
    v
  VALIDATE      Check generated RDF against SHACL constraints
```

## The core principle

> A machine-generated interpretation is a hypothesis, not a fact.

VocaBridge does not silently decide what your data means. Each proposed mapping records:

- The vocabulary term proposed and alternative candidates.
- Evidence supporting the proposal, such as label matches, synonyms, domain, range, datatype, value patterns, and cross-dataset identifier overlap.
- A confidence score used to rank hypotheses.
- The review decision: accepted or rejected, by whom, when, and why.

Only accepted hypotheses are used for RDF generation.

The mapping file is plain JSON, so it can be diffed, code-reviewed, version-controlled, and maintained like any other source file.

Confidence scores in the current baseline are heuristic ranking signals, not calibrated probabilities.

## Quick start

```bash
git clone https://github.com/Suchi-BITS/vocabridge.git
cd vocabridge

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

Run the complete procurement example:

```bash
./examples/procurement/run.sh
```

The example demonstrates how three related datasets — suppliers, purchase orders, and invoices — can be mapped to an existing procurement vocabulary and connected into an RDF graph.

## Working with your own data

VocaBridge supports a step-by-step workflow.

### 1. Profile the dataset

Understand the structure and contents of your CSV or JSON file.

```bash
vocabridge profile data.csv
```

Profiling examines information such as:

- Field names and detected data types.
- Completeness and uniqueness.
- Sample values.
- Value patterns that may help identify identifiers, dates, currencies, and other data types.

### 2. Discover vocabulary candidates (optional)

Search for published vocabulary terms that might be relevant.

```bash
vocabridge discover data.csv --keyword procurement
```

Vocabulary discovery currently uses Wikidata through a pluggable catalog interface.

Discovery results are leads for further investigation, not automatically approved mappings. You choose the vocabulary you want to use.

### 3. Suggest mappings

Provide an existing vocabulary file in a supported RDF serialization, such as Turtle.

```bash
vocabridge suggest data.csv \
    --vocab my-vocabulary.ttl \
    --base-iri https://example.org/ \
    -o data.mapping.json \
    --report data.review.md
```

The suggester proposes:

- A subject class representing the records in the dataset.
- Candidate vocabulary properties for individual fields.
- Literal or IRI value interpretations.
- Evidence, alternatives, and confidence scores.

### 4. Review the hypotheses

Reviewers can accept or reject proposed mappings.

For example:

```bash
vocabridge review data.mapping.json \
    --accept-above 0.9 \
    --reviewer "Your Name"

vocabridge review data.mapping.json \
    --accept country \
    --note "ISO alpha-2 country codes"

vocabridge review data.mapping.json \
    --reject notes \
    --note "Free-text field; no suitable vocabulary property"
```

Bulk acceptance is a review shortcut based on a confidence threshold. It should not be confused with independent verification of semantic correctness.

The mapping file retains review decisions and audit information.

### 5. Generate RDF and SHACL

Generate RDF instance data and SHACL shapes from accepted mappings.

```bash
vocabridge generate data.mapping.json \
    -o data.ttl \
    --shapes shapes.ttl
```

### 6. Validate the generated RDF

```bash
vocabridge validate data.ttl shapes.ttl
```

SHACL validation checks whether the generated RDF conforms to the generated shapes. Conformance does not, by itself, establish that every semantic mapping is correct.

---

## How the procurement example works

The procurement example demonstrates an important capability: mapping relationships across multiple datasets using evidence from their actual values.

The example contains three datasets:

| Dataset | What it represents | Example identifier |
|---|---|---|
| Suppliers | Organisations providing goods or services | `supplier_id` |
| Purchase Orders | Orders placed with suppliers | `po_number` |
| Invoices | Bills received against purchase orders | `invoice_number` |

All three datasets are mapped to an existing procurement vocabulary.

The important point is that the datasets are not processed as isolated files. Their relationships can be discovered through identifiers shared across datasets.

### Step 1: Map the Suppliers dataset

Start with the supplier data.

```bash
vocabridge profile examples/procurement/data/suppliers.csv
```

Suggest mappings against the procurement vocabulary:

```bash
vocabridge suggest examples/procurement/data/suppliers.csv \
    --vocab examples/procurement/ontology/procurement.ttl \
    --base-iri https://example.org/procurement/ \
    -o examples/procurement/output/suppliers.mapping.json \
    --report examples/procurement/output/suppliers.review.md
```

The suggester proposes:

- The `Supplier` ontology class as the subject class.
- Candidate mappings for supplier attributes.
- An identifier field, such as `supplier_id`.

Review and accept the subject class and appropriate field mappings.

The subject class is particularly important because it establishes what kind of resources the generated RDF records represent.

### Step 2: Map the Purchase Orders dataset

Process purchase orders independently.

```bash
vocabridge profile examples/procurement/data/purchase_orders.csv
```

```bash
vocabridge suggest examples/procurement/data/purchase_orders.csv \
    --vocab examples/procurement/ontology/procurement.ttl \
    --base-iri https://example.org/procurement/ \
    -o examples/procurement/output/purchase_orders.mapping.json \
    --report examples/procurement/output/purchase_orders.review.md
```

Review and accept the `PurchaseOrder` subject class and the appropriate field mappings.

At this point, the two datasets have independently reviewed mappings:

- Supplier records represent `Supplier` resources.
- Purchase order records represent `PurchaseOrder` resources.

These two steps can be performed in either order.

### Step 3: Connect Invoices to the reviewed datasets

Invoices contain references to suppliers and purchase orders.

For example:

| Invoice | payee_ref | po_ref |
|---|---|---|
| INV-7781 | S-1001 | PO-24-0001 |
| INV-7782 | S-1002 | PO-24-0002 |

The invoice column names do not necessarily resemble the property names in the ontology.

A name-only matcher may not understand that:

- `payee_ref` corresponds to `billedBy`.
- `po_ref` corresponds to `billsOrder`.

This is where cross-dataset value evidence becomes useful.

First, the supplier and purchase order subject classes must have been accepted. VocaBridge can then load their reviewed mappings and use their identifier values as reference datasets.

```bash
vocabridge suggest examples/procurement/data/invoices.csv \
    --vocab examples/procurement/ontology/procurement.ttl \
    --base-iri https://example.org/procurement/ \
    --link examples/procurement/output/suppliers.mapping.json \
    --link examples/procurement/output/purchase_orders.mapping.json \
    -o examples/procurement/output/invoices.mapping.json \
    --report examples/procurement/output/invoices.review.md
```

The `--link` option supplies previously reviewed datasets as reference points for identifier-overlap evidence.

VocaBridge compares the values in invoice reference columns with the identifiers in those datasets.

### Step 4: Understand how the relationships are identified

Consider the `payee_ref` column.

Its values match supplier identifiers. The ontology contains an object property called `billedBy`, whose range is `Supplier`.

The matching process combines:

1. The candidate ontology property's domain and range.
2. The fact that the property range matches the linked dataset's subject class.
3. The overlap between invoice reference values and supplier identifiers.

The resulting evidence can look like:

```text
Evidence [value-overlap, +0.45]:
4 of 4 distinct values (100%) appear in suppliers.supplier_id,
the identifiers of Supplier.
```

The same reasoning applies to `po_ref`.

Its values match purchase order identifiers, and the ontology property `billsOrder` has `PurchaseOrder` as its range.

The resulting mapping hypotheses are:

| Invoice field | Proposed ontology property | Target class |
|---|---|---|
| `payee_ref` | `billedBy` | Supplier |
| `po_ref` | `billsOrder` | PurchaseOrder |

These are object-property mappings. Their values are therefore represented as RDF resource references rather than ordinary text literals.

Value overlap supports a proposed relationship, but does not independently prove that the relationship is semantically correct. Human review remains necessary.

### Step 5: Review the Invoice mappings

Inspect the generated mapping file and review report.

Accept the proposed mappings only when the evidence and business meaning are appropriate.

The review process records the decision and its associated information, such as reviewer, timestamp, and note.

The important distinction is:

- A proposed mapping is a hypothesis.
- An accepted mapping is a human-reviewed decision.
- A rejected mapping is retained as a rejected decision rather than silently discarded.

### Step 6: Generate RDF for all three datasets

Generate RDF and SHACL shapes:

```bash
for d in suppliers purchase_orders invoices; do
    vocabridge generate "examples/procurement/output/$d.mapping.json" \
        -o "examples/procurement/output/$d.ttl" \
        --shapes "examples/procurement/output/$d.shapes.ttl"
done
```

The generated invoice RDF contains relationships similar to:

```turtle
<https://example.org/procurement/invoice/INV-7781>
    a vocab:Invoice ;
    vocab:invoiceNumber "INV-7781" ;
    vocab:amountDue 12500.00 ;
    vocab:billedBy
        <https://example.org/procurement/supplier/S-1001> ;
    vocab:billsOrder
        <https://example.org/procurement/purchaseorder/PO-24-0001> .
```

Notice what happened:

- The invoice remains an instance of `Invoice`.
- `billedBy` connects that invoice to a `Supplier` resource.
- `billsOrder` connects that invoice to a `PurchaseOrder` resource.

There is no change of class or conversion of an invoice into a supplier or purchase order. The ontology properties establish relationships between resources belonging to different classes.

Because the reference values resolve to the same resource IRIs used by the supplier and purchase order datasets, the three RDF files can form one connected graph when loaded together.

### Step 7: Validate the generated RDF

Validate each dataset:

```bash
for d in suppliers purchase_orders invoices; do
    vocabridge validate \
        "examples/procurement/output/$d.ttl" \
        "examples/procurement/output/$d.shapes.ttl"
done
```

The validation checks whether the generated RDF conforms to its corresponding SHACL shapes.

### Step 8: Query the connected graph

The example includes a SPARQL competency query:

```text
examples/procurement/queries/invoice-supplier-order.rq
```

It demonstrates how to retrieve:

- The invoice.
- The supplier who billed it.
- The purchase order associated with it.

This illustrates the final objective: transforming separate tabular datasets into connected RDF resources that can be queried together.

---

## What the review report looks like

A review report from the procurement example may contain information like:

| Field | Proposed term | Value kind | Confidence | Status |
|---|---|---|---:|---|
| `__subject__` | PurchaseOrder | IRI | 1.00 | accepted |
| `po_number` | order number | string | 0.94 | accepted |
| `vendor_id` | ordered from | IRI | 0.89 | accepted |
| `cost_centre` | raised by | IRI | 0.79 | accepted |
| `approved_by` | No suitable suggestion | string | 0.15 | rejected |

Each mapping includes its supporting evidence and alternatives.

For example, `vendor_id` may map to an object property because the vocabulary contains a relevant alternative label and the field values behave like references to Supplier resources.

When evidence is insufficient, VocaBridge can leave a field without a suitable suggestion rather than inventing a mapping.

---

## Extending VocaBridge to other domains

VocaBridge is designed to be domain-independent.

To apply it to another domain, developers generally need to:

1. Provide a suitable domain vocabulary or ontology in a supported RDF serialization, such as Turtle.
2. Prepare their CSV or JSON datasets.
3. Supply an appropriate base IRI and run the existing profiling, suggestion, review, generation, and validation workflow.
4. Extend the suggestion logic, particularly `suggest.py` and `values.py`, only when the domain requires specialised terminology, identifier patterns, or additional value-based evidence.

For example, the same core workflow could be applied to healthcare, finance, manufacturing, supply chains, or other domains.

The objective is to keep the core mapping and review workflow reusable while allowing domain-specific vocabularies and matching rules to evolve independently.

---

## What VocaBridge does today (v0.1)

| Capability | Status |
|---|---|
| Profile CSV and JSON (types, completeness, uniqueness, samples) | Implemented |
| Load RDFS/OWL/SKOS vocabulary files (Turtle, RDF/XML, JSON-LD, etc.) | Implemented |
| Explainable baseline suggester (labels, `skos:altLabel`, domain, range) | Implemented |
| Mapping hypotheses with evidence, alternatives, and review audit trail | Implemented |
| Markdown review report | Implemented |
| RDF generation with stable, cross-dataset resource IRIs and provenance | Implemented |
| SHACL shape generation and validation using pySHACL | Implemented |
| Vocabulary discovery through Wikidata, behind a pluggable catalog interface | Implemented |
| Value evidence: value patterns and cross-dataset identifier overlap (`--link`) | Implemented |

## Known limitations (v0.1)

vocabridge v0.1 is an early release. These limitations are known and tracked:

**Validation and graph structure**
- **Generated SHACL shapes validate one dataset at a time.** They are closed shapes, and `sh:minCount` is derived from that dataset's completeness. If several sources describe the same class (for example, two supplier systems) and their graphs are merged, the generated shapes will report false violations. Validating merged graphs against shared, human-governed domain shapes is planned for v0.2.
- **Reference fields are checked with `sh:nodeKind sh:IRI`, not `sh:class`.** That an invoice's supplier really is a `Supplier` can only be checked when both datasets are validated together, which v0.1 does not do yet.
- **Provenance metadata is written into the same graph as the data.** Named graphs per dataset, with provenance kept separate, are planned.
- **Mapping files record which vocabulary files were used, but not their version or checksum,** so a later vocabulary change cannot yet be detected automatically.

**Suggestions**
- The baseline suggester uses lexical, schema and value evidence only. There is no LLM suggester yet, and no published accuracy figures yet; an evaluation harness is the first v0.2 item.
- Matching assumes English labels.

**Inputs and scale**
- Comma-separated CSV and JSON arrays of flat objects only; files are read fully into memory. No database connectors yet.
- One class per dataset and one value per field per row.
- Review happens through the command line.

**Discovery**
- `vocabridge discover` depends on the public Wikidata Query Service. Its results are leads to investigate, not recommendations.

Feedback on which of these matters most to you helps decide what comes next: please open an issue.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the detailed plan.

The direction is to make mapping decisions trustworthy and maintainable over time, not merely generate mappings once.

### v0.2 — Measured trust

- Build an evaluation harness to measure mapping quality, precision, recall, and reviewer effort.
- Calibrate confidence scores using actual review outcomes.
- Prioritise uncertain or consequential hypotheses for human review.
- Detect changes in source data and vocabularies, and identify affected mappings.
- Introduce optional LLM-based suggesters that produce the same evidence-carrying hypothesis structure.
- Improve review usability and data profiling.

### v0.3 — Decisions as reusable assets

- Reuse previous human decisions as evidence for future mappings.
- Trace generated RDF back to source rows, fields, evidence, and reviewers.
- Add competency-question tests and richer provenance exports.
- Improve datatype and unit detection.
- Explore RML export and additional vocabulary catalogs such as LOV and OKG.

The roadmap deliberately starts with measurement. Before making the suggester smarter, VocaBridge needs a reliable way to measure whether its suggestions are correct and how much human effort they save.

---

## How VocaBridge relates to other tools

Mapping data to RDF is a well-studied problem. VocaBridge builds on that work rather than replacing it.

| Tool or approach | Main focus | Where VocaBridge differs |
|---|---|---|
| Karma | Interactive GUI for modelling data sources against ontologies, with semantic-type suggestions | Command-line and file-based workflow; mapping decisions are versionable JSON with evidence and reviewer information |
| OpenRefine reconciliation | Matching cell values to entities, such as Wikidata items, with human approval | Focuses on mapping dataset columns to vocabulary terms and uses cross-dataset value overlap as evidence for references |
| RDFMap | Ontology-aligned conversion with matching, confidence scores, and SHACL | Uses a hypothesis-first review model and cross-dataset identifier evidence |
| LLM mapping pipelines | Using language models to propose semantic mappings, often with human review | Any suggester, including an LLM, must produce the same evidence-carrying hypothesis objects and pass through the review workflow |
| SemTab | Benchmarking table annotation with knowledge-graph entities, types, and properties | VocaBridge is a practical mapping toolkit, not a benchmark; SemTab datasets are a potential evaluation source |

Use whichever tool best fits your requirements. VocaBridge focuses on making mapping decisions explainable, reviewable, measurable, and maintainable.

## Design choices

**Bring your own vocabulary**

VocaBridge does not bundle third-party domain vocabularies. You provide the vocabulary you want to reuse.

**No single external dependency**

Vocabulary discovery uses a small `CatalogSource` interface. Wikidata is the default implementation; additional catalogs can be integrated as optional sources. All operations other than discovery can run offline.

**Explainable before clever**

The baseline suggester is deliberately simple so that each score can be traced to named evidence. More advanced suggesters must produce the same hypothesis objects and follow the same review workflow.

**Human decisions remain explicit**

VocaBridge does not treat a high confidence score as a substitute for semantic review. Accepted and rejected decisions are retained in the mapping artifact.

**Standards-based output**

VocaBridge uses established standards and technologies, including RDF, RDFS/OWL, SKOS, SHACL, and PROV.

More detail:

- [Architecture](docs/architecture.md)
- [Principles](docs/principles.md)
- [Roadmap](ROADMAP.md)

## Contributing

Contributions are welcome, from fixing a typo to adding a vocabulary catalog source or improving mapping evidence.

Start with [CONTRIBUTING.md](CONTRIBUTING.md) and look for issues labelled `good first issue`.

## Acknowledgements

Vocabulary discovery uses the public Wikidata Query Service. Wikidata content is available under CC0.

Built with:

- [rdflib](https://rdflib.readthedocs.io/)
- [pySHACL](https://github.com/RDFLib/pySHACL)

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
