---
name: pr-description
description: Write a clear, scannable pull request description from a diff or branch. Use when the user asks to draft a PR description, summarize a branch, prepare a change for review, or fill out a PR template.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [git, pr, review]
---

# PR Description

A reviewer should be able to answer **"what changed and why"** in 30 seconds. That's the whole goal.

## When to use

- "Write a PR description for this branch"
- "Summarize what's in this PR"
- "Fill out the PR template"
- "Draft a pull request"

## Procedure

1. **Identify the change set.** Default to `git diff <base>...HEAD` where `<base>` is the merge target (usually `main` / `master` / `develop`).
   ```bash
   git fetch origin
   BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo main)
   git log --oneline "origin/$BASE..HEAD"
   git diff --stat "origin/$BASE...HEAD"
   ```

2. **Look for an existing template.** Check `.github/pull_request_template.md` or `docs/PULL_REQUEST_TEMPLATE.md`. If found, follow its structure; otherwise use the default below.

3. **Read the diff itself**, not just commit messages. Commit messages lie or lag; the diff is truth.

4. **Identify:**
   - The *one* sentence that summarizes the change (this is the PR title)
   - The *why* — problem, context, motivation
   - The *what* — what actually changed, grouped logically (not file-by-file)
   - Anything reviewer-visible: API changes, migrations, env vars, breaking changes
   - Verification steps the reviewer can run

5. **Draft. Then trim.** First draft is always too long. Cut anything the diff already shows.

## Default template

```markdown
## Summary
<one or two sentences — the elevator pitch>

## Why
<problem this solves, links to issues/discussions>

Closes: #123

## Changes
- <grouped logical change>
- <another grouped logical change>
- <…>

## How to verify
1. <concrete step a reviewer can run>
2. <…>

## Notes for reviewer
<anything non-obvious: tricky bits, deliberate trade-offs, things you want extra eyes on>

## Risk & rollout
<breaking changes, migrations, feature flags, env vars, deploy order>
```

Drop sections that don't apply. A docs PR doesn't need "Risk & rollout."

## Title

`<type>(<scope>): <imperative summary>` if the project uses Conventional Commits, otherwise a clear imperative sentence ≤72 chars. No trailing period.

✅ `feat(auth): support passwordless email login`
✅ `Fix race condition in cache invalidation`
❌ `Updates`
❌ `WIP - some changes to auth`

## Anti-patterns

- ❌ Listing files changed — the diff already does that
- ❌ "Various fixes and improvements" — useless to reviewer and to future archaeology
- ❌ Copy-pasting commit messages as the body
- ❌ Hiding breaking changes in the middle of a bullet list
- ❌ "Tested locally ✅" without saying *what* was tested
- ❌ Putting the "why" only in a linked issue — the reviewer should not need to context-switch

## Tips

- **Screenshots / before-after** are gold for UI changes
- **Migration notes**: if a consumer needs to do something, put it in its own section with a `⚠️` so it can't be missed
- **Stacked PRs**: link to the parent and explicitly say "depends on #N"
- **Draft PRs**: prefix the summary with what's still TODO before review is welcome
- If the PR ended up doing more than one thing, suggest splitting before writing the description — it'll be a better PR
