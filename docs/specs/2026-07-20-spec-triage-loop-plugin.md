# spec-triage-loop plugin — design

**Status:** reviewed (ce-doc-review 2026-07-20 applied; v1 trimmed to core)
**Date:** 2026-07-20
**Repo:** `leocaseiro/spec-triage-loop` (public, local-only until pushed)

---

## 1. Purpose

Make a `review → verify → triage → apply → re-review until clean` loop the
**default review workflow**, re-surfaced at every session start across every
project, by composing existing third-party skills (superpowers,
compound-engineering) rather than re-implementing them. Distributed as one
version-controlled plugin, installed once per machine.

v1 is deliberately small: the two review loops + the triage discipline + the
hook. Everything else (`before-pr` sequencer, `handoff`, delta convention,
tier-3 overrides) is staged to v1.1 to prove the core loop before adding to it
(see §8). The plugin is the dogfood of its own workflow: it is being built by
running the loop on itself.

---

## 2. What ships (v1 core)

```
leocaseiro/spec-triage-loop/             git repo = its own marketplace
├── .claude-plugin/
│   ├── plugin.json                      name, version, repository
│   └── marketplace.json                 plugins: [{ source: "./" }]
├── hooks/
│   ├── hooks.json                       SessionStart · matcher "startup|clear|compact"
│   └── session-start                    THIN: the triage rule + loop pointer (~8 lines)
├── skills/
│   ├── triage/SKILL.md                  the asking discipline
│   ├── doc-review-loop/SKILL.md         review any doc until clean
│   ├── code-review-loop/SKILL.md        review any diff until clean
│   └── _shared/review-loop.md           the loop shape, written ONCE (read-only at runtime)
├── docs/specs/ · docs/plans/            this repo's own artifacts
└── AGENTS.md                            docs convention + public-repo rule
```

Install anywhere: `/plugin marketplace add leocaseiro/spec-triage-loop` →
`/plugin install …`. User scope = available in every project, no per-project setup.

---

## 3. The three v1 skills

### `triage` — how every question is put to the person
Not review-specific. Governs **every** question the agent asks:
- Findings/context established in prose chunks FIRST.
- The picker (`AskUserQuestion`) emitted in the SAME turn — never a prose "answer 1-4".
- Lean question references the chunk; batch ≤ 4; always offer a defer option.
- No ghost references (a `(see chunk X)` must have X present).
- Written **generically** — about "the person you are working with", no personal data.
- The review-findings walk is a special case that uses it.

