#!/usr/bin/env bash
# Open the drafts in docs/issues/ as GitHub issues in your repository.
# Requires the GitHub CLI (`gh auth login`). Run from the repository root.
#
# Each draft starts with:
#   # Title
#   Labels: a, b, c
set -euo pipefail

REPO="${1:-}"
REPO_ARG=()
[[ -n "$REPO" ]] && REPO_ARG=(--repo "$REPO")

# Create every label used by the drafts (no error if it already exists).
grep -h '^Labels:' docs/issues/*.md | sed 's/^Labels: *//' | tr ',' '\n' \
  | sed 's/^ *//; s/ *$//' | sort -u | while read -r label; do
    [[ -z "$label" ]] && continue
    gh label create "$label" "${REPO_ARG[@]}" --force >/dev/null
done

for file in docs/issues/*.md; do
  title=$(sed -n '1s/^# *//p' "$file")
  labels=$(sed -n '2s/^Labels: *//p' "$file" | sed 's/, */,/g')
  body=$(tail -n +3 "$file")
  echo "Creating: $title"
  gh issue create "${REPO_ARG[@]}" --title "$title" --label "$labels" --body "$body"
done
