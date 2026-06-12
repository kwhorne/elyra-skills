---
name: task-breakdown
description: Break a feature or spec into small, atomic, independently verifiable tasks with explicit ordering and dependencies. Use when the user asks to plan implementation, create a task list, estimate work, or when a spec is ready and needs to become an executable plan.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, write
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [planning, tasks, estimation]
---

# Task Breakdown

Turn a spec into a sequence of tasks where **every task leaves the codebase working** and **every task can be verified on its own**.

## When to use

- "Plan how to build…" / "Break this down"
- A spec exists and implementation is about to start
- A task feels too big to start ("where do I even begin?")
- Estimating or splitting work across people/sessions

## Principles

- **Atomic.** One task = one concern = one commit. If the description contains "and", split it.
- **Vertical over horizontal.** Prefer "one working slice through all layers" over "all models, then all services, then all UI".
- **Always shippable.** After every task, tests pass and the app runs. No task ends mid-air.
- **Verification is part of the task.** A task without a "done when" is a wish.

## Process

### 1. Read before planning

- Read the spec (or write one first — see `spec-writing`)
- Read the code the plan will touch; note existing patterns to follow
- Identify the riskiest unknown — it goes **first**, not last

### 2. Slice vertically

Find the thinnest end-to-end slice that proves the approach works (walking skeleton), then widen:

```
Task 1: skeleton  — one happy-path case wired through all layers
Task 2..n: widen  — more cases, validation, edge cases, polish
```

### 3. Size each task

A task should be **15–60 minutes** of focused work. Bigger → split. Smaller → merge with its neighbor.

### 4. Order by dependency and risk

- Mark hard dependencies explicitly (`depends on: T2`)
- Risky/unknown tasks early; mechanical tasks late
- Tasks with no dependency between them are marked parallelizable

### 5. Define "done when" per task

Each task gets a concrete verification: a test that passes, a command that succeeds, a behavior observable in the running app.

## Output format

```markdown
# Plan: <feature>

**Spec:** <link/path>
**Riskiest unknown:** <what, and which task resolves it>

| # | Task | Done when | Depends on |
|---|------|-----------|------------|
| 1 | …    | …         | —          |
| 2 | …    | …         | 1          |

**Parallelizable:** T3 + T4
**Out of plan:** <things deliberately not tasks, with reason>
```

## Anti-patterns

- ❌ Layer-by-layer plans ("first all migrations, then all models…") — nothing is verifiable until the end
- ❌ Tasks named after files ("update UserController") instead of outcomes ("reject duplicate emails on signup")
- ❌ A final task called "testing" — tests belong inside every task
- ❌ Hiding the risky part in task 9 of 10
- ❌ Plans with no "done when" — they decay into vibes
- ❌ Re-planning the whole thing mid-build instead of amending the plan explicitly
