# claude-workflow plugin — design

**Status:** draft (brainstorm output, awaiting review)
**Date:** 2026-07-20
**Repo:** `leocaseiro/claude-workflow` (public, local-only until pushed)

---

## 1. Purpose

Make a `review → verify → triage → apply → re-review until clean` loop the
**always-on default** across every project, on every machine, by composing
existing third-party skills (superpowers, compound-engineering) rather than
re-implementing them. Distributed as one version-controlled plugin, installed
once per machine.

The plugin is the dogfood of its own workflow: it is being built by running the
loop on itself.

---

## 2. What ships

```
leocaseiro/claude-workflow/              git repo = its own marketplace
├── .claude-plugin/
│   ├── plugin.json                      name, version, repository
│   └── marketplace.json                 plugins: [{ source: "./" }]
├── hooks/
│   ├── hooks.json                       SessionStart · matcher "startup|clear|compact"
│   └── session-start                    THIN: the always-on rule (~8 lines triage + loop pointer)
├── skills/
│   ├── triage/SKILL.md                  the asking discipline
│   ├── doc-review-loop/SKILL.md         review any doc until clean
│   ├── code-review-loop/SKILL.md        review any diff until clean (model-tiered execute)
│   ├── before-pr/SKILL.md               sequences the 15 steps
│   ├── handoff/SKILL.md                  save a loop-aware handoff to resume in a new session
│   └── _shared/review-loop.md           the loop shape, written ONCE (read-only at runtime)
├── bin/
│   └── resolve-skill                    active-version resolver (jq over installed_plugins.json)
├── docs/specs/ · docs/plans/            this repo's own artifacts
└── AGENTS.md                            docs convention + public-repo rule
```

Install anywhere: `/plugin marketplace add leocaseiro/claude-workflow` →
`/plugin install …`. User scope = available in every project, no per-project setup.

---

## 3. The five skills

### `triage` — how every question is put to the person
Not review-specific. Governs **every** question the agent asks:
- Findings/context established in prose chunks FIRST.
- The picker (`AskUserQuestion`) emitted in the SAME turn — never a prose "answer 1-4".
- Lean question references the chunk; batch ≤ 4; always offer a defer option.
- No ghost references (a `(see chunk X)` must have X present).
- Written **generically** — about "the person you are working with", no personal data.
- The review-findings walk is a special case that uses it.

### `doc-review-loop` — review any doc until clean
Params (supplied to `_shared/review-loop.md`): review skill = `ce-doc-review`;
exit = its output buckets ("Proposed fixes" AND "Decisions" both empty — the rule
CE states at `walkthrough.md:28` but never surfaces as a verdict).

### `code-review-loop` — review any diff until clean
Params: review skill = `ce-code-review` in `mode:agent` (report-only, so the
picker stays the decision point — default mode would apply+commit and bypass it);
exit = CE's own `verdict` / `actionable_findings`.
**Owns the model-tiered executor** (§6).

### `before-pr` — the sequencer
Runs the 15-step runbook: `brainstorming → doc-review-loop → writing-plans →
doc-review-loop → code-review-loop → pr-checklist-audit → human review → merge`.
The model-tiered execute (§6) is `code-review-loop`'s own "produce" phase (§4),
not a separate step before it.

### `handoff` — resume in a new session
A `before-pr` run spans too much context for one session. At any step, `handoff`
writes a resume document so a fresh session continues exactly where this one
stopped. Adapted from the base-skill `handoff` pattern, made loop-aware: it
records the current `stage:`, the active artifact path, any `docs/decisions/pending/`
fragments, the lap count, and the next runbook step. A new session reads it and
resumes without re-deriving state. Invoke when ending a session, context-switching,
or when context runs long mid-loop.

---

## 4. The loop (`_shared/review-loop.md`, written once)

```
produce/hold artifact
  → review (param: review skill)
  → verify  (superpowers:receiving-code-review, External-Reviewer branch — BOTH loops)
  → triage  (the triage skill: chunks → picker)
  → apply   (per the person's decisions)
  → re-review IF a P0/P1 finding was applied   ← the re-lap trigger
  → exit    WHEN clean (param: exit signal)     ← the exit condition
```

- **Exit** and **re-lap** are two different jobs. Exit = "is it clean?" (the review
  skill's own signal). Re-lap = "did I change enough to invalidate the last review?"
  (a P0/P1 was applied). Manual override in both directions.
- `verify` runs `superpowers:receiving-code-review` before the picker — its
  External-Reviewer branch = verify a finding is correct before presenting it.
  This IS the person's Rule 2 + Rule 4 (verify against docs; no training-only
  claims), enforced at the moment they'd slip.
