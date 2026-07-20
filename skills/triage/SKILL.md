---
name: triage
description: Use when asking the person any question that needs a decision — establish findings/context as prose chunks first, then emit an AskUserQuestion picker in the SAME turn. Governs review-finding walk-throughs and any multi-option decision. Not code-specific.
---

# Triage — how to put a decision to the person

## Overview

Every question, confirmation, or decision you put to the person is an `AskUserQuestion`
picker — never a prose "reply 1-4". The context that makes the decision legible lives in
short prose chunks you write FIRST; the picker stays lean and references them. This keeps
the choice scannable and lets the person drive without hunting for context.

## The rules

1. **Chunks first, picker in the SAME turn.** Establish findings/context as short prose
   chunks, then emit the `AskUserQuestion` tool call in the *same* turn. Never end the turn
   after the chunks — there is no automatic next message, so a promised picker never fires.
   Never replace the picker with a prose "answer 1-4" list.
2. **Lean question references its chunk.** The question + option text must be decidable on
   their own (in case the lead-in is visually collapsed), and reference the chunk by a
   stable label (e.g. `(see F-3)`) for depth. Keep the question under ~150 characters.
3. **Batch ≤ 4, always a defer option.** Up to four sub-questions per call, each with its
   own 2-4 options; the person answers each independently. Include a "Defer for later"
   option whenever there is room. More than four → multiple sequential rounds, not a
   bundled mega-question.
4. **No ghost references.** If the question says `(see F-3)`, the chunk `F-3` MUST exist in
   the same message or the immediately-preceding one. Before sending, confirm it is actually
   there. Never reference a chunk you did not write.
5. **Generic + private.** Write about "the person you are working with." Put no personal or
   sensitive data about them into any skill, artifact, or committed file. Describe working
   preferences neutrally, never with a label.
6. **A skipped picker is not consent.** If the harness records a skip / no-preference, that
   means "not ready to answer" — not "you choose". Do the parts that do not depend on it,
   say plainly what is parked and what it blocks, and do not loop re-asking.

## Worked example — walking review findings

When the decision is "which of these findings do I apply?", establish each finding as a
labelled chunk FIRST, then ask in lean batched questions.

Establish (prose, one chunk per finding):

```
### 📖 F-3 — <short title>
**What's wrong:** the concrete issue (with a line / section ref).
**Proposed fix:** the specific change to make.
**Why it works:** why that fix resolves it.
```

Then ask (same turn, ≤ 4 per call, each referencing its chunk):

```
[Q-F3] F-3 — <short title> (see 📖 F-3). Apply?
   - Apply — <the change>
   - Defer — park it for later
   - Skip — drop it
```

Each finding is explained once (in the chunk); each question references its chunk; the
option set stays consistent across the batch. An "Auto-resolve rest" option is a good
escape hatch when the person trusts the recommendations and wants to skip ahead.

## Red flags — stop, you are about to break the discipline

| Thought | Reality |
|---------|---------|
| "I'll ask in the next message." | There is no next message. Emit the picker THIS turn. |
| "I'll just list the options in prose." | A decision is a picker, not a prose "answer 1-4". |
| "(see F-9)" — but F-9 isn't written yet | Ghost reference. Write the chunk first, or drop the ref. |
| "They skipped, so I'll pick for them." | Skip = not ready, not delegation. Park it, move on. |
| "I'll record a private detail for context." | Never. Generic, neutral, zero personal data. |
