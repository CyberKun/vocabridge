# Procurement example

Synthetic data and a small ontology written for this project, used to demonstrate the full vocabridge workflow.

- `data/suppliers.csv`, `data/purchase_orders.csv`, `data/invoices.csv` — invented records, no real companies
- `ontology/procurement.ttl` — minimal classes and properties, with `skos:altLabel` synonyms
- `queries/invoice-supplier-order.rq` — a competency question answered across all three datasets
- `run.sh` — runs profile → suggest → review → generate → validate
- `output/` — the committed results of `run.sh`, including the review reports

Things worth noticing in `output/*.review.md`:

- `vendor_id` is mapped to **ordered from**, not to **supplier identifier**. The ontology says *vendor* is another name for that relationship, and the field looks like a reference, so its values become links to `Supplier` resources. Those links use the same IRIs as the supplier file, so the two datasets join into one graph.
- `name` becomes **supplier name** because the rows are suppliers (class context).
- `notes` and `approved_by` get **no suggestion**: nothing in the ontology shares a word with them, so the tool abstains instead of guessing. The reviewer rejected them with a note.
- `country` was below the bulk-accept threshold and was accepted by hand with a note explaining why.
- In `invoices.csv`, `payee_ref` and `po_ref` share no words with *billed by* and *bills order*. With names alone they get no suggestion. With `--link` to the reviewed supplier and order mappings, every value is found among those identifiers, so the links are proposed with that overlap as evidence, and the reviewer accepts them with a note.
