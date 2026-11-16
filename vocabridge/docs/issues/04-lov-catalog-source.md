# Add Linked Open Vocabularies (LOV) as a catalog source
Labels: catalog-source, enhancement, v0.3

## Why

Wikidata describes vocabularies as items; LOV indexes vocabulary *terms*. Adding it improves discovery for field-level matches.

## What

- `LovSource` implementing the `CatalogSource` protocol, selectable with `discover --source lov`.
- Use LOV's public search API, a descriptive User-Agent and the existing `FileCache`.
- Map results to `CandidateVocabulary` (prefix, title, homepage).

## Acceptance

- Tests with a fake fetcher (no network).
- README acknowledgement and a note on LOV's terms of use.
