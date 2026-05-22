---
name: code-review
description: Perform a structured code review with severity-tagged feedback. Use when the user asks for a code review, PR feedback, evaluating a diff before merge, or wants a second opinion on a change.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [review, quality]
---

# Code Review

Reviews code with **actionable**, **severity-tagged** feedback. No vibes, no rubber-stamping, no nitpicking everything to death.

## When to use

- "Review this PR / branch / diff"
- "What do you think of this code?"
- "Is this ready to merge?"
- "Find issues in `src/...`"

## Procedure

1. **Establish scope.** What are you reviewing — a diff (`git diff main...HEAD`), a file, a directory, or a PR? If unclear, ask once.
2. **Read the code in context.** Open imports, callers, and tests. A review without context is just spell-checking.
3. **Run through the checklist** below, taking notes per finding.
4. **Group findings by severity** and emit the report (see Output format).
5. **Stop when done.** Don't pad the report with "nits" that aren't actually issues.

## Review checklist

- **Correctness** — does it do what it claims? Off-by-one, null/undefined, error paths, race conditions, async/await misuse
- **Tests** — are the new paths covered? Are existing tests updated? Any tests asserting on implementation rather than behavior?
- **API & contracts** — backward compatibility, error shapes, status codes, naming consistency with rest of codebase
- **Security** — input validation, SQL/command injection, auth/authz checks, secret handling, dependency choices
- **Performance** — obvious N+1, unbounded loops, sync I/O on hot paths, large allocations
- **Readability** — naming, function size, nesting depth, dead code, commented-out blocks
- **Consistency** — does it match patterns already used in this codebase? Different ≠ wrong, but flag it.

## Output format

Use this exact shape:

```markdown
## Review: <scope>

**Summary:** one or two sentences — overall assessment + recommendation (approve / request changes / needs discussion).

### 🔴 Blockers
- `path/to/file.ts:42` — <finding>. <why it matters>. <suggested fix>.

### 🟠 Major
- `path/to/file.ts:88` — …

### 🟡 Minor
- `path/to/file.ts:120` — …

### 💭 Questions
- About `path/to/file.ts:200` — …

### ✅ What's good
- One or two genuine positives. Skip if there are none — don't manufacture praise.
```

### Severity rubric

| Tag | Meaning |
|---|---|
| 🔴 **Blocker** | Bug, security issue, data loss risk, broken contract. Must fix before merge. |
| 🟠 **Major** | Likely bug, significant design issue, missing tests for new behavior. Should fix before merge. |
| 🟡 **Minor** | Style, naming, small refactor. Can be a follow-up. |
| 💭 **Question** | You don't understand intent. Ask before assuming. |

## Anti-patterns

- ❌ Listing every nit you can find. Pick what matters.
- ❌ "Consider using X instead of Y" without saying *why*.
- ❌ Reviewing only the diff when the bug is in code the diff *calls*.
- ❌ Restating what the code does without judgment ("this function adds two numbers").
- ❌ Pretending you're sure when you're not — use 💭 Question.

## Tips

- For diffs: `git diff <base>...HEAD --stat` first to see scope, then dig into the meaty files.
- For unfamiliar codebases: read the tests first. They tell you what the code is *supposed* to do.
- If the diff is huge (>500 lines), say so up front and review in layers (architecture → correctness → details).
