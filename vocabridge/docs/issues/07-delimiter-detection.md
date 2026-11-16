# Detect CSV delimiters (TSV, semicolon)
Labels: good first issue, profiling

## Why

Many exports use tabs or semicolons. Today only comma-separated files work.

## What

- Treat `.tsv` files as tab-separated.
- For `.csv`, use `csv.Sniffer` on the first few kilobytes to detect `,`, `;`, `\t` or `|`, falling back to comma.
- Add `--delimiter` to `profile`, `suggest` and `discover` to override detection; store the delimiter in the mapping file so `generate` reads the file the same way.

## Acceptance

- Tests for comma, semicolon and tab files.
- Existing mapping files without a delimiter keep working (default comma).
