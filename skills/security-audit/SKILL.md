---
name: security-audit
description: Perform an OWASP-flavored security review focused on input handling, authentication, authorization, secrets, and dependencies. Use when the user asks for a security audit, threat review, vulnerability check, or wants to harden code before release.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [security, review, owasp]
---

# Security Audit

A pragmatic, OWASP-flavored review. The goal is **finding real risks**, not generating a checklist that nobody acts on.

## When to use

- "Audit X for security issues"
- "Review this code for vulnerabilities"
- "Is this safe to deploy?"
- "Harden the auth flow"
- "Check for secrets / OWASP issues"

## Scope this first

Security is infinite; your time is not. Ask:

- **What are you protecting?** Data (PII, payments, secrets)? Availability? Integrity?
- **Who's the threat model?** Anonymous internet, authenticated users, malicious insiders, supply chain?
- **What's in scope this round?** Whole repo, one module, the auth surface, the public API?

If the user can't answer, suggest starting with **the public attack surface** (anything reachable without auth) and **secret handling**.

## Procedure

1. **Inventory the attack surface** — public endpoints, file uploads, deserialization points, command/SQL/template execution, third-party callbacks
2. **Walk the checklist** below, category by category
3. **For each finding**: confirm it's exploitable (or be honest that it's theoretical), estimate severity, propose a fix
4. **Report by severity** (see Output format)

## Checklist

### Input handling

- [ ] Every external input has explicit validation (type, length, range, format)
- [ ] User input never built into SQL via string concat → parameterized queries only
- [ ] User input never passed to `eval`, `exec`, `Function()`, `system()`, shell, deserializer
- [ ] Path inputs are normalized and checked against a base directory (no `../` traversal)
- [ ] Uploaded files: type checked by content, not extension; stored outside web root; size-limited; renamed
- [ ] Rendered output is context-correctly escaped (HTML / JS / URL / SQL / shell each need their own escaper)
- [ ] No regex with catastrophic backtracking on user input (ReDoS)
- [ ] XML/YAML parsers disable external entities and unsafe loaders

### AuthN (authentication)

- [ ] Passwords hashed with `argon2`, `bcrypt`, or `scrypt` — never MD5/SHA1/SHA256-only
- [ ] Login is rate-limited and lockout/back-off is implemented
- [ ] Session tokens are long, random, server-side invalidatable
- [ ] Cookies: `HttpOnly`, `Secure`, `SameSite=Lax` or `Strict`
- [ ] Password reset tokens are single-use, short-lived, and tied to user + email
- [ ] MFA available for sensitive accounts
- [ ] Logout actually invalidates the session server-side

### AuthZ (authorization)

- [ ] Every endpoint checks "is this user allowed to do this to this resource?"
- [ ] No relying on hidden fields / client-supplied IDs / `referer` headers for permissions
- [ ] Object-level authorization (IDOR) checked: `GET /orders/42` verifies 42 belongs to the caller
- [ ] Admin-only actions checked on server, not just hidden in UI
- [ ] Multi-tenant boundaries enforced in every query

### Secrets

- [ ] No secrets in source, history, CI logs, error responses, or client bundles
- [ ] Secrets loaded from env / secret manager / vault — not files in the repo
- [ ] `.env`, `.pem`, key material in `.gitignore`
- [ ] Rotate-able: nothing baked in at build time that can't be changed
- [ ] Quick scan: `git log -p -S 'BEGIN PRIVATE KEY'`, `grep -RIn 'api[_-]\?key\|secret\|password' .`

### Transport & headers

- [ ] HTTPS enforced (redirect from HTTP, HSTS header)
- [ ] CORS configured intentionally (no `Access-Control-Allow-Origin: *` for credentialed APIs)
- [ ] `Content-Security-Policy` set
- [ ] `X-Frame-Options` or CSP `frame-ancestors`
- [ ] `Referrer-Policy: strict-origin-when-cross-origin` or stricter

### CSRF / SSRF

- [ ] State-changing requests require CSRF token *or* are `SameSite` + auth-header-based
- [ ] Outbound requests to user-supplied URLs are blocked from internal ranges (169.254, 127.0.0.0/8, 10/8, 192.168/16, ::1) and metadata endpoints (`169.254.169.254`)

### Dependencies & supply chain

- [ ] Lockfile committed
- [ ] Audit tool run cleanly: `npm audit`, `pnpm audit`, `composer audit`, `pip-audit`, `cargo audit`, `bundle audit`
- [ ] No abandoned/unmaintained critical deps
- [ ] CI/build secrets scoped (no admin-level GitHub tokens in PR builds from forks)
- [ ] Pinned third-party CDN scripts use SRI

### Logging & errors

- [ ] No secrets, passwords, tokens, or PII in logs
- [ ] No stack traces leaked to end users in production
- [ ] Errors return generic messages externally, full detail internally
- [ ] Audit log for sensitive actions (login, role change, payment, deletion)

### Data

- [ ] PII encrypted at rest where regulation requires
- [ ] Backups exist and have been restored at least once
- [ ] Deletes are real deletes (or documented soft-delete with retention policy)
- [ ] Database access uses least-privilege accounts (the app doesn't connect as DB owner)

## Quick scans to run

```bash
# Hardcoded secrets (rough)
grep -RInE '(api[_-]?key|secret|password|token)\s*[:=]\s*["'\''][^"'\'']{6,}' \
  --include='*.{js,ts,jsx,tsx,php,py,rb,go,rs,java,kt,yml,yaml,env}' .

# Private key material
grep -RIn 'BEGIN .* PRIVATE KEY' .

# Eval-like primitives
grep -RInE '\b(eval|exec|Function|setTimeout|setInterval)\s*\(' --include='*.{js,ts}' .

# Raw SQL concatenation (heuristic, lots of false positives)
grep -RInE 'SELECT .*\+ .*\bFROM|"\s*\+\s*\$|f"SELECT.*\{' .

# Dependency audit (pick what applies)
npm audit --omit=dev || pnpm audit || composer audit || pip-audit || cargo audit
```

Treat all greps as *leads*, not verdicts.

## Severity rubric

| Tag | Meaning |
|---|---|
| 🔴 **Critical** | Remote exploit possible by unauthenticated user; data loss; account takeover. Fix before next deploy. |
| 🟠 **High** | Exploit possible by authenticated user, or critical with significant preconditions. Fix this sprint. |
| 🟡 **Medium** | Defense-in-depth gap, hardening recommendation, theoretical exploit. |
| 🟢 **Low** | Best-practice nit, not directly exploitable. |
| 💭 **Question** | Looks suspicious but you need more context to be sure. |

## Output format

```markdown
## Security audit: <scope>

**Threat model assumed:** <e.g. "anonymous internet attacker against public API">
**Scanned:** <files / modules / endpoints>

### 🔴 Critical
- `path/to/file.ts:42` — <finding>. **Exploit:** <how>. **Fix:** <what>.

### 🟠 High
- …

### 🟡 Medium
- …

### 🟢 Low
- …

### 💭 Questions
- …

### ✅ Looked at and clean
- <category> — <one sentence on what you verified>
```

## Anti-patterns

- ❌ "Looks fine 👍" — say what you actually checked
- ❌ Crying wolf — marking every finding "critical" devalues real ones
- ❌ Listing CVEs from `npm audit` without checking if the vulnerable path is reachable
- ❌ Recommending `DOMPurify` / `helmet` / a WAF as the *only* fix to an injection bug — fix the root cause too
- ❌ Suggesting custom crypto. Don't.

## Useful references

- [OWASP Top 10](https://owasp.org/Top10/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) — exhaustive checklist
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) — practical, per-topic
