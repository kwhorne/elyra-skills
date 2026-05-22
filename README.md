<div align="center">

# Elyra Skills

**Community-maintained registry of [Agent Skills](https://agentskills.io) for coding agents.**

Standalone, vendor-neutral workflows the agent loads on demand — code review, debugging, conventional commits, refactoring, API design, and more.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Spec: Agent Skills](https://img.shields.io/badge/spec-Agent%20Skills-8A2BE2)](https://agentskills.io)
[![Works with: Elyra](https://img.shields.io/badge/works%20with-Elyra-000)](https://github.com/kwhorne/elyra)
[![Works with: Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-D97757)](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Catalog](#-catalog) · [Install](#-install) · [Anatomy of a skill](#-anatomy-of-a-skill) · [Contributing](CONTRIBUTING.md) · [Docs](https://elyracode.com) · [Spec](https://agentskills.io)

</div>

---

## ✨ Why a skills registry?

Coding agents are most useful when they apply the *right* domain knowledge at the *right* moment. **Skills** are small Markdown files with frontmatter that the agent reads on demand — only when the task matches the skill's description. No bloated system prompt, no manual configuration per project.

This repo is a community pool of skills that:

- 🧩 **Are standalone** — generic workflows, no tie-in to a specific extension, package, or framework
- 🌍 **Are portable** — follow the [Anthropic Agent Skills spec](https://agentskills.io), so they work in Elyra, Claude Code, and any other compatible agent
- 🛡️ **Are safe** — every skill is plain Markdown (plus optional read-only scripts) and is reviewed before merge
- 📦 **Are versioned together** — one place to browse, install, and update

> **Not in scope:** stack-specific skills (Laravel, Vue, Filament, Docker, etc.) — those live in their respective Elyra extensions where they ship pre-installed.

---

## 📚 Catalog

| Skill | What it does |
|---|---|
| [`code-review`](skills/code-review/) | Structured review with severity-tagged feedback (blocker / major / minor / nit) |
| [`conventional-commits`](skills/conventional-commits/) | Generate [Conventional Commits](https://www.conventionalcommits.org) messages from staged changes |
| [`debugging`](skills/debugging/) | Systematic debugging loop: reproduce → isolate → fix → verify → prevent regression |
| [`pr-description`](skills/pr-description/) | Write clear, scannable pull-request descriptions from a diff |
| [`refactoring`](skills/refactoring/) | Safe refactoring: characterization tests first, small reversible steps |
| [`test-writing`](skills/test-writing/) | Decide what to test, structure tests with arrange/act/assert, avoid common pitfalls |
| [`api-design`](skills/api-design/) | Design consistent HTTP/REST endpoints: naming, status codes, pagination, errors |
| [`security-audit`](skills/security-audit/) | OWASP-flavored review focused on input handling, auth, secrets, and dependencies |

The full machine-readable index is in [`registry.json`](registry.json). It's what `/skills install` uses to resolve names → URLs.

---

## 🚀 Install

### Option 1 — Elyra slash command *(recommended)*

```text
/skills install code-review
```

This fetches the skill into `~/.elyra/agent/skills/<name>/` and makes it available in every project. List installed skills with `/skills`.

To install several at once:

```text
/skills install code-review debugging conventional-commits
```

### Option 2 — Clone the whole registry

Best if you want to browse, modify, or contribute back:

```bash
git clone https://github.com/kwhorne/elyra-skills ~/code/elyra-skills

# Symlink the ones you want into your agent skills dir
mkdir -p ~/.elyra/agent/skills
ln -s ~/code/elyra-skills/skills/code-review ~/.elyra/agent/skills/code-review
```

### Option 3 — Single skill via sparse checkout

```bash
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/kwhorne/elyra-skills /tmp/elyra-skills
cd /tmp/elyra-skills
git sparse-checkout set skills/debugging
cp -r skills/debugging ~/.elyra/agent/skills/
```

### Option 4 — Project-local

Want a skill available **only** in one project (e.g. committed alongside the code)? Drop it under `.elyra/skills/`:

```bash
mkdir -p .elyra/skills
cp -r path/to/skills/code-review .elyra/skills/
git add .elyra/skills/code-review
```

### Where skills live

| Location | Scope | Use when |
|---|---|---|
| `~/.elyra/agent/skills/<name>/` | Global, every project | Personal workflows you want everywhere |
| `.elyra/skills/<name>/` | Project-local, committed | Team conventions, project-specific rules |
| *(bundled in an Elyra extension)* | Auto-loaded with the extension | Maintainer-owned, shipped together |

Elyra automatically discovers all three locations on startup. Use `/skills` to see what's currently loaded and where it came from. Full setup guide: **[elyracode.com](https://elyracode.com)**.

---

## 🧬 Anatomy of a skill

A skill is a directory with a `SKILL.md` and optional helpers:

```text
skills/code-review/
├── SKILL.md              ← required, read by the agent
├── scripts/              ← optional, executable helpers
│   └── checklist.sh
└── references/           ← optional, long-form docs the agent can read on demand
    └── severity-rubric.md
```

The `SKILL.md` itself is YAML frontmatter + Markdown body:

```markdown
---
name: code-review
description: Perform a structured code review with severity-tagged feedback. Use when the user asks for a code review, PR feedback, or wants to evaluate a diff before merge.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, edit
metadata:
  author: jane-doe
  version: 1.0.0
  tags: [review, quality]
---

# Code Review

## When to use
…

## Procedure
1. …
2. …
```

### Frontmatter fields

| Field | Required | Notes |
|---|---|---|
| `name` | yes | Lowercase, hyphens, ≤64 chars. Must match the folder name. |
| `description` | yes | ≤1024 chars. **The agent uses this to decide whether to load the skill** — start with *what it does* and *when to use it*. |
| `license` | recommended | SPDX identifier (`MIT`, `Apache-2.0`, …). Falls back to the repo license. |
| `compatibility` | optional | Free-form list of agents/versions the skill targets. |
| `allowed-tools` | optional | Comma-separated tool whitelist the agent should respect inside the skill. |
| `metadata` | optional | Free-form object: author, version, tags, links. |
| `disable-model-invocation` | optional | If `true`, the skill is hidden from the prompt and only runs via explicit `/skill:<name>`. |

### How the agent uses it

1. On startup, Elyra scans every skills directory and parses each `SKILL.md`.
2. The `name` + `description` of every skill is injected into the system prompt as an `<available_skills>` index.
3. When your task matches a description, the agent reads the full `SKILL.md` via the `read` tool.
4. If the skill has `scripts/` or `references/`, those paths are exposed in the same index so the agent can run or read them as needed.
5. `/skills` in the TUI shows every loaded skill with name, description, script/reference counts, and source.

For a deeper dive — how skills interact with extensions, prompt templates, and the SDK — see the official docs at **[elyracode.com](https://elyracode.com)**.

---

## 🤝 Contributing

We love new skills. Check [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide. Quick rules:

- **One skill per PR**, in its own folder under `skills/`
- **Standalone & generic** — no extension, framework, or vendor lock-in (those belong in stack-specific Elyra extensions)
- **Folder name == `name`** in frontmatter, lowercase + hyphens, ≤64 chars
- **Description leads with purpose + trigger** — that's what the agent matches against
- **Test it locally** before opening a PR (symlink into `~/.elyra/agent/skills/` and try the trigger)
- **Update [`registry.json`](registry.json) and the catalog table** in this README
- **MIT-compatible license** required

Good first contributions: skill stubs for areas not yet covered (e.g. `accessibility-review`, `performance-budget`, `dependency-update`).

---

## ❓ FAQ

**How is this different from a prompt template?**
A prompt template is a one-shot text you invoke (`/prompt name`). A skill is *passive* — the agent loads it automatically when your task matches its description, then keeps the instructions in context for as long as relevant.

**How is this different from an Elyra extension?**
Extensions are npm packages that can ship tools, commands, themes, prompt templates, **and** skills. This registry only hosts skills, in plain Markdown, with no install step or runtime code. Use the registry for portable, agent-agnostic workflows; use extensions when you need executable tools or tight integration.

**Can I use these outside Elyra?**
Yes. Every skill follows the [Agent Skills spec](https://agentskills.io), so any compatible agent (Claude Code, etc.) can load them. The `/skills install` command is Elyra-specific; everywhere else, copy the folder into whatever path your agent scans.

**Does the agent read the whole skill all the time?**
No. Only the `name` + `description` are always in context. The body is loaded on demand when the task matches, which keeps token usage low even with many skills installed.

**Are scripts safe?**
Scripts are not auto-executed. The agent can choose to run them via its `bash` tool, subject to the same approval rules as any other command. Skills that ship scripts must document what they do; we review every one before merge.

---

## 🔗 Related

- 📖 **[elyracode.com](https://elyracode.com)** — full Elyra documentation: install, configuration, extensions, skills, themes, SDK
- [Elyra on GitHub](https://github.com/kwhorne/elyra) — the coding agent these skills are built for
- [Agent Skills spec](https://agentskills.io) — the format we follow
- [Anthropic Agent Skills docs](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)

---

## 📜 License

[MIT](LICENSE). Individual skills may declare their own `license` in frontmatter; the repo license applies when none is set.
