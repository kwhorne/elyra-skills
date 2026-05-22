---
name: accessibility-review
description: Perform a WCAG-flavored accessibility review of UI code or markup. Use when the user asks for an a11y review, accessibility audit, WCAG check, or wants to make a component/page usable for assistive tech.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [accessibility, a11y, wcag, review]
---

# Accessibility Review

A practical WCAG 2.2 AA-flavored review. The goal: real users on assistive tech can actually use this, not "lighthouse score 100".

## When to use

- "Review X for accessibility / a11y"
- "Is this component WCAG-compliant?"
- "Audit this page for screen reader support"
- "Make this form accessible"

## Procedure

1. **Identify the surface** — component, page, or whole app? Templating language (Blade, JSX, Vue, plain HTML)?
2. **Walk the checklist** below in order: semantics → keyboard → screen reader → visual → forms → dynamic
3. **For each finding**: cite the WCAG SC if you know it, explain user impact, propose a fix
4. **Group by severity** (see Output format)

## Checklist

### Semantic HTML

- [ ] Headings form a logical outline (one `<h1>`, no skipped levels)
- [ ] Landmarks present: `<header>`, `<nav>`, `<main>`, `<footer>`
- [ ] Lists are `<ul>`/`<ol>`/`<dl>` — not `<div>` soup
- [ ] Buttons are `<button>`, links are `<a href>` — never the other way around
- [ ] Form fields wrapped in `<form>` with `<label for>` (or `aria-label`/`aria-labelledby`)
- [ ] Tables use `<th scope>` and `<caption>` where appropriate
- [ ] `<img>` has `alt` (empty `alt=""` for decorative, descriptive for meaningful)

### Keyboard

- [ ] Every interactive element reachable via Tab in a logical order
- [ ] Visible focus indicator (don't `outline: none` without replacement) — WCAG 2.4.7
- [ ] `Enter` and `Space` activate buttons; `Enter` activates links
- [ ] Custom widgets follow [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/patterns/)
- [ ] No keyboard traps (modals, custom dropdowns must allow Escape / Tab out)
- [ ] Skip-to-content link on pages with lots of nav

### Screen reader

- [ ] Page has a meaningful `<title>`
- [ ] `<html lang="...">` set
- [ ] Icons have accessible names (`aria-label` on icon-only buttons)
- [ ] Decorative icons hidden: `aria-hidden="true"`
- [ ] Live regions (`aria-live="polite"` / `"assertive"`) for dynamic updates
- [ ] Loading/busy states announced (`aria-busy`)
- [ ] No `aria-hidden="true"` on focusable elements
- [ ] No `role="button"` on actual `<button>`s (redundant) — but also don't fake buttons with `<div>`

### Visual

- [ ] Text contrast: 4.5:1 for body, 3:1 for large text (WCAG 1.4.3)
- [ ] Non-text contrast: 3:1 for UI components and focus indicators (1.4.11)
- [ ] Information not conveyed by color alone (red error also has icon/text — 1.4.1)
- [ ] Text resizes to 200% without horizontal scroll (1.4.4)
- [ ] Respects `prefers-reduced-motion` (animations subdued or off)
- [ ] Respects `prefers-color-scheme` if dark mode exists

### Forms

- [ ] Every input has an associated label (visible or `aria-label`)
- [ ] Required fields marked with `required` *and* visually
- [ ] Errors associated with the field via `aria-describedby` + `aria-invalid="true"`
- [ ] Error messages are descriptive ("Email is missing the @" not "Invalid")
- [ ] Errors announced to screen readers (live region or focus-on-error)
- [ ] Autocomplete attributes set where relevant (`autocomplete="email"`, etc.)

### Dynamic content

- [ ] Modals: focus moves in, trapped while open, returns on close
- [ ] Modals have `role="dialog"` + `aria-labelledby` + `aria-modal="true"` (or use `<dialog>`)
- [ ] Toasts/notifications use `role="status"` or `role="alert"`
- [ ] Async loaders communicate state, not just spin silently
- [ ] Route changes in SPAs move focus to the new page region

## Useful greps

```bash
# Missing alt
grep -RInE '<img(?![^>]*\salt=)' --include='*.{html,jsx,tsx,vue,blade.php,erb}' .

# Click handlers on non-interactive elements (likely fake buttons)
grep -RInE '<(div|span)[^>]*onClick' --include='*.{jsx,tsx,vue}' .

# Outline removed without replacement
grep -RIn 'outline:\s*none\|outline:\s*0' --include='*.{css,scss,vue,jsx,tsx}' .

# Placeholder used as label (anti-pattern)
grep -RInE '<input[^>]*placeholder=' --include='*.{html,jsx,tsx,vue,blade.php}' . | grep -v 'aria-label\|<label'
```

These are leads, not verdicts.

## Output format

```markdown
## Accessibility review: <scope>

**Standard:** WCAG 2.2 AA (or as scoped)
**Tested with:** <static review / axe-core / VoiceOver / NVDA / keyboard only>

### 🔴 Blockers
- `path/file.tsx:42` — <issue>. **Impact:** <who can't use this>. **WCAG:** <SC if known>. **Fix:** <what>.

### 🟠 Major
- …

### 🟡 Minor
- …

### 💭 Questions
- …

### ✅ What's working
- <category> — <one sentence>
```

### Severity rubric

| Tag | Meaning |
|---|---|
| 🔴 **Blocker** | Some users literally cannot complete the task (keyboard trap, no labels, inaccessible form) |
| 🟠 **Major** | Significant friction (poor contrast, missing focus indicator, confusing announcements) |
| 🟡 **Minor** | Polish (redundant ARIA, suboptimal heading levels) |
| 💭 **Question** | Needs context or testing on actual AT to judge |

## Anti-patterns

- ❌ `aria-label` on every element "to be safe" — most native HTML elements already announce correctly
- ❌ `tabindex="0"` on `<div onClick>` to "make it accessible" — use a `<button>`
- ❌ `tabindex` > 0 — breaks natural tab order
- ❌ Removing focus outlines without providing a replacement
- ❌ Placeholder as the only label
- ❌ "Click here" link text
- ❌ Auto-playing audio/video with sound
- ❌ Color as the only error indicator
- ❌ Modals that don't trap focus or don't return focus on close
- ❌ Pretending an axe-core score of 0 issues means "accessible"

## What automation can and can't catch

| Tool catches | Tool misses |
|---|---|
| Missing alt, missing labels, low contrast (mostly), duplicate IDs, invalid ARIA | Whether alt text is *meaningful*, focus order, screen-reader UX, keyboard interactions, real cognitive load |

Static + automated checks are necessary, not sufficient. If the audit matters, test with a real screen reader at least once (VoiceOver on macOS/iOS, NVDA on Windows, TalkBack on Android).

## References

- [WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Inclusive Components](https://inclusive-components.design/) — Heydon Pickering's pattern library
