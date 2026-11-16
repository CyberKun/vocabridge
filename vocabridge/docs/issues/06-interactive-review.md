# Interactive review mode
Labels: good first issue, enhancement, cli

## Why

Typing `--accept field` repeatedly is slow for wide tables.

## What

`vocabridge review mapping.json --interactive` steps through every `proposed` hypothesis and shows the field, samples, proposed term, evidence and alternatives, then asks:

```
[a]ccept  [r]eject  [1-3] choose alternative  [s]kip  [q]uit
```

Choosing an alternative replaces the term (and records the original proposal in the review note) and marks it accepted. Save after each decision so quitting loses nothing.

## Acceptance

- Uses only the standard library (`input()`).
- Tests drive it with a fake input function.
