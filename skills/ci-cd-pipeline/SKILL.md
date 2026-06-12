---
name: ci-cd-pipeline
description: Design or review a CI/CD pipeline - stage ordering, quality gates, caching, secrets handling, and deploy strategy. Use when the user asks to set up CI, fix a slow or flaky pipeline, review GitHub Actions/GitLab CI config, add quality gates, or design a deployment workflow.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, edit, write
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [ci, cd, automation, github-actions, deploy]
---

# CI/CD Pipeline

A pipeline has two jobs: **block bad changes** and **ship good ones fast**. Every stage must serve one of those, or it's waste.

## When to use

- "Set up CI for this project" / "add a GitHub Actions workflow"
- "The pipeline is slow / flaky / red all the time"
- Reviewing `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, etc.
- Designing deploys: environments, approvals, rollback

## Principles

- **Fail fast, fail cheap.** Cheapest checks first: lint → types → unit → integration → e2e. A typo shouldn't wait 20 minutes to be reported.
- **Reproduce locally.** Every CI step must be runnable on a dev machine with one command. "Only fails in CI" is a design smell.
- **Flaky = broken.** A test that fails 5% of the time gets quarantined and fixed, not retried forever.
- **The pipeline is code.** Reviewed, versioned, no snowflake config in web UIs.

## Process

### 1. Inventory

- Detect stack and existing config: `ls .github/workflows/ .gitlab-ci.yml Jenkinsfile 2>/dev/null`
- What commands does the project already run locally? (`composer.json`/`package.json` scripts, `Makefile`) — CI should call those, not duplicate them

### 2. Design the stages

```
PR:    lint/format → type-check → unit tests → build → integration/e2e
Merge: all of the above → deploy staging → smoke test
Release: deploy production (gated) → smoke test → monitor window
```

- Stages with no dependency on each other run **in parallel**
- Target: PR feedback < 10 minutes. Past that, people batch changes and quality drops

### 3. Make it fast

- **Cache** dependency installs keyed on lockfile hash; cache build artifacts between jobs
- **Don't rebuild** — build once, pass the artifact to later stages
- Split slow test suites with sharding/parallelism rather than skipping them

### 4. Make it safe

- **Secrets** via the CI provider's secret store — never in YAML, never echoed in logs
- Pin third-party actions/images to a SHA or exact version, not `@latest`
- Least-privilege tokens: a test job doesn't need deploy credentials
- Production deploys: explicit approval gate or protected environment, and a **documented rollback** (previous artifact redeploy, not "fix forward and pray")

### 5. Make it honest

- No `continue-on-error` on quality gates
- No auto-retry as a flakiness blanket — max one retry, with the flake tracked as a bug
- Branch protection: green pipeline required to merge

## Output format

When reviewing or designing, report:

```markdown
## Pipeline: <project>

**Current state:** stages, duration, pain points (or "none — new setup")

### Proposed stages
| Stage | Runs on | Duration target | Gate? |
|-------|---------|-----------------|-------|
| …     | PR      | …               | yes   |

### Changes
1. … (why)

### Risks / follow-ups
- …
```

## Anti-patterns

- ❌ One mega-job running everything serially — no parallelism, no fail-fast
- ❌ CI commands that differ from local commands (drift guaranteed)
- ❌ `retry: 3` as the official fix for flaky tests
- ❌ Deploying from a laptop "just this once"
- ❌ `@latest`/`@main` on third-party actions — supply-chain roulette
- ❌ Secrets interpolated into commands where they leak into logs
- ❌ A red main branch that everyone has learned to ignore
