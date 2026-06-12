---
name: vue-component-patterns
description: Design Vue 3 components with Composition API discipline - props/emits contracts, composables for shared logic, state placement (local vs Pinia), and render performance. Use when creating or reviewing Vue components, deciding where state lives, extracting reusable logic, debugging reactivity issues, or when a Vue app's components have grown tangled.
license: MIT
compatibility: elyra >=0.1, claude-code
allowed-tools: read, bash, grep, edit, write
metadata:
  author: elyra-skills
  version: 1.0.0
  tags: [vue, components, composition-api, composables, pinia]
---

# Vue Component Patterns

A Vue component is a **contract**: typed props in, declared events out, everything else private. Most tangled Vue codebases broke exactly that contract.

## When to use

- Creating or reviewing Vue 3 components (`<script setup>`)
- "Where should this state live?" — local, parent, composable, or Pinia
- Extracting logic shared between components
- Reactivity bugs (stale values, lost reactivity, surprise re-renders)

## Principles

- **Props down, events up — no exceptions.** Mutating a prop, reaching into `$parent`, or passing callbacks-as-props breaks traceability. `defineModel` for two-way intent.
- **State lives at the lowest level that all readers share.** Local until two components need it; lift to the common parent; Pinia only for genuinely app-wide state (auth, cart) — not as a prop-drilling shortcut.
- **Composables own logic, components own presentation.** When a component grows watchers + fetches + transforms, the logic wants to be a `useX()` composable with its own test.
- **Types are the documentation.** Typed props, typed emits, typed composable returns. An `any` prop is an undocumented API.

## Process

### 1. Define the contract first

```vue
<script setup lang="ts">
const props = defineProps<{
  order: Order
  editable?: boolean
}>()

const emit = defineEmits<{
  save: [order: Order]
  cancel: []
}>()
</script>
```

- Props: data the component *renders or branches on*. Don't pass a whole object when it uses two fields — but don't explode into 12 scalar props either; group cohesive data
- Events: named after *what happened* (`save`, `item-selected`), not what the parent should do (`refetchList`)

### 2. Place the state

| State | Lives in |
|---|---|
| UI-only (open/closed, hover, input draft) | Component-local `ref` |
| Shared by siblings | Common parent, passed down |
| Form state across a multi-step flow | Parent or a scoped composable |
| Server data | Data-fetch layer (composable / query lib), cached — not copied into Pinia |
| True app-globals (auth user, locale, cart) | Pinia store |

### 3. Extract composables (when, not how)

Extract `useX()` when: the same logic appears twice, or a component mixes 2+ concerns (fetching + debouncing + formatting).

- Composable returns **refs + functions**, no DOM or component references
- One concern per composable: `useOrderSearch()`, not `useOrderStuff()`
- Side-effectful composables clean up after themselves (`onUnmounted`, abort controllers)

### 4. Respect reactivity rules

- Don't destructure `props` or a `reactive()` (loses reactivity) — `toRefs`/`computed` or access via the object
- `computed` for derived data; a `watch` that just recomputes a value should be a `computed`
- `watch` is for *side effects* (fetch on param change, sync to localStorage); keep them few — watcher webs are where reactivity bugs breed
- Lists: stable `:key` (id, never index when reordering/filtering)

### 5. Keep renders cheap

- Heavy lists: pagination/virtual scrolling before memo-tricks
- Expensive pure subtrees: `v-memo` / split into a child so its re-render scope shrinks
- `shallowRef` for large immutable structures (big API payloads) you replace wholesale
- Defer below-the-fold weight: `defineAsyncComponent`

### 6. Review pass

```bash
# Smells worth grepping for
grep -rn "props\.\w* =" src/            # prop mutation
grep -rn '\$parent\|getCurrentInstance' src/
grep -rn ":key=\"index\"\|:key=\"i\"" src/
```

Plus: components > ~200 lines of script (extract composable), stores imported by everything (Pinia as global junk drawer), emits not declared/typed.

## Output format

```markdown
## Vue review: <component/feature>

### Contract
Props: … | Emits: … | v-model: … — typed: ✅/❌

### State placement
| State | Now | Should be |
|-------|-----|-----------|
| …     | Pinia | parent-local |

### Extractions
- `useX()` from <component> — owns: …

### Findings (ranked)
1. <file:line> — <issue> → <fix>
```

## Anti-patterns

- ❌ Mutating props, or "syncing" a prop into a local ref and editing the copy
- ❌ Events named as commands to the parent (`refetch`) instead of facts (`saved`)
- ❌ Pinia as a prop-drilling workaround — every component coupled to global state
- ❌ Server data copied into a store, then drifting from the server
- ❌ Watcher chains where A watches B watches C — replace with computed
- ❌ `:key="index"` on a filterable/sortable list
- ❌ One 600-line component with fetching, transforming, and three modals inside
