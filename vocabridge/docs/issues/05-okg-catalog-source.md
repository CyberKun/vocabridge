# Add Open Knowledge Graphs (OKG) as an optional catalog source
Labels: catalog-source, enhancement, v0.3

## Why

Open Knowledge Graphs (openknowledgegraphs.com) publishes a semantic search API over a curated catalog of ontologies, vocabularies and standards, with domain categories. It complements Wikidata search.

## What

- `OkgSource` implementing the `CatalogSource` protocol, selectable with `discover --source okg`.
- Call the public search endpoint documented in the OKG README (`/ontologies?q=...`), with a descriptive User-Agent and the existing `FileCache`. Keep request volume low.
- Optional `--category` passthrough.
- Write the client from the public API documentation only; do not copy code from the OKG repository.

## Acceptance

- Tests with a fake fetcher (no network).
- README acknowledgement crediting OKG and linking to it.
- The project still works fully without this source.
