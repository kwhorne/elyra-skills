---
name: adr-author
description: Write an Architecture Decision Record - capture the context, options considered, decision, and consequences so future readers understand why, not just what. Use when the user makes a significant technical choice, asks to document a decision, asks "why did we choose X", or wants to set up ADRs in a project.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, write
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [adr, architecture, documentation, decisions]
---

# ADR Author

Record **why** a decision was made while the reasoning is still fresh. Code shows what was built; only the ADR shows what was *rejected* and why.

## When to use

- A choice was just made between frameworks, storage engines, protocols, patterns, or vendors
- A decision is expensive to reverse (schema, API contract, auth model, build system)
- Someone asks "why is this built this way?" and the answer lives in one person's head
- Recurring debates re-litigate a settled decision — write it down once

**Not every decision needs an ADR.** Rule of thumb: would a new team member six months from now be confused or tempted to "fix" it? Then yes.

## Principles

- **Context over conclusion.** The decision is one line; the constraints that forced it are the value.
- **Honest alternatives.** Each rejected option gets its real strengths stated — strawmen rot trust in the whole log.
- **Immutable.** An ADR is never edited into a new decision; it gets **superseded** by a new ADR that links back.
- **Consequences include the bad ones.** Every decision buys something and costs something. Name both.

## Process

### 1. Locate or create the log

- Look for an existing convention: `docs/adr/`, `docs/decisions/`, `adr/`
- If none exists, create `docs/adr/` and number files `NNNN-short-title.md` (e.g. `0007-use-postgres-for-search.md`)

### 2. Capture context

- What problem forced a decision? What constraints applied (deadlines, team skills, existing systems, cost, compliance)?
- Context must be true at the time of writing — it's the part that lets future readers judge whether the decision still applies

### 3. List the options actually considered

For each: what it is, its genuine pros, its genuine cons. Two to four options is typical. "Do nothing" is often a legitimate option.

### 4. State the decision and its consequences

- The decision in one or two sentences, active voice: "We will…"
- Consequences: what becomes easier, what becomes harder, what new obligations appear (ops, licensing, training)
- If known, the **revisit trigger**: "Reconsider if we exceed N requests/sec" / "when library X reaches 1.0"

## Output format

```markdown
# NNNN. <Title — short noun phrase>

**Status:** Proposed | Accepted | Superseded by NNNN
**Date:** YYYY-MM-DD

## Context
What situation and constraints forced this decision.

## Options considered
### Option A: …
Pros: … / Cons: …
### Option B: …
Pros: … / Cons: …

## Decision
We will … because …

## Consequences
- ✅ Easier: …
- ⚠️ Harder: …
- 🔁 Revisit if: …
```

## Anti-patterns

- ❌ Writing the ADR months later from memory — the real context is gone
- ❌ Strawman alternatives listed only to be knocked down
- ❌ ADRs as design docs — keep it about the *decision*, not the full implementation
- ❌ Editing an old ADR when the decision changes (supersede instead)
- ❌ Status forever "Proposed" — decide, then mark it
- ❌ Consequences section that only lists upsides
