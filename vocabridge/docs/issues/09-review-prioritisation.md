# Prioritise what people review first
Labels: trust, enhancement, v0.2

## Why

Human review is the expensive step. Active-learning studies on schema alignment report large reductions in labelling effort by asking about the most informative items first. vocabridge can apply the same idea without training a model.

## What

- `vocabridge review mapping.json --queue` lists proposed hypotheses ordered by a documented priority score combining: uncertainty (confidence near the acceptance threshold), small margin between the top suggestion and the best alternative, and impact (reference fields and identifier fields first; complete fields before sparse ones).
- Group near-identical decisions (e.g. several `*_date` fields mapping to date properties) so one decision can be applied to the group with `--accept-group`.
- Show the expected number of decisions saved.

## Acceptance

- Deterministic ordering, with the score's components shown for each item.
- Tests for ordering and grouping.
