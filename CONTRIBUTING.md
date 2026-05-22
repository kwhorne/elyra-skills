# Contributing to Elyra Skills

Thanks for wanting to add a skill! This registry lives or dies by community contributions. The bar is "useful, generic, portable" — not "perfect."

Full docs for Elyra (extensions, SDK, themes, skills internals) live at **[elyracode.com](https://elyracode.com)**.

---

## What belongs here

✅ **In scope:**

- Generic workflows that apply across languages and stacks (code review, debugging, refactoring, API design, …)
- Conventions and checklists (commit messages, PR descriptions, changelog entries, …)
- Cross-cutting concerns (security audits, accessibility reviews, performance budgets, …)

❌ **Out of scope** (these belong in stack-specific Elyra extensions instead):

- Framework-specific skills (Laravel, Vue, React, Filament, Django, …)
- Tool-specific skills (Docker, Kubernetes, Terraform, …)
- Skills that require a specific tool/runtime to be installed
- Skills that duplicate functionality already shipped by an Elyra extension

If you're unsure, open an issue first.

---

## Skill structure

```text
skills/<your-skill-name>/
├── SKILL.md              ← required
├── scripts/              ← optional executable helpers
│   └── <name>.sh
└── references/           ← optional long-form docs the agent can read on demand
    └── <name>.md
```

### SKILL.md template

```markdown
---
name: your-skill-name
description: One sentence describing what the skill does and when the agent should use it. The agent only sees this until it decides to load the full skill, so make it count.
license: MIT
compatibility: elyra >=0.1, claude-code
metadata:
  author: your-github-handle
  version: 1.0.0
  tags: [category, another-tag]
---

# Your Skill Name

## When to use

Bullet list of triggers — what the user might be asking for when this skill should kick in.

## Procedure

Numbered steps the agent should follow.

## Output format

What the agent should produce (sections, structure, tone).

## Anti-patterns

What the agent should *not* do.
```

---

## Rules

| # | Rule |
|---|---|
| 1 | Folder name **must equal** the `name` in frontmatter |
| 2 | `name` is lowercase, hyphens only, ≤64 chars, no leading/trailing/double hyphens |
| 3 | `description` is required and ≤1024 chars |
| 4 | Description **leads with purpose + trigger** — that string is what the agent matches against |
| 5 | Skill must be standalone — no required external tools beyond standard shell utilities |
| 6 | `scripts/` are not auto-executed; they are surfaced to the agent which decides whether to run them |
| 7 | MIT-compatible license (`MIT`, `Apache-2.0`, `BSD-*`, `ISC`, `CC0-1.0`) |
| 8 | Update [`registry.json`](registry.json) and the catalog table in [`README.md`](README.md) |

---

## Step-by-step

1. **Fork & branch**

   ```bash
   git clone https://github.com/<you>/elyra-skills
   cd elyra-skills
   git checkout -b skill/<your-skill-name>
   ```

2. **Create the skill**

   ```bash
   mkdir -p skills/<your-skill-name>
   $EDITOR skills/<your-skill-name>/SKILL.md
   ```

3. **Test locally**

   ```bash
   # Symlink into your agent skills dir
   ln -s "$PWD/skills/<your-skill-name>" ~/.elyra/agent/skills/<your-skill-name>

   # Start Elyra in any project and run /skills to confirm it loaded
   elyra
   > /skills
   ```

   Then trigger it naturally — give the agent a task that matches your description and verify the skill actually fires. If it doesn't, the description is probably too vague.

4. **Update the registry**

   Add an entry to [`registry.json`](registry.json):

   ```json
   {
     "name": "your-skill-name",
     "description": "Same as frontmatter description.",
     "path": "skills/your-skill-name",
     "tags": ["category"],
     "version": "1.0.0",
     "author": "your-github-handle"
   }
   ```

   And add a row to the catalog table in [`README.md`](README.md).

5. **Open the PR**

   - Title: `skill: <your-skill-name>`
   - Describe what it does, when it triggers, and how you tested it
   - One skill per PR, please

---

## Review criteria

PRs are reviewed for:

- **Utility** — would a working developer actually invoke this?
- **Generality** — does it apply across projects, or is it really stack-specific?
- **Description quality** — will the agent reliably pick it up at the right moment?
- **Safety** — scripts do nothing destructive without explicit confirmation; no network calls without docs
- **Style** — clear Markdown, no walls of text, examples where useful

Typical turnaround is a few days. We may suggest tweaks to the description (this is the single highest-leverage thing).

---

## Local development tips

- Run `/skills` in Elyra to inspect loaded skills, including script/reference counts and source path
- `/reload` re-scans skill directories without restarting Elyra
- If a skill isn't being picked up, check `/skills` output for validation warnings (name mismatch, missing description, etc.)
- See **[elyracode.com](https://elyracode.com)** for the full skills loading model, including precedence rules between extension / global / project scopes

---

## Code of Conduct

Be kind, be specific, assume good faith. Anything else gets you the door.
