#!/usr/bin/env bash
# Reproduce the procurement example end to end.
# Run from this directory after `pip install -e ../..`.
set -euo pipefail
cd "$(dirname "$0")"

VOCAB=ontology/procurement.ttl
BASE=https://example.org/procurement/
REVIEWER="Example Reviewer"
mkdir -p output

echo "== 1. Profile the data"
vocabridge profile data/suppliers.csv -o output/suppliers.profile.json

echo "== 2. Propose hypotheses (nothing is accepted yet)"
vocabridge suggest data/suppliers.csv --vocab "$VOCAB" --base-iri "$BASE" \
  -o output/suppliers.mapping.json
vocabridge suggest data/purchase_orders.csv --vocab "$VOCAB" --base-iri "$BASE" \
  -o output/purchase_orders.mapping.json

echo "== 3. Review: bulk-accept confident matches, then decide the rest by hand"
vocabridge review output/suppliers.mapping.json --accept-above 0.9 --reviewer "$REVIEWER" \
  --report /dev/null
vocabridge review output/suppliers.mapping.json --accept country --reviewer "$REVIEWER" \
  --note "Values are ISO 3166-1 alpha-2 codes" --report /dev/null
vocabridge review output/suppliers.mapping.json --reject notes --reviewer "$REVIEWER" \
  --note "Free text; no suitable property" --report output/suppliers.review.md

vocabridge review output/purchase_orders.mapping.json --accept-above 0.75 \
  --reviewer "$REVIEWER" --report /dev/null
vocabridge review output/purchase_orders.mapping.json --reject approved_by \
  --reviewer "$REVIEWER" --note "Approver is a person; out of scope for this example" \
  --report output/purchase_orders.review.md

echo "== 4. Invoices: names alone cannot link payee_ref / po_ref, the values can"
vocabridge suggest data/invoices.csv --vocab "$VOCAB" --base-iri "$BASE" \
  --link output/suppliers.mapping.json --link output/purchase_orders.mapping.json \
  -o output/invoices.mapping.json
vocabridge review output/invoices.mapping.json --accept-above 0.85 --reviewer "$REVIEWER" \
  --report /dev/null
vocabridge review output/invoices.mapping.json --accept payee_ref --accept po_ref \
  --reviewer "$REVIEWER" --note "All values found among reviewed supplier / order identifiers" \
  --report output/invoices.review.md

echo "== 5. Generate RDF + SHACL and validate"
vocabridge generate output/suppliers.mapping.json -o output/suppliers.ttl \
  --shapes output/suppliers.shapes.ttl
vocabridge generate output/purchase_orders.mapping.json -o output/purchase_orders.ttl \
  --shapes output/purchase_orders.shapes.ttl
vocabridge generate output/invoices.mapping.json -o output/invoices.ttl \
  --shapes output/invoices.shapes.ttl

echo "Done. Open output/*.review.md to see every decision and its evidence."
