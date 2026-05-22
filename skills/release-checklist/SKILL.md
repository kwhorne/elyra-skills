---
name: release-checklist
description: Run through a structured pre-release, release, and post-release checklist to ship safely. Use when the user asks to prepare a release, cut a version, deploy to production, or wants a checklist for shipping software.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [release, deployment, checklist]
---

# Release Checklist

A release is a transaction: every step should be reversible or independently verifiable. This is the boring-on-purpose list you run *before* the heroics are needed.

## When to use

- "Cut a release / ship v1.4.0"
- "Prepare to deploy"
- "Are we ready to release?"
- "Release checklist for X"

## Tailor it

The checklist below is exhaustive on purpose. Most projects need a subset. Match it to your actual risk: a marketing site has different needs than a payments backend. **Delete what doesn't apply; never skip a section without saying why.**

## Pre-release (T–1 day to T–1 hour)

### Code & quality

- [ ] All blockers in the release scope are closed
- [ ] CI is green on `main` / the release branch
- [ ] Linter / formatter clean
- [ ] Type-check clean
- [ ] Test suite passes (unit, integration, end-to-end)
- [ ] No `.only` / `.skip` / commented-out tests sneaking in
- [ ] No `TODO`/`FIXME`/`XXX` added with release-blocking intent
- [ ] Dependencies audit clean or known advisories documented
- [ ] No secrets in the diff (`git diff vLAST..HEAD | grep -iE 'api[_-]?key|secret|password|token'`)

### Versioning & changelog

- [ ] Version bumped (package.json, composer.json, pyproject.toml, etc.)
- [ ] `CHANGELOG.md` updated, `[Unreleased]` → `[X.Y.Z] - YYYY-MM-DD`
- [ ] Breaking changes clearly marked
- [ ] Migration guide written (if breaking)
- [ ] Release notes drafted for distribution channels

### Database & data

- [ ] Migrations reviewed for safety (zero-downtime, indexed, locks understood)
- [ ] Migrations tested against a prod-sized snapshot if schema is non-trivial
- [ ] Backward-compatible: old app version works against new schema (expand)
- [ ] Backups verified within last 7 days
- [ ] Backfill jobs planned (if needed) — separately from the migration

### Configuration

- [ ] New env vars / config flags documented and set in all environments
- [ ] Feature flags created and defaulted to safe (off)
- [ ] Rollout plan for flags written down
- [ ] Secrets rotated if anything was exposed

### Compatibility

- [ ] API backward-compatible, or breaking version documented
- [ ] Client/SDK compatibility checked (mobile apps with old versions in the wild)
- [ ] Webhook contracts unchanged or versioned
- [ ] Third-party integrations notified (if behavior changes)

### Performance & capacity

- [ ] Load test passed (if change affects hot path)
- [ ] No new N+1 queries / unbounded loops introduced
- [ ] Cache invalidation strategy clear
- [ ] Background queue capacity sufficient for any new jobs

### Communication

- [ ] Stakeholders informed of release window
- [ ] On-call notified
- [ ] Customer-facing changes drafted (in-app banners, email, docs)
- [ ] Status page entry prepared (maintenance window if applicable)
- [ ] Rollback owner identified

## Release (T–0)

### Deploy

- [ ] Deploy initiated from the **tagged commit**, not "latest main"
- [ ] Deploy log captured (link in incident channel just in case)
- [ ] Migrations run (or scheduled to run pre-deploy)
- [ ] Caches cleared if needed (carefully — cold caches can cause spikes)
- [ ] CDN purged if static assets changed

### Smoke test

Run these **within 5 minutes** of deploy:

- [ ] Homepage loads
- [ ] Login works
- [ ] Critical user journey works (whatever "buy", "post", or "submit" means for you)
- [ ] Background jobs are processing
- [ ] API health endpoint returns 200
- [ ] No spike in error rate (give it ~5 min to materialize)
- [ ] Latency normal
- [ ] New feature behind flag works *with the flag on for staff*

