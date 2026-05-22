---
name: database-migration
description: Plan and write safe database schema migrations using the expand/contract pattern with zero-downtime in mind, lock awareness, and rollback plans. Use when the user asks to add a migration, change schema, alter a table, or migrate data.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, edit
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [database, migration, schema, zero-downtime]
---

# Database Migration

The default assumption: **the old app version is still running while the new schema is being deployed**, and rolling back is non-negotiable. If you can plan migrations for that constraint, the easy cases become trivial.

## When to use

- "Add a migration for X"
- "Change this column / table / index"
- "Migrate data from A to B"
- "Plan a schema change for production"
- "Is this migration safe?"

## The two questions to ask first

1. **Does this migration acquire a long-held lock?** A few seconds on a small table is fine; minutes on a hot table is an outage.
2. **Is old app code still compatible with the new schema during deploy?** If no → use expand/contract.

If you can't answer both, stop and find out before writing the migration.

## Expand / contract (the core pattern)

The safe way to change schema in a running system. Each step ships independently.

```
1. Expand    — add new schema additively. Old code still works.
2. Migrate   — backfill / dual-write. Old + new coexist.
3. Switch    — new code reads from new schema.
4. Contract  — remove old schema. Old code is gone.
```

Each step is a separate deploy. Never combine steps that change the contract.

### Example: rename `email` → `email_address`

```sql
-- Step 1: EXPAND (deploy A)
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);

-- Step 2: BACKFILL + DUAL-WRITE (in app deploy A)
-- App writes to both email and email_address
-- Background job: UPDATE users SET email_address = email WHERE email_address IS NULL;

-- Step 3: SWITCH (deploy B)
-- App reads from email_address, still writes to both

-- Step 4: STOP DUAL-WRITE (deploy C)
-- App writes only to email_address

-- Step 5: CONTRACT (deploy D)
ALTER TABLE users DROP COLUMN email;
```

Yes, this is four deploys to "rename a column." On a system with users, that's the cost of doing it without an outage.

For a tiny project: do it in one migration during a maintenance window. Pick the strategy that matches the project.

## Operation safety matrix (PostgreSQL)

| Operation | Lock | Safe at scale? |
|---|---|---|
| `CREATE INDEX` | locks writes | ❌ — use `CREATE INDEX CONCURRENTLY` |
| `CREATE INDEX CONCURRENTLY` | brief | ✅ |
| `ADD COLUMN` (nullable, no default) | brief | ✅ |
| `ADD COLUMN` with non-volatile default (PG 11+) | brief | ✅ |
| `ADD COLUMN NOT NULL` with default | rewrites table on old PG | ⚠️ — check version |
| `DROP COLUMN` | brief, but stops old code | ⚠️ — contract step only |
| `RENAME COLUMN` | brief, but stops old code | ⚠️ — use expand/contract |
| `ALTER COLUMN TYPE` | rewrites table | ❌ — usually expand/contract |
| `ADD CONSTRAINT NOT NULL` | scans table | ⚠️ — use `NOT VALID` then `VALIDATE` |
| `ADD CONSTRAINT FOREIGN KEY` | locks both tables | ⚠️ — use `NOT VALID` then `VALIDATE` |
| `ADD UNIQUE` | scans + locks | ⚠️ — build index CONCURRENTLY first, then add constraint USING INDEX |
| `DROP INDEX` | brief, locks writes briefly | ⚠️ — use `DROP INDEX CONCURRENTLY` |

MySQL/MariaDB have different specifics; check your version. Production-grade tools (`gh-ost`, `pt-online-schema-change`) exist precisely because MySQL's online DDL has sharp edges.

## Migration safety checklist

For every migration, confirm:

- [ ] **Reversible?** A `down` migration exists or rollback strategy documented
- [ ] **Lock duration acceptable?** Long locks on a hot table = outage
- [ ] **Backward compatible with the running app?** Or split into expand/contract
- [ ] **Backfill plan?** New non-null columns need values for existing rows
- [ ] **Indexes built CONCURRENTLY?** (PG) or via online tool (MySQL)
- [ ] **Constraints added with NOT VALID then validated?** (PG)
- [ ] **Statement timeout / lock timeout set?** To fail loudly, not silently block
- [ ] **Tested against prod-sized data?** Migrations that work on 1k rows can stall on 100M
- [ ] **Idempotent?** Re-running the migration shouldn't break
- [ ] **No data deletion without explicit confirmation step**

## Long-running data migrations

A schema change is a moment; data backfills can take hours.

**Don't:**
- Put a 30-minute UPDATE in a regular migration
- Run as a single transaction (locks rows, fills WAL, can OOM)

