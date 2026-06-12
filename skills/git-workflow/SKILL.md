---
name: git-workflow
description: Work git like a professional - branching discipline, rebase vs merge, history hygiene, interactive rebase, bisect, and recovering from mistakes with reflog. Use when the user asks about branching strategy, fixing a messy history, undoing a git mistake, resolving conflicts, splitting commits, or any non-trivial git operation.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [git, branching, history, recovery]
---

# Git Workflow

History is a tool, not a diary. Optimize it for the **future reader** — the reviewer today and the person running `git bisect` in two years.

## When to use

- "How should we branch for this?" / "rebase or merge?"
- "I committed to the wrong branch / pushed a secret / lost my changes"
- Cleaning up a PR's history before review
- Conflicts, cherry-picks, splitting or reordering commits

## Principles

- **Small branches, short lives.** A branch older than a few days is a merge conflict farm. Integrate often.
- **Each commit compiles and passes tests.** That's what makes `git bisect` work and reverts surgical.
- **Rewrite local history freely, shared history never.** Rebase your own unpushed work; once others build on it, it's immutable.
- **Almost nothing is lost.** Committed work is recoverable via `reflog` for ~90 days. Don't panic; don't `rm -rf` and re-clone.

## Branching discipline

- Branch from up-to-date main; name by intent: `feat/...`, `fix/...`, `chore/...`
- One branch = one reviewable concern. Two features = two branches
- Keep current with main via `git rebase main` (own branch) — resolves conflicts while they're small
- **Rebase vs merge rule of thumb:** rebase your private branch onto main; merge (or squash-merge) the branch *into* main per the team's convention. Never rebase a branch others have pulled

## History hygiene (before review)

```bash
git rebase -i main          # squash fixups, reorder, reword
git commit --fixup <sha>    # mark a fix for an earlier commit…
git rebase -i --autosquash main   # …then fold it in automatically
git add -p                  # stage hunks selectively → atomic commits
```

Target: each commit is one logical change with a message explaining **why** (see `conventional-commits`).

## Recovery cookbook

| Situation | Fix |
|---|---|
| Committed on wrong branch | `git checkout right-branch && git cherry-pick <sha>`, then remove from wrong branch |
| Undo last commit, keep changes | `git reset --soft HEAD~1` |
| Undo a *pushed* commit | `git revert <sha>` — never reset shared history |
| "I lost my work" | `git reflog` → find the sha → `git checkout -b rescue <sha>` |
| Messed-up rebase/merge in progress | `git rebase --abort` / `git merge --abort` |
| Secret pushed | Rotate the secret **first** (history rewrite alone never un-leaks it), then scrub with `git filter-repo` |
| Find the commit that broke X | `git bisect start && git bisect bad && git bisect good <sha>` (automate: `git bisect run <test-cmd>`) |

## Conflict resolution

- Resolve conflicts **per commit** during rebase — smaller, with context
- Read both sides before choosing; "take mine" without reading is how regressions ship
- After resolving: build + run tests *before* `--continue`
- Recurring conflicts in lockfiles/generated files → regenerate instead of hand-merging

## Output format

When advising on or performing git surgery, report:

```markdown
## Git: <operation>

**Situation:** what state the repo was in.
**Plan:** commands, in order, with one-line why each.
**Safety:** what's backed up (branch/sha) before destructive steps.
**Result:** end state + how to verify (`git log --oneline -5`, tests).
```

## Anti-patterns

- ❌ `git push --force` to a shared branch (`--force-with-lease` on your own, after rebase, is fine)
- ❌ Commits named "wip", "fix", "fix2", "final" reaching main
- ❌ Long-lived feature branches integrating monthly
- ❌ Resolving a rebase conflict by mass-accepting one side
- ❌ Re-cloning the repo because the working tree "feels broken" — diagnose with `status`/`reflog` first
- ❌ Rewriting pushed history to hide a leaked secret instead of rotating it
