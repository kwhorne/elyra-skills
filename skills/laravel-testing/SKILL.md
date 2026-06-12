---
name: laravel-testing
description: Test Laravel applications effectively with Pest or PHPUnit - feature vs unit boundaries, factories, database strategy, what to fake, and HTTP/Livewire assertions. Use when writing tests for Laravel code, reviewing a Laravel test suite, deciding how to test a controller, job, or command, or when tests are slow or brittle.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, edit, write
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [laravel, testing, pest, phpunit, factories]
---

# Laravel Testing

In Laravel, the **feature test is the workhorse**: hit the route, assert the response and the database. Unit tests are for real logic, not for ceremony.

## When to use

- Writing tests for Laravel controllers, jobs, commands, actions, or models
- Reviewing a Laravel test suite (coverage, speed, brittleness)
- "How should I test this?" for anything framework-coupled
- Tests are slow, flaky, or break on every refactor

## Principles

- **Test through the front door.** `$this->post(route(...))` exercises routing, middleware, validation, authorization, and persistence in one honest test.
- **Fake the edges, not the middle.** `Mail::fake()`, `Queue::fake()`, `Http::fake()`, `Storage::fake()` — but don't mock your own repositories and services into a tautology.
- **Factories are the vocabulary.** States (`->suspended()`, `->paid()`) make tests read like specifications.
- **Each test = one behavior.** Arrange, act, assert — and assert the *outcome* (DB row, response, dispatched job), not the implementation path.

## Process

### 1. Choose the test type

| Code under test | Type |
|---|---|
| Route/controller behavior, auth, validation | **Feature** (HTTP test) |
| Pure logic: calculators, value objects, rules | **Unit** (no framework boot if possible) |
| Queued job | Feature-style: instantiate, `handle()`, assert outcomes |
| Artisan command | `$this->artisan(...)->assertExitCode(0)` + DB asserts |
| Livewire component | `Livewire::test(...)` — state, actions, events, validation |
| Blade/UI flows across pages | Few, high-value browser tests (Dusk/Pest browser) |

### 2. Set the database strategy

- `RefreshDatabase` + SQLite `:memory:` for speed — **unless** you use DB-specific features (JSON columns, full-text, triggers); then test against the real engine, matching production
- `LazilyRefreshDatabase` skips migration cost for tests that never touch the DB

### 3. Build with factories

```php
$user = User::factory()->create();
$order = Order::factory()->for($user)->paid()->create();   // states > attribute soup
```

- Define states in the factory for every domain status the tests mention
- `make()` when persistence isn't needed; `create()` only when the test reads it back
- Never seed global fixtures the whole suite shares — each test builds its own world

### 4. Write the feature test

```php
it('refunds a paid order', function () {
    Queue::fake();
    $order = Order::factory()->paid()->create();

    $this->actingAs($order->user)
        ->post(route('orders.refund', $order))
        ->assertRedirect()
        ->assertSessionHas('status');

    expect($order->fresh()->status)->toBe(OrderStatus::Refunded);
    Queue::assertPushed(ProcessRefund::class, fn ($job) => $job->orderId === $order->id);
});
```

Cover per endpoint: happy path, validation failure (`assertSessionHasErrors` / `assertJsonValidationErrors`), **authorization** (wrong user → 403), and the relevant edge case. Auth tests are the ones that prevent incidents.

### 5. Fake the boundaries

- `Http::fake([...])` with per-URL responses; `Http::assertSent(...)` for contract checks; add `Http::preventStrayRequests()` suite-wide
- `Time`: `$this->travel(3)->days()` / `Carbon::setTestNow()` for anything date-dependent
- `Event::fake()` **narrowly** (`Event::fake([OrderShipped::class])`) — global fakes silence model events your code depends on

### 6. Keep it fast and honest

```bash
php artisan test --parallel          # paratest
php artisan test --profile           # find the slow ones
```

- Suite target: minutes, not tens of minutes; single test: milliseconds unless it's a browser test
- A test that breaks when you rename a private method tests the wrong thing — assert outcomes

## Output format

```markdown
## Tests: <feature/area>

**Type mix:** N feature / M unit / K browser — why.
**DB strategy:** RefreshDatabase + <engine>.

### Coverage
| Behavior | Test |
|----------|------|
| happy path | ✅ … |
| validation | ✅ … |
| authorization | ✅ … |
| <edge case> | ✅ … |

**Faked:** Queue, Http (+preventStrayRequests). **Deliberately real:** …
```

## Anti-patterns

- ❌ Mocking Eloquent models or your own services so the test asserts the mock, not the behavior
- ❌ Unit-testing a controller with mocked request/response instead of one feature test
- ❌ Skipping authorization tests — the most expensive gap in any Laravel suite
- ❌ Shared seeders creating hidden coupling between tests
- ❌ SQLite in tests + MySQL JSON queries in production = green suite, broken prod
- ❌ `Event::fake()` globally, then wondering why observers "don't work" in tests
- ❌ Asserting `assertStatus(200)` and nothing else — the page can be 200 and wrong
