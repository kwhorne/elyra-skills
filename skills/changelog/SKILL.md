---
name: changelog
description: Maintain a CHANGELOG.md following the Keep a Changelog format with semver. Use when the user asks to update the changelog, add release notes, prepare a release, or generate changelog entries from commits or merged PRs.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, edit, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [changelog, release, semver]
---

# Changelog

Maintains a `CHANGELOG.md` that humans actually read. Follows [Keep a Changelog 1.1.0](https://keepachangelog.com/) and [Semantic Versioning 2.0.0](https://semver.org/).

## When to use

- "Update the changelog"
- "Add a changelog entry for X"
- "Generate release notes"
- "Prepare a release / cut version X.Y.Z"

## Why this format

- Written for **users**, not maintainers — "what changed for me?"
- Categorized so users can scan for what matters to them
- Semver-aligned so the version number signals what to expect
- Diff-friendly so PRs adding entries don't conflict

## Procedure

### Adding entries during development

Every user-visible change gets an entry under `[Unreleased]` *in the same PR* that makes the change. Don't batch this at release time.

1. **Open `CHANGELOG.md`**, find the `## [Unreleased]` section (create if missing)
2. **Pick the category** (Added / Changed / Deprecated / Removed / Fixed / Security)
3. **Write one line** — user-visible outcome, not implementation
4. Optionally append `(#PR)` or `(thanks @contributor)`

### Cutting a release

1. **Decide the version bump** based on what's in `[Unreleased]`:
   - `Removed` or breaking `Changed` → **major**
   - `Added` or non-breaking `Changed` → **minor**
   - `Fixed` or `Security` only → **patch**
2. **Rename** `## [Unreleased]` to `## [X.Y.Z] - YYYY-MM-DD`
3. **Add a new empty** `## [Unreleased]` block at the top
4. **Update the link references** at the bottom of the file
5. **Tag and push** (`git tag vX.Y.Z`)

### Generating entries from history

If entries weren't added during development, reconstruct from commits or merged PRs:

```bash
# Conventional Commits → grouped log since last tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)
echo "Changes since $LAST_TAG:"
git log --no-merges --pretty=format:'%s' "$LAST_TAG"..HEAD | sort | uniq

# Group by Conventional Commit type
git log --no-merges --pretty=format:'%s' "$LAST_TAG"..HEAD | awk -F: '
  /^feat(\(|:)/   { print "Added:", $0 }
  /^fix(\(|:)/    { print "Fixed:", $0 }
  /^perf(\(|:)/   { print "Changed (perf):", $0 }
  /^refactor(\(|:)/ { next }   # not user-visible
  /^docs(\(|:)/   { next }
  /^test(\(|:)/   { next }
  /^chore(\(|:)/  { next }
  /^build(\(|:)/  { next }
  /^ci(\(|:)/     { next }
  /BREAKING CHANGE/ { print "Changed (BREAKING):", $0 }
  { print "Other:", $0 }
'

# PRs merged since last release (needs gh CLI)
gh pr list --state merged --base main --search "merged:>$(git log -1 --format=%aI $LAST_TAG)" \
  --json number,title,author --jq '.[] | "- \(.title) (#\(.number)) by @\(.author.login)"'
```

These are starting points. Rewrite for **user-visible impact** before pasting into the changelog.

## Categories (Keep a Changelog)

| Category | Use for | Semver impact |
|---|---|---|
| **Added** | New features | minor |
| **Changed** | Changes in existing functionality | minor (or major if breaking) |
| **Deprecated** | Soon-to-be-removed features | minor (the deprecation itself) |
| **Removed** | Now-removed features | **major** |
| **Fixed** | Bug fixes | patch |
| **Security** | Vulnerability fixes | patch (or higher if breaking) |

## Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Passwordless email login flow (#482)

### Fixed
- Cart total miscalculation when applying multiple coupons (#491)

## [1.4.0] - 2026-05-15

### Added
- Dark mode toggle in settings (#460)
- Bulk import for CSV files up to 10 MB (#467)

### Changed
- Order list now paginates server-side; client-side filter removed.

### Deprecated
- `/api/v1/legacy-export` will be removed in 2.0.0. Use `/api/v1/exports` instead.

### Fixed
- Timezone offset issue in scheduled reports for users east of UTC+12 (#471)

### Security
- Updated `image-magick` to address CVE-2026-1234 ([advisory](https://...)).

## [1.3.2] - 2026-04-22

### Fixed
- Session expiring after 10 minutes instead of configured 24 hours (#445)

[Unreleased]: https://github.com/org/repo/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/org/repo/compare/v1.3.2...v1.4.0
[1.3.2]: https://github.com/org/repo/compare/v1.3.1...v1.3.2
```

## Writing good entries

Each line should answer: **"What changed for the user, in plain language?"**

| ❌ Don't | ✅ Do |
|---|---|
| `Refactor cart service` | *(don't include — not user-visible)* |
| `Bumped lodash to 4.17.21` | *(don't include unless it fixes a known issue)* |
| `Add new feature` | `Added bulk CSV import (up to 10 MB)` |
| `Fix bug` | `Fixed cart total when multiple coupons applied` |
| `Updated stuff` | `Changed order list to paginate server-side; client-side filter removed` |
| `Closes #482` | `Added passwordless email login flow (#482)` |

### What to leave out

- Internal refactors with no user impact
- Test additions / CI changes
- Dependency bumps without behavior change
- Docs typos
- Anything that wouldn't matter if a user skipped reading it

If in doubt: **would a user want to know?** If no, leave it out.

## Breaking changes

Make them impossible to miss:

```markdown
## [2.0.0] - 2026-06-01

### Changed
- **BREAKING:** API timestamps are now ISO 8601 strings (were unix epoch integers).
  Migration: parse `created_at`/`updated_at` as ISO 8601 in your client.

### Removed
- **BREAKING:** Removed `/api/v1/legacy-export` (deprecated in 1.4.0).
  Migration: switch to `/api/v1/exports`.
```

Use **BREAKING** in bold at the start of the line. Include a one-line migration note.

## Output format

When asked to update the changelog, propose the diff:

```markdown
I'll add to CHANGELOG.md under [Unreleased]:

### Added
- <entry>

### Fixed
- <entry>

Apply? (yes/no)
```

When cutting a release:

```markdown
Proposed release: v<X.Y.Z>
- Bump reason: <added features → minor / fixes only → patch / breaking → major>
- Entries moving from [Unreleased] to [<X.Y.Z>]:
  - …

Will:
1. Rename [Unreleased] → [<X.Y.Z>] - <date>
2. Insert new empty [Unreleased]
3. Update link references at bottom
4. Tag v<X.Y.Z>

Apply? (yes/no)
```

## Anti-patterns

- ❌ Batching all changelog entries at release time — they always end up vague
- ❌ Copy-pasting commit messages as entries
- ❌ Listing every internal refactor
- ❌ "Various improvements and bug fixes"
- ❌ Mixing patch / minor / major changes without bumping version appropriately
- ❌ Silently breaking the API without a `**BREAKING**` marker
- ❌ Deleting old entries when re-organizing (they're history; preserve them)

## References

- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) — for publishing the changelog as a release
