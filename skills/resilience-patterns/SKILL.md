---
name: resilience-patterns
description: Make calls to dependencies survive failure - timeouts, retries with backoff and jitter, idempotency, circuit breakers, bulkheads, and graceful degradation. Use when the user integrates an external service or API, asks about retries or timeouts, debugs cascading failures, or wants a resilience review of service-to-service calls.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, edit
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [resilience, retries, timeouts, circuit-breaker, reliability]
---

# Resilience Patterns

Every remote call **will** fail, hang, or succeed-without-you-knowing. Resilience is deciding what happens then — before it happens at 3 AM.

## When to use

- Integrating an external API, payment provider, queue, or another internal service
- "Should this retry?" / "What timeout should this have?"
- A dependency outage took the whole system down (cascading failure)
- Reviewing service-to-service calls for production readiness

## Principles

- **Timeouts are not optional.** A call without a timeout is a thread/connection held hostage by someone else's outage. Every remote call gets one.
- **Retries amplify load.** A retry storm against a struggling dependency is a self-inflicted DDoS. Retry less than you think, with backoff and jitter.
- **Idempotency before retries.** Retrying a non-idempotent call (payments!) trades an error for a duplicate. Fix idempotency first.
- **Degrade, don't die.** The feature failing should cost the feature — not the page, not the app.

## The decision ladder

For each remote call, answer in order:

### 1. Timeout — how long will you wait?

- Set from the caller's budget, not the dependency's average: if the user gives up at 3s, a 30s timeout is a 30s hang
- Separate connect timeout (short, ~1s) from read timeout
- Total budget across retries must fit the caller's deadline

### 2. Retry — is it safe, and is it worth it?

| Failure | Retry? |
|---|---|
| Connection error, 503, 429 | Yes — with backoff (429: honor `Retry-After`) |
| Timeout on a **read** (GET) | Yes |
| Timeout on a **write** | Only if idempotent (see 3) |
| 400, 401, 403, 404, 422 | **No** — retrying a validation error N times yields N errors |

Policy: 2–3 attempts max, exponential backoff **with jitter** (e.g. 0.5s → 1s → 2s ± random). Retry storms come from synchronized clients.

### 3. Idempotency — can this run twice safely?

- Writes get an **idempotency key** (client-generated UUID); the server dedupes on it
- Consumers of queues assume at-least-once delivery: handlers must tolerate duplicates
- If you can't make it idempotent, don't auto-retry — surface the ambiguity ("payment status unknown") instead of guessing

### 4. Circuit breaker — when do you stop trying?

- After N consecutive failures (or failure-rate threshold), **open**: fail fast without calling, for a cool-down period
- Then **half-open**: let one probe through; success closes the circuit
- Per-dependency, not global — and emit a metric/alert when state changes

### 5. Bulkhead — what does this failure NOT get to take down?

- Separate connection pools / worker pools per dependency, so a hung dependency can't exhaust shared resources
- Queue non-urgent work instead of calling inline

### 6. Degradation — what does the user see?

Decide per feature: cached/stale data, a hidden widget, a default value, or an honest "temporarily unavailable". Defining this is product work — do it at design time, not mid-incident.

## Review checklist

For each remote call in the code under review:

- [ ] Explicit timeout (connect + read), justified against caller's budget
- [ ] Retry policy matches the failure table above; backoff has jitter
- [ ] Writes are idempotent or not auto-retried
- [ ] Failure of this dependency cannot cascade (breaker/bulkhead where it matters)
- [ ] Degraded behavior is defined and tested
- [ ] Failures are observable: metric per dependency, alert on breaker-open (see `observability`)

## Output format

```markdown
## Resilience review: <service/integration>

| Call | Timeout | Retry | Idempotent | Breaker | Degradation |
|------|---------|-------|------------|---------|-------------|
| …    | 1s/3s   | 2× backoff+jitter | key-based | yes | cached data |

### Gaps (ranked)
1. <call>: <missing control> → <concrete fix>

### Cascade analysis
If <dependency> hangs: <what happens today> → <what should happen>
```

## Anti-patterns

- ❌ No timeout ("the library default is fine" — do you know what it is? It's often infinite)
- ❌ Retrying 4xx errors, or retrying writes without idempotency keys
- ❌ Exponential backoff without jitter — synchronized retry waves
- ❌ Catch-and-continue swallowing failures so nothing degrades *visibly* but data quietly goes missing
- ❌ One shared connection pool for all dependencies — one outage drains it for everyone
- ❌ Circuit breaker with no alert on open — you've automated hiding the outage
- ❌ Testing only the happy path; resilience code that has never seen a failure is decoration
