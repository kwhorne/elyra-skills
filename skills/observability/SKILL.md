---
name: observability
description: Decide what to instrument with logs, metrics, and traces so a system is debuggable in production. Use when the user asks about observability, monitoring, logging, metrics, tracing, alerts, or how to make a service debuggable.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, edit
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [observability, monitoring, logging, metrics, tracing]
---

# Observability

You're observable if a stranger on-call at 3 AM can answer "what's broken and why" **from the data alone**, without pinging the author. That's the whole goal.

## When to use

- "Add logging / metrics / tracing"
- "How should I instrument X?"
- "Make this service observable"
- "Set up alerts"
- "Debug production without a debugger"

## The three pillars (and what they're each good at)

| Signal | Answers | Cost |
|---|---|---|
| **Logs** | "What happened?" — discrete events, full detail | High volume; cheap per event, expensive at scale |
| **Metrics** | "How much / how often?" — aggregated, low-cardinality, time-series | Cheap, fast to query, lossy on details |
| **Traces** | "Where did time go?" — request flow across services | Sampled; great for latency and dependency analysis |

You need all three. Each compensates for the others' weaknesses.

## Logs

### What to log

- Boundary events: request received, request completed (status, latency)
- Business events: order placed, user registered, payment captured
- Errors with full context (stack, inputs, user/account ID, request ID)
- State transitions that matter
- External calls: which service, latency, outcome
- Background job: started, completed, retried, failed

### What NOT to log

- Secrets, tokens, passwords, full credit card numbers
- Personally identifiable info beyond what's necessary (and never in plaintext if you can avoid it)
- Inside hot loops without throttling
- "Success" pings every second from a healthy heartbeat — too much noise
- Anything you wouldn't want screen-shared in a debugging session

### Structure them

Structured logs (JSON) > text logs. They're greppable *and* queryable.

```json
{
  "ts": "2026-05-22T14:30:00.123Z",
  "level": "info",
  "msg": "order.placed",
  "request_id": "req_01HX...",
  "user_id": "usr_42",
  "order_id": "ord_7",
  "amount_cents": 1999,
  "currency": "USD",
  "duration_ms": 42
}
```

Rules:
- One event per line, valid JSON
- Stable field names across the codebase (`request_id`, not `reqId` here and `requestId` there)
- `ts` in ISO 8601 UTC
- `level` from a fixed set: `debug`, `info`, `warn`, `error`
- `msg` is a stable identifier, **not a sentence** — `order.placed` not `"Order placed for user 42 at $19.99"`. Put dynamic values in their own fields.

### Levels

| Level | Use for | Production volume |
|---|---|---|
| `debug` | Detailed flow info | Off in prod (or sampled) |
| `info` | Normal events worth recording | High but bounded |
| `warn` | Unexpected but handled | Low |
| `error` | Failures requiring attention | Very low, every one investigated |

If `error` is firing constantly, it's not `error` — it's noise. Either fix the cause or change the level.

## Metrics

### The four golden signals (for any user-facing service)

1. **Latency** — how long requests take (p50, p95, p99, **never average**)
2. **Traffic** — how many requests (RPS)
3. **Errors** — error rate (% or absolute)
4. **Saturation** — how close to capacity (CPU, memory, queue depth, connection pool usage)

Instrument these four for every service. Almost everything else follows.

### Naming

- Snake_case, dot-separated namespace: `http.request.duration_ms`, `payment.captured.count`
- Include the unit in the name: `_ms`, `_bytes`, `_count`, `_ratio`, `_total`
- Counter names end in `_total` if cumulative (Prometheus convention)
- Histograms for distributions (latency), counters for events, gauges for current state

### Labels / tags / dimensions

Add labels for dimensions you'll filter by: `method`, `route`, `status_code`, `region`.

**Cardinality is the silent killer.** Each unique combination of label values creates a separate time series. Don't put high-cardinality values in labels:

- ❌ `user_id` — millions of unique values, kills your metrics backend
- ❌ `request_id`, `order_id`, exact URLs with path params
- ✅ `user_tier` (free / pro / enterprise), `route` (parameterized: `/users/:id`)

If you need per-user investigation, that's what logs and traces are for. Not metrics.

### Histograms, not averages

```
Average latency: 150ms
p50: 80ms, p95: 400ms, p99: 2000ms, max: 30s
```

The first number is comforting. The other four describe what users actually experience. Always histogram for latency.

## Traces

### When to add tracing

- Multi-service request flows (frontend → API → downstream → DB → cache)
- Background jobs with multiple stages
- Anywhere "where did the time go?" is asked frequently
- Async workflows: connect the trace across queues

### What a trace tells you

