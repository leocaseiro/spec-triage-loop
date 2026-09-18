---
name: triage
description: Use when asking the person any question that needs a decision — establish findings/context as prose chunks first, each showing a Before → After or worked example rather than only describing it, then emit an AskUserQuestion picker in the SAME turn. Governs review-finding walk-throughs, comparing alternatives, and any multi-option decision. Not code-specific.
---

# Triage — how to put a decision to the person

## Overview

Every question, confirmation, or decision you put to the person is an `AskUserQuestion`
picker — never a prose "reply 1-4". The context that makes a decision legible lives in short
prose chunks you write FIRST; the picker stays lean and references them. This keeps the choice
scannable and lets the person drive it without hunting for context. The rules below are the
whole discipline; follow all of them, not just the convenient ones.

## 1. Every decision is a picker

- Every question / confirmation / decision → an `AskUserQuestion` tool call. Never solicit a
  prose answer ("reply go", "say yes", "confirm below", "answer 1-4"). The only messages that
  stand without a picker are **pure notifications that need no answer**.
- **Emit the picker in the SAME turn** as any lead-in. Announcing "I'll ask below" and then
  ending the turn *strands* the picker — there is no automatic next message, so it never fires.

## 2. Batch as separate sub-questions — never bundle (the anti-pattern)

`AskUserQuestion` takes an array of 1–4 sub-questions, each with its own 2–4 options; the
person answers each independently. Never collapse several decisions into one question's options.

```text
❌ anti-pattern — one question, bundled options (destroys per-decision granularity):
   [Q] Approve §4, §5, §6?
      - Approve all   - Approve some   - Reject all
   → the person can't say "approve §4 and §5 but defer §6".

✅ correct — an array of separate sub-questions, each with its own options:
   [Q-§4.ack] Approve §4?  → LGTM / Comments / Defer
   [Q-§5.ack] Approve §5?  → LGTM / Comments / Defer
   [Q-§6.ack] Approve §6?  → LGTM / Comments / Defer
```

## 3. The picker's shape

- **Tag every question** with a stable `[Q-X.Y]` prefix so the person can reply `[R: Q-X.Y]`.
- **Always offer a "Skip — decide later" option** (the defer disposition) when there is room
  (≤ 3 substantive options + it = 4) — so the person never has to reach for the harness Skip
  button, whose `[No preference]` record reads ambiguously.
- **Keep the lead-in short** (~10 lines) — some clients push preceding text into a cramped,
  scrollable region above the picker.
- **Option-label glyphs:** prefer keycap numbers (1️⃣ 2️⃣ 3️⃣ 4️⃣). Avoid filled enclosed
  letters (🅰 / 🅐 — hard to read); if you need letter labels use `A)` `B)` or outline Ⓐ Ⓑ.
- **Don't duplicate** the option text in the question body when the options array already
  carries it — that is a wall in the cramped UI.
- **Expand acronyms** on first use in the response AND inside every question's text — the
  cramped picker strips the surrounding context that would otherwise explain them.
- **Expand document-local identifiers the same way** — finding ids (`F-2`), task numbers
  (`Task 10`), requirement ids (`R5`), severity codes (`P1`), section refs (`§4.2`). These are
  worse than acronyms: they mean something only inside a source document the person has not
  opened and cannot look up from inside the picker. On first use in **any** question or chunk,
  expand the id into **what it is** — never the bare number.

  ```text
  ❌ "F-2: Task 4 blocks Task 10 (P1) — apply?"
  ✅ "F-2 (finding 2 of 7): the plan lists the design-system export task — already shipped —
      as blocking the theming task, which has not started. P1 = ships broken. Apply?"
  ```

  A reader who never opened the source must still be able to follow the question. Keep the
  bare id too — it is the stable handle for `[R: Q-F2]` — but never let it travel alone.

## 4. The decision options — Apply / Skip—decide-later / Drop

- **Apply** — do it now.
- **Skip — decide later** — not now. The item stays open; come back to it later (a later round,
  or later in the same session). It is neither decided nor discarded. (This is the "defer"
  disposition; label the picker option with this exact wording so the transcript records the
  intent — not a bare "Skip".)
- **Drop** — explicitly discard it (a chosen "no").
- **Auto-resolve rest** — trust the recommendations for the remaining items; an escape hatch
  when the person wants to skip ahead.

