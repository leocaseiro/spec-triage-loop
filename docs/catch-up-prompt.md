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

2. Apply it from here on. These four rules are new since you started:

   §1  Before asking, check it IS a decision.
       - SPIKE anything you have not actually run, then come back with the result.
         A picker built on a guess spends my judgment on a question you owned.
         Mark anything you genuinely could not test as (untested).
       - Make ambiguity-only changes WITHOUT asking me — naming, stale comments,
         missing units, undefined terms, typos. Just say you did. The test is
         whether it changes behaviour, scope, or a real trade-off; not diff size.

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

If you are mid-lap in doc-review-loop or code-review-loop, also re-read
skills/_shared/review-loop.md: step 3 now spikes each fix (not just the finding),
and the artifact must carry a scenario plus each fix's spike result.

If the Skill tool is unavailable here, follow the four rules above as written.
```

## Short prompt

Use this when the session only needs a nudge.

```text
Re-run Skill("spec-triage-loop:triage") — the file changed on disk, your copy is
stale, and it re-reads from disk. New since you started: spike anything untried
before asking me; make ambiguity-only fixes without asking; expand every document
id (F-2, P1, Task 10) into what it IS; open each finding with a second-person
scenario; one decision = one self-contained message, never a file.
```

## What each rule is, and when it landed

| Rule | What it fixes | Landed |
|------|---------------|--------|
| §1 spike the untried | Pickers built on guesses; approved fixes that then fail to compile | 2026-09-26 |
| §1 ambiguity-only fixes need no approval | Approval requests that cost more attention than the change | 2026-09-26 |
| §3 expand document-local ids | `F-2`, `Task 10`, `P1` arriving bare, meaningless outside the source | 2026-09-18 |
| §10 open with the scenario | Findings that open with the mechanism, readable only to whoever wrote them | 2026-09-26 |
| §12 one self-contained message | One decision split across a chunk, a file, the source doc and the picker | 2026-09-18 |

Both prompts work from any project — the plugin is symlinked into `~/.claude/skills`.

**When the rules change again,** update the prompts here rather than writing a new note, and
add a row to the table above.
