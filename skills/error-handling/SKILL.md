---
name: error-handling
description: Design a coherent error-handling strategy across a codebase - what to throw vs return, where to catch, how to log, how errors surface to users and to operators. Use when the user asks about error handling, exception design, Result types, error boundaries, or wants to review how errors flow through the code.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, edit
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [errors, reliability, design]
---

# Error Handling

The hardest part of error handling isn't catching errors — it's deciding **where** each kind of error belongs and **who** is responsible for it. Get that wrong and you end up with `try/catch` everywhere and nothing actually handled.

## When to use

- "How should we handle errors in X?"
- "Design an error strategy"
- "Should this throw or return?"
- "Review error handling in this code"
- "Errors aren't being logged / are too noisy"

## Core principles

### 1. Classify errors by who can do something about them

| Class | Who handles it | Example |
|---|---|---|
| **Bug** | The developer (after deploy) | Null deref, off-by-one, wrong type |
| **Expected user error** | The user (via feedback) | Invalid email, password too short |
| **Expected system condition** | The code (retry, fallback) | Network timeout, rate-limited, lock contention |
| **Disaster** | Operators (via alert) | Database down, disk full, secrets revoked |

The handling strategy follows from the class. Mixing them is where most error code goes wrong.

### 2. Errors are values; exceptions are control flow

- **Predictable failures** (validation, lookups, parsing): return them. The caller decides.
- **Unpredictable failures** (DB down, OOM): throw. They propagate to a boundary.

Throwing for predictable failures forces every caller to either know to catch or to silently pass the buck. Returning for unpredictable failures forces every caller to check for things that shouldn't normally happen.

### 3. Catch at boundaries, not everywhere

`try/catch` belongs at:

- **Request boundaries** (HTTP handler, RPC, queue worker) — turn exceptions into responses
- **Resource boundaries** (file/network call) — to retry, fall back, or release resources
- **Trust boundaries** (calls to untrusted code, plugins) — to contain damage

Anywhere else, let it propagate. A `try/catch` in the middle of business logic that swallows or re-throws is almost always wrong.

### 4. Don't lose information

Every layer that catches an error should add context, not erase it.

```ts
// ❌ Loses the original
catch (e) {
  throw new Error("Failed to process order");
}

// ✅ Preserves the chain
catch (e) {
  throw new OrderProcessingError("Failed to process order 42", { cause: e });
}
```

In languages with error wrapping (`Error.cause`, Go's `errors.Wrap`, Rust's `?` + `thiserror`), use it.

## Patterns by language family

### TypeScript / JavaScript

Pragmatic split:

- **Exceptions** for bugs and unexpected conditions
- **Tagged unions / Result types** for domain errors

```ts
type Result<T, E = AppError> = { ok: true; value: T } | { ok: false; error: E };

async function getUser(id: string): Promise<Result<User, "not_found" | "forbidden">> {
  const row = await db.users.findById(id);
  if (!row) return { ok: false, error: "not_found" };
  if (!can(currentUser, "read", row)) return { ok: false, error: "forbidden" };
  return { ok: true, value: row };
}
```

