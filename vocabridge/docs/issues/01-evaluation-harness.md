# Evaluation harness: measure suggester accuracy against gold mappings
Labels: evaluation, enhancement, v0.2

## Why

We should not claim a suggester is "better" without numbers. Before adding an LLM suggester, we need a repeatable way to measure any suggester.

## What

- A gold file format, e.g. `examples/procurement/gold/purchase_orders.gold.json`, listing the correct term (or `null` for "no suitable term") for each field and the subject class.
- `vocabridge evaluate <data> --vocab ... --gold ...` that runs a suggester and reports, per field and overall:
  - top-1 accuracy, top-3 accuracy (using `alternatives`)
  - precision / recall of non-null suggestions
  - correct abstentions (gold is `null` and the suggester gave no term)
  - calibration: accuracy per confidence bucket (0–0.5, 0.5–0.75, 0.75–0.9, 0.9–1)
- Output as Markdown and JSON.

## Acceptance

- Gold files for both procurement datasets.
- Results for `lexical-baseline` committed to `docs/evaluation.md`.
- Tests for the metric calculations.
