---
name: debugging
description: Systematically debug a problem - reproduce, isolate, fix, verify, prevent regression. Use when the user reports a bug, an unexpected error, a failing test, or asks to investigate why something is broken.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, edit
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [debugging, troubleshooting]
---

# Debugging

A disciplined debugging loop. The goal is **understanding, then fixing** — not pattern-matching a fix and hoping.

## When to use

- "X is broken / not working / throwing"
- "This test is failing"
- "Why does this return the wrong value?"
- "Find the bug in …"

## The loop

```
1. Reproduce  →  2. Isolate  →  3. Hypothesize  →  4. Fix  →  5. Verify  →  6. Prevent
```

Never skip steps 1–3. A fix without reproduction is a guess.

### 1. Reproduce

Get the bug to happen on demand before changing anything.

- Ask for: exact command/input, expected vs actual, stack trace, environment
- Run it yourself. If you can't reproduce locally, that **is** the first finding.
- Capture the minimal reproduction (smallest input that triggers it)

### 2. Isolate

Shrink the problem space.

- **Bisect by location** — comment out / short-circuit halves until you find the failing region
- **Bisect by history** — `git bisect` if it used to work
- **Bisect by data** — strip input down to the smallest failing case
- Read the actual stack trace top-to-bottom; don't skim

### 3. Hypothesize

Form a *specific*, *testable* theory of what's wrong before touching code.

- Write it down: "I think X happens because Y."
- Predict what you'd see if the theory is correct (a value, a log line, a call order)
- Verify the prediction *before* writing the fix — print, log, breakpoint, REPL

### 4. Fix

Now, and only now, change code.

- Smallest change that addresses the root cause
- If you're tempted to add defensive code "just in case," stop — that's a sign you haven't understood the bug
- Note any related code paths with the same flaw

### 5. Verify

Prove the fix works and didn't break anything else.

- Re-run the minimal repro → must pass
- Run the existing test suite → must pass
- If there was no test covering this bug, **write one now** (see step 6)

### 6. Prevent regression

A bug that came back is twice as expensive.

- Add a regression test that fails without the fix and passes with it
- If the bug class is recurring (e.g. null in a specific shape), consider a type/lint rule
- Note any sibling code paths that should be patched the same way

## Output format

When done, report:

```markdown
## Bug: <short title>

**Root cause:** one or two sentences. What was actually wrong.

**Trigger:** minimal reproduction.

**Fix:** what changed and why this is the right level to fix at.

**Verification:** tests run, new tests added.

**Related risks:** other code paths with the same shape (or "none found").
```

## Anti-patterns

- ❌ "I think this might work, let me try it" → that's not debugging, that's slot-machining
- ❌ Adding `try/catch` to make an error go away without understanding it
- ❌ Fixing symptoms (the wrong value displayed) instead of cause (where it became wrong)
- ❌ Skipping the regression test because "it's obvious now"
- ❌ Changing five things at once and not knowing which one fixed it

## Useful commands

```bash
# Git bisect — find the commit that introduced the bug
git bisect start
git bisect bad                       # current is broken
git bisect good <known-good-commit>
# (run repro, then git bisect good/bad until it converges)
git bisect reset

# Re-run only the failing test in watch mode (adjust per stack)
# pytest: pytest path/to/test.py::test_name -x -vv
# vitest: npx vitest run path/to/test --reporter=verbose
# phpunit: vendor/bin/phpunit --filter testName

# Show recent changes to a file
git log -p --follow path/to/file
```