### `doc-review-loop` — review any doc until clean
Params (supplied to `_shared/review-loop.md`):
- review skill = `ce-doc-review` **in `mode:headless`** — report-only, so its own
  interactive walk-through never fires and the picker stays *our* triage's job.
  (Default/interactive mode would deadlock the loop on CE's own routing question.)
- exit = the headless envelope's `Review complete` line **with the `Proposed fixes`
  and `Decisions` buckets both empty** (spec: `ce-doc-review/references/synthesis-and-presentation.md`,
  the headless envelope — NOT the interactive `walkthrough.md`).
- verify = a **doc-specific** check (§4), not `receiving-code-review`.

### `code-review-loop` — review any diff until clean
Params:
- review skill = `ce-code-review` in `mode:agent` (report-only, so the picker stays
  the decision point — default mode would apply+commit and bypass it).
- exit = CE's own `verdict` / `actionable_findings` (a deterministic JSON object).
- verify = `superpowers:receiving-code-review` (its checks are code-scoped — correct here).
- **model tiering** is not a new build: it *configures* superpowers'
  `subagent-driven-development`, which already ships a `## Model Selection` section
  ("Always specify the model explicitly when dispatching a subagent", cheap /
  standard / most-capable tiers). The loop's produce phase composes that skill and
  passes the cheap tier for mechanical implementers while the orchestrator stays on
  the capable model. Nothing is re-implemented.

---

## 4. The loop (`_shared/review-loop.md`, written once)

```
produce/hold artifact
  → review (param: review skill + mode)
  → verify (param: verify check — doc-specific for docs, receiving-code-review for code)
  → triage (the triage skill: chunks → picker)
  → apply  (per the person's decisions)
  → re-review IF a P0/P1 finding was applied   ← the re-lap trigger
  → exit   WHEN clean (param: exit signal)      ← the exit condition
  → HALT to the person at the lap cap / on no-progress   ← the bound
```

- **Exit** and **re-lap** are two different jobs. Exit = "is it clean?" (the review
  skill's own signal). Re-lap = "did I change enough to invalidate the last review?"
  (a P0/P1 was applied). Manual override in both directions.
- **The bound.** Applying a P0/P1 fix can surface *new* P0/P1 findings, so the re-lap
  trigger can fire indefinitely. The loop halts and hands to the person when it hits a
  lap cap, or when a lap's findings are not a strict subset of the previous lap's
  (no-progress). "Until clean" is bounded, not open-ended.
- **verify is per-input, not one skill.** For code, `receiving-code-review`'s
  External-Reviewer checks (codebase reality, breakage, platform/version) fit. For a
  prose doc none of those apply, so doc-review-loop verifies differently: the finding
  cites a real section, the quote is verbatim, and the fix doesn't contradict another
  section.
- Shared file lives in the plugin repo, ships read-only. 12+ concurrent worktrees
  READ it; none WRITE it — so it cannot conflict the way a shared registry does.

---

## 5. Composition — two tiers (tier 3 staged to v1.1)

- **Tier 1 — Skill tool by plugin-qualified name.** `Skill(superpowers:brainstorming)`
  etc. Current while the invoked skill's name + parsed output stay stable. The default.
- **Tier 2 — Skill tool + a stated override.** Where the sub-skill documents a lever
  (e.g. superpowers defers spec location to user preference).
- **Tier 3 — read-from-disk + skip-lists.** Staged to v1.1 (§8). Climb only when a
  skill provably won't defer.

Cross-plugin invocation via the Skill tool is **observed working** (this session
loaded `superpowers:brainstorming` and, nested, `compound-engineering:ce-doc-review`
from inside the workflow). An explicit second-machine falsification test is on the
backlog before v1 ships.

---

## 6. The family rule

The two skill families have different document models:
- **superpowers** — `design.md` (brainstorm) + a SEPARATE `plan.md` (TDD script).
- **compound-engineering** — ONE unified doc enriched in place
  (`requirements-only → implementation-ready`).

**Rule:** stay in one family for the `brainstorm → plan` lineage; never cross
mid-lineage. **Default spine = superpowers** (brainstorm + writing-plans).
**ce = reviews only** (reviews read any doc, so they are family-neutral).
**Execution is family-neutral** (reads a plan, writes code).

---

## 7. Paths, state, and decisions (concurrency-safe)

- **Artifacts:** `docs/specs/YYYY-MM-DD-<slug>.md` + `docs/plans/YYYY-MM-DD-<slug>-plan.md`
  (no `-NNN-` counter, no `-design` suffix). Plugin ships this default; a repo's
  `AGENTS.md` overrides.
- **Loop state — frontmatter on the artifact:**
  - `stage:` — coarse position (`shape` / `plan` / `build`; the plan carries the build
    stage since code has no frontmatter).
  - `last_applied:` + `lap:` — the re-lap decision variables. A compaction discards
    working memory, so the "was a P0/P1 applied this lap" flag and the lap count MUST
    live on disk; the loop recomputes the re-lap decision from frontmatter on resume.
    Without this, a resumed loop either re-laps a clean doc forever or ships an
    unreviewed change — the one fact §1's "until clean" guarantee rests on.
- **Decision entries — the fragment pattern:** one file per session at
  `docs/decisions/pending/YYYY-MM-DD-<slug>.md`, folded into the registry when the
  person chooses. No two sessions touch the same file → git never conflicts (how
  changesets / towncrier solve this). Fixes "PR lands a registry entry" colliding
  across 12+ worktrees.

---

## 8. Staged to v1.1 (deferred, not dropped — see `TODO.md`)

Cut from v1 to prove the core loop first (Q-V1SIZE, 2026-07-20). Each has its reason
recorded in `TODO.md`.

- **`before-pr` skill** — the 15-step brainstorm→merge sequencer. The two loops + hook
  deliver the review value without it.
- **`handoff` skill** — loop-aware session-resume doc; justified by `before-pr`'s
  length, so it follows `before-pr`.
- **Delta vocabulary** (`## ADDED / MODIFIED / REMOVED`) — a per-lap change-record
  convention borrowed from OpenSpec (the *idea* only — OpenSpec's DAG can't express
  iterate-until-clean, and completion is file-existence with no content check).
- **Tier 3 + `bin/resolve-skill`** — the version resolver has no v1 consumer; it ships
  with tier 3.
- **A guard against ce-compound-refresh deletions** — withdrawn: verified it only
  touches `docs/solutions/`, never specs/plans/archives; the alarm was unfounded.

---

## 9. Open / future

- **Always-on strength.** The hook fires at `startup|clear|compact`, not every turn,
  and carries a lossy ~8-line summary — so v1 promises "re-surfaced at session start",
  not a per-turn guarantee. Revisit strengthening the mechanism (recurring re-assert,
  or force-load the full skill), and add `resume` to the matcher.
- **Parse fragility.** The doc-review exit reads CE's headless prose envelope; a CE
  reformat breaks it. Future: a format-drift smoke check against a fixture. Consider
  pinning the versions whose *output format* the loop parses.
- **`ce-plan`'s `-NNN-` counter** only bites on direct `/ce-plan` use (not in the loop,
  which uses `writing-plans`). One AGENTS.md note; tier-3 candidate if it ever annoys.
