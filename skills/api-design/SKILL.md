---
name: api-design
description: Design consistent HTTP/REST endpoints with sensible naming, status codes, pagination, error formats, and versioning. Use when the user asks to design, review, or extend an HTTP API, or wants feedback on endpoint shape.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [api, rest, design]
---

# API Design

Principles for HTTP/REST APIs that are predictable, debuggable, and pleasant to consume. Opinionated where the field has converged; flexible where reasonable people disagree.

## When to use

- "Design an endpoint for X"
- "How should this API look?"
- "Review this API"
- "Add an endpoint to …"

## Procedure

1. **Anchor to existing patterns.** Read 2–3 existing endpoints in the same codebase. New endpoints should look like neighbors.
2. **Model the resource, not the action.** Most actions become CRUD on a resource. If they don't (e.g. "publish"), see "Actions on resources" below.
3. **Sketch the contract before writing code:** path, method, request body, response body, status codes, errors.
4. **Check it against the consistency checklist** below.
5. **Document it** — even one paragraph in the PR is better than nothing.

## Resource naming

- Use **plural nouns** for collections: `/users`, `/orders`, `/articles`
- Use **IDs**, not slugs, for identity: `/users/42` (slugs are for SEO, not for APIs)
- **Nest** to express ownership, max 2 levels deep:
  - ✅ `/users/42/orders`
  - ❌ `/users/42/orders/7/items/3/shipments`
- Use **kebab-case** in paths: `/account-settings`, not `/accountSettings` or `/account_settings`
- **Lowercase** everything in paths
- No verbs in paths — the HTTP method *is* the verb

## Methods

| Method | Purpose | Idempotent | Safe |
|---|---|---|---|
| `GET` | Retrieve | yes | yes |
| `POST` | Create, or non-idempotent action | no | no |
| `PUT` | Replace (full update) | yes | no |
| `PATCH` | Partial update | no\* | no |
| `DELETE` | Remove | yes | no |

\* PATCH *can* be idempotent if you design it that way; don't rely on it.

## Status codes

Pick from this short list. Resist the urge to be clever.

| Code | Meaning | Use for |
|---|---|---|
| `200 OK` | Success with body | `GET`, `PATCH`, `PUT` returning resource |
| `201 Created` | Resource created | `POST` that creates a resource (return it + `Location` header) |
| `202 Accepted` | Accepted for async processing | Long-running jobs |
| `204 No Content` | Success, no body | `DELETE`, `PUT` without return |
| `400 Bad Request` | Malformed request | Bad JSON, missing required fields |
| `401 Unauthorized` | Not authenticated | Missing/invalid credentials |
| `403 Forbidden` | Authenticated but not allowed | Permission denied |
| `404 Not Found` | Resource doesn't exist | Unknown ID |
| `409 Conflict` | State conflict | Duplicate, version mismatch |
| `422 Unprocessable Entity` | Validation failed | Well-formed but semantically invalid |
| `429 Too Many Requests` | Rate-limited | Include `Retry-After` |
| `500 Internal Server Error` | We broke it | Unexpected server fault |
| `503 Service Unavailable` | Temporarily down | Maintenance, dependency outage |

Don't invent custom codes. Don't return `200` with `{"error": "..."}`.

## Errors

Use a single, documented error shape across the entire API:

```json
{
  "error": {
    "code": "validation_failed",
    "message": "Request failed validation.",
    "details": [
      { "field": "email", "code": "invalid_format" },
      { "field": "age", "code": "must_be_positive" }
    ],
    "request_id": "req_01HX…"
  }
}
```

- **Stable, machine-readable `code`** (snake_case, never localized)
- **Human-readable `message`** (English; localize on the client)
- **`details`** for per-field validation
- **`request_id`** for support / log correlation

Consider [RFC 9457 Problem Details](https://www.rfc-editor.org/rfc/rfc9457) if the consumer already uses it.

## Pagination

Pick one and stick with it across the API.

- **Cursor-based** (preferred for large/changing data):
  - Request: `?limit=50&cursor=eyJpZCI6...`
  - Response: `{ "data": [...], "next_cursor": "...", "has_more": true }`
- **Page-based** (fine for small/static data):
  - Request: `?page=2&per_page=50`
  - Response: `{ "data": [...], "page": 2, "per_page": 50, "total": 1234 }`

Always cap `limit` / `per_page` server-side. Document the max.

## Filtering, sorting, sparse fields

- **Filter**: `?status=active&created_after=2025-01-01`
- **Sort**: `?sort=-created_at,name` (leading `-` = descending)
- **Sparse fields**: `?fields=id,email,created_at`

## Versioning

Pick one strategy and commit:

- **URL**: `/v1/users` — most visible, easiest to route
- **Header**: `Accept: application/vnd.example.v1+json` — cleaner URLs, harder to debug
- Avoid query-string versioning

Only bump the major version for **breaking** changes. Additive changes (new fields, new endpoints) don't require a new version.

## Actions on resources

When CRUD doesn't fit (publish, archive, retry, refund), prefer:

- **State transitions via PATCH:** `PATCH /articles/42 {"status": "published"}` — best if you have multiple states
- **Sub-resources for explicit actions:** `POST /articles/42/publish` — pragmatic when the action has side effects or its own payload

Don't go full RPC: `POST /publishArticle?id=42`. You're using HTTP; use it.

## Consistency checklist

- [ ] Resource name is a plural noun
- [ ] Path uses kebab-case and lowercase
- [ ] HTTP method matches semantics (idempotency!)
- [ ] Status codes from the short list
- [ ] Error response matches the API-wide error shape
- [ ] `POST` that creates returns `201` + `Location` header
- [ ] List endpoints paginate and cap `limit`
- [ ] Timestamps are ISO 8601 with timezone (`2026-05-22T14:30:00Z`)
- [ ] IDs are opaque strings (not auto-increment ints leaked) when possible
- [ ] No sensitive data in URLs (use headers / body)
- [ ] Versioning strategy followed
- [ ] Authentication / authorization checks documented per endpoint

## Anti-patterns

- ❌ `GET /getUser?id=42` — verb in path, query param for identity
- ❌ `POST /users/delete/42` — DELETE exists for a reason
- ❌ Returning `200` with `{"success": false}`
- ❌ Inconsistent casing: `userId` in one response, `user_id` in another
- ❌ Auto-increment IDs in URLs leaking row counts to the public
- ❌ Pagination with no upper bound on `limit`
- ❌ Mixing snake_case and camelCase in the same payload
- ❌ "Soft 200" — returning HTTP success but logical failure
