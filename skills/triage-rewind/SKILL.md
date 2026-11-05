---
name: triage-rewind
description: Use when the person says your question is an enigma, a puzzle, too compressed, or that you are not following the triage skill — when they re-send the skill's name or path, trigger it repeatedly, say "more context please", "what is even your question", "I don't understand any of your questions", or refuse to answer at all. Recovers a failed ask.
---

# triage-rewind — recover a failed ask

## Overview

You are reading this because a question you put to the person failed. They could not read
your card, and they are telling you so — possibly for the second or third time.

**They are not asking you for format advice, and they are not asking you to make the question
shorter. They are refusing a card they could not read.** Recovery is mechanical. Follow the
six steps; do not improvise, do not defend the card, and do not write a single word into any
instruction file.

**The most likely cause is not your judgment — it is that you cannot see the triage skill any
more.** A compaction deletes the loaded skill body. Having loaded it earlier in this session
is not having it now. Step 2 fixes that before anything else.

## The procedure

1. **Stop. Do not re-ask yet.** No apology paragraph, no explanation of what you meant, no
   "let me clarify" that re-sends the same card with different words. One line is enough:
   *"The card was unreadable. Reloading the skill and re-asking properly."*

2. **Reload the skill, unconditionally:** `Skill("spec-triage-loop:triage")` — or
   `Skill("triage")` if these skills came from the skills CLI rather than the plugin. Do this
   **even if you believe you already loaded it this session.** You cannot tell from the inside
   whether a compaction removed it, and the cost of reloading when you did not need to is one
   tool call. The cost of not reloading is another refused question.

3. **Check what else is giving you orders.** Before you re-ask, look for any instruction —
   a memory file, a session summary, a hook's bullet list, a message from another session —
   that tells you to put every fact *inside* the picker, or that the card is the only thing
   the person will see, or that it overrides the triage skill. If you find one: **follow the
   skill, not the paraphrase, and say the conflict out loud in one line.** That paraphrase is
   the single most common cause of the card they just refused.

4. **Re-ask the same questions.** Not fewer. Not merged. Not "the important one first and the
   rest later". The same decisions, in full triage form: scenario, `Before → After` per
   option, pros/cons, the trade-off line, the recommendation, then the lean card — all in one
   turn (see the `triage` skill, and `triage-ask-with-context` for the shape).

5. **Shrinking is the wrong direction.** This is the failure this skill exists to stop. Told
   that a question was unclear, an agent's reflex is to compress it further — fewer words,
   more abbreviations, the reasoning deleted. That produces what the person called *"even
   harder… shrink into a enigma"* and *"a tiring enigma"*. **Unclear means under-explained,
   never over-long.** Add the scenario and the before/after you left out. Spend the words.

6. **Record the failed ask as a failure, not as a rule.** If the project logs answers, write
   the refused ask and the person's verbatim words there, marked as unanswered. Then re-ask.
   That is the whole of the bookkeeping.

## ⛔ Never rewrite an instruction file in response to this

**Do not touch a memory file, `CLAUDE.md`, `AGENTS.md`, a skill, or any other standing
instruction because a question failed.** Not to "capture the feedback", not to "make sure this
doesn't happen again", not even if the person's complaint sounds like a new rule.

This is the second failure mode, and it is worse than the first, because it is durable. The
observed chain: an agent's card was refused → the agent wrote a memory saying "every fact
needed to decide goes inside the picker" → a later agent obeyed that memory instead of the
skill → its card was refused → it rewrote the memory again. **Five reversals in nine days, in
one file, none of them asked for.** Each one read as a faithful summary of a real complaint
and each one made the next ask worse.

A complaint about one card is evidence that you did not follow the skill. It is not evidence
that the skill is wrong, and it is never authority to replace it.

If you genuinely believe a standing instruction needs changing, that is a **decision for the
person** — put it to them as its own picker, with the current text and your proposed text
shown (`Before → After`), and change nothing until they choose.

| Rationalization | Reality |
|---|---|
| "I should capture this feedback in the memory so it sticks." | The feedback is "follow the skill". Writing a new rule is how the skill got overridden in the first place. |
| "They said the card must be self-contained, so I'll record that." | They said they could not read it. Recording a card-shape rule is what produced five contradictory rules. |
| "This memory contradicts the skill — I'll update the memory to match what they just said." | Put the conflict to them as a picker. Never resolve it by writing. |
| "The old rule is clearly stale; I'll just replace it." | You are mid-failure and low on context. That is the worst possible moment to author a standing rule. |
| "I'll note it now and ask them later." | A written rule takes effect immediately and outlives this session. Ask first. |

## Red flags — stop, you are repeating the failure

- About to re-ask with **fewer** words than last time → you are shrinking. Step 5.
- About to skip the reload because "I loaded it an hour ago" → a compaction may have deleted
  it. Step 2 is unconditional.
- About to open a memory file, `CLAUDE.md`, or a skill → stop. Nothing in recovery writes.
- About to drop one of the questions to "reduce the load" → re-ask all of them. The person
  refused the *format*, not the agenda.
- About to write a paragraph explaining what you meant → they do not want the explanation,
  they want the question asked properly. One line, then the re-ask.
- About to ask them which format they would prefer → the format is in the skill. Load it.

## When the ask still fails

If a re-asked question is refused again, the missing piece is almost always one of these —
check in this order:

1. **No scenario.** The card describes a mechanism (a flag, a colour value, a rule id) instead
   of what the person does and what they see go wrong. Open with the walk-through.
2. **Described, not shown.** An option says what would change without showing the text or code
   before and after. Show it.
3. **A bare identifier.** `F-3`, `R2`, `T63`, `P1`, `U16` travelling alone. Expand each into
   what it *is*, next to the id.
4. **Context in an earlier message.** One decision = one self-contained message. Quote the
   source inline; never send them scrolling.
5. **You never ran it.** An option you have not tested is a guess, and they can tell. Spike it
   and re-ask with the result.