Or libraries: [neverthrow](https://github.com/supermacro/neverthrow), [Effect](https://effect.website/).

### Go

Idiomatic: return `error` as the last value. Wrap with context.

```go
func getUser(id string) (*User, error) {
    row, err := db.QueryRow(id)
    if err != nil {
        return nil, fmt.Errorf("getUser %s: %w", id, err)
    }
    return row, nil
}

// Caller:
user, err := getUser(id)
if errors.Is(err, ErrNotFound) { ... }
```

### Rust

`Result<T, E>` is the language. Use `?` to propagate, `thiserror` for ergonomic enums, `anyhow` for application code.

### Python

Exceptions are idiomatic. Define a domain hierarchy:

```python
class AppError(Exception): ...
class ValidationError(AppError): ...
class NotFoundError(AppError): ...
class ExternalServiceError(AppError):
    def __init__(self, service: str, cause: Exception):
        self.service = service
        super().__init__(f"{service} failed: {cause}")
        self.__cause__ = cause
```

### Java / Kotlin

Checked exceptions become noise — wrap in unchecked at the boundary. In Kotlin, prefer sealed-class results for domain errors.

### PHP

Exceptions for unexpected; tagged returns / Result classes for domain. Laravel: lean into typed exceptions + a global handler that maps them to HTTP responses.

## Error → user mapping

For user-facing errors, the **error class** should determine the response shape and message tone.

| Class | HTTP | User message | Logging |
|---|---|---|---|
| Validation | 400 / 422 | Specific, actionable, per field | info |
| AuthN failure | 401 | Generic ("invalid credentials") | info (be careful with detail) |
| AuthZ failure | 403 | Generic ("not allowed") | warn (potentially malicious) |
| Not found | 404 | "Not found" | info |
| Conflict | 409 | What conflicts, what to do | info |
| Rate limit | 429 | Retry-After header + clear message | warn |
| External service | 502 / 503 | Generic ("temporary issue, try again") | error + alert |
| Unknown / bug | 500 | Generic + request ID | error + alert |

**Never leak internal details to the user.** Stack traces in API responses are a security issue.

## Error → operator mapping

| Severity | Source | Logging | Alerting |
|---|---|---|---|
| Bug (uncaught) | code path | `error` with full context, request ID, user ID | yes |
| External dep failed | network call | `warn` with attempt count | only if rate > threshold |
| Validation failed | user input | `info` with field | no |
| Permission denied | authz | `warn` with user/route | only on burst (probing) |
| Auth failure | login | `info` | only on burst (brute force) |

Tune levels until pages reflect actionable problems. If `error` fires constantly, change the level (it's not an error) or fix the cause (it shouldn't be happening).

## The boundary handler

Each request/job boundary should have **one** error handler that:

1. Catches anything not already caught
2. Maps domain error class → HTTP response (or job retry decision)
3. Logs with request ID, user ID, route, latency
4. Includes the request ID in the response (so users can quote it to support)
5. Reports to error tracker (Sentry / Rollbar / etc.) for unexpected errors

```ts
// Express-ish example
app.use((err, req, res, next) => {
  const requestId = req.id;
  if (err instanceof ValidationError) {
    log.info({ requestId, err }, "validation_failed");
    return res.status(422).json({ error: { code: err.code, details: err.details, request_id: requestId } });
  }
  if (err instanceof NotFoundError) {
    return res.status(404).json({ error: { code: "not_found", request_id: requestId } });
  }
  // Unexpected — log + alert
  log.error({ requestId, err }, "unhandled");
  sentry.captureException(err, { tags: { requestId } });
  res.status(500).json({ error: { code: "internal", request_id: requestId } });
});
```

## Retries

Don't retry blindly. Retry **on specific errors**, with **bounded attempts**, **exponential backoff with jitter**, and **idempotency**.

```ts
async function callWithRetry<T>(fn: () => Promise<T>, opts = { tries: 3, base: 200 }): Promise<T> {
  let lastErr: unknown;
  for (let i = 0; i < opts.tries; i++) {
    try {
      return await fn();
    } catch (e) {
      if (!isRetryable(e)) throw e;
      lastErr = e;
      const delay = opts.base * 2 ** i + Math.random() * opts.base;
      await sleep(delay);
    }
  }
  throw lastErr;
}
```

Retry on: timeouts, 502/503/504, transient network errors, lock contention.
**Do not** retry on: 4xx (except 408, 425, 429), parse errors, auth failures.

Pair retries with a **circuit breaker** for downstream services.

## Idempotency

Retries require idempotency. Without it, retries cause duplicate side effects.

- Reads are naturally idempotent
- Writes: use an **idempotency key** sent by the client; cache the response for N hours; replay if seen again
- Outbound calls: include a unique key the receiver can dedupe on

## Error message style

Messages have **three audiences**: developer, operator, user. Don't try to write one string for all three.

| Audience | Where | Tone |
|---|---|---|
| Developer | Logs, stack traces | Technical, specific, full IDs |
| Operator | Alerts, dashboards | Symptom + runbook link |
| User | UI, API response | Plain language, no jargon, actionable |

Each gets a tailored string. The log message is not the user message.

## Output format

When reviewing error handling:

```markdown
## Error handling review: <scope>

**Current style:** <exceptions everywhere / mixed / Result types / …>

### Strengths
- ✅ <thing>

### Gaps

#### 🔴 Lost information / dangerous swallowing
- `path:42` — catches everything, logs nothing, returns null

#### 🟠 Wrong layer
- `path:88` — try/catch around business logic that should propagate

#### 🟡 Inconsistent or noisy
- Same error class returned 3 different HTTP codes
- `error` log firing for expected validation failures (false alerts)

### Proposed strategy
- **Throw** for: bugs, infrastructure failures
- **Return** for: validation, lookup misses, business-rule denials
- **Catch at**: HTTP handler, queue worker, external-call site
- **Domain error hierarchy:** `AppError → {ValidationError, NotFoundError, ExternalServiceError, …}`
- **Boundary handler:** mapped table of class → HTTP code → log level

### Action items
1. Add boundary handler (see template)
2. Replace silent `catch (e) {}` instances (n found)
3. Add request_id propagation
4. …
```

## Anti-patterns

- ❌ `catch (e) {}` — silent swallow. The bug becomes invisible.
- ❌ `catch (e) { console.log(e); throw e; }` — pure noise, no added value
- ❌ Returning `null` for both "not found" and "error" — caller can't distinguish
- ❌ Exceptions for control flow (`throw new EndOfLoop()`)
- ❌ One giant `try { everything } catch { showError() }` at the top level
- ❌ Leaking stack traces / SQL / internal IDs to users
- ❌ Error messages without IDs — users say "I got an error" and you can find nothing
- ❌ Retrying 4xx errors (especially 400, 401, 403) — they won't get better
- ❌ Retrying without backoff — DDoS your own backend
- ❌ Reporting every validation failure to Sentry — drowns real bugs
- ❌ Different error formats per endpoint
- ❌ `if (err.message.includes("not found"))` — never type-check via string matching

## Tips

- **A request ID on every log line + every error response** is the single highest-leverage thing
- **One error format across the API.** Document it.
- **Convert legacy throws to typed errors gradually** at the boundary. Don't try to rewrite all at once.
- **Test the error paths.** They're famously under-tested and famously where prod incidents live.
- **Read your own logs.** Once a week, scan recent `error` logs. If you don't recognize them, they're either real bugs or noise — both worth fixing.

## References

- [Joe Armstrong on "Let it crash"](https://erlang.org/download/armstrong_thesis_2003.pdf) — Erlang's approach
- [Rust Book: Error Handling chapter](https://doc.rust-lang.org/book/ch09-00-error-handling.html)
- [Go blog: error handling and Go](https://go.dev/blog/error-handling-and-go)
- [Stripe API errors](https://stripe.com/docs/api/errors) — a polished error-response design
- [Designing Data-Intensive Applications — Reliability chapter](https://dataintensive.net/)
