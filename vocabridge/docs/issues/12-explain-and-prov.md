# `explain` any triple and export decisions as PROV
Labels: trust, provenance, enhancement, v0.3

## Why

An audit trail is only useful if people can query it. When someone asks "why does the graph say this supplier is preferred?", the answer should be one command away.

## What

- `generate --decisions decisions.ttl` writes the mapping decisions as RDF using PROV-O: each hypothesis as an entity with its evidence, method and confidence; each review as an activity associated with the reviewer.
- Link each generated property to its decision so lineage can be queried with SPARQL.
- `vocabridge explain mapping.json "<subject IRI>" "<property IRI>"` prints: source file and row, field, proposed term, evidence, alternatives, reviewer, date and note.

## Acceptance

- The PROV output parses and passes a small SHACL shape written for it.
- `explain` works for literal and reference triples in the procurement example.