**The Skip button means "Skip — decide later," NEVER "you pick."** When the person presses the
picker's Skip button, the harness records the literal `[No preference]` — a *misleading* string:
it does **not** mean "no preference, you choose." It means **decide later** (the option above).
So on `[No preference]`: never choose for the person, never Apply, never Drop — leave the item
open, do the parts that don't depend on it, and say plainly what is still open. Don't
loop-pester it, but do bring it back in a later round or when it becomes relevant. To remove the
ambiguity entirely, always offer the explicit **Skip — decide later** option so the person
records the intent directly.

## 5. The `[Q-add]` catcher — inert, approves nothing

- With **1–3 real questions**, make the LAST card a catcher: *"Anything else? Any topic — an
  earlier question, a new one, a suggestion."* → *Nothing else / Yes — in my Other box / Hold —
  still typing.* It goes last because "anything else" only makes sense after the rest is read.
- It is the person's **out-of-band channel** — NOT a duplicate of "Other". ("Other" on card N
  is about card N's own question; the catcher is everything else — an earlier picker, a new
  topic, an unrelated suggestion.)
- Because it decides nothing, its options carry **zero scope and zero action**. Never write
  work into the "Nothing" option, and never use the approval phrase *"go ahead"* on it.

```json
// ❌ NEVER — "Nothing" now silently authorizes work
{"label":"Nothing — go ahead","description":"Start building X, Y, Z."}
// ✅ inert — every option is content-only
{"label":"Nothing else","description":"No extra context. This card approves nothing."}
```

- With a **full 4 real questions** there is no spare card: post a brief FYI notification (not a
  question), pause ~10–20s so the person can add context, then send the picker. Declining to
  add context is not consent — a scope you need approved is its own real question with the
  scope stated, never smuggled into the catcher.

## 6. Context depth — chunks in the body, lean picker

- **Short context (1–2 sentences)** → inline in the question; it stands alone.
- **Long context (paragraphs, code, trade-offs)** → the RESPONSE BODY as small labeled chunks
  (`📖 Chunk A / B`, `📖 F-N`); the picker stays lean and references them by label.
- **The decision is still a picker** — never an appended prose "answer 1-4" after the chunks.
- **Per-option rationale** lives in the chunk as **What / Why / Cost**, and every option
  carries something **shown** (§9) — a `Before → After` when it changes something that already
  exists, a POC snippet when it is new code / types / APIs. An option described but never shown
  is not decidable: the snippet makes trade-offs visible that prose cannot.

## 7. Comparing competing alternatives (A vs B vs C)

Trigger this whenever the person must choose between alternatives, or says **"compare"**. This
is *not* an approve/reject-one-change decision — its whole purpose is to lay out the **pros and
cons of each option** so the person can decide. Present it in *layers*, never a bare grid:

1. **Depth per option** — prose **pros / cons** for each alternative, plus **What / Why /
   Cost** and a **worked example of that option** (§9): the `Before → After` it produces, or a
   POC snippet of what it looks like. *Every* option gets one — a comparison that only shows the
   recommended option is not a comparison. This is the core; never strip the reasoning down to
   only a table.
2. **An at-a-glance comparison table** — the scannable summary of that depth:

   ```text
   | Option      | Pros                  | Cons                  | Best when         |
   |-------------|-----------------------|-----------------------|-------------------|
   | 1️⃣ Option A | fast, no new deps     | weaker types          | shipping today    |
   | 2️⃣ Option B | type-safe, composable | more setup            | a long-lived API  |
   | 3️⃣ Option C | simplest to read      | doesn't scale past N  | a throwaway spike |
   ```

3. **A weighted decision matrix** — the score on top of the pros/cons: options × named
   criteria, each cell scored 1–5, multiplied by the criterion weight, summed, and ranked:

   ```text
   | Criterion (weight)    | 1️⃣ Option A | 2️⃣ Option B | 3️⃣ Option C |
   |-----------------------|-------------|-------------|-------------|
   | Fit for the job (×3)  | 5 → 15      | 4 → 12      | 3 → 9       |
   | Simplicity (×2)       | 3 → 6       | 5 → 10      | 4 → 8       |
   | Cost to build (×1)    | 2 → 2       | 4 → 4       | 5 → 5       |
   | Weighted total        | 23          | 26 ← best   | 22          |
   ```

   State the criteria and weights explicitly so the score is auditable, not a black box.
4. **The decisive trade-off** — one line naming the axis the choice turns on.
5. **A recommendation + flip condition** — *"Recommend 2️⃣ because …; flip to 1️⃣ if …"* — or,
   if it is a genuine toss-up, say so rather than fake a pick. Mark the pick `(Recommended)` in
   the lean picker.

The tables never replace the depth — they are the scannable summary on top of the pros/cons.

## 8. Findings walk-through (reviews)

