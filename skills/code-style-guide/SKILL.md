---
name: code-style-guide
description: Establish, document, and enforce a code style guide for a codebase - naming, structure, formatting, lints. Use when the user asks to set up a style guide, define coding conventions, configure linters/formatters, or enforce consistency across a team.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, edit
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [style, conventions, linting, formatting]
---

# Code Style Guide

A style guide isn't about taste — it's about **removing decisions** so the team can think about the actual problem. The best style guide is the one you can stop arguing about.

## When to use

- "Set up a style guide for this project"
- "What's the convention here?"
- "Configure ESLint / Prettier / Biome / PHP-CS-Fixer / …"
- "Enforce consistent code style"
- "Review this code for style"

## Core principle

**Automate everything you can. Document only what you can't.**

The order of preference:

1. **Formatter** — runs on save, no debate (Prettier, Biome, `gofmt`, `rustfmt`, Black, …)
2. **Linter** — catches errors and enforced patterns (ESLint, Biome, Pylint, Rubocop, golangci-lint, PHPStan, …)
3. **Type checker** — TypeScript strict, mypy strict, Phpstan max, …
4. **Pre-commit hook** — make it impossible to commit unformatted code
5. **CI gate** — last line of defense
6. **Written guide** — only for things the tools can't enforce

If you find yourself adding a "rule" to the written guide that a linter could enforce, configure the linter instead.

## Procedure

1. **Detect the stack and existing conventions** — read 5–10 representative files before proposing anything
2. **Pick a base style** rather than inventing one (see "Pick a base" below)
3. **Configure the formatter + linter** with that base
4. **Add the pre-commit hook**
5. **Add the CI gate**
6. **Write the short prose guide** for things tools can't catch
7. **Run the formatter across the codebase once** in a dedicated PR — no review on that PR, just code formatting

## Pick a base

Don't invent. Adopt one and tweak.

| Language | Strong default base |
|---|---|
| JavaScript/TypeScript | Prettier + ESLint with `eslint:recommended` + `@typescript-eslint/recommended`, **or** Biome (one tool for both) |
| Python | Black + Ruff (Ruff replaces most of flake8/isort/pylint) |
| Go | `gofmt` is the law; add `golangci-lint` with `staticcheck`, `govet`, `errcheck` |
| Rust | `rustfmt` + `clippy` with `-W clippy::pedantic` reviewed selectively |
| PHP | Laravel: Pint; otherwise PHP-CS-Fixer with `@PSR12` + PHPStan level 8 |
| Ruby | RuboCop with `rubocop-rails-omakase` (or Standard) |
| Java | Spotless + Checkstyle + Error Prone |

## What to put in the written guide

Only things the tools can't enforce. Keep it short — a page, max two.

### Worth documenting

- **Naming patterns** the linter can't validate (e.g., "components are nouns, hooks start with `use`, store modules are singular nouns")
- **File/directory layout** ("controllers in `app/Http/Controllers/`, one resource per file")
- **Module boundaries** ("the `auth` package depends on `core` but never vice versa")
- **Conventions for things with multiple valid options** (e.g., "prefer async/await over `.then()`")
- **Error handling style** ("prefer Result types over throws in the domain layer; throws at boundaries")
- **Test layout** ("one test file per module, mirror the source tree, name `*.test.ts`")
- **Comment policy** ("comments explain *why*; if the code needs a comment to explain *what*, refactor")
- **Commit message format** (see `conventional-commits` skill)

### Not worth documenting

- Indent width — formatter
- Quote style — formatter
- Semicolons — formatter
- Trailing commas — formatter
- Import order — formatter or linter
- Line length — formatter
- Anything subjective with no observed cost when violated

## Naming guidance

Pick **one convention per category** and stick with it.

| Element | Common choice |
|---|---|
| Constants | `UPPER_SNAKE_CASE` |
| Variables, parameters | `camelCase` (JS/TS/Java/PHP), `snake_case` (Python/Ruby/Rust) |
| Functions | same as variables |
| Classes, types | `PascalCase` everywhere |
| Interfaces | `PascalCase`; no `I` prefix |
| Files | match the dominant export: `UserProfile.tsx` for a `UserProfile` component, `kebab-case.ts` for utility modules |
| Booleans | `is`, `has`, `should`, `can` prefix: `isOpen`, `hasPermission` |
| Event handlers | `handleX` (component-internal), `onX` (exposed as prop) |
| Async functions | no special suffix; the return type is the signal |

