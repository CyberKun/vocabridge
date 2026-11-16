# Decision memory: reuse past human decisions as evidence
Labels: trust, enhancement, v0.3

## Why

Organisations map similar columns again and again. Every reviewed decision is knowledge that should make the next mapping faster and more consistent.

## What

- A local memory file (`.vocabridge/memory.json`, or a path given with `--memory`) that stores accepted and rejected (field profile fingerprint → term) pairs, with reviewer and date.
- `suggest --memory` adds `Evidence` of kind `prior-decision` ("accepted for `vendor_id` in purchase_orders.csv by A. Rao on 2026-11-16"), positive for prior accepts and negative for prior rejects.
- Prior decisions never auto-accept anything; they are evidence only.
- `vocabridge memory add <mapping files>` and `vocabridge memory show`.

## Acceptance

- Tests showing a prior rejection prevents the same suggestion from ranking first.