- Shared file lives in the plugin repo, ships read-only. 12+ concurrent worktrees
  READ it; none WRITE it — so it cannot conflict the way a shared registry does.

---

## 5. Composition — two tiers (tier 3 out of v1)

- **Tier 1 — Skill tool by plugin-qualified name.** `Skill(superpowers:brainstorming)`
  etc. Upgrade-proof, auto-current. The default for everything.
- **Tier 2 — Skill tool + a stated override.** Where the sub-skill documents a
  lever (e.g. superpowers defers spec location to user preference).
- **Tier 3 — read-from-disk + skip-lists.** OUT of v1. `bin/resolve-skill` ships
  (jq over `installed_plugins.json`, picks the active user-scoped version) for
  future use. Climb only when a skill provably won't defer.

Cross-plugin invocation via the Skill tool is **verified working** (this brainstorm
loaded `superpowers:brainstorming` from inside the workflow).

---

## 6. Model-tiered executor (v1)

superpowers' `subagent-driven-development` dispatches implementer subagents but
never sets a model, so they inherit the session model (expensive model doing
mechanical typing). Our `code-review-loop` owns a replacement:

| Role | Model | Does |
| --- | --- | --- |
| Orchestrator (main session) | Opus | triage, pickers, decisions |
| Implementer subagents | Haiku / Sonnet | mechanical code-writing |

Legal because **execution has no "family" format** (§7) — it reads a plan and
writes code; code carries no family shape. So a custom executor does not break
family consistency.

---

## 7. The family rule

The two skill families have different document models:
- **superpowers** — `design.md` (brainstorm) + a SEPARATE `plan.md` (TDD script).
- **compound-engineering** — ONE unified doc enriched in place
  (`requirements-only → implementation-ready`).

**Rule:** stay in one family for the `brainstorm → plan` lineage; never cross
mid-lineage. **Default spine = superpowers** (brainstorm + writing-plans).
**ce = reviews only** (reviews read any doc, so they are family-neutral).
**Execution is family-neutral** (reads a plan, writes code).

---

## 8. Paths, state, and decisions (concurrency-safe)

- **Artifacts:** `docs/specs/YYYY-MM-DD-<slug>.md` + `docs/plans/YYYY-MM-DD-<slug>-plan.md`
  (no `-NNN-` counter, no `-design` suffix). Plugin ships this default; a repo's
  `AGENTS.md` overrides.
- **Loop state:** `stage:` frontmatter on the artifact (the plan carries `stage: build`,
  since code has no frontmatter). Survives compaction and new sessions.
- **Decision entries:** the **fragment pattern** — one file per session at
  `docs/decisions/pending/YYYY-MM-DD-<slug>.md`, folded into the registry when the
  person chooses. No two sessions touch the same file → git never conflicts (how
  changesets / towncrier solve this). Fixes Rule 3's "PR lands a registry entry"
  colliding across 12+ worktrees.

---

## 9. Borrowed, not adopted: the delta idea

From OpenSpec (evaluated and rejected as a dependency — its DAG cannot express
iterate-until-clean; completion is file-existence with no content check):
borrow the **delta vocabulary** (`## ADDED / MODIFIED / REMOVED Requirements`) as
a documentation convention inside `docs/specs/`, so each review lap leaves a record
of what changed. No CLI, no `openspec/` tree, no schema.

---

## 10. Explicitly NOT in v1

- Tier 3 read-from-disk overrides (deferred until a skill won't defer).
- The OpenSpec tool (idea only).
- A guard against ce-compound-refresh deletions — **withdrawn**: verified it only
  touches `docs/solutions/`, never specs/plans/archives; the alarm was unfounded.
- A hard lap cap (not requested; the P0/P1 re-lap + manual override suffices).

---

## 11. Open / future

- The triage discipline in the SessionStart hook is a lossy ~8-line summary of the
  full skill — accept the loss for turn-1 coverage; the skill carries depth.
- `ce-plan`'s `-NNN-` counter only bites on direct `/ce-plan` use (not in the loop,
  which uses `writing-plans`). One AGENTS.md note; tier-3 candidate if it ever annoys.
- `ce-doc-review`'s exit read parses a prose envelope — fragile if CE reformats.
  Revisit if it breaks.
