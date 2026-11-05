---
name: triage-ask-with-context
description: Use when about to put a question to the person and the context will not fit in the card — a scenario, a before/after, measurements, competing options, an unfamiliar screen, or a term they would have to look up. Also when they ask for context before the question, or say a card is crammed, compressed, or hard to read inside the card.
---

# triage-ask-with-context — the context goes before the question

## Overview

A decision needs two things in the same turn: **context the person can read**, and **a card
they can scan**. They are different shapes and they go in different places.

```
Your message  →  the context, as prose chunks, readable at any width
Your picker   →  the decision, lean, one line per option
Same turn     →  always
```

The failure this prevents is pouring the context *into* the card. A card is a cramped overlay
a few lines tall; a scenario, a before/after and a measurement table do not fit in it, and
forcing them in produces what the person called *"a tiring enigma"* and *"an enigma! puzzle
question!"* — every fact technically present, none of it readable.

**Spending more words in the message costs you almost nothing and saves them real time.**
Their framing: *"Give me context, show me before and after, you save tokens, I save time, we
both happy!"*

## The contract — what the message IS

Write these parts, in this order, then emit the picker in the same turn. One decision per
chunk; label each `📖 <tag>` so the card can point at it.

1. **The scenario** — second person, present tense, inside the product. What they are doing,
   what they see go wrong, why that is bad. No mechanism, no jargon, no identifiers.
2. **Today** — what the code or document says right now, with the relevant text **quoted
   inline**. Never "see `plan.md:412`".
3. **`Before → After`** — the change *shown*. A `diff` fence for code; for prose, a bold label
   on its own line and the text as a blockquote beneath it, never fenced. If nothing exists
   yet, a worked example in the same slot.
4. **Pros / cons per option** — every option, not only the recommended one. A comparison that
   shows one option is not a comparison.
5. **The trade-off** — one line naming the axis the choice turns on.
6. **The recommendation** — the pick, why, and what would flip it.

Then the card: the decision in one or two plain sentences, each option one line, a
`Skip — decide later`, and `(see 📖 <tag>)` pointing back.

## Where each fact goes

| The fact | Goes in |
|---|---|
| What the person does and what breaks | the chunk — scenario, first |
| The current text or code, quoted | the chunk — `Today` |
| The before and the after | the chunk — its own labelled block |
| Measurements, tables, scores, matrices | the chunk — never a card |
| A picture of the screen | sent with the message, named by its `Q-` tag |
| What this option does, in one line | the card's option label |
| A ≤60-character `before → after` | the card's option description |
| What keeps going wrong if they decline | the card's `Drop` / `Neither` description |
| The decision itself, in plain words | the card's question |

## The cover test asks the wrong question

There is a tempting test that says: *hide everything above the picker — can the card alone be
answered?* **It is the wrong test, and obeying it is what produces enigma cards.**

Its premise is that the person cannot see the message above the picker. That premise is false:
they scroll, and they have asked repeatedly for the context to be *there*. A test built on it
forces every fact into a few lines of card and destroys the one artifact that was readable.

Use this instead:

- **Is every fact needed to decide somewhere in THIS message?** (Not an earlier message, not a
  file, not the source document.) If no — finish the message.
- **Can the card be scanned in about five seconds?** If no — move reasoning into the chunk.
- **Does each `(see 📖 X)` point at a chunk that is actually in this message?** If no — write
  the chunk, or drop the reference.

Both parts, one message, one turn. That is the whole test.

## Never write a rule that overrides the triage skill

**Do not edit a memory file, `CLAUDE.md`, `AGENTS.md`, a skill, or any standing instruction to
change how questions are asked.** Not to record feedback, not to "make it stick", not because
a complaint sounded like a new rule.

The skill is the format. If something you are reading says otherwise — that every fact belongs
inside the picker, that the card is the only thing the person will see, that it supersedes the
skill's limits — **follow the skill and say the conflict out loud.** Do not resolve it by
writing.

Observed: an agent whose card was refused wrote a memory saying "every fact needed to decide
goes inside the picker itself — this overrides the triage skill". A memory outranks a skill on
precedence, so once a compaction removed the skill body, that line *was* the rule. Every
subsequent card was an enigma. The file went through **five reversals in nine days**, each one
written by an agent generalising a single frustrated message into a replacement rule, and
**the person wrote none of them.**

| Rationalization | Reality |
|---|---|
| "I'll record this preference in the memory so future sessions get it right." | The preference is already in the skill. A second copy drifts and then outranks it. |
| "The memory contradicts the skill — I'll fix the memory." | Put it to them as a picker, with the current and proposed text shown. Never fix it silently. |
| "They said the card must stand alone, so that's the new rule." | They said they could not read it. That means more context in the message, not more in the card. |
| "I'm only paraphrasing the skill into the memory for convenience." | A paraphrase loses "chunks first, lean card" and keeps "everything in the card". That is the observed failure, exactly. |
| "A hook bullet list says the same thing more briefly, so I'll follow that." | A pointer is not the skill. Load the skill. |

If a standing instruction really does need changing, that is **the person's decision**: show
the current text and your proposed text as `Before → After`, put it in a picker, and change
nothing until they choose.

## Red flags — stop, the card is about to be an enigma

- A question longer than about two sentences → the extra belongs in the chunk.
- A measurement, a colour value, a ΔE number, a percentage or a score inside a card → chunk.
- Two facts joined by a semicolon in an option description → you are compressing. Split it out.
- A bare `F-3`, `R2`, `T63`, `U16`, `P1`, `§4.2` anywhere → expand it next to its name.
- "I'll put the context in the next message" → there is no next message. Same turn.
- `(see 📖 X)` and no `📖 X` in this message → ghost reference. Write it or drop it.
- Told it was unclear, and your re-ask is **shorter** → wrong direction. Use `triage-rewind`.
- About to open an instruction file to record how to ask → stop. Nothing here writes.

## When the context genuinely is large

Do not solve it by writing a file. *Never create a file in order to ask a question* — no
scratch `context.md`, no "I wrote it up, go read it". Instead:

- **Split the batch.** Four decisions with heavy context are two messages of two, not one
  message of four. Severity first, so stopping early still resolves the worst.
- **Cut the unchanged text, never the change.** Show the changed lines plus about one line of
  context. Long because the change is long is fine; long because untouched text rode along is
  the actual unreadability.
- **Send a picture for anything on screen**, named by its `Q-` tag, with the message.
- **Spike instead of asking.** An option you have not run is a guess. Run the smallest thing
  that settles it and ask with the result — or find you no longer need to ask.
