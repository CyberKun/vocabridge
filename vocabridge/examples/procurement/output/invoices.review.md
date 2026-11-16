# Mapping review: `../data/invoices.csv`

Every row below is a **hypothesis**. Only accepted hypotheses are used to generate RDF.

- Base IRI: `https://example.org/procurement/`
- Identifier field: `invoice_number`
- Vocabularies: ontology/procurement.ttl
- Status: 7 accepted, 0 rejected, 0 awaiting review

| Field | Proposed term | Value | Confidence | Status |
| --- | --- | --- | --- | --- |
| `__subject__` | `Invoice` <https://example.org/vocabridge/procurement#Invoice> | IRI | 0.98 | accepted |
| `invoice_number` | `invoice number` <https://example.org/vocabridge/procurement#invoiceNumber> | string | 1.00 | accepted |
| `payee_ref` | `billed by` <https://example.org/vocabridge/procurement#billedBy> | IRI | 0.63 | accepted |
| `po_ref` | `bills order` <https://example.org/vocabridge/procurement#billsOrder> | IRI | 0.63 | accepted |
| `issued_on` | `invoice date` <https://example.org/vocabridge/procurement#invoiceDate> | date | 0.94 | accepted |
| `amount_due` | `amount due` <https://example.org/vocabridge/procurement#amountDue> | decimal | 1.00 | accepted |
| `currency` | `currency code` <https://example.org/vocabridge/procurement#currencyCode> | string | 0.90 | accepted |

## Evidence

### `__subject__`

- Proposed: `Invoice` <https://example.org/vocabridge/procurement#Invoice> (method `lexical-baseline`, confidence 0.98)
- Evidence [label-match, +1.00]: field tokens ['invoice'] vs 'Invoice'
- Evidence [domain-votes, +0.18]: 3 field(s) match properties whose domain is Invoice
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:02+00:00 — bulk-accepted at confidence >= 0.85

### `invoice_number`

- Proposed: `invoice number` <https://example.org/vocabridge/procurement#invoiceNumber> (method `lexical-baseline`, confidence 1.00)
- Evidence [label-match, +1.00]: field tokens ['invoice', 'number'] vs 'invoice number'
- Evidence [domain, +0.12]: domain includes Invoice
- Evidence [range, +0.05]: values look like string; range xsd:string is compatible
- Evidence [value-pattern, +0.08]: all values are prefixed identifiers (e.g. PO-24-0001); the term mentions number
- Alternatives: `order number` (0.39), `invoice date` (0.28)
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:02+00:00 — bulk-accepted at confidence >= 0.85

### `payee_ref`

- Proposed: `billed by` <https://example.org/vocabridge/procurement#billedBy> (method `lexical-baseline`, confidence 0.63)
- References resources of class `Supplier`
- Evidence [label-match, +0.07]: field tokens ['payee'] vs 'billed by'
- Evidence [value-overlap, +0.45]: 4 of 4 distinct values (100%) appear in suppliers.supplier_id, the identifiers of Supplier
- Evidence [domain, +0.12]: domain includes Invoice
- Alternatives: `ordered from` (0.39)
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:03+00:00 — All values found among reviewed supplier / order identifiers

### `po_ref`

- Proposed: `bills order` <https://example.org/vocabridge/procurement#billsOrder> (method `lexical-baseline`, confidence 0.63)
- References resources of class `PurchaseOrder`
- Evidence [label-match, +0.07]: field tokens ['po'] vs 'bills order'
- Evidence [value-overlap, +0.45]: 5 of 5 distinct values (100%) appear in purchase_orders.po_number, the identifiers of PurchaseOrder
- Evidence [domain, +0.12]: domain includes Invoice
- Alternatives: `order number` (0.30)
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:03+00:00 — All values found among reviewed supplier / order identifiers

### `issued_on`

- Proposed: `invoice date` <https://example.org/vocabridge/procurement#invoiceDate> (method `lexical-baseline`, confidence 0.94)
- Evidence [alt-label-match, +0.90]: field tokens ['issued'] vs alternative label 'issued on'
- Evidence [domain, +0.12]: domain includes Invoice
- Evidence [range, +0.05]: values look like date; range xsd:date is compatible
- Alternatives: `raised by` (0.23)
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:02+00:00 — bulk-accepted at confidence >= 0.85

### `amount_due`

- Proposed: `amount due` <https://example.org/vocabridge/procurement#amountDue> (method `lexical-baseline`, confidence 1.00)
- Evidence [label-match, +1.00]: field tokens ['amount', 'due'] vs 'amount due'
- Evidence [domain, +0.12]: domain includes Invoice
- Evidence [range, +0.05]: values look like decimal; range xsd:decimal is compatible
- Alternatives: `total amount` (0.26), `country code` (0.22)
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:02+00:00 — bulk-accepted at confidence >= 0.85

### `currency`

- Proposed: `currency code` <https://example.org/vocabridge/procurement#currencyCode> (method `lexical-baseline`, confidence 0.90)
- Evidence [alt-label-match, +0.90]: field tokens ['currency'] vs alternative label 'currency'
- Evidence [range, +0.05]: values look like string; range xsd:string is compatible
- Evidence [value-pattern, +0.08]: all values are three-letter upper-case codes (e.g. ISO 4217 currency codes); the term mentions code, currency, iso
- Decision: accepted by Example Reviewer at 2026-11-16T17:15:02+00:00 — bulk-accepted at confidence >= 0.85
