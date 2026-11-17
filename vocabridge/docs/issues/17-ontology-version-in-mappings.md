# Record ontology version and checksum in every mapping file
Labels: architecture, maintenance, v0.2

## Problem

Mapping files list the vocabulary files used, but not which version of them. If the ontology changes, nothing tells you which mappings were reviewed against an older version. Change impact (issue 10) needs this information.

## Proposal

- When `suggest` loads a vocabulary, record for each file: path, SHA-256 of its content, `owl:versionIRI` / `owl:versionInfo` when present, and the number of terms.
- `review` and `generate` warn when the current vocabulary checksum differs from the recorded one.
- Optional `vocabridge.json` registry at the project root: the domain ontology and domain shapes files with their versions, and the list of mapping files with the ontology version each was reviewed against. `vocabridge status` prints which mappings are current and which are stale.
- Increment the mapping file `format_version`, staying backward compatible with v1 files.

## Acceptance

- Tests: changing one label in the ontology produces a checksum warning on `generate`.
- v1 mapping files still load.
- `vocabridge status` lists every mapping with current / stale.
