<!--
Thanks for contributing! Fill in the sections below.

For new skills: title should be `skill: <skill-name>`
For bug fixes:   title should be `fix(<skill>): <summary>`
For improvements: title should be `improve(<skill>): <summary>`
For other:       follow Conventional Commits (chore:, docs:, ci:, ...)
-->

## What & why

<!-- One or two sentences. What does this PR change, and why? -->

## Type of change

<!-- Tick whichever applies -->

- [ ] New skill
- [ ] Bug fix to an existing skill (incorrect or harmful advice)
- [ ] Improvement to an existing skill (clarity, completeness, references)
- [ ] Repo infrastructure (CI, scripts, schema, docs)
- [ ] Other:

## Related

<!-- e.g. Closes #42, Refs #17 -->

---

## Checklist

### For all PRs

- [ ] Ran `python3 scripts/validate.py` locally and it passed
- [ ] Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] Only one logical change in this PR (split if not)

### For new skills

- [ ] Folder name matches frontmatter `name` (lowercase, hyphens, ≤64 chars)
- [ ] `description` starts with **what the skill does + when to use it** (≤1024 chars)
- [ ] Skill is **standalone and generic** — not tied to a specific framework/vendor
- [ ] Follows the section template: When to use / Procedure / Output format / Anti-patterns
- [ ] Added an entry to [`registry.json`](../registry.json) (and `description` matches the frontmatter exactly)
- [ ] Added a row to the catalog table in [`README.md`](../README.md)
- [ ] Tested locally by symlinking into `~/.elyra/agent/skills/` and confirming the agent picks it up on a relevant prompt
- [ ] License is MIT-compatible (or absent — repo license applies)

### For bug fixes / improvements to existing skills

- [ ] Linked the original issue (or explained the rationale here)
- [ ] If the change affects the agent's behavior on a real prompt, described how you verified it
- [ ] Updated `registry.json` description if the SKILL.md `description` changed
- [ ] Did **not** combine unrelated changes (style + content fixes in same PR → split)

### For repo infrastructure

- [ ] Tested CI changes by pushing a branch and watching the run
- [ ] Updated [`CONTRIBUTING.md`](../CONTRIBUTING.md) or [`README.md`](../README.md) if the developer experience changes

## Verification

<!--
How did you confirm this works? Examples:
  - "Ran `/skills install <name>` in Elyra; agent picked it up on prompt 'X'."
  - "Followed the new procedure on a real bug; recommendation matched."
  - "Triggered each error path in scripts/validate.py manually."

For new skills: paste a short example of the agent actually using the skill, if you can.
-->

## Notes for reviewer

<!-- Tricky parts, deliberate trade-offs, things you want extra eyes on. Delete if none. -->
