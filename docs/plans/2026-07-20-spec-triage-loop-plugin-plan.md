# spec-triage-loop v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the v1 core of a Claude Code plugin that makes a `review → verify → triage → apply → re-review until clean` loop the default review workflow, re-surfaced at every session start, by composing superpowers + compound-engineering skills.

**Architecture:** A git repo that is its own plugin marketplace. A thin SessionStart hook injects the triage rule + a loop pointer. Three skills (`triage`, `doc-review-loop`, `code-review-loop`) carry the depth; a shared `_shared/review-loop.md` holds the loop shape once. All composition is via the Skill tool by plugin-qualified name (tier 1). Verified against the source spec at `docs/specs/2026-07-20-spec-triage-loop-plugin.md`.

**Tech Stack:** Markdown (SKILL.md), JSON (plugin/marketplace manifests, hooks.json), POSIX shell (hook script). No compiled code, no test framework — verification is structural validity + install/load/compose smoke checks, using the installed superpowers plugin (`~/.claude/plugins/cache/claude-plugins-official/superpowers/6.1.1/`) as the reference shape.

## Global Constraints

- Repo/plugin name: `spec-triage-loop`; owner `leocaseiro`; public repo. Copied verbatim everywhere.
- **No personal data** in any committed file (public repo). Describe the person's working style neutrally; never a diagnosis. (spec §3, AGENTS.md)
- Composition is **tier 1 only** — `Skill(<plugin>:<skill>)` by qualified name. No read-from-disk, no `bin/resolve-skill` (staged to v1.1).
- `doc-review-loop` → `ce-doc-review` in **`mode:headless`**; exit on the headless `Review complete` envelope with `Proposed fixes` + `Decisions` buckets empty (spec: `ce-doc-review/references/synthesis-and-presentation.md`).
- `code-review-loop` → `ce-code-review` in **`mode:agent`**; exit on `verdict` / `actionable_findings`; configure (never rebuild) superpowers' existing `## Model Selection`.
- The loop is **bounded**: a lap cap / no-progress halt, and `last_applied` + `lap` persisted to artifact frontmatter (spec §4, §7).
- `verify` is per-input: `receiving-code-review` on code-loop; a doc-specific check on doc-loop (spec §4).
- v1 scope is exactly: scaffold + hook + 3 skills + `_shared/review-loop.md` + AGENTS.md + repo hygiene. NOT `before-pr`, `handoff`, delta vocab, tier-3 (spec §8, TODO.md).
- Hook must stay THIN (~8 lines of injected rule) — it is taxed every session (spec §1, §9).

---

### Task 1: Plugin + marketplace scaffold

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Reference: `~/.claude/plugins/cache/claude-plugins-official/superpowers/6.1.1/.claude-plugin/{plugin,marketplace}.json`

**Interfaces:**
- Produces: an installable plugin named `spec-triage-loop` in a self-hosted marketplace (`source: "./"`), consumed by every later task's install check.

- [ ] **Step 1: Write `.claude-plugin/plugin.json`**

```json
{
  "name": "spec-triage-loop",
  "description": "Make a review→verify→triage→apply→re-review loop the default review workflow, composing superpowers + compound-engineering.",
  "version": "0.1.0",
  "author": { "name": "leocaseiro" },
  "homepage": "https://github.com/leocaseiro/spec-triage-loop",
  "repository": "https://github.com/leocaseiro/spec-triage-loop",
  "license": "MIT",
  "keywords": ["skills", "code-review", "workflow", "triage"]
}
```

- [ ] **Step 2: Write `.claude-plugin/marketplace.json`**

```json
{
  "name": "spec-triage-loop",
  "description": "Self-hosted marketplace for the spec-triage-loop plugin.",
  "owner": { "name": "leocaseiro" },
  "plugins": [
    { "name": "spec-triage-loop", "version": "0.1.0", "source": "./" }
  ]
}
```

- [ ] **Step 3: Verify both JSON files are valid**

Run: `jq . .claude-plugin/plugin.json && jq . .claude-plugin/marketplace.json`
Expected: both pretty-print with no parse error.

- [ ] **Step 4: Verify local install resolves**

