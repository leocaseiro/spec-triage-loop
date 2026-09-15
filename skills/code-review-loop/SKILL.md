---
name: code-review-loop
description: Use to review any code diff until clean. Composes compound-engineering:ce-code-review in agent mode, verifies findings with superpowers:receiving-code-review, triages with the person, applies, and re-reviews until clean. Its produce phase configures superpowers' existing model tiering for cheap-model implementers.
---

# code-review-loop — review any diff until clean

## Overview

Run the shared review loop with a code diff as the artifact. The review engine is
`compound-engineering:ce-code-review` in **`mode:agent`** (report-only — it returns JSON and
never touches the working tree), so applying stays the person's decision via `triage`, not the
review skill's own auto-commit.

**Announce at start:** "Using code-review-loop to review <diff> until clean."

## The procedure

Read `../_shared/review-loop.md` (the shared loop shape) and run it with these four
parameters bound:

- **REVIEW-SKILL** = `compound-engineering:ce-code-review`
- **REVIEW-MODE** = `mode:agent` — report-only. Invoke it as:

      Skill("compound-engineering:ce-code-review", "mode:agent")

  (append a `pr:<n>` or `base:<ref>` scope token after `mode:agent` to target a PR or base;
  blank reviews the current branch.) `mode:agent` buys JSON rather than markdown, so
  EXIT-SIGNAL is parseable — bare mode is already report-only. **Never pass `apply:local`:**
  that token is ce-code-review's only local-mutation authority (its Stage 5c), and it would
  bypass the person's triage decision. Without it the reviewer mutates nothing.
- **EXIT-SIGNAL** = the returned JSON object (one raw JSON value, emitted with no code fence).
  The diff is clean when `verdict` is `"Ready to merge"` **and** `actionable_findings` is
  empty. A `verdict` of `"Ready with fixes"` / `"Not ready"`, or a non-empty
  `actionable_findings`, means not clean — apply, then re-lap. Apply from `actionable_findings`
  only; never from `triage_groups`, which is a triage lens over *all* findings, not an apply
  queue (it can list advisory / human-owned findings you must not apply).
- **VERIFY-CHECK** = `superpowers:receiving-code-review`, its **From External Reviewers**
  branch. ce-code-review is an external reviewer here, so run each finding through those checks
  — verify it against codebase reality, ask whether it actually breaks anything, and whether
  the reviewer is missing context — before it is shown to the person. Drop findings that fail;
  note why.

## Produce phase — configure, do not rebuild

The loop's produce / apply step implements the person's Apply decisions. Do **not** build a new
executor for this. Compose `superpowers:subagent-driven-development` and use its existing
`## Model Selection`:

- Mechanical implementers (1-2 files, complete spec — most applied fixes) → the **cheap**
  model tier.
- The orchestrator (this loop, which holds the judgment and the broad context) stays on the
  **most capable** model.
- Always specify the model explicitly when dispatching a subagent, per that skill.

Model tiering is not re-implemented here — this skill only *selects the tiers* from
superpowers' existing mechanism.

## Notes

- The re-lap trigger, the on-disk state (`last_applied` + `lap`), and the lap-cap /
  no-progress bound all live in `../_shared/review-loop.md`. Code carries no frontmatter, so
  that state rides on the plan / spec driving the change (spec §7).
- Because `mode:agent` never mutates the tree, a re-review always runs against exactly what
  you applied — never against something the reviewer silently changed underneath you.
- `triage` (step 4 of the shared loop) walks the surviving findings past the person as
  chunks-then-picker. Load it if it is not already active.