**Do:**
- Run backfill as a **background job**, separate from schema migration
- **Batch** in chunks: `WHERE id BETWEEN x AND x+1000`, sleep between batches
- **Track progress** (separate table or column) so it's resumable
- **Throttle** so it doesn't starve regular queries
- **Verify** at the end: count of rows updated vs expected

```sql
-- Batched backfill (PG, pseudo)
DO $$
DECLARE
  batch INT := 1000;
  last_id BIGINT := 0;
  done INT;
BEGIN
  LOOP
    UPDATE users SET email_address = email
    WHERE id IN (
      SELECT id FROM users
      WHERE email_address IS NULL AND id > last_id
      ORDER BY id LIMIT batch
    );
    GET DIAGNOSTICS done = ROW_COUNT;
    EXIT WHEN done = 0;
    SELECT MAX(id) INTO last_id FROM users
      WHERE email_address IS NOT NULL AND id > last_id;
    PERFORM pg_sleep(0.1);
  END LOOP;
END $$;
```

For real systems, write the backfill in the application language with proper logging, retry, and resume — not as a giant SQL block.

## Rollback strategy

Every migration should answer: **if this is bad, how do we get back to a working state?**

| Situation | Strategy |
|---|---|
| Additive change (new column/table/index) | Drop the addition |
| Backfill running | Pause the backfill job; partial state is fine |
| Destructive change (drop column/table) | **You cannot roll back data loss** — use expand/contract so you never need to |
| Bad data in backfilled column | Backfill again from authoritative source |

A `down` migration that drops a column is fine **only** when no app version reads it. Otherwise rollback breaks the deployed app.

## Output format

When proposing a migration:

```markdown
## Migration: <one-line description>

**Strategy:** single migration / expand-contract (steps: N)
**Estimated lock time on prod:** <duration>
**Estimated backfill time:** <duration> (if applicable)
**Reversible:** yes / partial (data loss after step N)

### Schema steps
\`\`\`sql
-- <DDL with comments per step>
\`\`\`

### App changes per step
| Deploy | Reads | Writes |
|---|---|---|
| A (current) | old | old |
| B (expand) | old | both |
| C (switch) | new | both |
| D (contract) | new | new |

### Backfill
- Tool: <background job / SQL script>
- Batch size: <n>
- Throttle: <delay>
- Resumable: <yes/no>
- Progress tracking: <how>

### Verification
- Pre-migration: <counts / sentinel values>
- Post-migration: <expected state>
- Query to verify: \`SELECT … \`

### Rollback
- Step A–C: <how to revert>
- Step D: irreversible after this point because <reason>
```

## Anti-patterns

- ❌ `ALTER TABLE huge_table ADD COLUMN x NOT NULL DEFAULT 'foo'` on old PG — rewrites the entire table under a lock
- ❌ `CREATE INDEX` on a busy table without `CONCURRENTLY`
- ❌ Renaming a column in one deploy — old app code immediately breaks
- ❌ Backfill in the schema migration itself
- ❌ Backfill in a single un-throttled UPDATE
- ❌ No `down` migration *and* no documented rollback plan
- ❌ Dropping a column the same release it stopped being read — leave one release of grace
- ❌ Migration that succeeds on staging because staging has 100 rows
- ❌ `DELETE FROM users WHERE …` in a migration without a confirmation gate
- ❌ Adding a foreign key with `VALIDATE` on a 100M-row table at midnight on a Friday

## Useful commands

```sql
-- PostgreSQL: see locks in flight
SELECT pid, locktype, mode, granted, relation::regclass, query
FROM pg_locks JOIN pg_stat_activity USING (pid)
WHERE NOT granted OR mode LIKE '%Exclusive%';

-- PostgreSQL: set a statement timeout per session (fail loudly)
SET statement_timeout = '5s';
SET lock_timeout = '2s';

-- MySQL: check current online DDL support
SHOW VARIABLES LIKE 'innodb_online%';

-- Estimate table size before touching it
-- PG: SELECT pg_size_pretty(pg_total_relation_size('users'));
-- MySQL: SELECT table_name, ROUND(data_length/1024/1024, 1) AS mb FROM information_schema.tables WHERE table_schema = DATABASE();
```

## References

- [PostgreSQL: Safer Migrations](https://www.depesz.com/2024/05/03/safe-postgresql-migrations/) — operation-by-operation lock guide
- [Strong Migrations (Rails gem, but the doc is universal)](https://github.com/ankane/strong_migrations) — list of unsafe operations and how to rewrite them
- [GitHub `gh-ost`](https://github.com/github/gh-ost) — online MySQL schema changes
- [Percona `pt-online-schema-change`](https://docs.percona.com/percona-toolkit/pt-online-schema-change.html)
- [Expand/Contract pattern explained](https://martinfowler.com/articles/evodb.html)
