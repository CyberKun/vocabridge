# LLM suggester that produces reviewable hypotheses
Labels: suggester, enhancement, v0.2

## Why

Lexical matching cannot understand that `amt_net` means "total amount excluding tax". A language model can often infer this from field names, samples and term definitions — but it can also be confidently wrong, so its output must go through the same review.

## What

- `suggest --method llm` alongside the existing `lexical-baseline`.
- Provider-agnostic interface: a small `LanguageModel` protocol (`complete(prompt) -> str`) with one reference adapter; API keys from environment variables only.
- The prompt includes the field profile (name, type, samples) and a shortlist of candidate terms (from the lexical scorer) with labels and comments. The model must answer in structured JSON: chosen term or `null`, rationale, and which evidence it relied on.
- Each rationale becomes an `Evidence` entry of kind `llm-rationale`. Method is recorded as `llm:<model-name>`.
- Invalid or out-of-shortlist answers are discarded, not trusted.
- Status is always `proposed`. Never auto-accept.

## Acceptance

- Tests use a fake model (no network).
- Evaluation (see the evaluation-harness issue) compares `llm` with `lexical-baseline` on the procurement gold files.