```bash
# Quick post-deploy smoke
curl -sw '\nstatus=%{http_code} time=%{time_total}s\n' -o /dev/null https://example.com/
curl -sw '\nstatus=%{http_code} time=%{time_total}s\n' -o /dev/null https://example.com/health
curl -sw '\nstatus=%{http_code} time=%{time_total}s\n' -o /dev/null https://example.com/api/version

# Compare versions deployed
curl -s https://example.com/api/version | jq .
```

### Communicate

- [ ] Internal: announce release shipped (with version + summary)
- [ ] Status page: maintenance window closed if open
- [ ] External: release notes / blog / email published (if applicable)
- [ ] GitHub Release created with tag + changelog excerpt

## Post-release (T+1 hour to T+24 hours)

### Watch

- [ ] Error rate vs baseline — within 0.1pp
- [ ] Latency vs baseline — p95 within 20%
- [ ] Key business metrics (signups, purchases, etc.) — no sudden drop
- [ ] Background queue depth — not growing unbounded
- [ ] Customer support inbox — no spike in tickets
- [ ] On-call alerts — quiet (or expected alerts only)

If anything regresses → see `incident-response` skill.

### Rollout (if behind flags)

- [ ] Begin staged ramp per the rollout plan (see `feature-flag-rollout`)
- [ ] First stage observed for the agreed duration
- [ ] Metrics meeting success criteria before advancing

### Cleanup

- [ ] Delete release branch (if used)
- [ ] Close release tracking issue / milestone
- [ ] Move any deferred items back to backlog with notes
- [ ] Update internal docs that referenced the old version

## Rollback plan (always write this *before* release)

```markdown
## Rollback plan: v<X.Y.Z>

**Trigger:** any of —
- Error rate > <n>x baseline for >5 min
- p95 latency > <n>x baseline for >5 min
- New blocker bug reported
- Data integrity issue

**Rollback procedure:**
1. Flip flag <name> to off (covers <%> of risk)
2. Redeploy v<X.Y-1.Z>: `<exact command>`
3. Revert migration <id>? <yes / no — explain>
4. Communicate: status page + internal channel

**Owner during release window:** @<person>
**Window:** <start> – <end>
```

If you can't write a credible rollback plan, the release isn't ready.

## Output format

When asked for a checklist for a specific release:

```markdown
## Release readiness: v<X.Y.Z>

**Scope:** <one-line summary>
**Target window:** <date/time>
**Owner:** @<person>

### ✅ Done
- <item>

### 🟡 In progress
- <item> — <who, by when>

### 🔴 Blocking
- <item> — <why blocking>

### 🚫 Not applicable (with reason)
- <item> — <why skipped>

### Rollback plan
<as above>

**Recommendation:** GO / NO-GO / GO with caveats: <…>
```

## Anti-patterns

- ❌ Friday afternoon release with no on-call until Monday
- ❌ Deploying "latest main" — release from a tag so you know what shipped
- ❌ Migrations baked into the release deploy with no backward compatibility
- ❌ Rollback plan written *after* it's needed
- ❌ Skipping the smoke test because "CI passed"
- ❌ One person does everything — no second pair of eyes
- ❌ Treating the checklist as ceremony — tick the box without doing the thing
- ❌ "We'll write release notes after" (you won't)
- ❌ Releasing during a known-busy traffic window
- ❌ Releasing right before a freeze you can't roll back through

## Tips

- **Cadence beats heroics**: small, frequent releases are dramatically safer than rare big ones
- **Release windows**: pick one or two slots a day where the team is alert and dependencies are stable
- **Pair on releases**: one person drives, one watches metrics
- **Practice rollbacks** in staging, including reverting a migration — first time should never be in prod
- **Automate the boring parts**: tag → deploy → smoke test should be one command, not ten manual steps
- **Track release outcomes**: which releases needed rollback, which had no incident — patterns emerge

## References

- [Google SRE Workbook — Canarying Releases](https://sre.google/workbook/canarying-releases/)
- [Continuous Delivery (Humble & Farley)](https://continuousdelivery.com/) — the canonical text
- [DORA metrics](https://dora.dev/research/) — deployment frequency, lead time, change failure rate, MTTR
