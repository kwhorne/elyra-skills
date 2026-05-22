---
name: caching-strategy
description: Design a caching strategy - decide what to cache, where, with what TTL and invalidation, and how to avoid the classic foot-guns (stampede, stale data, key collisions). Use when the user asks about caching, cache invalidation, Redis/Memcached design, HTTP caching, or fixing cache-related bugs.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [caching, performance, redis, http-cache]
---

# Caching Strategy

> "There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton

Caching is a leverage tool. Used well, it transforms scalability. Used badly, it creates inconsistency bugs that take weeks to track down.

## When to use

- "Add caching to X"
- "Why is this slow / how do we make it faster?"
- "Design a cache layer"
- "Cache invalidation isn't working"
- "Stale data showing up"
- "Redis / Memcached / HTTP cache config"

## First question: do you actually need a cache?

Caching is **not** the first answer to slowness. Before caching, check:

- [ ] Is there an obvious N+1 query? (fix that first)
- [ ] Are the right indexes in place? (`EXPLAIN ANALYZE`)
- [ ] Is the response payload bloated? (only return what's needed)
- [ ] Is there an algorithmic issue? (O(n²) on a list that grows)

A cache **hides** a problem that profiling could have surfaced. Hidden problems compound. Fix the underlying issue when you can; cache when you can't.

Cache when:

- ✅ The computation is expensive *and* the result is reusable
- ✅ The source of truth is slow or rate-limited (third-party API, complex aggregation)
- ✅ Read >> write, and slight staleness is acceptable
- ✅ You can afford the operational complexity

## The decision matrix

For every cache, answer these before writing code:

| Decision | Question |
|---|---|
| **What** | Exactly which computation / response is being cached? |
| **Key** | What uniquely identifies a cached value? |
| **Where** | Application memory, distributed cache, CDN, HTTP, client? |
| **TTL** | How long until it's allowed to be stale? |
| **Invalidation** | What event makes this value wrong, and how does the cache learn? |
| **Stampede** | What happens when 1000 clients ask for it at once after expiry? |
| **Cost of staleness** | What's the worst that happens if a user sees an old value? |
| **Cost of miss** | If the cache is down, can the system still serve? |

If you can't answer all eight, **don't ship the cache yet.**

## Cache layers (closest to user first)

| Layer | What | Pros | Cons |
|---|---|---|---|
| **Browser / client** | HTTP cache headers, IndexedDB | Free, zero latency | Hard to invalidate, varies per client |
| **CDN / edge** | Static assets, cacheable API responses | Geo-close, offloads origin | Per-CDN config, purge complexity |
| **Reverse proxy** | Varnish, nginx fastcgi cache | Application-agnostic | Less flexible than app cache |
| **Application memory** | LRU in-process map | Nanosecond latency, simple | Per-process, lost on restart, no cross-instance consistency |
| **Distributed cache** | Redis, Memcached, DynamoDB | Shared across instances, survives restart | Network hop, ops burden |
| **Database query cache** | Some DBs (be careful) | Transparent | Often broken or removed in newer versions |
| **Materialized view** | DB-level precomputation | SQL-native, consistent | Refresh strategy needed |

Use multiple layers when each pays its own way. **Don't cache a cache** without a reason.

## TTL strategies

| Strategy | When |
|---|---|
| **Fixed TTL** | Slight staleness OK; simplest |
| **Sliding TTL** (reset on read) | Hot keys stay hot, cold expire |
| **No TTL + explicit invalidation** | Mutations are infrequent and well-controlled |
| **Stale-while-revalidate (SWR)** | Serve stale up to N seconds while refreshing in background — UX win |
| **Negative caching** | Cache "not found" too, to protect against scraping for missing keys |

**TTL should reflect tolerance for staleness**, not arbitrary numbers. "5 minutes" is a smell unless there's a reason.

## Cache invalidation patterns

Pick consciously. The pattern is your invalidation contract.

### Write-through

App writes to cache **and** DB on every write. Reads are guaranteed fresh.

- ✅ Strong consistency
- ❌ Slower writes; cache must be available on writes

### Write-around

App writes to DB only. Cache is populated on read.

- ✅ Simple
- ❌ Cold reads after writes, requires invalidation on update

### Write-back (write-behind)

App writes to cache only; cache batches to DB.

- ✅ Fast writes
- ❌ Data loss risk if cache dies before flush. **Use only when you can afford to lose recent writes.**

### Cache-aside (lazy loading)

App checks cache; on miss, fetches from DB and populates cache.

```python
def get_user(user_id):
    cached = cache.get(f"user:{user_id}")
    if cached is not None:
        return cached
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    cache.set(f"user:{user_id}", user, ttl=300)
    return user
```

The most common pattern. Needs explicit invalidation on writes:

```python
def update_user(user_id, data):
    db.execute("UPDATE users SET ... WHERE id = ?", user_id)
    cache.delete(f"user:{user_id}")  # the contract
```

If you can't guarantee the `cache.delete` runs after **every** write, you have a bug waiting to happen.

## Key design

Keys are an API. Treat them like one.

### Rules

- **Namespace** the key: `user:42`, `user:42:profile`, `feature:beta:user:42`
- **Include version** for cached shapes that might change: `v2:user:42`. Bump version = invalidate everything.
- **Stable across processes**: don't include process IDs, request IDs, or timestamps
- **No high-cardinality variations**: `search:q=hello+world` vs `search:q=hello world` will be different keys
- **Normalize**: lowercase, trim, sort query params before hashing
- **Length matters**: very long keys waste memory; hash if > 100 chars

### Anti-keys

```
❌ user                                   # too generic, collisions
❌ user_data_for_id_42_v2_final_2_real    # human-named chaos
❌ user:42:2026-05-22T14:30:00.123        # timestamp in key = no hits
❌ ${userId}                              # forgot the namespace
```

```
✅ user:42
✅ v3:user:42:profile
✅ search:normalized_query_hash:page:2
```

## The big foot-guns

### 1. Cache stampede / thundering herd

A popular key expires. 1000 requests hit at once. All miss. All hit the database. Database melts.

**Mitigations:**

- **Lock / single-flight**: only one request computes, others wait
  ```python
  with redis.lock(f"lock:user:42", timeout=5):
      # only one client gets the lock and recomputes
  ```
- **Probabilistic early refresh**: refresh before expiry with rising probability ([XFetch algorithm](https://www.vldb.org/pvldb/vol8/p886-vattani.pdf))
- **Stale-while-revalidate**: serve stale while one client refreshes in background
- **Random jitter on TTLs**: spread out expirations so a deploy doesn't cause a herd

### 2. Cache penetration (negative miss attack)

Attackers (or buggy clients) request keys that don't exist. Every request goes to the DB.

**Mitigations:**

- Cache the "not found" result with a short TTL
- Bloom filter in front of the cache
- Rate-limit requests for non-existent keys

### 3. Cache avalanche

A whole class of keys expires at once (e.g., all set with the same TTL during a deploy). Backend is overwhelmed.

**Mitigations:**

- Random jitter on TTLs: `ttl + random(-60s, +60s)`
- Stagger warming during deploys

### 4. Hot key

One key has 90% of traffic. The cache node holding it is saturated.

**Mitigations:**

- Replicate hot keys across multiple nodes
- Add a local in-process cache in front of the distributed cache for hot keys
- Shard by something other than the hot dimension

### 5. Inconsistent reads after writes

User updates their name, refreshes, sees the old name. Cache-aside without invalidation.

**Mitigations:**

- Invalidate on every write — and verify the call site does it
- "Read your own writes" semantics: read from primary for N seconds after a write by this user
- Don't cache user-private data with long TTLs

### 6. Stale "forever" because nobody invalidated

A cached value lives until someone restarts the service.

**Mitigations:**

- Always set a TTL, even if "long"
- Invalidation events should be reliable (idempotent, retried)
- Periodic background refresh as a safety net

## HTTP caching specifically

If it's a public GET, push as much caching as possible to HTTP layer / CDN.

```
Cache-Control: public, max-age=3600, s-maxage=86400, stale-while-revalidate=86400
ETag: "abc123"
Vary: Accept-Encoding, Accept-Language
```

- `public` vs `private` — `private` for per-user data (CDN won't cache)
- `max-age` — browser
- `s-maxage` — shared / CDN
- `stale-while-revalidate` — serve stale while async refresh
- `ETag` + `If-None-Match` — conditional, returns 304 with no body
- `Vary` — split cache by header (be careful, fragments the cache)

For per-user data: `Cache-Control: private, no-store` or you're leaking data through the CDN.

## Output format

```markdown
## Caching design: <what's being cached>

**What:** <exact computation>
**Why:** <why this is a candidate — current cost, expected traffic>
**Layer:** <browser / CDN / app / distributed>
**Key:** `<namespace:fields>`
**TTL:** <duration> (with rationale)
**Invalidation:** <events that invalidate + how>
**Stampede protection:** <lock / SWR / probabilistic refresh / none + reason>
**Cost of staleness:** <impact if user sees a stale value>
**Cost of cache miss / down:** <degraded mode>

### Implementation
\`\`\`<lang>
<key pattern + get + set + invalidate>
\`\`\`

### Metrics to add
- Hit rate
- Miss latency
- Stampede protection trigger count
- Key cardinality (memory growth indicator)

### Rollout plan
- Start: <%> of traffic
- Watch: <metric thresholds>
- Roll forward: <criteria>
```

## Anti-patterns

- ❌ Adding a cache instead of finding the underlying performance bug
- ❌ TTL chosen arbitrarily ("5 minutes seems fine")
- ❌ No invalidation strategy — relying on TTL alone for correctness
- ❌ Caching user-private data at the CDN
- ❌ Caching mutations or write-side responses
- ❌ Caching errors as if they were successes
- ❌ Keys without namespace prefix
- ❌ No metrics — no idea what the hit rate is
- ❌ Cache that the app needs to start (the cache is a hard dependency, not a cache)
- ❌ "We'll cache everything" without picking what

## Tips

- **Measure first.** Profile, don't guess. The slow thing is often not what you think.
- **Make the cache optional.** App should degrade — not die — if cache is down.
- **Instrument hit rate per cache.** A 5% hit rate is a deletion candidate, not a cache.
- **Memory is finite.** Set max sizes and eviction policies (LRU usually).
- **Cache miss latency matters.** A cache that's only checked when slow makes the slow path even slower.
- **Beware of caching during incidents** — they make the system harder to reason about while debugging.
- **Cache hierarchies multiply complexity.** Two layers (app + distributed) is often the sweet spot.

## References

- [Caching at Reddit (2017)](https://www.reddit.com/r/programming/comments/8orrt0/cachingatreddit/) — real-world lessons
- [Facebook scaling memcache](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf) — the canonical paper
- [Cloudflare on HTTP caching](https://developers.cloudflare.com/cache/concepts/cache-control/)
- [Designing Data-Intensive Applications — chapter on caching/consistency](https://dataintensive.net/)
