# Security Policy

Skills in this registry are read by AI agents and acted on. Bad content here has real impact, so we take security reports seriously and ship fixes quickly.

## What counts as a security issue

Please report **privately** if you find any of:

- A `scripts/*` file that does something destructive, exfiltrates data, or runs untrusted code
- A skill recommending a command that could cause data loss, unauthorized access, or credential leakage if followed literally
- Hardcoded secrets, API keys, credentials, or private keys in any file
- A skill that instructs the agent to disable safety mechanisms (auth, audit, rate-limiting) without proper context
- Malicious instructions hidden in a skill that attempt prompt injection against the calling agent
- Any vulnerability in `scripts/validate.py` or the CI workflow that could be exploited by a PR

**Not security issues** — file these as regular [issues](https://github.com/kwhorne/elyra-skills/issues/new/choose):

- A skill has wrong or outdated advice → [bug template](https://github.com/kwhorne/elyra-skills/issues/new?template=skill-bug.yml)
- A skill could be clearer or more complete → [improvement template](https://github.com/kwhorne/elyra-skills/issues/new?template=improvement.yml)
- A typo or formatting issue → open a PR

## How to report

**Don't open a public issue.** Use one of these instead, in order of preference:

1. **GitHub Security Advisories** — [Report a vulnerability](https://github.com/kwhorne/elyra-skills/security/advisories/new) (preferred; private, threaded, lets us issue a CVE if warranted)
2. **Email** — security@elyracode.com with subject `[elyra-skills] <short summary>`

Include:

- Which file(s) or skill(s) are affected
- A description of the impact (what could an attacker / careless agent do)
- A minimal reproduction (the exact command, prompt, or input that triggers it)
- Suggested fix if you have one
- Whether you'd like credit in the fix announcement (and how to credit you)

## What happens next

| Step | Timeline |
|---|---|
| Acknowledgement | Within **3 business days** |
| Initial assessment (severity, scope, reproducibility) | Within **7 days** |
| Fix or mitigation in `main` | As soon as practical; critical issues within 7 days |
| Public disclosure | Coordinated with reporter, typically after fix is merged |

We'll keep you updated through the advisory thread or email. If you don't hear back within the acknowledgement window, please ping again — the message may have been missed.

## Scope

This policy covers:

- The contents of this repository (`skills/`, `scripts/`, workflows, schemas)
- The `registry.json` index used by `/skills install`

It does **not** cover:

- Elyra itself (the coding agent) — report at [github.com/kwhorne/elyra/security](https://github.com/kwhorne/elyra/security)
- Third-party tools or libraries referenced by skills (report to those projects)
- The semantic correctness of advice that isn't *dangerous* (use the bug template)

## Safe-harbor

Good-faith security research is welcome. If you:

- Make a reasonable effort to avoid privacy violations, data destruction, and service degradation while researching
- Give us a reasonable opportunity to fix before disclosure
- Don't exploit the issue beyond what's necessary to demonstrate it

…we will not pursue legal action and will publicly credit your contribution (with your permission).

## Hall of fame

Reporters who have helped improve security of this registry will be acknowledged here.

*(empty — be the first)*
