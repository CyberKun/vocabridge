# Export accepted mappings as RML
Labels: enhancement, interoperability, v0.3

## Why

Teams may want to run mappings in their existing RML engine (e.g. RMLMapper, Morph-KGC) instead of vocabridge's generator.

## What

- `vocabridge export-rml mapping.json -o mapping.rml.ttl`
- One `rr:TriplesMap` per mapping file: logical source (CSV), subject template matching vocabridge's IRI scheme, `rr:class` for the subject class, one predicate-object map per accepted field (datatype for literals, template for IRI references).
- Only accepted hypotheses are exported.

## Acceptance

- The exported RML for the procurement example parses with rdflib.
- A test checks that every accepted field appears once and no rejected field appears.
- Document in the README how to run the export with one RML engine.
