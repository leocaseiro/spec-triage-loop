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
