---
name: architecture-review
description: Evaluate a system or component design against non-functional requirements - scalability, reliability, maintainability, security, cost. Use when the user asks for an architecture review, design critique, system review, or wants to evaluate a proposed design or ADR before commit.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [architecture, design, review, adr]
---

# Architecture Review

The goal is to **surface assumptions and trade-offs** while the design is still cheap to change. Code review catches bugs; architecture review catches missing requirements.

## When to use

- "Review this architecture / design / proposal"
- "Does this design make sense?"
- "Critique this ADR"
- "Evaluate <option A> vs <option B>"
- "What's wrong with this approach?"

## Procedure

1. **Restate the problem** in your own words. If you can't, the design doc is unclear — flag that first.
2. **Identify the constraints**: scale, latency, reliability, team size, cost, deadline, regulatory
3. **Walk the dimensions** below, looking for unstated assumptions and missing trade-offs
4. **Compare against at least one alternative** — designs with no rejected alternatives haven't been *designed*, they've been *proposed*
5. **Produce the review** with explicit recommendations

## Dimensions

### Requirements clarity

- [ ] **Functional**: what the system does, with concrete user-visible scenarios
- [ ] **Non-functional** numbers: throughput, latency p95/p99, availability target, RPO/RTO
- [ ] **Out-of-scope**: explicit list of what's intentionally not addressed
- [ ] **Success criteria**: how do you know it worked?

If the design starts with "the system will be fast and scalable," push back. Numbers or it didn't happen.

### Scalability

- Where's the bottleneck at 10x current load? 100x?
- Is the design **stateless where it should be**, **stateful where it must be**, and clear about which?
- Horizontal scaling primitives identified (partitioning key, sharding strategy)
- Read vs write paths separated where load profile demands it
- Caching layer's invalidation story is explicit, not vibes

### Reliability

- What happens when each dependency is down? (DB, cache, queue, third party)
- Graceful degradation paths or hard-fail with retry?
- Timeouts, retries, circuit breakers on every external call
- No single points of failure for SLAs you've committed to
- Disaster recovery plan: RPO, RTO, last tested when?

### Data

- Schema migration strategy compatible with deployment model (see `database-migration`)
- Backup, restore tested
- Data retention / deletion policy (GDPR, CCPA, …)
- PII handling: stored where, encrypted how, accessible to whom
- Multi-region: where's the source of truth, what's eventually consistent

### Security

- Threat model articulated (who, what, how)
- Authentication, authorization, encryption-at-rest, encryption-in-transit
- Secret rotation possible without redeploy
- Audit log for sensitive operations
- See `security-audit` for the deeper checklist

### Operability

- How do you **detect** a problem? (see `observability`)
- How do you **debug** a problem at 3 AM with no context?
- Runbooks exist for likely failures
- Deploys are reversible (or expand/contract pattern used)
- Feature flags for risky launches (see `feature-flag-rollout`)

### Maintainability

- Boundaries between modules clear and tested at the boundary
- Tech choices are **boring** (load-bearing systems are not the place for novelty)
- Dependency count justified — each new system is more on-call surface
- The team can actually run, debug, and deploy this

### Cost

- Order-of-magnitude estimate of monthly cost at current and 10x load
- Cost of failure (downtime, data loss) understood
- Cost of *operating* it (engineer-hours, on-call burden), not just infra
- Cheaper alternative considered and rejected for stated reasons

### Migration / rollout

- How do you get from current state to designed state?
- Coexistence period plan (old + new running together)
- Backout plan if it goes wrong mid-migration
- Communication plan for affected consumers

### Reversibility

A useful frame: which decisions are **one-way doors** vs **two-way doors**?

- One-way doors (database engine, primary cloud, public API contract) deserve disproportionate scrutiny
- Two-way doors (internal library choice, internal service boundaries) should be made fast

## Comparison table (always include one)

A design without alternatives is a proposal pretending to be a design.

