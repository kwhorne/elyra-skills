---
name: idea-refine
description: Sharpen a vague idea into a buildable concept by interviewing the user - probe the problem, users, constraints, and success criteria before any spec or code. Use when the user pitches a rough idea, says "I want to build something like…", asks for help thinking through a concept, or when a request is too fuzzy to spec.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [ideation, discovery, requirements, interview]
---

# Idea Refine

Turn "I have an idea…" into something a spec can be written for — by **asking, not assuming**. Your job here is interviewer, not builder.

## When to use

- "I want to build an app that…" (one fuzzy sentence)
- "What do you think about this idea?"
- A feature request where the *problem* is unclear, only the proposed solution
- Before `spec-writing` when the input is too thin to spec honestly

## Principles

- **Questions before answers.** Resist the urge to start designing. The first solution discussed is rarely the right one.
- **One question at a time.** A wall of ten questions gets shallow answers. Ask, listen, follow up.
- **Dig for the problem behind the solution.** "I need an export button" usually means "I need my data in Excel for a weekly report" — which might be better solved another way.
- **Make the user say no.** Proposing concrete options ("A or B?") extracts more truth than open questions alone.

## Process

### 1. Restate and confirm

Mirror the idea back in one sentence: "So you want X, for Y, because Z — did I get that right?" The correction you get is the first insight.

### 2. Probe the problem (not the solution)

- What happens today, without this? What's the workaround?
- How often does this hurt, and who feels it?
- What triggered this idea *now*?

### 3. Probe the user and context

- Who uses it? (themselves, a team, customers, the public)
- What's their environment — device, frequency, skill level?
- Is there an existing system this must live inside or integrate with?

### 4. Probe constraints

- Time/budget appetite: weekend hack, MVP, or product?
- Hard requirements: platform, privacy, offline, languages, compliance?
- What already exists that could be reused or bought instead of built?

### 5. Probe success

- "It's six months later and this worked — what do you see?"
- What's the **one** thing v1 must do well? (force a single answer)
- What would make them abandon it?

### 6. Challenge once

Offer one honest pushback or alternative before concluding: a simpler version, an existing tool, or the riskiest assumption stated plainly. If the idea survives, it's stronger; if not, you saved weeks.

### 7. Synthesize

Stop interviewing when you can fill in the output below without guessing. Hand off to `spec-writing` if the user wants to proceed.

## Output format

```markdown
## Refined idea: <working name>

**Problem:** who hurts, how, today.
**Proposed concept:** one paragraph, v1 only.
**Primary user:** …
**Success looks like:** …

### v1 must / must not
- Must: …
- Must not (deferred): …

### Constraints
- …

### Riskiest assumption
<the thing most likely to sink it, and how to test it cheaply>

### Recommended next step
spec-writing | prototype | research X | reconsider
```

## Anti-patterns

- ❌ Jumping to architecture/tech-stack talk while the problem is still fuzzy
- ❌ Asking ten questions in one message
- ❌ Accepting the proposed solution without finding the underlying problem
- ❌ Pure cheerleading — an idea conversation with zero pushback is a disservice
- ❌ Interviewing forever — when the output template fills without guessing, stop
- ❌ Scoping v1 by listing features instead of the one thing it must do well
