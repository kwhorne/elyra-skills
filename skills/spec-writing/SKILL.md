---
name: spec-writing
description: Write a focused spec before building - problem statement, scope, acceptance criteria, edge cases, and open questions. Use when the user describes a feature to build, asks for a spec or PRD, or starts a task that is too vague to implement directly.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, write
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [spec, planning, requirements]
---

# Spec Writing

Define **what** to build and **how you'll know it's done** before writing code. A good spec is the cheapest place to find a design flaw.

## When to use

- "Build a feature that…" (and the description fits in one sentence)
- "Write a spec / PRD for…"
- The task has unstated assumptions, multiple interpretations, or unclear success criteria
- Before any task expected to take more than an hour of implementation

## Principles

- **Spec before code.** Changing a sentence is cheaper than changing a system.
- **Shorter is better.** One page that gets read beats ten pages that don't.
- **Acceptance criteria are the contract.** If you can't write a testable criterion, the requirement isn't understood yet.
- **Unknowns are content, not gaps.** An explicit "Open questions" section is a feature of the spec.

## Process

### 1. Interrogate the request

Before writing anything, answer (ask the user if needed):

- **Who** is this for? (end user, admin, another system, developer)
- **What problem** does it solve? Not the solution — the problem.
- **Why now?** What breaks or stays broken without it?
- **What already exists?** Read the relevant code first; the spec must fit reality.

### 2. Draw the boundary

The most valuable section is **Out of scope**. Explicitly list:

- Adjacent features that will *not* be built
- Cases that will be rejected or deferred, not handled
- Quality attributes intentionally skipped (e.g. "no i18n in v1")

### 3. Write acceptance criteria

Each criterion must be **verifiable** — a test, a command, or an observable behavior.

- Use Given/When/Then or a checklist; be consistent
- Cover the happy path *and* the named failure modes
- If a criterion can't fail, delete it

### 4. Hunt edge cases

Walk these categories explicitly:

- **Empty / zero / null** — no items, empty string, missing field
- **Boundaries** — max length, first/last page, exactly-at-limit
- **Concurrency** — double submit, race between two users
- **Permissions** — wrong role, expired session, cross-tenant access
- **Failure** — dependency down, timeout, partial write

### 5. Surface open questions

Anything you'd otherwise silently assume goes here, with your proposed default:

> Q: Should deleted items appear in the export? **Proposed: no.**

## Output format

```markdown
# Spec: <feature name>

**Problem:** 1–3 sentences. The user pain, not the solution.

**Goal:** What changes for the user when this ships.

## In scope
- …

## Out of scope
- …

## Acceptance criteria
- [ ] Given …, when …, then …
- [ ] …

## Edge cases
| Case | Expected behavior |
|------|-------------------|
| …    | …                 |

## Open questions
- Q: …? Proposed: …
```

## Anti-patterns

- ❌ Writing the spec as a disguised implementation plan ("add a column, then a service…")
- ❌ Acceptance criteria that restate the feature ("the export works correctly")
- ❌ Resolving open questions by silent assumption instead of writing them down
- ❌ Specs longer than the code they describe
- ❌ Skipping the codebase read — a spec that ignores existing architecture is fiction
