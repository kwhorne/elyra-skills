---
name: performance-budget
description: Define and enforce performance budgets for web apps - bundle size, Core Web Vitals, render time, API latency. Use when the user asks to set perf budgets, review performance, investigate slowness, or set up performance gates in CI.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [performance, budgets, web-vitals]
---

# Performance Budget

A performance budget is a **number you refuse to cross**. Without it, "is this fast enough?" is opinion-driven and slowly loses every argument to features.

## When to use

- "Set up performance budgets"
- "Is this app fast enough?"
- "Investigate why X is slow"
- "Add a perf gate to CI"
- "Review the bundle / render / latency of …"

## Procedure

1. **Decide what you're budgeting** (see categories below) — don't try to budget everything at once
2. **Measure the current state** — you can only budget what you measure
3. **Set a target + a ceiling**, not a single magic number
   - Target: what you want
   - Ceiling: what fails CI
4. **Enforce in CI** so regressions can't sneak in
5. **Review monthly** — budgets that never change are decoration

## Budget categories

### 1. Bundle size

| Metric | Reasonable starting point |
|---|---|
| Initial JS (compressed, gzip/brotli) | ≤ 170 KB |
| Initial CSS (compressed) | ≤ 60 KB |
| Total transferred (initial load, compressed) | ≤ 500 KB |
| Largest single chunk | ≤ 250 KB |
| Image weight (above the fold) | ≤ 200 KB |

Adjust for your audience. A B2B internal tool on corporate desktops tolerates more than a public site for emerging markets on 3G.

### 2. Core Web Vitals (real-user)

| Metric | Good | Needs improvement | Poor |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| **INP** (Interaction to Next Paint) | ≤ 200ms | ≤ 500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | ≤ 0.25 | > 0.25 |

Budget on the **75th percentile** of real users, not your dev laptop.

### 3. Lab metrics (synthetic, Lighthouse-style)

| Metric | Target |
|---|---|
| Time to Interactive (TTI) | ≤ 3.5s on mid-tier mobile, 4G |
| First Contentful Paint (FCP) | ≤ 1.8s |
| Total Blocking Time (TBT) | ≤ 200ms |
| Lighthouse Performance | ≥ 90 |

### 4. API & backend

| Metric | Target |
|---|---|
| p50 endpoint latency | ≤ 100ms |
| p95 endpoint latency | ≤ 300ms |
| p99 endpoint latency | ≤ 1s |
| Error rate | ≤ 0.1% |

Percentiles, not averages. The average hides the users having a bad time.

### 5. Database

| Metric | Target |
|---|---|
| Queries per request (p95) | ≤ 10 |
| Slowest query per request | ≤ 50ms |
| N+1 queries detected | 0 |

## Measuring

```bash
# Bundle size (most bundlers expose this)
# Vite: npx vite build --report
# Webpack: npx webpack --json | npx webpack-bundle-analyzer
# Next: ANALYZE=true npm run build
# Show gzipped sizes:
find dist -name '*.js' -exec sh -c 'gzip -c "$1" | wc -c | xargs -I{} echo "$1: {} bytes"' _ {} \;

# Lighthouse from CLI
npx lighthouse https://example.com --output=json --output-path=./lh.json \
  --preset=desktop  # or --form-factor=mobile

# Real user metrics
# - web-vitals npm package, sent to your analytics
# - Chrome UX Report (CrUX) for public sites
# - Vercel/Cloudflare/Netlify all expose CWV dashboards

# API latency
# - APM tool (Datadog, Sentry, New Relic, Honeycomb, …)
# - For quick local measurement:
ab -n 100 -c 10 https://example.com/api/users
hey -n 100 -c 10 https://example.com/api/users
```

## Enforcing in CI

```yaml
# .github/workflows/perf.yml — bundle size check
- name: Check bundle size
  uses: andresz1/size-limit-action@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

```json
// package.json — size-limit config
{
  "size-limit": [
    { "path": "dist/index.js", "limit": "170 KB" },
    { "path": "dist/index.css", "limit": "60 KB" }
  ]
}
```

```yaml
# Lighthouse CI
- name: Lighthouse CI
  run: |
    npm install -g @lhci/cli
    lhci autorun --collect.url=https://staging.example.com \
                 --assert.preset=lighthouse:recommended
```

## Investigation playbook

When something is slow:

1. **Measure first** — don't optimize on hunch
2. **Identify the layer**: network, parse/compile, render, layout, paint, API, DB
3. **Use the right tool**:
   - **Network slow** → DevTools Network panel, response sizes, cache headers
   - **JS slow** → DevTools Performance profile, look for long tasks
   - **Render slow** → React/Vue DevTools profiler, count re-renders
   - **API slow** → APM trace, span breakdown
   - **DB slow** → `EXPLAIN ANALYZE`, slow query log
4. **Fix the biggest item, re-measure** — don't batch micro-optimizations
5. **Add a regression test or budget gate** so it doesn't come back

## Common wins by category

### Frontend
- Code-split routes; lazy-load below-the-fold
- Preload critical fonts, eliminate FOIT
- `<img loading="lazy">`, modern formats (AVIF/WebP), correct sizing
- Server-side render or static-generate where you can
- Audit dependencies — one accidental `moment` import can be 70KB

### Backend
- Eliminate N+1 (eager loading / batch fetches)
- Add indexes for columns in WHERE / JOIN / ORDER BY
- Cache hot reads (Redis, HTTP cache headers)
- Move expensive work to background jobs
- Compress responses (gzip / brotli)

### Database
- `EXPLAIN ANALYZE` the slow query, look at scan vs index
- Avoid `SELECT *` when you need three columns
- Connection pool sized appropriately
- Read replicas for read-heavy workloads

## Output format

```markdown
## Performance audit: <scope>

**Baseline measurements:**
- Bundle: <kb>
- LCP / INP / CLS (p75): … / … / …
- API p95: …

**Budget proposal:**
| Metric | Current | Target | Ceiling |
|---|---|---|---|
| … | … | … | … |

### Findings
- 🔴 **Critical:** <largest single regression vs target>
- 🟠 **Major:** …
- 🟡 **Minor:** …

### Recommended actions (ordered by impact)
1. …
2. …

### CI gates to add
- …
```

## Anti-patterns

- ❌ "Make it faster" without a target
- ❌ Measuring on your dev laptop and calling it a day
- ❌ Averaging out the p99 users
- ❌ Premature micro-optimization (loop unrolling) before profiling
- ❌ Budget gates that bypass with `--force` every week — fix the cause
- ❌ Optimizing the part of the request that's already fast
- ❌ Re-rendering the world to "fix" a 2ms task

## References

- [web.dev / Core Web Vitals](https://web.dev/vitals/)
- [Performance Budgets 101](https://web.dev/articles/performance-budgets-101)
- [The Cost of JavaScript](https://v8.dev/blog/cost-of-javascript-2019)