- **Finding format** — one chunk per finding, labelled `📖 F-N` (**F** for Finding, **N** its
  number: `📖 F-3` is finding 3; the question about it is `[Q-F3]`) =
  **What's wrong** (concrete, with a line / section ref) /
  **Before → After** (the current text and its exact replacement, *shown* — or a worked
  example when there is no "before" yet; §9) /
  **Proposed fix** (the specific change, in words) /
  **Why it works** (why that change resolves it).
- **Establish all findings as chunks FIRST** (prose), then walk them in batched lean questions
  (≤ 4 per call), each referencing its chunk, with a consistent option set across the batch
  (`Apply / Skip—decide-later / Drop / Auto-resolve rest`). Each finding is explained once; each
  question stays under ~150 characters.
- **Batch by area; order the batches by severity.** Group findings touching the same file,
  section or feature into one batch, then run the batches in order of the highest severity each
  contains. Locality is what makes a batch cheap — that area's context loads once and amortises
  across its findings instead of reloading per finding. Severity-ordered batches keep the
  important decisions early, so stopping after any batch still leaves the worst resolved.

## 9. Show it — `Before → After`, or a worked example

Describing a change is not showing it. *"Proposed fix: tighten the wording"* makes the person
rebuild the result in their head; showing the text they have and the text they would get hands
it to them. **Every finding and every option carries something shown.** Ambiguity is exactly
what a snippet removes and prose cannot.

- **The thing already exists** → a **`Before → After`** block **of its own**, between
  **What's wrong** and **Proposed fix**. Four parts, four jobs: *What's wrong* states it,
  *Before → After* shows it, *Proposed fix* names the change, *Why it works* explains it. It
  carries its own label precisely so it cannot be quietly folded away into prose.
- **Nothing exists yet** (a new file, a greenfield option) → a **worked example** in that same
  slot: what the person would see or type, and what comes back. Same job — *what are we
  solving, and what does solving it look like.*
- **Never** put a finding or an option to the person with neither.

**How to render it** — chosen by what changed. Excerpt the changed lines plus ~1 line of
context, never the whole file:

- **Code, config, or a line-level edit** → one `diff` fence; it carries both sides at once:

  ```diff
  - const timeout = 30
  + const timeout = Number(env.TIMEOUT ?? 30)
  ```

- **Prose, copy, or a rewritten block** → two labeled fences, each with its source ref:

  ```text
  Before (SKILL.md:149):  **Proposed fix** (the specific change)
  After:                  **Proposed fix** (the specific change, showing the After)
  ```

- **A one-token change** → inline, no fence: `lap: 3` → `lap: 4`.

**Empty sides are stated, never left blank** — `Before: (absent — no such section today)` for a
pure addition, `After: (removed)` for a deletion. A blank side reads as an oversight; a labelled
empty one is information.

**Keep the picker self-sufficient (§10):** put a ≤ 60-character `before → after` in the option's
own description, so the choice stays decidable once the chunk has scrolled away — e.g.
*"`Proposed fix` prose → prose + the shown After"*.

**Size guard:** past ~12 lines a side it is a plan, not a fix. Show the representative hunk, say
how many other sites match, and split the finding if they differ.

## 10. Send the picker in the SAME turn — never strand it

- Write the chunks, then emit the `AskUserQuestion` tool call **in the same turn**. Ending the
  turn after the chunks hands control back and the promised picker never fires — the single
  most common failure.
- Keep the **picker self-sufficient**: its question + option text must be decidable even if the
  lead-in is visually hidden on some clients. The chunks add depth, not the essentials.
- Never split the chunks and the picker across two turns.

## 11. One decision, one self-contained message — and never a file

A decision the person can only answer by assembling it from several places is not a question,
it is homework. Observed: one decision split four ways — a chunk in an earlier message, a file
written to disk, the source document, and the picker text — leaving the person to merge the
four by hand before they could answer at all.

- **Everything needed to decide lives in the ONE message that carries the picker.** Not the
  previous message, not the source document, not a file, not a scroll-back. If the person has
  to leave the message to understand the question, the message is incomplete — finish it.
- **Quote the source text inline; never cite where to find it.** `See plan.md:412` and
  `as covered in Task 4` are errands, not context. Paste the one or two relevant lines
  verbatim into the chunk — that is exactly what `Before → After` (§9) and the findings
  artifact's evidence quotes exist to make cheap.
