# Principles

These principles decide what vocabridge does and does not do. When a design question is unclear, come back here.

## 1. Suggestions are hypotheses

Any mapping produced by software — a string-similarity rule, an embedding model or an LLM — is a claim about what data means. It may be wrong. vocabridge therefore stores it as a hypothesis with:

- **status**: `proposed`, `accepted` or `rejected`
- **evidence**: named reasons with signed weights, so a reviewer can see *why*
- **confidence**: a number in `[0, 1]` derived from that evidence
- **alternatives**: what else was considered
- **review**: who decided, when, and an optional note

Nothing reaches the output graph unless it is accepted.

## 2. Keep evidence, claims and decisions separate

| Layer | Where it lives | Example |
| --- | --- | --- |
| Source evidence | dataset profile | "all 6 values parse as `xsd:date`" |
| Machine claim | hypothesis | "`order_date` means `proc:orderDate`" |
| Human decision | review | "accepted by A. Rao on 2026-11-16" |
| Published fact | generated RDF | `<po/1> proc:orderDate "2024-01-08"^^xsd:date` |

Mixing these layers is how AI-assisted data pipelines quietly produce confident nonsense.

## 3. Say "I don't know"

When there is no good evidence, the suggester returns no term rather than its least-bad guess. An honest gap is cheaper to fix than a plausible error.

## 4. Reuse before invent

The goal is to connect data to vocabularies that already exist and are already understood by others. vocabridge helps find and apply them; it does not encourage minting new terms when a published one fits.

## 5. Validate what you publish

Every generation run produces SHACL shapes from the accepted mappings and validates the output against them. A mapping that produces invalid data is a mapping that needs review.

## 6. Stay independent and standards-based

No component depends on a single external service or vendor. Catalog sources are pluggable and optional. Inputs and outputs use open W3C standards.
