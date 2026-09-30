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

**Entry rule.** On invocation, look for a findings artifact for this artifact that is not yet
marked triaged — **including one a previous triage half left partly decided at the cap**. If one
exists, start at **step 4**, on its undecided findings only. Otherwise start at **step 1**.

**Cap the triage half at 12 findings, or 5 picker rounds — whichever comes first.** Then write
the undecided findings plus the decisions so far back to the artifact and stop, exactly as the
review half does. A finding that needed more than one picker round counts as two against the
finding cap. The cap is a ceiling, not a quota: a short list just finishes early.

Stopping at the cap leaves the artifact un-marked, so the entry rule sends the next invocation
back to step 4. **That is the same lap continuing, not a new one** — `lap` bumps only at step 6,
once every finding is decided. The undecided findings are already verified and carry their own
chunks, so they are picked up as they are and never re-reviewed. A long list therefore costs
more triage invocations, not more laps.

**In the triage half, read the findings artifact and nothing else.** Never re-open the source
document to compose a chunk — measured across real sessions, `Read` was 24.5% of all context
growth at ~17,500 tokens per call. The artifact carries each finding's Before → After inline
precisely so the triage half never has to.

**State the finding count in the artifact header**, so the cap is checkable at a glance
instead of by recount.

*Where 12 comes from.* Measured on the 2026-09-25 code-review triage: context entered the walk
at 149,680 tokens and each finding cost ~17,900 more, triage plus apply plus spikes plus
commits. Twelve therefore projects to ~364k — under the 374k median peak of sessions that use a
findings artifact, and well under the 558k worst case observed across nineteen of them. That
same session ran 21 findings to 472k without trouble, so 12 keeps real headroom. Re-measure
before moving it again.

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
triage half may not re-open the source to look one up), each fix's spike result from step 3
or the mark **(untested)**, every dropped finding with its drop reason, the already-applied
silent edits from step 2b, and the raw EXIT-SIGNAL. If the triage half cannot reconstruct the
whole walk-through from this file alone, the file is incomplete — go back and finish it
before stopping.

### Paths in the artifact must RESOLVE — three forms, and never a bare one

The loop runs across worktrees by design: the session doing the review often has a different
cwd from the worktree holding the document. So a repo-relative path in the artifact is not a
path — it is a path *fragment*, and the triage half, which may read only this file, will hand
that fragment to the person as if it were a location. Measured failure (2026-09-30): a triage
half printed `docs/plans/<doc>.md` as a resume command; the document was in a different
worktree entirely and the person could not find it.

`header` therefore carries **three** forms, and the review half fills all three:

```json
"artifact_path":            "docs/plans/<doc>.md",
"artifact_worktree":        "<worktree-dir-name>",
"artifact_path_from_root":  ".claude/worktrees/<worktree-dir-name>/docs/plans/<doc>.md",
"artifact_permalink":       "https://<host>/<owner>/<repo>/blob/<pushed-sha>/docs/plans/<doc>.md"
```

- **Tracked files get the repo-root-relative form.** `findings.json` is committed, and in a
  public repo it must leak nothing and stay portable across machines: never an absolute
  `/Users/<name>/...`, and not `~/<dir>/<repo>/...` either — that still hardcodes one layout.
  Any reader prepends its own repo root.
- **Chat gets the ABSOLUTE form**, built by prepending the real repo root at print time, in a
  code block, so the person can paste it into a terminal or a file dialog. This is the one
  place the absolute path belongs. Never print the bare `artifact_path` to a person.
- **The permalink is the always-resolvable second reference**, which means the artifact and
  the reviewed document must be **pushed before either half hands one over**. Record the sha
  the permalink pins.

**Both halves print the absolute path and the permalink when they hand over.** A resume
command whose path resolves against the wrong worktree sends the next lap at a file that is
not there.

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
   **Spike the fix, not only the finding.** VERIFY-CHECK confirms the *Before* exists; it never
   runs the *After*. Where a proposed fix is cheap to try — it compiles, a test runs, one
   command answers — have that same subagent apply it on a throwaway branch and report whether
   it holds. Carry the result into the artifact, and mark any fix that could not be tried
   **(untested)**, so triage can say so in the option rather than implying it was checked.
   **Then commit, push, write the artifact and STOP.** Push before you hand over, so the
   permalink resolves. Tell the person the lap is half done, how many findings survived
   verification, and the exact command that resumes it — carrying the **absolute** path to
   the document (a code block, built from the real repo root, naming the worktree that
   actually holds it) plus its permalink, never the bare repo-relative fragment. Do not begin the
   walk-through in this session, however much context appears to be left.

## Triage half (invocation B)

4. **Triage** — use the `triage` skill: establish surviving findings as prose chunks
   (The scenario / What's wrong / Before → After / Proposed fix / Why it works — every
   finding opens with the scenario and *shows* the change), then one AskUserQuestion
   picker in the same turn,
   batched <=4. The person decides Apply / Skip — decide later / Drop per finding.
5. **Apply** the Apply decisions.
5b. **Apply as you go, not at the end.** Steps 4 and 5 interleave: apply each batch's Apply
   decisions right after that picker round, each as its own commit, before the next round. The
   cap and the ≤4-per-round batching make a single apply-everything-at-the-end pass impossible,
   and a per-batch commit keeps every decision revertable on its own.
6. **Record state** — write `last_applied` (highest severity applied this lap) and bump
   `lap` to STATE-STORE, so a compaction cannot lose the re-lap decision. Mark the lap's
   findings artifact triaged, so the entry rule does not re-enter this half. **Only when every
   finding is decided.** At the cap you write partial state instead — decisions so far plus the
   undecided findings — and neither bump `lap` nor mark the artifact triaged.
7. **Decide the lap** — **only once this lap's artifact has no undecided findings left.**
   If any remain — you stopped at the cap — you are NOT at step 7: apply what was decided,
   write the partial state, and end the session so the next invocation resumes at step 4.
   Stopping at the cap **pauses** the triage half; it never completes it. "A P1 was applied"
   is true from the first applied P1 onward, so it can never be your reason to move on while
   findings are still undecided. The person may choose to re-lap early — but only by saying
   so: ask, name what is still undecided, and never assume it. Then evaluate in order:
   a. **Bound first** — halt and hand to the person if `lap` reached the cap (default 5), or
      if this lap did not reduce the count of unresolved P0/P1 findings (no progress).
      Identify findings across laps by section + title; lap 1 has no previous set and never
      trips this.
   b. **Re-lap** — if a P0 or P1 was applied this lap, or EXIT-SIGNAL is not clean, return
      to step 2 — **as a new invocation**, never by continuing this one. A re-lap starts a
      fresh review half.
      **Carry the undecided forward.** If the person overrode the gate to re-lap with
      findings still open, copy those findings into lap N+1's artifact before the review
      runs, keeping their ids and severities. They are already verified — they get triaged
      alongside the new findings, are never re-reviewed, and are never left behind in a file
      nothing reads again. "Skip — decide later" is a promise that later exists.
   c. **Exit** — EXIT-SIGNAL reports clean and nothing above fired.

   (The person may override in either direction.) Never loop unbounded.
