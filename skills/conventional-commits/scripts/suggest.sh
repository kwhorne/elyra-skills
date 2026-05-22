#!/usr/bin/env bash
# suggest.sh — quick summary of staged changes + a Conventional Commits type guess.
# Read-only: makes no changes to the repo.
#
# Usage: bash scripts/suggest.sh
#
# Output:
#   - files changed (added / modified / deleted / renamed counts)
#   - top touched paths
#   - guessed type (feat / fix / docs / test / build / chore)

set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "error: not inside a git repository" >&2
  exit 1
fi

DIFF_BASE="--staged"
if [ -z "$(git diff --staged --name-only)" ]; then
  if [ -n "$(git diff --name-only)" ]; then
    echo "note: nothing staged; analyzing working tree instead" >&2
    DIFF_BASE=""
  else
    echo "nothing to commit (no staged or unstaged changes)"
    exit 0
  fi
fi

# shellcheck disable=SC2086
mapfile -t FILES < <(git diff $DIFF_BASE --name-only)
# shellcheck disable=SC2086
STATUS=$(git diff $DIFF_BASE --name-status)

added=$(printf '%s\n' "$STATUS" | awk '$1=="A"' | wc -l | tr -d ' ')
modified=$(printf '%s\n' "$STATUS" | awk '$1=="M"' | wc -l | tr -d ' ')
deleted=$(printf '%s\n' "$STATUS" | awk '$1=="D"' | wc -l | tr -d ' ')
renamed=$(printf '%s\n' "$STATUS" | awk '$1 ~ /^R/' | wc -l | tr -d ' ')

echo "Staged change summary"
echo "---------------------"
echo "  added:    $added"
echo "  modified: $modified"
echo "  deleted:  $deleted"
echo "  renamed:  $renamed"
echo
echo "Top paths:"
printf '%s\n' "${FILES[@]}" | head -10 | sed 's/^/  /'
echo

# Heuristic type guess
guess="chore"
if printf '%s\n' "${FILES[@]}" | grep -qiE '(^|/)(test|tests|spec|__tests__)/'; then
  guess="test"
fi
if printf '%s\n' "${FILES[@]}" | grep -qiE '\.(md|mdx|rst|txt)$|^docs/'; then
  guess="docs"
fi
if printf '%s\n' "${FILES[@]}" | grep -qiE '(package(-lock)?\.json|pnpm-lock\.yaml|yarn\.lock|composer\.(json|lock)|Cargo\.(toml|lock)|go\.(mod|sum)|pyproject\.toml|requirements.*\.txt)$'; then
  guess="build"
fi
if printf '%s\n' "${FILES[@]}" | grep -qiE '(^|/)\.github/workflows/|(^|/)\.gitlab-ci\.yml$|(^|/)Dockerfile$'; then
  guess="ci"
fi
# feat/fix heuristic from added vs modified
if [ "$added" -gt "$modified" ] && [ "$added" -gt 0 ]; then
  guess="feat"
elif [ "$modified" -gt 0 ]; then
  guess="fix"
fi

echo "Type guess: $guess"
echo "(verify by reading the actual diff; this is a heuristic, not a decision)"
