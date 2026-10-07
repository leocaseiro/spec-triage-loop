# Catching up an ongoing session

A session loads the `triage` skill once and carries that copy for the rest of its life. The
`SessionStart` hook fires only on `startup|clear|compact`. So when these rules change, every
session already running keeps working from the old text — silently, with no error.

Paste one of the prompts below into such a session.

**The re-load works.** The `Skill` tool reads the file from disk at invocation time; there is
no cache and no build step, so re-invoking pulls the current version even in a session that
loaded an older one. Verified 2026-09-26 by invoking it immediately after an edit and
confirming the new text came back.

## Full prompt

Use this when the session is mid-task and you want it to actually re-read the rules.

```text
The spec-triage-loop rules changed on disk since this session started. Whatever you
have in context — the SessionStart hook summary, or an earlier load of the triage
skill — is STALE. Do not work from it.

Before your next question to me:

1. Run Skill("spec-triage-loop:triage"). It re-reads the file from disk, so this
   pulls the current version even if you loaded it earlier in this session. Read it
   in full. Do not skip it on the grounds that you already know it — you have an
   older copy.

2. Apply it from here on. These rules are new since you started:

   §1  Before asking, check it IS a decision.
       - SPIKE anything you have not actually run, then come back with the result.
         A picker built on a guess spends my judgment on a question you owned.
         Mark anything you genuinely could not test as (untested).
       - Make ambiguity-only changes WITHOUT asking me — naming, stale comments,
         missing units, undefined terms, typos. Just say you did. The test is
         whether it changes behaviour, scope, or a real trade-off; not diff size.

   §2  A run of P2/P3 findings goes in ONE multiSelect card, not one card each.
       Every option is exactly "Approve F-N (recommended)", its description naming
       the finding in plain words — never a compressed before → after, never a
       truncated rationale. The context still goes in the chat as one 📖 chunk per
       finding. Say in the question text that an unchecked box leaves the finding
       OPEN for a later round and is never a Drop. Four findings per card maximum.
       P0 and P1 always keep their own card.

   §8  Show the REVIEWER'S CONFIDENCE next to the severity, in every chunk header and
       every question. The engines score each finding 100 / 75 / 50 and it never used to
       reach me. 100 = the reviewer confirmed it; 75 = inferred from reading, not run;
       50 = a suspicion, not a finding. Expand it, never ship the bare number.
       §1 adds the trigger: a 50 must be SPIKED before you ask me, or put to me labelled
       a suspicion with the spike you could not run named. Spike a 75 when that is cheap.

   §3  Expand every document-local identifier on first use: F-2, Task 10, R5, P1,
       §4.2. I have not opened your source and cannot look one up from inside the
       picker. Tell me what the thing IS, not the bare number.

   §10 Open every finding with THE SCENARIO, before any mechanism — a short
       second-person walk-through of what I am doing and what I see go wrong.
       Concrete, no jargon. Then What's wrong / Before → After / Proposed fix /
       Why it works. Carry the scenario into the Drop option too.

   §12 One decision = ONE self-contained message. Quote the source text inline
       instead of telling me where to find it. Never write a file to ask me
       something — put it in the chat message, picker in the SAME turn.

3. If you are running doc-review-loop or code-review-loop, re-read
   skills/_shared/review-loop.md as well. What changed there:

   - NEVER start a new lap while any finding is undecided. Stopping at the cap
     PAUSES the triage half — it does not complete it. "A P0 or P1 was applied"
     is true from the first applied P1 onward, so it is never your reason to move
     on. If an early re-lap is worth it, ask me and name what is still open.
   - The triage cap is 12 findings (was 8), or 5 picker rounds.
   - Apply per batch, right after each picker round, each as its own commit —
     not one apply pass at the end.
   - An artifact left partly decided resumes at step 4 on its undecided findings.
     That is the same lap continuing, not a new one, and they are never
     re-reviewed.
   - If I do override and you re-lap early, copy the undecided findings into the
     next lap's artifact, ids and severities intact.
   - Hand off between halves with /compact, not a brand-new session — I prefer it and
     the loop now says so. The split protects the CONTEXT, not the session's identity;
     the hook re-fires on compact and the artifact is on disk. Write the artifact
     BEFORE compacting: a compaction summary is lossy, the artifact is the contract.
   - The artifact must carry each finding's confidence score, not just its severity.

If the Skill tool is unavailable here, follow the rules above as written.
```

## Short prompt

Use this when the session only needs a nudge.

```text
Re-run Skill("spec-triage-loop:triage") — the file changed on disk, your copy is
stale, and it re-reads from disk. New since you started: spike anything untried
before asking me; make ambiguity-only fixes without asking; expand every document
id (F-2, P1, Task 10) into what it IS; open each finding with a second-person
scenario; one decision = one self-contained message, never a file; batch P2/P3
findings into one multiSelect card whose options are just "Approve F-N
(recommended)"; and show each finding's reviewer confidence (100/75/50) next to its
severity, spiking any 50 before you ask me. If you are mid-lap: never start a new lap
while any finding is undecided — the cap pauses triage, it does not finish it — the cap
is now 12, apply per batch with its own commit, and hand off with /compact rather than a
new session.
```

## What each rule is, and when it landed

| Rule | What it fixes | Landed |
|------|---------------|--------|
| §1 spike the untried | Pickers built on guesses; approved fixes that then fail to compile | 2026-09-26 |
| §1 ambiguity-only fixes need no approval | Approval requests that cost more attention than the change | 2026-09-26 |
| §2 multi-select for P2/P3 runs | Eleven cosmetic findings arriving as eleven separate cards | 2026-09-26 |
| §3 expand document-local ids | `F-2`, `Task 10`, `P1` arriving bare, meaningless outside the source | 2026-09-18 |
| §10 open with the scenario | Findings that open with the mechanism, readable only to whoever wrote them | 2026-09-26 |
| §12 one self-contained message | One decision split across a chunk, a file, the source doc and the picker | 2026-09-18 |
| loop: never re-lap with findings open | A lap that decided 8 of 25 and started the next lap anyway | 2026-09-26 |
| loop: cap 8 → 12 | 25 findings needing 3–4 sittings, which made "move on" tempting | 2026-09-26 |
| loop: apply per batch | Written order said triage-all-then-apply, which the cap makes impossible | 2026-09-26 |
| loop: resume a partial artifact | A partly decided artifact matching neither "triaged" nor "untriaged" | 2026-09-26 |
| loop: carry undecided across an override | Deferred findings stranded in a file nothing reads again | 2026-09-26 |
| §8 show reviewer confidence | 63% of findings are only 75% sure; 0 of 2,280 questions said so | 2026-10-08 |
| §1 spike a confidence-50 finding | A suspicion arriving in the same voice as a confirmed defect | 2026-10-08 |
| loop: /compact is the preferred handoff | "must not share a session" read as banning the compact workflow | 2026-10-08 |

Both prompts work from any project — the plugin is symlinked into `~/.claude/skills`.

**When the rules change again,** update the prompts here rather than writing a new note, and
add a row to the table above.
