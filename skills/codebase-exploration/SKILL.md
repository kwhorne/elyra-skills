---
name: codebase-exploration
description: Systematically explore and understand an unfamiliar codebase - entry points, architecture, data flow, conventions, and hotspots - before changing anything. Use when the user asks how a project works, asks to onboard onto a codebase, asks "where is X handled", or before implementing in a project you haven't mapped yet.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [exploration, onboarding, architecture, reading-code]
---

# Codebase Exploration

Build an accurate mental model **before** touching code. Changes made on a wrong model look fine and break things.

## When to use

- "How does this project work?" / "Where is X handled?"
- First task in a codebase you haven't mapped
- Estimating or planning work in unfamiliar territory
- Investigating "who calls this / what happens when…"

## Principles

- **Top-down, then targeted.** Skeleton first (structure, entry points), detail only where the task needs it.
- **Follow the data, not the files.** Tracing one real request/command end-to-end teaches more than reading ten files alphabetically.
- **Conventions are law.** The goal isn't just understanding *what* exists, but *how things are done here* — you'll be expected to imitate it.
- **Verify, don't assume.** Run it, test it, log it. A model you haven't tested is a guess.

## Process

### 1. Orient (5 minutes, breadth)

```bash
ls                                   # top-level shape
cat README.md                        # claimed purpose & setup
cat package.json composer.json pyproject.toml 2>/dev/null   # deps + scripts
git log --oneline -15                # what's being worked on now
```

Identify: language(s), framework, build/test commands, and **what kind of thing this is** (web app, library, CLI, service).

### 2. Find the entry points

- Web: routes file(s), middleware stack, main controller/handler layout
- CLI: bin/ entries, command registration
- Service: main loop, queue consumers, scheduled jobs
- Library: the public API surface (exports, index files)

### 3. Trace one real flow end-to-end

Pick one representative operation (e.g. "user submits form X") and follow it through every layer: route → validation → business logic → persistence → response. Write the chain down as you go.

### 4. Extract the conventions

Look at 2–3 examples of the same kind of artifact (controllers, components, tests) and note:

- Naming and file placement patterns
- How errors are handled, how things are tested
- What abstractions exist (services? repositories? hooks?) and when they're used vs bypassed

### 5. Map the hotspots

```bash
# Most-changed files — where the action (and risk) is
git log --format= --name-only | sort | uniq -c | sort -rn | head -15
```

Cross-reference with size: large *and* frequently changed = the file to be careful in.

### 6. Verify your model

- Run the test suite — does it pass? What does it cover?
- Make a trivial prediction ("changing this string should change that page") and confirm it
- Note anything that contradicted your expectations — those are the landmines

## Output format

```markdown
## Codebase: <name>

**What it is:** one sentence.
**Stack:** language, framework, key deps.
**Run/test:** commands.

### Architecture
Entry points → layers → persistence (short prose or arrow diagram).

### One traced flow
<operation>: file → file → file (with one-line role each)

### Conventions to follow
- …

### Hotspots & landmines
- <file/area>: why it needs care

### Open questions
- …
```

## Anti-patterns

- ❌ Reading files alphabetically instead of tracing a flow
- ❌ Assuming the README is current — verify commands actually work
- ❌ Stopping at "I found a function with the right name" without checking who calls it
- ❌ Proposing changes that ignore the house conventions
- ❌ Exploring everything when the task needs one subsystem — depth follows need
- ❌ Trusting your model without one verified prediction
