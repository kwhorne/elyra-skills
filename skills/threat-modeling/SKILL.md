---
name: threat-modeling
description: Model threats before building - map assets, trust boundaries, and attack surfaces, walk STRIDE categories, and rank risks with concrete mitigations. Use when the user designs a new feature or system that handles sensitive data or auth, asks "how could this be abused", or wants a threat model or security design review before implementation.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, write
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [security, threat-modeling, stride, design]
---

# Threat Modeling

Find the attacks **on paper, before the code exists**. A security-audit reviews what was built; a threat model shapes what gets built.

## When to use

- Designing anything that touches auth, money, PII, file uploads, or external input
- "How could this be abused?" / "Is this design secure?"
- Adding a new integration, webhook, or API surface
- Before `spec-writing` finalizes scope for a sensitive feature

## Principles

- **Think like the attacker, list like an engineer.** Creative in finding threats, systematic in recording them.
- **Trust boundaries are where it happens.** Every place data crosses from less-trusted to more-trusted is a finding generator.
- **Rank ruthlessly.** Ten mitigated critical threats beat a hundred documented trivial ones.
- **Assume breach of the outer layer.** "The WAF catches that" is not a mitigation; defense has depth or it doesn't.

## Process

### 1. Scope and assets

- What are we protecting? (credentials, PII, money/credits, business data, availability, reputation)
- Who are the realistic attackers? (anonymous internet, authenticated user, malicious insider, compromised dependency)

### 2. Draw the data flow

Sketch components and the data moving between them (text diagram is fine):

```
[Browser] --creds--> [API] --query--> [DB]
                       |--webhook--> [3rd party]
```

Mark every **trust boundary**: internet→app, app→db, app→third party, user→admin, tenant→tenant.

### 3. Walk STRIDE per boundary

| Category | Ask |
|---|---|
| **S**poofing | Can someone pretend to be another user/service here? |
| **T**ampering | Can data be modified in transit or at rest? |
| **R**epudiation | Can an actor deny an action because we can't prove it? |
| **I**nformation disclosure | What leaks — errors, timing, IDs, logs, caches? |
| **D**enial of service | What's cheap for an attacker and expensive for us? |
| **E**levation of privilege | Path from low-priv to high-priv? (IDOR, mass assignment, admin routes) |

Also walk the **abuse cases**: how would a *legitimate* user cheat? (free-tier laundering, scraping, referral fraud)

### 4. Rank

Score each threat simply: **likelihood (L/M/H) × impact (L/M/H)**. Anything H×H or H×M gets a mitigation *in the design*; M×M gets a mitigation or an explicit accepted-risk note; the rest is documented.

### 5. Mitigate in the design

For each ranked threat, name the concrete control: authz check at X, signed URLs, rate limit per Y, idempotency keys, audit log of Z, input validation at the boundary. Each mitigation should be traceable into the spec/tasks.

### 6. Decide residual risk

What remains unmitigated, who accepted it, and what would trigger revisiting.

## Output format

```markdown
## Threat model: <feature/system>

**Assets:** …
**Attackers considered:** …

### Data flow & trust boundaries
<diagram>

### Threats
| # | Threat (STRIDE) | Boundary | L×I | Mitigation | Status |
|---|-----------------|----------|-----|------------|--------|
| 1 | …               | …        | H×M | …          | in design / accepted |

### Accepted risks
- <risk>: accepted by <whom>, revisit when <trigger>

### Carry into spec
- [ ] <mitigation as requirement>
```

## Anti-patterns

- ❌ Threat modeling after the code is written (that's an audit, and rework is 10× pricier)
- ❌ Only modeling external attackers — insiders and compromised accounts are boundaries too
- ❌ "We use HTTPS" as the answer to everything
- ❌ A 60-row threat table with no ranking and no owner
- ❌ Mitigations that never become spec requirements or tasks — a model nobody builds from is theater
- ❌ Forgetting abuse cases: the attacker with valid credentials and creative incentives
