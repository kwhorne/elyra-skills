---
name: cost-optimization
description: Review cloud/infrastructure spend and propose specific cost reductions without sacrificing reliability - sized instances, storage tiers, idle resources, data egress, observability spend. Use when the user asks for cost review, FinOps audit, cloud bill investigation, or wants to reduce infra spend.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [cost, finops, cloud, optimization]
---

# Cost Optimization

The goal: **find spend that nobody would defend if asked, and stop it.** Most cloud waste isn't from anything clever — it's from things nobody is looking at.

## When to use

- "Why is our AWS / GCP / Azure bill so high?"
- "Reduce infra costs"
- "Review cloud spend"
- "Cost optimization for X"
- "Where's the money going?"

## Principles

1. **You can't optimize what you can't see.** Get visibility before cutting.
2. **Cut waste before optimizing fit.** Idle resources beat right-sized resources.
3. **Don't sacrifice reliability or developer productivity** to save money on coffee-budget items.
4. **Engineer hours cost more than most infra**. A 3-week optimization saving $200/month is a bad trade.
5. **Tag everything.** Untagged spend is unaccountable spend.

## Procedure

1. **Get the breakdown** — by service, by environment, by team if tagged
2. **Identify the top 5 line items** — typically 80% of the bill
3. **For each top line item**, walk the relevant section below
4. **Quantify savings** before recommending (rough is fine; "save 30%" with a number behind it)
5. **Order by ROI**: $/month saved ÷ engineer-hours to do it

## The big buckets

### 1. Idle and forgotten resources

The single biggest source of waste, almost always.

- **Unattached storage volumes** (EBS, persistent disks) from terminated instances
- **Old snapshots** with no retention policy
- **Unassociated elastic IPs** charged hourly
- **Idle load balancers** (created for an experiment, never deleted)
- **Stopped instances still incurring storage / IP cost**
- **Test/staging environments running 24/7** when no one's testing
- **Forgotten dev environments** from former employees
- **Database instances at zero queries/day**
- **Logs / metrics retained forever** at hot-tier pricing

**Action:** weekly automated report of resources with low/no utilization > 30 days. Default action: delete after a 7-day grace period with owner notification.

### 2. Right-sizing

- Instances at <20% sustained CPU → downsize one step
- Instances at <40% memory → downsize or change family
- Over-provisioned databases (look at connections, IOPS, CPU)
- Over-provisioned Kubernetes requests/limits → use VPA or examine actuals
- "Burstable" workloads on always-on instances

**Watch for**: noisy neighbors on shared tiers, head-room needed for spikes, fast-recovery requirements. Don't right-size below your recovery requirements.

### 3. Storage tiering

| Tier | Use for | Relative cost |
|---|---|---|
| Hot (SSD, S3 Standard) | Active data, <30 days old | 1x |
| Warm (S3 IA, similar) | Accessed monthly | ~0.5x |
| Cold (S3 Glacier, Archive) | Compliance, rarely accessed | ~0.1x |
| Delete | Past retention period | 0 |

- [ ] Lifecycle policies move objects to colder tiers automatically
- [ ] Old objects past retention are deleted, not archived forever
- [ ] Log retention configured per signal (debug < info < audit)
- [ ] Backups: retention matches actual recovery requirements, not "forever"

### 4. Data transfer / egress

The line item most people miss. Egress to internet, cross-region, and cross-AZ are often pricier than the storage itself.

- [ ] Audit egress in cost report — by service if possible
- [ ] Co-locate chatty services in same AZ
- [ ] CDN in front of static assets (cheaper egress than direct from origin)
- [ ] Compression on responses
- [ ] Avoid cross-region replication unless you need it
- [ ] Watch egress to S3 from outside the region

### 5. Compute pricing model

| Model | When to use | Typical savings |
|---|---|---|
| **On-demand** | Spiky workloads, dev/test | 0% (baseline) |
| **Savings plans / reserved (1y)** | Steady-state workloads you know you'll need | 25–40% |
| **Savings plans / reserved (3y)** | Very steady, long-term | 40–60% |
| **Spot / preemptible** | Interruptible: batch, build, ML training, stateless web behind LB | 60–90% |

**Don't commit before you have ≥3 months of steady-state usage data.** Over-commitment is worse than no commitment.

### 6. Observability spend

Logs, metrics, traces, and APM are commonly the #2 line item after compute.

- [ ] Audit log volume per service — top emitters often have one verbose path
- [ ] Reduce log levels in prod (`debug` off; `info` lean)
- [ ] Drop noisy log lines at the agent before they hit ingest
- [ ] Sample traces (head + tail) instead of 100% retention
- [ ] Drop high-cardinality metric dimensions (`user_id` in tags = explosion)
- [ ] Shorten retention on debug logs, keep audit logs longer
- [ ] Many vendors charge for *unique* metric series — kill unused ones