Run: `/plugin marketplace add /Users/leocaseiro/Sites/spec-triage-loop` then `/plugin install spec-triage-loop@spec-triage-loop`
Expected: the plugin installs; `/plugin` lists `spec-triage-loop`. (No skills yet — that's fine; this checks the manifest shape.)

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin/
git commit -m "feat: plugin + self-hosted marketplace scaffold"
```

---

### Task 2: SessionStart hook (thin, always-on)

**Files:**
- Create: `hooks/hooks.json`
- Create: `hooks/session-start` (executable)
- Reference: superpowers `hooks/hooks.json` (matcher shape) and `hooks/run-hook.cmd` (cross-platform wrapper pattern)

**Interfaces:**
- Consumes: nothing.
- Produces: on every session start/clear/compact, the triage rule + loop pointer is injected into context (stdout from the hook is added to the model's context).

- [ ] **Step 1: Write `hooks/hooks.json`**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/session-start\"", "async": false }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: Write `hooks/session-start`** (the ~8-line rule — keep it thin)

```sh
#!/usr/bin/env sh
cat <<'RULE'
[spec-triage-loop] Default review workflow is active.
- When you ask the person a question, use the triage discipline: establish findings/context
  in prose chunks FIRST, then emit the AskUserQuestion picker in the SAME turn (never a prose
  "answer 1-4"); batch <=4; always offer a defer option; no ghost references.
- Before a PR, review docs with the doc-review-loop skill and code with the code-review-loop
  skill; loop until clean. Load those skills for the full procedure.
RULE
```

- [ ] **Step 3: Make it executable**

Run: `chmod +x hooks/session-start`
Expected: `test -x hooks/session-start` succeeds.

- [ ] **Step 4: Verify the hook emits the rule**

Run: `CLAUDE_PLUGIN_ROOT="$PWD" ./hooks/session-start`
Expected: the rule text prints to stdout (this is what gets injected).

- [ ] **Step 5: Verify hooks.json is valid + matcher matches superpowers' working shape**

Run: `jq . hooks/hooks.json`
Expected: valid JSON; `SessionStart[0].matcher == "startup|clear|compact"`.

- [ ] **Step 6: Commit**

```bash
git add hooks/
git commit -m "feat: thin SessionStart hook injecting the triage rule + loop pointer"
```

---

### Task 3: The shared loop shape (`_shared/review-loop.md`)

**Files:**
- Create: `skills/_shared/review-loop.md`

**Interfaces:**
- Produces: the parameterized loop procedure that `doc-review-loop` and `code-review-loop` both reference. Params named here (review-skill, review-mode, exit-signal, verify-check) are supplied by the calling skill.

- [ ] **Step 1: Write `skills/_shared/review-loop.md`**

Content (the loop shape, written once — an instruction file, not frontmatter'd):

```markdown
# The review loop (shared)

The calling skill supplies four parameters: REVIEW-SKILL, REVIEW-MODE,
EXIT-SIGNAL, VERIFY-CHECK. Run this procedure.

1. **Produce/hold** the artifact under review (a doc, or a diff).
2. **Review** — invoke REVIEW-SKILL in REVIEW-MODE (report-only). Collect its findings.
3. **Verify** — apply VERIFY-CHECK to each finding before showing it to the person.
   Drop findings that fail verification; note why.
4. **Triage** — use the `triage` skill: establish surviving findings as prose chunks
   (What's wrong / Proposed fix / Why it works), then one AskUserQuestion picker in the
   same turn, batched <=4. The person decides Apply / Defer / Skip per finding.
5. **Apply** the Apply decisions.
6. **Record state** — write `last_applied` (highest severity applied this lap) and bump
   `lap` in the artifact frontmatter, so a compaction cannot lose the re-lap decision.
7. **Re-lap trigger** — if a P0 or P1 finding was applied this lap, return to step 2.
   Otherwise go to step 8. (The person may override in either direction.)
8. **Exit** when EXIT-SIGNAL reports clean.
9. **Bound** — halt and hand to the person if `lap` reaches the cap (default 5), or if this
   lap's finding set is not a strict subset of the previous lap's (no progress). Never loop
   unbounded.
```

- [ ] **Step 2: Verify it references no undefined skill and states all 4 params**

Run: `grep -E "REVIEW-SKILL|REVIEW-MODE|EXIT-SIGNAL|VERIFY-CHECK" skills/_shared/review-loop.md`
Expected: all four param names present; the file names only `triage` as a concrete skill dependency.

- [ ] **Step 3: Commit**

```bash
git add skills/_shared/review-loop.md
git commit -m "feat: shared review-loop shape (written once, read-only at runtime)"
```

---

### Task 4: `triage` skill

**Files:**
- Create: `skills/triage/SKILL.md`

**Interfaces:**
- Produces: the `spec-triage-loop:triage` skill, consumed by `_shared/review-loop.md` step 4 and by the person directly.

- [ ] **Step 1: Write `skills/triage/SKILL.md`** frontmatter + body

Frontmatter (exact):

```markdown
---
name: triage
description: Use when asking the person any question that needs a decision — establish findings/context as prose chunks first, then emit an AskUserQuestion picker in the SAME turn. Governs review-finding walk-throughs and any multi-option decision. Not code-specific.
---
```

Body must specify, as imperative rules: (1) chunks first, picker same turn; (2) lean question references its chunk; (3) batch ≤4, always a defer option; (4) no ghost references — the chunk exists in the same or immediately-preceding message; (5) generic language about "the person you are working with", zero personal data; (6) the review-findings walk (`📖 F-N` = What's wrong / Proposed fix / Why it works) as the worked example.

- [ ] **Step 2: Verify frontmatter is valid + language is generic**

Run: `head -4 skills/triage/SKILL.md` and `grep -iE "adhd|diagnos|medicat" skills/triage/SKILL.md`
Expected: valid `name`/`description`; the grep returns NOTHING (no personal/medical terms).

- [ ] **Step 3: Verify it loads after install**

Run: reinstall the plugin; confirm `spec-triage-loop:triage` appears in the available-skills list.
Expected: present.

- [ ] **Step 4: Commit**

```bash
git add skills/triage/
git commit -m "feat: triage skill — chunk-then-picker asking discipline (generic)"
```

---

### Task 5: `doc-review-loop` skill

**Files:**
- Create: `skills/doc-review-loop/SKILL.md`

**Interfaces:**
- Consumes: `skills/_shared/review-loop.md` (the procedure); `spec-triage-loop:triage`; `compound-engineering:ce-doc-review`.
- Produces: `spec-triage-loop:doc-review-loop`.

- [ ] **Step 1: Write `skills/doc-review-loop/SKILL.md`**

Frontmatter (exact):

```markdown
---
name: doc-review-loop
description: Use to review any document (spec, plan, design, RFC) until clean. Composes compound-engineering:ce-doc-review in headless mode, verifies findings, triages them with the person, applies, and re-reviews until clean. Use before merging a doc, or whenever asked to review a doc thoroughly.
---
```

Body must: (1) read `_shared/review-loop.md` and bind params — REVIEW-SKILL = `compound-engineering:ce-doc-review`, REVIEW-MODE = `mode:headless`, EXIT-SIGNAL = the headless `Review complete` envelope with `Proposed fixes` AND `Decisions` buckets empty (cite `synthesis-and-presentation.md`, NOT `walkthrough.md`), VERIFY-CHECK = doc-specific (finding cites a real section, quote is verbatim, fix doesn't contradict another section); (2) invoke `ce-doc-review` as `Skill("compound-engineering:ce-doc-review", "mode:headless <path>")`.

- [ ] **Step 2: Verify the composition + mode are correct**

Run: `grep -E "ce-doc-review|mode:headless|synthesis-and-presentation" skills/doc-review-loop/SKILL.md`
Expected: all three present; `walkthrough.md` is NOT cited as the exit source.

- [ ] **Step 3: Smoke test — compose on a fixture doc**

Run: follow the skill against a tiny throwaway doc; confirm it invokes `ce-doc-review` in headless mode and reaches an exit decision without CE firing its own interactive picker.
Expected: headless envelope parsed; no deadlock.

- [ ] **Step 4: Commit**

```bash
git add skills/doc-review-loop/
git commit -m "feat: doc-review-loop — ce-doc-review headless, bounded, triaged"
```

---

### Task 6: `code-review-loop` skill

**Files:**
- Create: `skills/code-review-loop/SKILL.md`

**Interfaces:**
- Consumes: `_shared/review-loop.md`; `spec-triage-loop:triage`; `compound-engineering:ce-code-review`; `superpowers:receiving-code-review`; `superpowers:subagent-driven-development` (for the model-tiered produce phase).
- Produces: `spec-triage-loop:code-review-loop`.

- [ ] **Step 1: Write `skills/code-review-loop/SKILL.md`**

Frontmatter (exact):

```markdown
---
name: code-review-loop
description: Use to review any code diff until clean. Composes compound-engineering:ce-code-review in agent mode, verifies findings with superpowers:receiving-code-review, triages with the person, applies, and re-reviews until clean. Its produce phase configures superpowers' existing model tiering for cheap-model implementers.
---
```

Body must: (1) bind params — REVIEW-SKILL = `compound-engineering:ce-code-review`, REVIEW-MODE = `mode:agent` (report-only; never default mode, which self-applies+commits), EXIT-SIGNAL = `verdict` / `actionable_findings` from the returned JSON, VERIFY-CHECK = `superpowers:receiving-code-review` (External-Reviewer branch); (2) for the produce phase, compose `superpowers:subagent-driven-development` and **use its `## Model Selection`** — pass the cheap tier for mechanical implementers while the orchestrator stays on the capable model. Do NOT build a new executor.

- [ ] **Step 2: Verify mode + no-rebuild**

Run: `grep -E "ce-code-review|mode:agent|receiving-code-review|Model Selection" skills/code-review-loop/SKILL.md`
Expected: all present; body says "configure"/"use" superpowers' Model Selection, not "replace"/"rebuild".

- [ ] **Step 3: Smoke test — compose on a fixture diff**

Run: follow the skill against a trivial diff; confirm it invokes `ce-code-review` in `mode:agent` (report-only, tree not mutated) and reads `verdict`.
Expected: JSON verdict parsed; working tree untouched by the review.

- [ ] **Step 4: Commit**

```bash
git add skills/code-review-loop/
git commit -m "feat: code-review-loop — ce-code-review agent mode + superpowers model tiering"
```

---

### Task 7: Public-repo hygiene (README, .gitignore, AGENTS.md check)

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Verify: `AGENTS.md` (already present) still states the docs convention + public-repo rule

**Interfaces:**
- Consumes: everything above (README documents installed behavior).

- [ ] **Step 1: Write `.gitignore`**

```gitignore
.DS_Store
```

- [ ] **Step 2: Remove any already-tracked `.DS_Store`**

Run: `git rm --cached -r --ignore-unmatch $(git ls-files '*.DS_Store')`
Expected: any tracked `.DS_Store` files are untracked (no-op if none).

- [ ] **Step 3: Write `README.md`** — lead with the SIMPLE story (product-lens advisory)

Open with the one-line value ("one hook makes review always-on; two loops review any doc/diff until clean"), then Install (the two `/plugin` commands), then the three skills, then a "How it composes" note (superpowers + compound-engineering, tier-1 Skill tool), then a link to `docs/specs/…` and `TODO.md` for depth. No personal data.

- [ ] **Step 4: Verify AGENTS.md still holds**

Run: `grep -iE "no personal|neutral|docs/specs" AGENTS.md`
Expected: the docs convention + public-repo rule are present.

- [ ] **Step 5: Commit**

```bash
git add README.md .gitignore
git commit -m "chore: public-repo hygiene — README (simple story first), gitignore .DS_Store"
```

---

## Self-Review

**1. Spec coverage.** Each spec section → a task: §2 What ships → Tasks 1,2,3,4,5,6,7; §3 three skills → Tasks 4,5,6; §4 loop (verify split, bound, re-lap) → Task 3 (`_shared`); §5 composition tier-1 → Tasks 5,6; §6 family rule → informs §3 skill bodies (documented, not code); §7 paths/state frontmatter → Task 3 steps 6/9; §8 staged / §9 open → intentionally NOT implemented (TODO.md). No v1 gap.

**2. Placeholder scan.** JSON manifests, hook script, and `_shared/review-loop.md` are given verbatim. The three SKILL.md bodies specify exact frontmatter + an enumerated rule list rather than full prose — acceptable because the skill *is* the deliverable authored during execution, and each rule is concrete and checkable; not "TODO"/"handle edge cases".

**3. Type consistency.** Param names (`REVIEW-SKILL`, `REVIEW-MODE`, `EXIT-SIGNAL`, `VERIFY-CHECK`) are identical in Task 3's `_shared/review-loop.md` and in Tasks 5/6 that bind them. Skill invocation names (`compound-engineering:ce-doc-review`, `compound-engineering:ce-code-review`, `superpowers:receiving-code-review`, `superpowers:subagent-driven-development`) are consistent across tasks and match the spec.

**Dependencies:** Task 1 → all. Task 3 → Tasks 5, 6. Task 4 → Tasks 5, 6 (they call `triage`). Tasks 5, 6, 7 independent of each other. Suggested order: 1 → 2 → 3 → 4 → 5 → 6 → 7.