```
[─────────── HTTP GET /api/orders/42 (320ms) ──────────────]
  [── auth (5ms) ──]
  [─────── DB: SELECT orders (180ms) ──────]
  [── DB: SELECT items (40ms) ──]
  [── cache get (1ms) ─]
  [─── external: shipping API (80ms) ───]
```

You see where time goes and what's in the critical path. No more "is the DB slow or the external API slow?" guesswork.

### Sampling

Tracing every request is expensive and rarely useful. Sample:
- **Head-based**: decide at the start (simple, may miss interesting traces)
- **Tail-based**: collect all, sample based on outcome (slow / errored / unusual) — keeps the interesting ones
- Always sample errors at 100%

### Correlation IDs

A `request_id` (or `trace_id`) on every log line + propagated to downstream services + included in error responses lets you stitch everything together. **This is the single highest-leverage observability investment.**

```
Frontend log:  request_id=req_01HX... user clicked /checkout
Gateway log:   request_id=req_01HX... routed to api-service
API log:       request_id=req_01HX... ERROR validation failed
Customer email: support reference: req_01HX...
```

One ID, the whole story.

## Alerts — make them actionable

An alert should answer **what's wrong + what to do**.

### Good alerts

- Fire on **user-visible symptoms**, not internal causes ("error rate > 1% for 5 min" not "CPU > 80%")
- Include a runbook link
- Have an owner
- Are tested (synthetic failure to verify they fire)

### Alert fatigue is the failure mode

If on-call ignores or auto-silences alerts, your alerts are broken. Symptoms:
- Alerts that fire and recover before anyone sees them
- "It always fires, just ignore it"
- Multiple alerts for the same underlying cause
- Pages outside business hours for non-pageable severity

Fix the alerts, not the humans.

### Alert template

```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
  for: 5m
  labels:
    severity: page
    service: api
    owner: payments-team
  annotations:
    summary: "API error rate above 1% for 5 minutes"
    description: "Current rate: {{ $value | humanizePercentage }}"
    runbook: "https://runbooks/api/high-error-rate"
    dashboard: "https://grafana/d/api-overview"
```

## Dashboards — one per service, no more

Every service should have **one canonical dashboard** answering:

1. Is it up? (traffic + error rate)
2. Is it fast? (latency percentiles)
3. Is it healthy? (saturation)
4. What's it doing? (top routes, top errors)

More dashboards ≠ better observability. They scatter attention. One good dashboard, kept up to date, beats twelve neglected ones.

## What to instrument first (priority order)

If you have nothing yet:

1. **Request log** with `request_id`, status, latency, route — on every endpoint
2. **Four golden signals** as metrics
3. **Error tracker** (Sentry / Honeybadger / Rollbar) — uncaught errors with stack + context
4. **One canonical dashboard** + one runbook
5. **Alert on error rate** and **alert on p95 latency**
6. **Trace** the top 1–2 user journeys end-to-end
7. **Saturation alerts**: disk, memory, queue depth

That gets you 80% of the value. Add more only when a real debugging session was hampered by missing data.

## Output format

When reviewing instrumentation:

```markdown
## Observability review: <service / scope>

**Current signals:** logs / metrics / traces / alerts

### What's instrumented
- ✅ <thing> — <how>

### Gaps
- 🔴 <missing critical instrumentation> — <user impact when debugging>
- 🟠 <missing significant signal>
- 🟡 <nice to have>

### High-cardinality risks (metrics)
- `<metric>{<label>}` — <why this is dangerous>

### Alert quality
- ✅ <good alert>
- 🔴 <noisy / unactionable alert>

### Recommended additions (prioritized)
1. …
2. …
```

## Anti-patterns

- ❌ Logging at `error` level for handled exceptions — false alarms
- ❌ `console.log("here")` left in production code
- ❌ Unstructured logs ("User 42 placed order 7 for $19.99 on 2026-05-22") — hard to query
- ❌ Average latency as your latency metric
- ❌ `user_id` in metric labels
- ❌ Logging passwords, tokens, credit cards, full PII
- ❌ Alerts on causes (CPU high) instead of symptoms (users seeing 500s)
- ❌ Twelve dashboards, none of them maintained
- ❌ Adding logs but not searching them — if you've never queried it, you don't need it
- ❌ Tracing on but never sampled / never looked at

## References

- [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) — the four golden signals
- [USE Method (Brendan Gregg)](https://www.brendangregg.com/usemethod.html) — Utilization, Saturation, Errors for resources
- [RED Method (Tom Wilkie)](https://thenewstack.io/monitoring-microservices-red-method/) — Rate, Errors, Duration for services
- [OpenTelemetry](https://opentelemetry.io/) — vendor-neutral instrumentation API
- [Charity Majors on observability](https://charity.wtf/category/observability/) — pointed essays on doing it well
