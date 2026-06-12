---
name: incremental-implementation
description: Implement a plan one small, verified, committed step at a time - never leave the codebase broken between steps. Use when implementing a planned feature, executing a task list, doing a large change that must stay reviewable, or when the user asks to build something step by step.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, edit, write
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [implementation, workflow, commits]
---

# Incremental Implementation

Execute a plan as a series of **small, verified, committed** steps. The codebase is green after every step — there is no "it'll compile again on Thursday".

## When to use

- A task plan exists and it's time to build (see `task-breakdown`)
- "Implement this feature" where the change spans multiple files/layers
- Large refactors or migrations that must remain reviewable
- Resuming work across sessions — each committed step is a safe resume point

## Principles

- **One task per cycle.** Pick the next task, finish it completely, commit, then look up.
- **Green to green.** Tests pass before the step and after it. A red intermediate state never gets committed.
- **Smallest diff that completes the task.** Resist drive-by fixes — note them, don't do them.
- **Follow the house style.** Match existing patterns in the codebase, even when you'd personally do it differently.

## The cycle

```
pick task → read context → implement → verify → commit → report → next
```

### 1. Pick

Take the next unblocked task from the plan. If no plan exists, make one first — even three bullet points.

### 2. Read context

Read the files you're about to change *and* one example of the pattern you're imitating (a similar controller, component, test).

### 3. Implement

- Stay inside the task boundary; out-of-scope discoveries go to a **deferred list**, not into the diff
- Write/adjust the test for this task as part of the step, not afterwards
- If the task turns out bigger than expected, **stop and split it** rather than pushing through

### 4. Verify

- Run the task's "done when" check
- Run the affected test suite (full suite if cheap)
- Run linter/formatter/type-checker if the project has them

### 5. Commit

One commit per task, message describing the outcome (see `conventional-commits`). The commit is the checkpoint — if step n+1 goes wrong, reset to it.

### 6. Report and continue

After each task, state: what was done, how it was verified, what's next. Then proceed — don't wait for permission unless the next step is risky or ambiguous.

## When things go wrong

- **Verification fails** → fix forward only if the cause is obvious; otherwise `git checkout .` back to green and re-approach
- **Plan turns out wrong** → stop, amend the plan visibly, then continue. Don't silently improvise
- **Blocked on a question** → pick another unblocked task; park the question, don't guess on irreversible decisions

## Output format (per step)

```markdown
### Task n: <name> ✅
**Changed:** files + one-line summary
**Verified:** <command/test that proves it>
**Deferred:** <out-of-scope findings, or "—">
**Next:** Task n+1: <name>
```

## Anti-patterns

- ❌ Implementing tasks 1–6 in one giant diff, then debugging the pile
- ❌ "Tests are failing but it's because of the next step" — then the steps are wrong
- ❌ Drive-by refactoring inside a feature task
- ❌ Committing "WIP" — if it's not a completed task, it's not a commit
- ❌ Pushing through a too-big task instead of splitting it
- ❌ Silently deviating from the plan when reality disagrees with it
