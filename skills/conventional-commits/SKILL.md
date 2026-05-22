---
name: conventional-commits
description: Generate Conventional Commits messages from staged changes. Use when the user asks to write a commit message, follow Conventional Commits, summarize staged changes, or prepare a commit.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [git, commits, conventions]
---

# Conventional Commits

Writes commit messages that follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) spec — useful for automated changelogs, semver bumps, and humans skimming history.

## When to use

- "Write a commit message for these changes"
- "Commit this with a conventional commit message"
- "Summarize what's staged"

## Procedure

1. **Inspect what's actually staged** (not the working tree):
   ```bash
   git diff --staged --stat
   git diff --staged
   ```
   If nothing is staged, ask the user whether to use `git diff` (working tree) instead.

2. **Optionally run the helper script** in `scripts/suggest.sh` to get a quick summary of touched paths and a type guess.

3. **Pick a type** (see table below). When multiple apply, choose the one that best describes the *user-facing* intent.

4. **Pick a scope** (optional but recommended) — usually a top-level module, package, or feature area. Lowercase, no spaces.

5. **Write the subject line:**
   - `<type>(<scope>): <imperative summary>`
   - ≤72 chars, no trailing period
   - Imperative mood: "add", "fix", "rename" — not "added", "adds"

6. **Add a body** if the change is non-trivial:
   - Blank line after subject
   - Wrap at ~72 chars
   - Explain *why*, not *what* (the diff already shows what)

7. **Footer** for breaking changes or issue refs:
   - `BREAKING CHANGE: <description>` or `!` after type/scope
   - `Refs: #123` / `Closes: #123`

## Types

| Type | Use for | Triggers semver |
|---|---|---|
| `feat` | New user-facing feature | minor |
| `fix` | Bug fix | patch |
| `perf` | Performance improvement | patch |
| `refactor` | Code change that neither fixes a bug nor adds a feature | none |
| `docs` | Documentation only | none |
| `test` | Adding or fixing tests | none |
| `build` | Build system, dependencies, packaging | none |
| `ci` | CI configuration | none |
| `chore` | Maintenance with no code impact | none |
| `style` | Formatting, whitespace, no logic change | none |
| `revert` | Revert a previous commit | depends |

Breaking changes: append `!` (e.g. `feat(api)!: rename /users to /accounts`) **and** add a `BREAKING CHANGE:` footer explaining the migration.

## Output format

Show the proposed message in a code block, then offer to run `git commit`:

```text
feat(auth): support passwordless email login

Adds a magic-link flow alongside the existing password login.
Tokens are single-use and expire after 10 minutes.

Refs: #482
```

Then: "Run `git commit -F-` with this message? (yes/no)"

## Anti-patterns

- ❌ `chore: updates` — meaningless; pick the real type and say what changed
- ❌ Past tense ("added X") — use imperative ("add X")
- ❌ Multiple unrelated changes in one commit — suggest splitting instead
- ❌ Trailing period on the subject line
- ❌ Wrapping the subject across lines

## Examples

```text
fix(parser): handle escaped quotes inside attribute values

Closes: #1204
```

```text
refactor(http): extract retry logic into a helper

No behavior change. Sets up the next commit which adds exponential backoff.
```

```text
feat(api)!: return ISO 8601 timestamps everywhere

BREAKING CHANGE: `created_at` and `updated_at` were unix timestamps;
they are now ISO 8601 strings. Update clients accordingly.
```
