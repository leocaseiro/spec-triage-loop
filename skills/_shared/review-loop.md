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

**Cap the triage half at 8 findings, or 5 picker rounds — whichever comes first.** Then write
the undecided findings plus the decisions so far back to the artifact and stop, exactly as the
review half does. A finding that needed more than one picker round counts as two. The cap is a
ceiling, not a quota: a short list just finishes early.

**In the triage half, read the findings artifact and nothing else.** Never re-open the source
document to compose a chunk — measured across real sessions, `Read` was 24.5% of all context
growth at ~17,500 tokens per call. The artifact carries each finding's Before → After inline
precisely so the triage half never has to.

**State the finding count in the artifact header**, so the cap is checkable at a glance
instead of by recount.

*Why a count and not a token budget: the model cannot observe its own context. There is no
gauge, no warning, and no auto-compact event before the ceiling — one sampled session reached
972,050 tokens without one — and roughly a third of all growth is thinking, which the model
neither chooses nor sees. A budget it cannot measure is a wish. If the harness ever exposes a
real gauge (a per-session token count that decreases monotonically, or a compaction warning),
switch to "hand off at 50% of the window" and demote this count to a backstop.*

**The artifact.** `.spec-triage-loop/<artifact-slug>/lap-<n>/findings.json`, relative to
the repo root. It must carry everything the triage half needs, because that half will not
re-read the review: the artifact path, the lap number, REVIEW-SKILL and REVIEW-MODE, every
verified finding (What's wrong / Before → After / Proposed fix / Why it works, plus
the scenario — what the person is doing and what they see go wrong, in their own terms,
written by THIS half while the source is still open, because the triage half cannot see it —
plus severity and evidence quotes, and a plain-language expansion of every document-local id it
names — `Task 10` → "the theming task, not started"; `P1` → "ships broken" — because the
triage half may not re-open the source to look one up), every dropped finding with its drop
reason, the already-applied silent edits from step 2b, and the raw EXIT-SIGNAL. If the
triage half cannot reconstruct the whole walk-through from this file alone, the file is
incomplete — go back and finish it before stopping.

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
3. **Verify — dispatch it, never inline.** Send the findings to a subagent that applies
   VERIFY-CHECK against the source and returns, per finding, a pass/fail plus the verbatim
   *Before* text it confirmed. Do not open the source document in this context: measured on a
   real lap, a reviewer burned 139,895 tokens of its own context and handed back 248, while an
   inline `Read` of the source costs ~17,500 every time. Drop findings that fail; record why.
   **Then write the artifact and STOP.** Tell the person the lap is half done, how many
   findings survived verification, and the exact command that resumes it. Do not begin the
   walk-through in this session, however much context appears to be left.

## Triage half (invocation B)

4. **Triage** — use the `triage` skill: establish surviving findings as prose chunks
   (The scenario / What's wrong / Before → After / Proposed fix / Why it works — every
   finding opens with the scenario and *shows* the change), then one AskUserQuestion
   picker in the same turn,
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
