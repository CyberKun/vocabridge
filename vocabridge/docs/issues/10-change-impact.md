# Change impact: reopen only the decisions a change affects
Labels: trust, maintenance, enhancement, v0.2

## Why

Mappings rot. Studies of real mapping repositories find that changes are driven mostly by changes in the data, and that broken URIs and namespaces are the most common bug. Propagating ontology changes to mappings is still described in the literature as largely manual.

## What

`vocabridge diff mapping.json [--data new.csv] [--vocab new-vocab.ttl]` compares the current inputs with what the decisions were based on:

- **Data changes**: fields added, removed or renamed (detected by value similarity), inferred type changed, completeness or uniqueness lost, value pattern changed, link overlap dropped.
- **Vocabulary changes**: accepted term removed, deprecated (`owl:deprecated`), domain or range changed.
- Each affected hypothesis is set back to `proposed` with a review note explaining the change; unaffected decisions are kept.
- Output a change report in Markdown and a non-zero exit code when decisions were reopened, so CI can block a stale mapping.
- Lint generated IRIs: base IRI ending, illegal characters, namespace mismatches.

To support this, `suggest` stores a fingerprint of the field profile and the term definition inside each hypothesis.

## Acceptance

- Tests for each change type using small fixture files.
- The procurement example gains a `data/v2/` with a renamed and a retyped column to demonstrate the report.
