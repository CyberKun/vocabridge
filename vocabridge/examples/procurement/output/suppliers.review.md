# Mapping review: `../data/suppliers.csv`

Every row below is a **hypothesis**. Only accepted hypotheses are used to generate RDF.

- Base IRI: `https://example.org/procurement/`
- Identifier field: `supplier_id`
- Vocabularies: ontology/procurement.ttl
- Status: 6 accepted, 1 rejected, 0 awaiting review

| Field | Proposed term | Value | Confidence | Status |
| --- | --- | --- | --- | --- |
| `__subject__` | `Supplier` <https://example.org/vocabridge/procurement#Supplier> | IRI | 0.98 | accepted |
| `supplier_id` | `supplier identifier` <https://example.org/vocabridge/procurement#supplierId> | string | 1.00 | accepted |
| `name` | `supplier name` <https://example.org/vocabridge/procurement#supplierName> | string | 0.98 | accepted |
| `country` | `country code` <https://example.org/vocabridge/procurement#countryCode> | string | 0.76 | accepted |
| `registered_on` | `registration date` <https://example.org/vocabridge/procurement#registrationDate> | date | 0.94 | accepted |
| `is_preferred` | `preferred supplier` <https://example.org/vocabridge/procurement#preferredSupplier> | boolean | 0.98 | accepted |
| `notes` | _no suggestion_ | string | 0.17 | rejected |

## Evidence

### `__subject__`

- Proposed: `Supplier` <https://example.org/vocabridge/procurement#Supplier> (method `lexical-baseline`, confidence 0.98)
- Evidence [label-match, +1.00]: field tokens ['supplier'] vs 'Supplier'
- Evidence [domain-votes, +0.18]: 3 field(s) match properties whose domain is Supplier
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:01+00:00 — bulk-accepted at confidence >= 0.9

### `supplier_id`

- Proposed: `supplier identifier` <https://example.org/vocabridge/procurement#supplierId> (method `lexical-baseline`, confidence 1.00)
- Evidence [label-match, +1.00]: field tokens ['supplier', 'id'] vs 'supplierId'
- Evidence [domain, +0.12]: domain includes Supplier
- Evidence [range, +0.05]: values look like string; range xsd:string is compatible
- Evidence [value-pattern, +0.08]: all values are prefixed identifiers (e.g. PO-24-0001); the term mentions id, identifier
- Alternatives: `ordered from` (0.61), `supplier name` (0.59), `preferred supplier` (0.23)
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:01+00:00 — bulk-accepted at confidence >= 0.9

### `name`

- Proposed: `supplier name` <https://example.org/vocabridge/procurement#supplierName> (method `lexical-baseline`, confidence 0.98)
- Evidence [label-match, +0.95]: field tokens ['supplier', 'name'] vs 'supplier name' (with class context)
- Evidence [domain, +0.12]: domain includes Supplier
- Evidence [range, +0.05]: values look like string; range xsd:string is compatible
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:01+00:00 — bulk-accepted at confidence >= 0.9

### `country`

- Proposed: `country code` <https://example.org/vocabridge/procurement#countryCode> (method `lexical-baseline`, confidence 0.76)
- Evidence [label-match, +0.59]: field tokens ['country'] vs 'country code'
- Evidence [domain, +0.12]: domain includes Supplier
- Evidence [range, +0.05]: values look like string; range xsd:string is compatible
- Evidence [value-pattern, +0.08]: all values are two-letter upper-case codes (e.g. ISO 3166-1 alpha-2 country codes); the term mentions code, country, iso
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:01+00:00 — Values are ISO 3166-1 alpha-2 codes

### `registered_on`

- Proposed: `registration date` <https://example.org/vocabridge/procurement#registrationDate> (method `lexical-baseline`, confidence 0.94)
- Evidence [alt-label-match, +0.90]: field tokens ['registered'] vs alternative label 'registered on'
- Evidence [domain, +0.12]: domain includes Supplier
- Evidence [range, +0.05]: values look like date; range xsd:date is compatible
- Alternatives: `raised by` (0.21)
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:01+00:00 — bulk-accepted at confidence >= 0.9

### `is_preferred`

- Proposed: `preferred supplier` <https://example.org/vocabridge/procurement#preferredSupplier> (method `lexical-baseline`, confidence 0.98)
- Evidence [label-match, +0.95]: field tokens ['supplier', 'preferred'] vs 'preferred supplier' (with class context)
- Evidence [domain, +0.12]: domain includes Supplier
- Evidence [range, +0.05]: values look like boolean; range xsd:boolean is compatible
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:01+00:00 — bulk-accepted at confidence >= 0.9

### `notes`

- Proposed: _no suggestion_ (method `lexical-baseline`, confidence 0.17)
- Evidence [no-match,  0.00]: no property scored above 0.35; needs a human or a better suggester
- Decision: rejected by Example Reviewer at 2026-11-16T17:15:01+00:00 — Free text; no suitable property
