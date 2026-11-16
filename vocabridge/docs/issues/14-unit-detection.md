# Detect units in numeric columns
Labels: profiling, enhancement, v0.3

## Why

Numbers without units silently break integration: a weight column may mix kilograms and pounds, or carry units inside the values ("5.2 kg", "12 lb"). Research on tabular data treats unit identification as its own problem.

## What

- Profile numeric-looking columns whose values carry unit symbols; detect the symbols and whether they are mixed.
- Read unit hints from headers (`weight_kg`, `amount_usd`).
- Record the unit as profile evidence and as a hypothesis attribute; when vocabularies use QUDT or similar, propose a unit IRI.
- Warn (negative evidence) when a column mixes units.

## Acceptance

- Tests for clean, embedded-symbol and mixed-unit columns.