```markdown
| Aspect | Option A (proposed) | Option B (rejected) | Option C (rejected) |
|---|---|---|---|
| Latency p95 | 50ms | 200ms | 30ms |
| Cost / month | $2k | $500 | $8k |
| Implementation weeks | 3 | 1 | 6 |
| Operability | medium (new service) | low (uses existing) | high (managed) |
| Reversibility | one-way (data format) | two-way | two-way |
| Failure mode | degrades gracefully | hard fails | degrades gracefully |

**Choice: Option A** because <specific reason tying back to constraints>.
```

## ADR (Architecture Decision Record) template

For each significant decision, write a short ADR. Future-you will thank present-you.

```markdown
# ADR <NNN>: <decision title>

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Superseded by ADR-MMM | Deprecated

## Context
What's the situation? What constraints apply?

## Decision
We will <decision>, because <primary reasons>.

## Alternatives considered
- <Option B>: rejected because <…>
- <Option C>: rejected because <…>

## Consequences
**Positive:** …
**Negative:** …
**Reversibility:** one-way / two-way (and what would it take to undo?)

## Follow-ups
- <action items if any>
```

Keep ADRs **short** (one page) and **immutable** (don't edit accepted ones; supersede with a new ADR).

## Output format

```markdown
## Architecture review: <design name>

**Reviewed:** <doc link / commit / module>
**Stated requirements:** <one-line summary>
**Assumed but unstated:** <things the doc relies on but doesn't say>

### Strengths
- <one or two genuine positives>

### Concerns

#### 🔴 Blockers (must address before commit)
- <issue>. **Impact:** <…>. **Suggested fix:** <…>.

#### 🟠 Major (should address)
- …

#### 🟡 Minor (consider)
- …

### Missing
- <dimension or scenario not addressed at all>

### Questions
- <things that aren't issues yet because you need more info>

### Alternatives not considered
- <option> — worth at least a one-paragraph comparison

### Recommendation
APPROVE / APPROVE WITH CHANGES / REWORK / REJECT

<one-paragraph justification>
```

### Severity rubric

| Tag | Meaning |
|---|---|
| 🔴 **Blocker** | Design will fail to meet stated requirements, or one-way door not properly considered |
| 🟠 **Major** | Significant operational risk, missing dimension, or under-justified choice |
| 🟡 **Minor** | Improvement, alternative phrasing, missing-but-non-critical detail |

## Anti-patterns

- ❌ Reviewing only the happy path
- ❌ "Looks good 👍" without checking against the stated requirements
- ❌ Bikeshedding tech-choice preferences without tying back to constraints
- ❌ Proposing rewrites — review the design that's in front of you, suggest fixes
- ❌ Approving designs with no alternatives considered
- ❌ Letting "we'll figure it out later" stand in for the deploy / rollback / data-migration plan
- ❌ Ignoring cost and operability ("the cloud is cheap")
- ❌ Not articulating the trade-off you're making (every design has them)

## Tips

- **The five whys** apply to design too: if a constraint isn't justified, ask why until you hit something concrete
- **Steel-man the rejected alternatives** before rejecting them — if you can't, the comparison is unfair
- **Operability often gets short shrift** — bring it up explicitly
- **Watch for "we'll just …"** — small words often hide huge work (just shard, just add caching, just retry)
- **Reviewers should restate the design back to authors** — if you got it wrong, the doc is unclear

## References

- [ADR (Architecture Decision Records)](https://adr.github.io/) — formats, examples, tooling
- [System Design Primer](https://github.com/donnemartin/system-design-primer) — patterns and trade-offs
- [Designs, Lessons and Advice from Building Large Distributed Systems (Jeff Dean)](https://www.cs.cornell.edu/projects/ladis2009/talks/dean-keynote-ladis2009.pdf)
- [Choose Boring Technology (Dan McKinley)](https://boringtechnology.club/)
