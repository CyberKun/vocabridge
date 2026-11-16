# Competency questions as executable tests
Labels: quality, enhancement, v0.3

## Why

SHACL proves the data is well-formed, not that it is useful. Competency questions state what the graph must be able to answer. Checking them is a long-standing ontology-engineering practice, and still mostly manual.

## What

- A `questions/` folder of `.rq` SPARQL files, each with a header comment stating the question and an expectation (`# expect: rows >= 1`, `# expect: rows == 6`, `# expect: ask true`).
- `vocabridge test <data.ttl...> --questions questions/` runs them and reports pass/fail.
- Optional later: an LLM drafts SPARQL from a natural-language question, stored as a proposed hypothesis that a person approves.

## Acceptance

- `examples/procurement/queries/invoice-supplier-order.rq` gains an expectation and passes in CI.