What matters more than the choice is **consistency within the codebase**.

## Configuration starting points

### TypeScript + Biome (single tool, fast)

```json
// biome.json
{
  "$schema": "https://biomejs.dev/schemas/1.9.0/schema.json",
  "formatter": { "enabled": true, "indentStyle": "space", "indentWidth": 2, "lineWidth": 100 },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "correctness": { "noUnusedVariables": "error" },
      "style": { "useConst": "error", "useTemplate": "error" }
    }
  },
  "organizeImports": { "enabled": true }
}
```

### Python

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "RUF"]

[tool.black]
line-length = 100
target-version = ["py312"]
```

### Pre-commit (universal)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: format
        name: format
        entry: <your formatter command>
        language: system
        pass_filenames: false
      - id: lint
        name: lint
        entry: <your linter command>
        language: system
        pass_filenames: false
```

Or use [Husky](https://typicode.github.io/husky/) for JS projects, [Lefthook](https://github.com/evilmartians/lefthook) for cross-language.

## Rolling it out to an existing codebase

The trick: don't try to fix everything in one PR.

1. **PR 1**: add config files (formatter, linter, hooks), do **not** apply yet
2. **PR 2**: run the formatter on the whole codebase. **No other changes.** Use `.git-blame-ignore-revs` so `git blame` doesn't blame this commit:
   ```bash
   echo "$(git rev-parse HEAD)" >> .git-blame-ignore-revs
   git config blame.ignoreRevsFile .git-blame-ignore-revs
   ```
3. **PR 3**: enable lint rules that auto-fix
4. **PR 4+**: tackle remaining lint warnings in small batches, by category, never by file count

Don't `--no-verify` your way past the new hooks. If a hook is wrong, fix the rule.

## Output format

When proposing or reviewing a style setup:

```markdown
## Style guide: <project>

**Language(s):** …
**Tooling chosen:**
- Formatter: <name + config file>
- Linter: <name + config file>
- Type checker: <name + level>
- Pre-commit: <hook tool>
- CI gate: <workflow file>

**Base style adopted:** <e.g., Biome recommended, PSR-12, PEP 8 via Black>

**Project-specific rules (in written guide):**
- <rule>

**Migration plan (if existing codebase):**
1. …
2. …
```

## Anti-patterns

- ❌ A 40-page style guide when a formatter + 5-rule preamble would do
- ❌ Style rules that aren't enforced — they degrade into folklore
- ❌ Different formatter config in each subdirectory ("legacy uses tabs")
- ❌ Bikeshedding on tab vs spaces when the formatter picks for you
- ❌ Style PRs that also change behavior — keep them separate
- ❌ "We follow Airbnb except…" with 30 exceptions — pick a different base
- ❌ Disabling lint rules inline (`// eslint-disable`) without a comment explaining why
- ❌ Letting one team member's PR push through with `--no-verify`

## Tips

- **Run the formatter in your editor on save.** "Format before commit" is too late and creates churn.
- **Enable `editor.formatOnSave` in a committed `.vscode/settings.json`** so new contributors get it automatically.
- **Pin tool versions** (`.nvmrc`, `pyproject.toml`, `composer.json`) — different versions produce different output.
- **Disagreement about a rule is fine; relitigating it every week is not.** Decide, write it down, move on.
- **The style guide is a living doc, but rare to edit.** If it's changing weekly, you're rule-fitting to last week's PR review.

## References

- [Google Style Guides](https://google.github.io/styleguide/) — opinionated, battle-tested, multi-language
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) — popular JS reference
- [PEP 8](https://peps.python.org/pep-0008/) — Python style
- [Effective Go](https://go.dev/doc/effective_go) — style + idioms together
- [The Tao of Code](https://www.youtube.com/watch?v=Pcw1JTetiAA) — Bryan Cantrill on enforced style
