---
name: context-engineering
description: Write and maintain agent context files (AGENTS.md, CLAUDE.md, .cursorrules) that actually steer coding agents - commands, conventions, architecture, and boundaries, without bloat. Use when the user wants to set up or improve agent instructions for a project, asks why an agent keeps making the same mistake, or wants to make a codebase agent-friendly.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, write
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [agents, context, agents-md, documentation]
---

# Context Engineering

A context file is a **standing prompt** every agent session pays for. Every line either prevents a mistake or wastes tokens and attention.

## When to use

- "Set up an AGENTS.md / CLAUDE.md for this project"
- An agent repeatedly makes the same mistake (wrong test command, wrong patterns, touching forbidden files)
- Onboarding a codebase for agent-heavy development
- Auditing an existing context file that has grown stale or bloated

## Principles

- **Write what the agent can't infer.** It can read code; it can't read your team's intentions, taboos, or tribal knowledge. Don't restate what `ls` reveals.
- **Commands over descriptions.** `composer test -- --filter=X` beats a paragraph about the testing philosophy.
- **Every line earns its place.** Context files are read on *every* session. 400 lines of boilerplate buries the 20 lines that matter.
- **Falsifiable rules.** "Write clean code" steers nothing. "Controllers never touch Eloquent directly — go through a Service" is checkable.

## Process

### 1. Mine the real friction

The best source is **past mistakes**: what has an agent (or new hire) gotten wrong in this repo?

- Wrong build/test/lint commands
- Ignored architectural rules (layering, naming, where things live)
- Touched generated/vendored files
- Used a deprecated pattern that still exists in the code as bad examples

### 2. Structure the file

Recommended skeleton (order = priority):

```markdown
# <Project>

One paragraph: what this is, stack, what kind of app.

## Commands
- dev / build / test (full + single test) / lint / format — exact, copy-pasteable

## Architecture
3–8 bullets: layers, where things live, the one diagram-in-words that matters.

## Conventions
The rules an agent would otherwise break. Each one concrete:
- "X goes in Y"
- "Never do Z; do W instead (see path/to/good-example)"

## Boundaries
- Files/dirs never to edit (generated, vendored, migrations already run)
- Actions requiring explicit confirmation (deploys, destructive db ops)

## Gotchas
Known traps: flaky test X, env var Y required locally, …
```

### 3. Point to exemplars

Instead of describing patterns, **link them**: "New Livewire components follow `app/Livewire/Products/Index.php`." One good example outperforms three paragraphs.

### 4. Layer for monorepos / large projects

- Root file: global commands + cross-cutting rules only
- Per-package/dir context files for local conventions — agents pick up the nearest one
- Don't duplicate; deeper files override/extend the root

### 5. Test it

- Fresh agent session, representative task, **zero extra instructions** — does it use the right commands and patterns?
- Each failure = a missing or unclear line. Add the *rule*, not a transcript of the incident.

### 6. Maintain

- Update in the same PR that changes a command or convention — a stale context file is worse than none
- Quarterly prune: delete lines that no longer prevent anything

## Output format

When auditing an existing file, report:

```markdown
## Context audit: <file>

**Verified commands:** ran them — pass/fail per command.
**Keep:** lines doing real work.
**Fix:** stale/wrong lines (with correction).
**Cut:** boilerplate that restates the obvious — N lines.
**Add:** missing rules, sourced from <evidence: code pattern / past mistake>.
```

## Anti-patterns

- ❌ Generic filler: "write tests", "follow best practices", "be careful"
- ❌ Documenting the directory tree the agent can `ls` itself
- ❌ Context written once at project start and never touched again
- ❌ One 600-line root file for a monorepo instead of layered files
- ❌ Commands that were never actually run to verify they work
- ❌ Describing a pattern in prose when a file path to a good example exists
- ❌ Treating it as marketing copy ("this elegant codebase…") — it's an operations manual
