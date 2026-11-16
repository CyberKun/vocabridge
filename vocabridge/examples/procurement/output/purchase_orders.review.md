# Mapping review: `../data/purchase_orders.csv`

Every row below is a **hypothesis**. Only accepted hypotheses are used to generate RDF.

- Base IRI: `https://example.org/procurement/`
- Identifier field: `po_number`
- Vocabularies: ontology/procurement.ttl
- Status: 7 accepted, 1 rejected, 0 awaiting review

| Field | Proposed term | Value | Confidence | Status |
| --- | --- | --- | --- | --- |
| `__subject__` | `Purchase order` <https://example.org/vocabridge/procurement#PurchaseOrder> | IRI | 1.00 | accepted |
| `po_number` | `order number` <https://example.org/vocabridge/procurement#orderNumber> | string | 1.00 | accepted |
| `vendor_id` | `ordered from` <https://example.org/vocabridge/procurement#orderedFrom> | IRI | 0.89 | accepted |
| `order_date` | `order date` <https://example.org/vocabridge/procurement#orderDate> | date | 1.00 | accepted |
| `total_amount` | `total amount` <https://example.org/vocabridge/procurement#totalAmount> | decimal | 1.00 | accepted |
| `currency` | `currency code` <https://example.org/vocabridge/procurement#currencyCode> | string | 0.90 | accepted |
| `cost_centre` | `raised by` <https://example.org/vocabridge/procurement#raisedBy> | IRI | 0.79 | accepted |
| `approved_by` | _no suggestion_ | string | 0.15 | rejected |

## Evidence

### `__subject__`

- Proposed: `Purchase order` <https://example.org/vocabridge/procurement#PurchaseOrder> (method `lexical-baseline`, confidence 1.00)
- Evidence [label-match, +1.00]: field tokens ['purchase', 'order'] vs 'Purchase order'
- Evidence [domain-votes, +0.24]: 4 field(s) match properties whose domain is Purchase order
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:02+00:00 — bulk-accepted at confidence >= 0.75

### `po_number`

- Proposed: `order number` <https://example.org/vocabridge/procurement#orderNumber> (method `lexical-baseline`, confidence 1.00)
- Evidence [alt-label-match, +0.90]: field tokens ['po', 'number'] vs alternative label 'PO number'
- Evidence [domain, +0.12]: domain includes PurchaseOrder
- Evidence [range, +0.05]: values look like string; range xsd:string is compatible
- Evidence [value-pattern, +0.08]: all values are prefixed identifiers (e.g. PO-24-0001); the term mentions number
- Alternatives: `invoice number` (0.39)
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:02+00:00 — bulk-accepted at confidence >= 0.75

### `vendor_id`

- Proposed: `ordered from` <https://example.org/vocabridge/procurement#orderedFrom> (method `lexical-baseline`, confidence 0.89)
- References resources of class `Supplier`
- Evidence [alt-label-match, +0.90]: field tokens ['vendor'] vs alternative label 'vendor'
- Evidence [domain, +0.12]: domain includes PurchaseOrder
- Alternatives: `supplier identifier` (0.32)
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:02+00:00 — bulk-accepted at confidence >= 0.75

### `order_date`

- Proposed: `order date` <https://example.org/vocabridge/procurement#orderDate> (method `lexical-baseline`, confidence 1.00)
- Evidence [label-match, +1.00]: field tokens ['order', 'date'] vs 'order date'
- Evidence [domain, +0.12]: domain includes PurchaseOrder
- Evidence [range, +0.05]: values look like date; range xsd:date is compatible
- Alternatives: `order number` (0.56), `invoice date` (0.29), `registration date` (0.22)
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:02+00:00 — bulk-accepted at confidence >= 0.75

### `total_amount`

- Proposed: `total amount` <https://example.org/vocabridge/procurement#totalAmount> (method `lexical-baseline`, confidence 1.00)
- Evidence [label-match, +1.00]: field tokens ['total', 'amount'] vs 'total amount'
- Evidence [domain, +0.12]: domain includes PurchaseOrder
- Evidence [range, +0.05]: values look like decimal; range xsd:decimal is compatible
- Alternatives: `amount due` (0.26)
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:02+00:00 — bulk-accepted at confidence >= 0.75

### `currency`

- Proposed: `currency code` <https://example.org/vocabridge/procurement#currencyCode> (method `lexical-baseline`, confidence 0.90)
- Evidence [alt-label-match, +0.90]: field tokens ['currency'] vs alternative label 'currency'
- Evidence [range, +0.05]: values look like string; range xsd:string is compatible
- Evidence [value-pattern, +0.08]: all values are three-letter upper-case codes (e.g. ISO 4217 currency codes); the term mentions code, currency, iso
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:02+00:00 — bulk-accepted at confidence >= 0.75

### `cost_centre`

- Proposed: `raised by` <https://example.org/vocabridge/procurement#raisedBy> (method `lexical-baseline`, confidence 0.79)
- References resources of class `Department`
- Evidence [alt-label-match, +0.90]: field tokens ['cost', 'centre'] vs alternative label 'cost centre'
- Evidence [reference, -0.10]: object property, but the field name does not look like an identifier or reference
- Evidence [domain, +0.12]: domain includes PurchaseOrder
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:02+00:00 — bulk-accepted at confidence >= 0.75

### `approved_by`

- Proposed: _no suggestion_ (method `lexical-baseline`, confidence 0.15)
- Evidence [no-match,  0.00]: no property scored above 0.35; needs a human or a better suggester
- Decision: rejected by Example Reviewer at 2026-11-16T17:15:02+00:00 — Approver is a person; out of scope for this example
