---
name: refactoring
description: Refactor code safely with characterization tests first, small reversible steps, and verification after each step. Use when the user asks to refactor, restructure, clean up, simplify, extract, or rename existing code.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, edit, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [refactoring, quality]
---

# Refactoring

> Refactoring: changing the structure of code without changing its observable behavior.

The discipline is in the **without**. If tests fail or behavior changes, it's no longer a refactor — it's a rewrite, and it needs to be reviewed as one.

## When to use

- "Refactor X"
- "Clean up / simplify / restructure …"
- "Extract this into a function/module/class"
- "Rename / move / split …"
- "Reduce duplication"

## When NOT to use

- The user wants new behavior → that's a feature, not a refactor
- There are no tests *and* no time/permission to add them → flag the risk first
- The code is going to be deleted soon → don't polish it

## Procedure

### 0. Confirm scope and goal

Refactoring is open-ended. Pin it down:

- What's the smell? (duplication, long function, unclear naming, tight coupling, …)
- What does "done" look like?
- What must *not* change? (public API, file paths, performance, …)

### 1. Establish a safety net

Behavior preservation needs proof. In order of preference:

1. **Existing tests** that cover the affected code. Run them; they must pass *before* you start.
2. **Characterization tests** — write tests that pin down *current* behavior (including warts), so you'll notice if you change it.
3. **Manual repro** of key paths if tests are impossible. Document what you checked.

If you can't get to step 1 or 2, **stop and tell the user**. Don't refactor on faith.

### 2. Refactor in small steps

Each step:

- Is one transformation (extract, rename, inline, move, …)
- Compiles / lints / type-checks
- Passes the test suite

Commit (or at least stash) after each green step. If a step turns red, revert it — don't pile fixes on top.

### 3. Common refactoring moves

| Move | Use when |
|---|---|
| **Extract function** | A block of code has a clear single purpose and a good name suggests itself |
| **Inline** | A function adds no clarity over its body |
| **Rename** | The current name lies, lags, or shrugs |
| **Move** | A function sits closer to data it doesn't use than data it does |
| **Replace conditional with polymorphism** | A `switch`/`if` chain on type repeats in multiple places |
| **Introduce parameter object** | A function takes 4+ related args, or the same cluster appears together repeatedly |
| **Replace magic value with named constant** | A literal appears more than once or its meaning isn't obvious |
| **Split phase** | One function does parsing *and* processing, or fetch *and* transform |

### 4. Verify

After all steps:

- All tests pass (including ones you wrote in step 1)
- Public API unchanged (or changes are deliberate and documented)
- No dead code left over
- Run a diff stat: large diff is fine, surprises are not

### 5. Stop

Refactoring is open-ended; that's why it's dangerous. Stop at the goal you set in step 0. If you spot more smells, **note them, don't fix them now.**

## Output format

```markdown
## Refactor: <short title>

**Goal:** what we set out to do.

**Approach:** sequence of small steps actually taken.

**Behavior preservation:** tests run / written / checked.

**Out of scope (noted, not fixed):** other smells you spotted.
```

## Anti-patterns

- ❌ "Refactor + add a feature in the same change" — split into two PRs
- ❌ Big-bang rewrite labeled as "refactor"
- ❌ Refactoring without running the tests after each step
- ❌ Renaming things at the same time as moving them at the same time as changing signatures
- ❌ Polishing code that's about to be deleted
- ❌ Reformatting unrelated code — keep diffs reviewable

## Tips

- If the test suite is slow, scope down: `pytest path/to/affected`, `vitest run src/affected/`, etc. But run the full suite at the end.
- Use the IDE/LSP refactor tools for renames and moves when available — they're more reliable than text search-replace.
- If a refactor "needs" you to change a test, pause: are you changing behavior? If yes, label it as such.