A halving of observability spend often saves more than a year of right-sizing. Check it.

### 7. Databases

- Stopped/idle non-prod databases
- Aurora I/O optimized vs standard — depends on workload, run the math
- Read replicas you stopped reading from
- Multi-AZ on non-prod environments
- Backup retention longer than needed
- Storage auto-scaling that grew once and never shrank

### 8. Kubernetes specifics

- Over-provisioned resource requests starve the bin-packer
- Cluster autoscaler not enabled or too conservative
- HPA / VPA tuned for the workload
- Node group families matching workload shape
- Unused PVCs from deleted pods
- Out-of-cluster ELBs from old Services

### 9. SaaS / per-seat tools

- Inactive seats on per-seat licenses (CI, observability, vendor portals)
- Tier downgrade where lower tier covers actual usage
- Renewal date awareness — negotiate before, not after

### 10. Build / CI minutes

- Caching layers (Docker layer, dependency caches) configured correctly
- Parallelism vs total minutes — sometimes serial is cheaper
- Self-hosted runners for high-volume orgs
- Kill obviously stuck jobs after a timeout

## Quantifying before recommending

For each finding:

```markdown
- **Finding**: <what's wasteful>
- **Current cost**: $<n>/month (source: <line item / query>)
- **Proposed change**: <what>
- **Estimated savings**: $<n>/month
- **Effort**: <hours/days>
- **Risk**: <low/medium/high + what could go wrong>
```

Without numbers, "we could save money by …" is unfalsifiable.

## Tagging

Untagged resources can't be attributed. Set this up if it isn't:

| Tag | Why |
|---|---|
| `env` | prod / staging / dev — usually the biggest split |
| `team` or `owner` | accountability |
| `service` or `app` | per-service cost |
| `cost-center` | finance reporting |

Enforce via cloud policy: untagged resources can't be created (or are flagged within 24h).

## Output format

```markdown
## Cost review: <scope, e.g., AWS account / GCP project>

**Monthly spend (last 3 mo trend):** $X → $Y → $Z
**Top 5 line items:**
1. EC2 — $A (B%)
2. RDS — $C (D%)
3. Datadog — $E (F%)
4. S3 — $G (H%)
5. Data transfer — $I (J%)

### Findings (ordered by ROI)

#### 🟢 Quick wins (low risk, low effort)
- **Unused EBS volumes**: $480/month, 2 hrs effort, low risk
- **Forgotten staging RDS**: $320/month, 1 hr effort, low risk

#### 🟡 Medium (some effort or coordination)
- **Right-size 12 EC2 instances**: ~$1,200/month, 2 days effort
- **Datadog log volume**: drop debug logs from svc-x, $800/month, 1 day

#### 🟠 Larger (commitment or design change)
- **3-year savings plan for steady-state**: ~$2,400/month after evaluation period

### Estimated total monthly savings if all implemented: $<n> (<%> of bill)

### Not recommended (with reason)
- Switching all to spot: too much state in our workloads
- Reducing backup retention: against compliance policy

### Tagging gaps
- <%> of compute untagged — fix before further cost work
```

## Anti-patterns

- ❌ "Move to a cheaper cloud" — almost always more expensive than fixing waste
- ❌ Cutting reliability for cost (removing replicas, disabling backups)
- ❌ Cost-optimizing dev productivity (slow CI, throttled prod-like staging)
- ❌ Big commitment plans before you know steady-state
- ❌ Over-engineering for cost ("we'll write our own S3")
- ❌ One person's pet optimization that saves $50/month
- ❌ Buying observability and then not using it ("we'll grow into it")
- ❌ Killing resources without notifying owners — political damage exceeds savings
- ❌ Recommending without numbers
- ❌ Ignoring the human cost (engineer hours) of optimizations

## Tips

- **Cost anomaly alerts** beat monthly reviews — catch a runaway cost on day 2, not day 30
- **Show, don't tell**: a shared dashboard of monthly spend by team beats a memo
- **Get a "delete after 7 days" tag** working for ad-hoc resources
- **Rerun the audit quarterly** — waste regrows
- **Engineer time has a cost** — optimize the bill items that don't require ongoing engineer attention first
- **Talk to your account manager** — sometimes the cheapest optimization is a phone call

## References

- [FinOps Foundation](https://www.finops.org/) — vendor-neutral framework
- [AWS Well-Architected Cost Optimization Pillar](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html)
- [Google Cloud Cost Optimization](https://cloud.google.com/architecture/framework/cost-optimization)
- [Azure Cost Management best practices](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/cost-mgt-best-practices)