- **Never create a file in order to ask a question.** No scratch `context.md`, no
  `questions.md`, no "I wrote it up, go read it". Put the context in the chat message. A
  picker overlay that covers the message text is *not* a reason to write a file — it is the
  reason the picker must be self-sufficient (§10): question and option text carry the
  essentials, the chunk carries the depth.
  *(Not this: the loop's `findings.json` handoff between the review and triage halves. That is
  state you write for yourself across invocations — never an artifact handed to the person.)*

**The shape that works** — per decision, in one message, with the picker in that same turn:

1. **Today** — what the code or doc does right now, with the relevant source text quoted inline.
2. **Before → After** — the change *shown*: a diff fence, or two labelled fences for prose (§9).
3. **Pros / cons** — a short table across the options (§7) whenever there is more than one.
4. **The trade-off** — one line naming the axis the choice actually turns on.
5. **Recommendation** — the pick, why, and what would flip it.

````text
📖 F-3 (finding 3 of 6) — the retry helper hides the error it failed on

**Today** — `fetchWithRetry` returns `null` once attempts run out (src/net.ts:41):
    if (attempt === max) return null

**Before → After**
```diff
- if (attempt === max) return null
+ if (attempt === max) throw lastError
```

| Option           | Pros                       | Cons                          | Best when        |
|------------------|----------------------------|-------------------------------|------------------|
| 1️⃣ Throw         | callers see the real cause | 3 call sites need a try/catch | errors matter    |
| 2️⃣ Return Result | typed failure, no throw    | touches every caller          | a long-lived API |

**Trade-off:** blast radius now (2️⃣ — every caller) vs. a smaller fix that still hides
nothing (1️⃣ — three call sites).
**Recommend 1️⃣** — those three call sites already sit inside a try/catch; flip to 2️⃣ if the
helper becomes public API.
````

…and in the same turn: `[Q-F3] Retry helper hides the failing error — throw instead? (see 📖 F-3)`

## 12. No ghost references

- If a question says `(see 📖 F-X)`, the chunk `📖 F-X` MUST exist **in the same message** as
  the question (§11) — never in an earlier one the person has to scroll back for.
- **❌ Wrong:** referencing a chunk you never wrote — the person has nothing to read, asks for
  context, and you loop re-issuing the same lean question thinking they want format help.
- **✅ Correct:** the chunk sits in the same message as the question that references it.
- **Self-check:** if you are about to write `(see 📖 X)`, re-read *this* message — is the
  chunk actually in it? If not, write it here, before the `AskUserQuestion` call.

## 13. Skills and subagents do not suspend this

The moment control returns to you after any `Skill` invocation or `Agent` dispatch, the **next
decision is a picker again** — never a numbered prose "confirm before I …" list. Report-style
skills and subagents may return prose; that is their output, not your way of asking the person.

## 14. "Other" is a side channel

The person sometimes types new, unrelated context into a picker's **"Other"** box because it
lands faster than a separate message. Treat "Other" content as **potentially-real content**,
not merely a custom answer to that one question.

## 15. Confirm before saving memories

Propose any memory write via a picker (or prose) and save only after an explicit yes — never
persist a fact about the person's preferences silently.

## Commit before review (pointer)

Before you put an artifact up for review, it must be a **committed, green checkpoint** —
review happens on the committed diff, never the uncommitted working tree. The full rule lives
in the review loop (`../_shared/review-loop.md`).

## Red flags — stop, you are about to break the discipline

| Thought | Reality |
|---------|---------|
| "I'll ask in the next message." | There is no next message. Emit the picker THIS turn. |
| "I'll just list the options in prose." | A decision is a picker, not a prose "answer 1-4". |
| "I'll bundle these three approvals into one question." | Separate sub-questions — never bundle. |
| "(see 📖 F-9)" — but F-9 isn't written yet | Ghost reference. Write the chunk first, or drop the ref. |
| "Proposed fix: tighten the wording." | Describing isn't showing. Attach a `Before → After` (§9). |
| "I'll show the example for the option I recommend." | Every option gets one, or it is not a comparison (§7). |
| "They pressed Skip → `[No preference]`, so I'll pick." | Skip = decide later, NOT you-pick. Leave it open; never Apply/Drop/choose. |
| "Nothing else — go ahead (and do the work)." | The catcher approves nothing. Put scope in its own question. |
| "F-2: Task 4 blocks Task 10 (P1) — apply?" | A bare id is not a question. Expand it into what it IS (§3). |
| "The context is in my earlier message / in the plan doc." | One decision = one message. Quote the source inline (§11). |
| "The overlay hides the text — I'll write it to a file." | Never a file to ask a question. Chat message + self-sufficient picker (§11). |
| "I'll record a private detail for context." | Never. Generic, neutral, zero personal data. |
