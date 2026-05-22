---
name: incident-response
description: Work through a production incident calmly - triage severity, mitigate first, communicate clearly, then root-cause and document. Use when the user reports prod is down, an outage is in progress, a degraded service, or asks for help during/after an incident.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [incident, sre, ops, postmortem]
---

# Incident Response

When prod is broken, the priorities are **stop the bleeding → communicate → understand → prevent**. In that order. Root-causing while users are down is the wrong order.

## When to use

- "Prod is down"
- "Site is slow / 500-ing / not loading"
- "We're having an incident"
- "Help me write the postmortem"
- "Triage this alert"

## The phases

```
Detect  →  Triage  →  Mitigate  →  Communicate  →  Resolve  →  Review
```

Phases overlap during a real incident; the sequence is for priorities, not gating.

### 1. Detect

Confirm there *is* an incident. False alarms cost trust and sleep.

- Reproduce the symptom (try the broken path yourself)
- Check your status dashboard, error tracker, APM
- Verify dependencies (third-party status pages: providers, CDN, DNS, payments)

### 2. Triage — assign a severity

| Severity | Meaning | Response |
|---|---|---|
| **SEV-1** | Full outage or data loss affecting most users | Page on-call, all hands, public comms |
| **SEV-2** | Major feature broken, significant user impact | On-call leads, user comms within 30 min |
| **SEV-3** | Degraded experience or impacting some users | Normal hours fix, internal comms |
| **SEV-4** | Minor issue, workaround available | Ticket, fix in normal cycle |

Pick higher when in doubt. Downgrading is free; upgrading later looks bad.

### 3. Mitigate first, understand later

**The goal in the first 15 minutes is to make users stop hurting**, not to understand why.

| If you can… | Do |
|---|---|
| Roll back the last deploy | Roll back. Now. Root-cause from the rolled-back diff. |
| Flip a feature flag | Flip it off |
| Failover to a healthy region | Failover |
| Scale up / restart degraded service | Do it (capture state first if possible) |
| Block a bad request pattern at the edge | WAF/rate-limit rule |

Investigate only what's needed to choose a mitigation. **Don't fix forward** unless rollback is impossible.

### 4. Communicate

Silence = panic. Communicate even when there's nothing new.

**Internal (chat channel):**
```
🚨 SEV-1 declared: <one-line summary>
Incident commander: @<person>
Comms lead: @<person>
Channel: #incident-<date>
Status page: <link>
Updates every 15 min until resolved.
```

**External (status page / Twitter / customer email):**
```
[Investigating] We are aware of an issue affecting <feature>.
Started: <time UTC>
Impact: <who and how>
We'll post an update within 30 minutes.
```

**Update cadence:**
- SEV-1: every 15 min, even if "still investigating"
- SEV-2: every 30 min
- SEV-3: every hour

Status template progression: `Investigating → Identified → Monitoring → Resolved`.

### 5. Resolve

Mitigation worked → users are okay. But you're not done.

- Confirm metrics are back to normal (don't just trust the mitigation)
- Update the incident channel: `[Resolved] <summary>`
- Update the status page
- **Keep the incident channel open** for the postmortem prep

### 6. Review (postmortem / incident review)

Within **5 business days** of resolution. Blameless — focus on systems, not people.

## During the incident: roles

For SEV-1/2, name explicit roles. Even on a small team, roles prevent the chaos of "everyone debugging at once."

| Role | Owns |
|---|---|
| **Incident Commander (IC)** | Coordinates, makes decisions, declares resolved. *Doesn't debug.* |
| **Comms Lead** | Internal + external updates. Updates status page. |
| **Tech Lead / Investigator** | Actual debugging and mitigation |
| **Scribe** (optional) | Timeline of what happened and when, for the postmortem |

On a 2-person team, one person is IC+Comms, the other is Investigator. Switching roles mid-incident is fine; everyone knowing who's IC at any moment is not optional.

## Useful in-flight commands

```bash
# Quick service health
curl -sw '\nstatus=%{http_code} time=%{time_total}s\n' -o /dev/null https://example.com/health

# Recent deploys (adjust per setup)
git log --oneline --since='2 hours ago' --all
kubectl rollout history deploy/<name>

# Quick rollback
kubectl rollout undo deploy/<name>
# or
git revert <bad-commit> && git push  # if CD watches main

# Error spike — log greps for the obvious
kubectl logs deploy/<name> --since=15m | grep -iE 'error|panic|fatal' | sort | uniq -c | sort -rn | head

# Database — long-running queries
# psql:    SELECT pid, age(clock_timestamp(), query_start), state, query FROM pg_stat_activity WHERE state != 'idle' ORDER BY 2 DESC LIMIT 10;
# mysql:   SHOW FULL PROCESSLIST;

# Connection count / resource exhaustion
ss -tan | awk '{print $1}' | sort | uniq -c
df -h
free -h
```

## Postmortem template

Write it in a shared doc. **Blameless.** Names of services, not people.

```markdown
# Incident <id>: <one-line title>

**Date:** <YYYY-MM-DD>
**Duration:** <start UTC> → <end UTC> (<n> minutes)
**Severity:** SEV-<n>
**Impact:** <user-visible impact: which users, what they saw, how many>
**Detected by:** <alert / user report / synthetic / dashboard>

## Summary
One paragraph. Lay-reader friendly.

## Timeline (UTC)
- HH:MM — <event>
- HH:MM — <event>
- HH:MM — alert fired
- HH:MM — incident declared SEV-<n>, IC @<person>
- HH:MM — mitigation applied: <what>
- HH:MM — metrics recovered
- HH:MM — incident resolved

## Root cause
What actually caused this. Often a chain: trigger + latent bug + missing guardrail.

## What went well
- …

## What went poorly
- …

## What we got lucky on
- The things that, if slightly different, would have made this much worse.

## Action items
| Item | Owner | Due | Type |
|---|---|---|---|
| <concrete action> | @owner | YYYY-MM-DD | prevent / detect / mitigate |

Each action item should be **assignable, scheduleable, and verifiable**. "Be more careful" is not an action item.
```

## Anti-patterns

- ❌ Root-causing before mitigating — users are still down while you "understand"
- ❌ Going silent for 45 minutes because there's no news
- ❌ "It's working again, let's skip the postmortem"
- ❌ Naming people as root causes — name the missing guardrail that allowed the mistake
- ❌ Vague action items ("improve monitoring") — make them specific and owned
- ❌ Closing the postmortem without assigning the actions
- ❌ Fix-forward when rollback would work — slower and riskier
- ❌ Heroic solo debugging during SEV-1 — call for help, name an IC

## Tips

- **Pre-write your status page templates** so you're filling blanks under pressure, not composing
- **Practice rollbacks** in non-prod regularly. The first time you roll back should not be during a real outage.
- **Runbooks for top alerts** beat heroics — when the on-call has a checklist, they don't have to be the smartest person on the team
- **Track MTTD / MTTA / MTTR** (detect / acknowledge / resolve) over time
- **Read other companies' postmortems** ([sre.google](https://sre.google/), GitHub, Cloudflare, Honeycomb, AWS, Heroku archives) — pattern-matching saves time during real ones

## References

- [Google SRE Book — Managing Incidents](https://sre.google/sre-book/managing-incidents/)
- [PagerDuty Incident Response Docs](https://response.pagerduty.com/)
- [Atlassian Incident Handbook](https://www.atlassian.com/incident-management/handbook)
- [Etsy Debriefing Facilitation Guide](https://extfiles.etsy.com/DebriefingFacilitationGuide.pdf) — gold standard for blameless reviews
