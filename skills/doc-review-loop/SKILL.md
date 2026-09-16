---
name: doc-review-loop
description: Use to review any document (spec, plan, design, RFC) until clean. Composes compound-engineering:ce-doc-review in headless mode, verifies findings, triages them with the person, applies, and re-reviews until clean. Use before merging a doc, or whenever asked to review a doc thoroughly.
---

# doc-review-loop — review any document until clean

## Overview

Run the shared review loop with a document as the artifact. The review engine is
`compound-engineering:ce-doc-review` in **headless** mode (report-only), so its own
interactive routing question and per-finding walk-through never fire — putting the decision
to the person stays `triage`'s job.

**Announce at start:** "Using doc-review-loop to review <doc> until clean." Say which
half you are running — the review half or the triage half — so the person knows what this
invocation will and will not do.

## The procedure

Read `../_shared/review-loop.md` (the shared loop shape) and run it with these five
parameters bound. Apply its **context guardrail** first: every lap is two invocations
(review half → findings artifact → triage half), and its entry rule decides which half
this invocation is.

- **REVIEW-SKILL** = `compound-engineering:ce-doc-review`
- **REVIEW-MODE** = `mode:headless` — report-only. Invoke it as:

      Skill("compound-engineering:ce-doc-review", "mode:headless <path-to-doc>")

  Never call it without `mode:headless`: default/interactive mode fires ce-doc-review's own
  routing question and per-finding walk-through, which would deadlock the loop against our
  own triage picker.
- **EXIT-SIGNAL** = the headless envelope reports **clean**. ce-doc-review's headless output
  is documented in its `references/synthesis-and-presentation.md` (NOT
  `references/walkthrough.md`, which is the interactive path we are avoiding). That envelope
  ends with the terminal line `Review complete` and omits any section that has zero items.
  The doc is clean when the envelope carries **neither a `Proposed fixes` section nor a
  `Decisions` section** (both omitted ⇒ nothing actionable remains). An `FYI observations`
  section may still be present — those are observations, not decisions, and do not block exit.
- **VERIFY-CHECK** = doc-specific. ce's findings are prose claims about a document, so
  `superpowers:receiving-code-review` (code-scoped) does NOT apply here. Before a finding is
  shown to the person, confirm:
  1. it cites a section that actually exists in the doc;
  2. any quoted text is verbatim — it matches the doc character-for-character;
  3. its proposed fix does not contradict another section of the same doc.

  Drop findings that fail verification; note why they were dropped.
- **STATE-STORE** = the reviewed document's own YAML frontmatter (`last_applied`, `lap`). The
  document is the artifact, so its frontmatter is the natural home for the loop's state; if it
  has none, add it.

## Notes

- The re-lap trigger, the lap decision, and the lap-cap / no-progress bound all live in
  `../_shared/review-loop.md`. This skill only binds the five doc-specific parameters above.
- `triage` (step 4 of the shared loop) is what actually walks the surviving findings past
  the person as chunks-then-picker. Load it if it is not already active.
- Live composition smoke test: run this loop on this plugin's own `docs/plans/…-plan.md`
  after install — that is the intended dogfood and the first real exercise of the headless
  envelope parse.
