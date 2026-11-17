# Write each dataset to its own named graph, with provenance kept separate
Labels: architecture, provenance, v0.2

## Problem

v0.1 writes instance data and run provenance (`prov:Activity`, reviewers, timestamps) into the same default graph in a Turtle file. When several datasets are combined, it is no longer clear which triples came from which source, and provenance is mixed with business data.

## Proposal

- `generate --format trig` (and `nquads`) writes the instance data into a named graph per dataset, e.g. `<{base}graph/invoices>`.
- Provenance goes into a separate graph, e.g. `<{base}graph/invoices/provenance>`, linked to the data graph.
- Turtle output stays available (`--format turtle`, the default), with an option to leave provenance out.
- `validate-graph` (see the domain-shapes issue) accepts TriG / N-Quads and validates the union of the data graphs.

## Acceptance

- Generated TriG parses with rdflib and contains one data graph and one provenance graph per dataset.
- A SPARQL query using `GRAPH ?g` can tell which dataset each invoice came from.
- Existing Turtle output is unchanged by default.
