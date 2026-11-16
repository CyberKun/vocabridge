# Changelog

## 0.1.0 — unreleased

- `profile`, `discover`, `suggest`, `review`, `generate`, `validate` commands
- Lexical baseline suggester using labels, `skos:altLabel`, domain and range evidence
- Hypothesis mapping file (format version 1) with review audit trail
- RDF generation with cross-dataset resource IRIs and PROV run metadata
- Closed SHACL shape generation and pySHACL validation
- Wikidata catalog source with file cache
- Value evidence: pattern detection (codes, e-mails, URLs, prefixed identifiers) and `suggest --link` identifier overlap with reviewed datasets
- Procurement example with three synthetic datasets (suppliers, purchase orders, invoices), ontology and a competency-question query
