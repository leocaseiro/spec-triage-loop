# The review loop (shared)

The calling skill supplies five parameters: REVIEW-SKILL, REVIEW-MODE,
EXIT-SIGNAL, VERIFY-CHECK, STATE-STORE. Run this procedure.

## Context guardrail — every lap is two invocations

A lap splits at the verify boundary, and the two halves do **not** share a session:

```text
invocation A — REVIEW half   steps 1-3   writes findings.json, then STOPS
invocation B — TRIAGE half   steps 4-7   reads findings.json, and little else
```

**Why.** The review half fills a context window with machinery the triage half has no
use for: the review skill's own instructions, its subagent template and findings schema,
persona selection, raw reviewer payloads, verification output. Triage is the
judgment-heavy half — it decides what lands in the person's artifact — and it must not
inherit that load. The split is **structural, not a threshold**: nothing has to read a
context gauge, which the model cannot do anyway.

**Entry rule.** On invocation, look for an untriaged findings artifact for this artifact.
If one exists, start at **step 4**. Otherwise start at **step 1**.

**The artifact.** `.spec-triage-loop/<artifact-slug>/lap-<n>/findings.json`, relative to
the repo root. It must carry everything the triage half needs, because that half will not
re-read the review: the artifact path, the lap number, REVIEW-SKILL and REVIEW-MODE, every
verified finding (What's wrong / Before → After / Proposed fix / Why it works, plus
severity and evidence quotes), every dropped finding with its drop reason, the
already-applied silent edits from step 2b, and the raw EXIT-SIGNAL. If the triage half
cannot reconstruct the whole walk-through from this file alone, the file is incomplete —
go back and finish it before stopping.

## Review half (invocation A)

1. **Produce/hold** the artifact under review as a **committed, green checkpoint** (a doc, or
   a committed diff). Commit before you review: review runs on the committed diff, never the
   uncommitted working tree, so every lap has a durable, revertable baseline.
2. **Review** — invoke REVIEW-SKILL in REVIEW-MODE. Collect its findings. The doc engine is
   NOT fully report-only: `ce-doc-review mode:headless` writes its anchor-100 `safe_auto`
   fixes into the document silently, before you see them.
2b. **Catch the silent edits** — read the envelope's `Applied N fixes:` list, run VERIFY-CHECK
   over each against step 1's commit, and carry them into step 4 as already-applied
   (revertable) items. Fold their severity into step 6's `last_applied`.
2c. **Failure branch** — if the review returned `Review failed: …` (doc loop — no
   `Review complete` line) or a JSON object whose `status` is `failed`, `skipped` or
   `degraded` (code loop — no `verdict` key), halt immediately and hand the returned `reason`
   to the person. Do not count the lap, do not re-lap, and never read an absent envelope as a
   not-clean result.
3. **Verify** — apply VERIFY-CHECK to each finding before showing it to the person.
   Drop findings that fail verification; note why.
   **Then write the artifact and STOP.** Tell the person the lap is half done, how many
   findings survived verification, and the exact command that resumes it. Do not begin the
   walk-through in this session, however much context appears to be left.

## Triage half (invocation B)

4. **Triage** — use the `triage` skill: establish surviving findings as prose chunks
   (What's wrong / Before → After / Proposed fix / Why it works — every finding *shows* the
   change, never only describes it), then one AskUserQuestion picker in the same turn,
   batched <=4. The person decides Apply / Skip — decide later / Drop per finding.
5. **Apply** the Apply decisions.
6. **Record state** — write `last_applied` (highest severity applied this lap) and bump
   `lap` to STATE-STORE, so a compaction cannot lose the re-lap decision. Mark the lap's
   findings artifact triaged, so the entry rule does not re-enter this half.
7. **Decide the lap** — evaluate these in order, every lap:
   a. **Bound first** — halt and hand to the person if `lap` reached the cap (default 5), or
      if this lap did not reduce the count of unresolved P0/P1 findings (no progress).
      Identify findings across laps by section + title; lap 1 has no previous set and never
      trips this.
   b. **Re-lap** — if a P0 or P1 was applied this lap, or EXIT-SIGNAL is not clean, return
      to step 2 — **as a new invocation**, never by continuing this one. A re-lap starts a
      fresh review half.
   c. **Exit** — EXIT-SIGNAL reports clean and nothing above fired.

   (The person may override in either direction.) Never loop unbounded.
