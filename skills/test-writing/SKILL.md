---
name: test-writing
description: Decide what to test, structure tests with arrange/act/assert, and avoid common pitfalls. Use when the user asks to write, add, or improve tests for existing code, or wants test coverage for a new feature.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, edit, grep
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [testing, quality]
---

# Test Writing

Tests exist to **catch regressions** and **document intent**. Coverage numbers are a side effect, not a goal.

## When to use

- "Write tests for this function/class/module"
- "Add tests for the new feature"
- "Improve test coverage in X"
- "This isn't tested — fix that"

## Procedure

### 1. Detect the stack

Find the existing test framework and conventions *before* writing anything new:

```bash
# Quick stack sniff
ls package.json composer.json pyproject.toml Cargo.toml go.mod 2>/dev/null
grep -l 'vitest\|jest\|pytest\|phpunit\|pest\|mocha\|rspec' \
  package.json composer.json pyproject.toml 2>/dev/null
```

Then read **one existing test file** to match style: file location, naming (`*.test.ts` vs `*_test.go` vs `test_*.py`), helpers, factories.

**Always match existing conventions.** A "better" test style in an inconsistent codebase is a worse test.

### 2. Decide what to test

For each unit under test, ask:

| Category | Examples |
|---|---|
| **Happy path** | Typical input → expected output |
| **Edge cases** | Empty, null, zero, one, max, boundary, off-by-one |
| **Error paths** | Bad input, missing dependency, network/IO failure |
| **Branches** | Every meaningful `if` / `switch` / `match` arm |
| **Invariants** | Things that must always be true (idempotency, sort order, …) |

Don't test:

- Trivial getters/setters
- Third-party library internals
- Generated code
- Implementation details (private methods, internal call order)

### 3. Structure each test: Arrange / Act / Assert

```python
def test_user_can_redeem_valid_coupon():
    # Arrange — set up the world
    user = make_user()
    coupon = make_coupon(code="SAVE10", percent=10)

    # Act — do the one thing
    result = redeem(user, coupon)

    # Assert — check the outcome
    assert result.discount == 10
    assert coupon.used_by == user.id
```

One **Act** per test. If you have two, it's two tests.

### 4. Name tests for behavior, not implementation

Test names are sentences the codebase tells you when something breaks.

- ✅ `redeem_marks_coupon_as_used_for_redeeming_user`
- ✅ `it returns 404 when product does not exist`
- ❌ `test_redeem_1`
- ❌ `testRedeemFunction`

### 5. Assert on observable behavior

Tests should fail when the *behavior* changes, not when the *code structure* changes.

- ✅ "After `register()`, the user can log in with that email"
- ❌ "After `register()`, `userRepository.save` was called once with `{email: ...}`"

The second one breaks the moment you rename a repo, even though behavior is unchanged.

### 6. Run and iterate

- Run the new test → it must pass
- Break the code under test deliberately → the test must fail (otherwise it doesn't actually test anything)
- Run the full suite → must still pass

## Common pitfalls

| Pitfall | Why it hurts | Fix |
|---|---|---|
| **Testing mocks instead of behavior** | Refactors break tests even when behavior is preserved | Assert on outputs/state, not on mock calls |
| **Shared mutable fixtures** | Tests pass/fail depending on order | Fresh setup per test, or explicit factories |
| **Time-dependent tests** | Flaky on slow CI / different timezones | Inject a clock, freeze time |
| **Hitting the network / real DB** | Slow + flaky | In-memory DB, recorded fixtures, contract tests |
| **Asserting too much** | Brittle to unrelated changes | Assert only what the test name claims |
| **Asserting too little** | Test passes even when broken | Mutation test: break the code, watch the test fail |
| **Sleep/setTimeout in tests** | Flaky | Poll with timeout, or use the framework's async primitives |

## Output format

Report:

```markdown
## Tests added: <scope>

**Framework:** <pytest / vitest / phpunit / …>

**Coverage:**
- ✅ Happy path: …
- ✅ Edge cases: …
- ✅ Error paths: …

**Deliberately not covered (and why):**
- …

**How to run:**
\`\`\`
<exact command>
\`\`\`
```

## Anti-patterns

- ❌ Writing tests after deploying — you tested in prod, then doubled down
- ❌ Chasing 100% coverage by testing trivia
- ❌ One giant test that does seven things
- ❌ Tests that pass without an assertion (yes, this happens)
- ❌ Skipped/commented-out tests left in the codebase
