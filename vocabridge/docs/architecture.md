# Architecture

vocabridge is a small pipeline of independent stages. Each stage reads and writes plain files, so stages can be run, inspected and replaced separately.

```
                    ┌──────────────┐
                    │ catalog/     │  discover: which published vocabularies
                    │  wikidata.py │  might fit? (optional, online)
                    └──────┬───────┘
                           │ leads for the user to choose vocabulary files
                           ▼
┌──────────┐   ┌──────────────┐   ┌────────────┐   ┌───────────────┐   ┌─────────────┐
│ data.csv │──►│ profiling.py │──►│ suggest.py │──►│ hypotheses.py │──►│ generate.py │
│ data.json│   │ DatasetProfile│  │ + vocab.py │   │ MappingSet    │   │ RDF + SHACL │
└──────────┘   └──────────────┘   └────────────┘   │ (JSON file)   │   │ + pySHACL   │
                                                   └──────┬────────┘   └─────────────┘
                                                          │
                                                   review (cli.py) + report.py
                                                   people accept / reject
```

## Modules

| Module | Responsibility |
| --- | --- |
| `profiling.py` | Read CSV/JSON; infer `boolean`, `integer`, `decimal`, `date` or `string`; count missing and distinct values; keep samples. |
| `vocab.py` | Parse any rdflib-readable vocabulary into `Term` objects (classes, datatype/object properties, labels, `skos:altLabel`, domains, ranges). |
| `text.py` | Tokenise `snake_case`, `camelCase` and labels; light singularisation. |
| `values.py` | Value evidence: value-pattern detection and identifier overlap with linked, already-reviewed datasets. |
| `suggest.py` | The baseline suggester. Scores each property for each field from named evidence and picks the subject class and identifier field. |
| `hypotheses.py` | The data model: `MappingHypothesis`, `Evidence`, `Review`, `MappingSet`, JSON (de)serialisation. |
| `report.py` | Markdown review report. |
| `generate.py` | RDF generation from accepted hypotheses, SHACL shape generation, validation. |
| `catalog/` | `CatalogSource` protocol, `discover()` merger, file cache, Wikidata source. |
| `cli.py` | `profile`, `discover`, `suggest`, `review`, `generate`, `validate`. |

## Key decisions

**Mapping file as the contract.** The JSON mapping file is the interface between "suggest" and "generate". Any suggester — the lexical baseline today, an LLM later — must emit the same structure, and the generator only trusts `accepted` entries. This keeps the review step mandatory whatever the suggester.

**Stable resource IRIs.** Resources are minted as `{base}{class-slug}/{key}`. A reference field (`vendor_id` → `ordered from`, range `Supplier`) therefore produces the same IRI as the supplier dataset's own rows, so separate files join into one graph without a separate reconciliation step.

**Generated shapes are closed.** Each subject class gets a closed `sh:NodeShape` listing exactly the accepted properties, their datatypes or `sh:nodeKind sh:IRI`, `sh:maxCount 1`, and `sh:minCount 1` for fields that were complete in the profile.

**Value evidence beats name evidence.** Names say what someone called a column; values show what it holds. When `--link` points at reviewed mapping files, a reference field whose values are found among a linked dataset's identifiers gets strong positive evidence, and a field whose values are absent gets negative evidence, even when the names match. Only datasets with an accepted subject class can be linked, so evidence is never built on unreviewed guesses.

**Paths are relative to the mapping file.** A mapping file and its dataset can be moved together and still regenerate.

## Extending

- **New catalog source**: implement `name` and `search(keyword, limit) -> list[CandidateVocabulary]`, register it in `catalog/__init__.py:SOURCES`, add tests with a fake fetcher (no network in tests).
- **New suggester**: write a function that returns a `MappingSet` whose hypotheses have `method` set to your suggester's name and carry evidence. Reuse `choose_id_field` and the existing review/generate stages unchanged.
