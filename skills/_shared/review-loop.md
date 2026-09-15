# The review loop (shared)

The calling skill supplies four parameters: REVIEW-SKILL, REVIEW-MODE,
EXIT-SIGNAL, VERIFY-CHECK. Run this procedure.

1. **Produce/hold** the artifact under review as a **committed, green checkpoint** (a doc, or
   a committed diff). Commit before you review: review runs on the committed diff, never the
   uncommitted working tree, so every lap has a durable, revertable baseline.
2. **Review** — invoke REVIEW-SKILL in REVIEW-MODE. Collect its findings. The doc engine is
   NOT fully report-only: `ce-doc-review mode:headless` writes its anchor-100 `safe_auto`
   fixes into the document silently, before you see them.
2b. **Catch the silent edits** — read the envelope's `Applied N fixes:` list, run VERIFY-CHECK
   over each against step 1's commit, and carry them into step 4 as already-applied
   (revertable) items. Fold their severity into step 6's `last_applied`.
3. **Verify** — apply VERIFY-CHECK to each finding before showing it to the person.
   Drop findings that fail verification; note why.
4. **Triage** — use the `triage` skill: establish surviving findings as prose chunks
   (What's wrong / Before → After / Proposed fix / Why it works — every finding *shows* the
   change, never only describes it), then one AskUserQuestion picker in the same turn,
   batched <=4. The person decides Apply / Skip — decide later / Drop per finding.
5. **Apply** the Apply decisions.
6. **Record state** — write `last_applied` (highest severity applied this lap) and bump
   `lap` in the artifact frontmatter, so a compaction cannot lose the re-lap decision.
7. **Re-lap trigger** — if a P0 or P1 finding was applied this lap, return to step 2.
   Otherwise go to step 8. (The person may override in either direction.)
8. **Exit** when EXIT-SIGNAL reports clean.
9. **Bound** — halt and hand to the person if `lap` reaches the cap (default 5), or if this
   lap did not reduce the count of unresolved P0/P1 findings (no progress). Identify findings
   across laps by section + title. Lap 1 has no previous set and never trips this. Never loop
   unbounded.
