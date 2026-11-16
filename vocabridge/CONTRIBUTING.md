# Contributing to vocabridge

Thank you for helping. All contributions are welcome: bug reports, documentation, examples, tests, catalog sources and suggesters.

## Set up

```bash
git clone https://github.com/YOUR-USERNAME/vocabridge.git
cd vocabridge
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Before you open a pull request

```bash
ruff check src tests
pytest
./examples/procurement/run.sh   # the example must still run and validate
```

## Ground rules

1. **Hypotheses stay hypotheses.** No code path may write RDF from a mapping that has not been accepted, and no suggester may set a status other than `proposed`.
2. **Every suggestion explains itself.** New scoring logic must add `Evidence` entries with a clear `kind` and `detail`.
3. **Tests never touch the network.** Catalog sources take an injectable fetch function; use a fake one in tests (see `tests/test_catalog.py`).
4. **Write it yourself.** Do not copy code, data or documentation from other projects into this repository. Depending on a library through `pyproject.toml` is fine; pasting its source is not. If you adapt an idea, credit it in the pull request.
5. **No bundled third-party vocabularies.** Examples use vocabularies written for this project; users bring their own files.
6. **Keep pull requests focused.** One issue per pull request, with a short description of the behaviour change.

## Adding a catalog source

Implement `name` and `search(keyword, limit)` returning `CandidateVocabulary` objects, register the class in `src/vocabridge/catalog/__init__.py`, respect the service's usage policy (identify yourself with a User-Agent, cache results), and credit the service in the README.

## Reporting bugs

Open an issue with the command you ran, a small input file that reproduces the problem (synthetic data only, never confidential data), and what you expected.

By contributing you agree that your contributions are licensed under the Apache License 2.0.
