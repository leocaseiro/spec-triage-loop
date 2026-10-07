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

## 1. Every decision is a picker — but first, is it a decision?

- Every question / confirmation / decision → an `AskUserQuestion` tool call. Never solicit a
  prose answer ("reply go", "say yes", "confirm below", "answer 1-4"). The only messages that
  stand without a picker are **pure notifications that need no answer**.
- **Emit the picker in the SAME turn** as any lead-in. Announcing "I'll ask below" and then
  ending the turn *strands* the picker — there is no automatic next message, so it never fires.

The person's judgment is the scarce resource. Two things must never be spent on it:

- **What you could settle by trying it — spike it first.** An option you have not run is a
  guess, and a picker built on guesses spends the person's judgment on a question you owned.
  Run the smallest thing that settles it — a scratch script, a throwaway branch, one command,
  one query — then ask with the answer in hand, or find you no longer need to ask at all. This
  is also how an option earns the worked example §7 and §9 demand: you cannot show the result
  of something you never ran. Say what you spiked and what came back, and mark any option you
  genuinely could not test **(untested)**, so the person can see which way the evidence runs.
  **Reviewer confidence is the objective trigger.** Review engines score every finding 100 / 75
  / 50. A **50 is a suspicion, not a finding** — spike it before it reaches the person, or put it
  to them labelled a suspicion, naming the spike you could not run. A **75** was inferred from
  reading rather than running: spike it whenever that is cheap. A **100** the reviewer already
  confirmed — state it and move on.
- **A change that only removes ambiguity — just make it, and say so.** A confusing name, a
  stale comment, a sentence with two readings, a missing unit, an undefined term, a typo: fix
  it and report it in one line. Asking costs more of the person's attention than the change is
  worth. The moment a fix changes behaviour, scope, or a real trade-off it stops being
  disambiguation and becomes a real question — **that line is the test, not the size of the
  diff.**

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

### Multi-select, for a run of low-severity findings

`AskUserQuestion` also takes `multiSelect: true`, which turns one card's options into
independent checkboxes. That is **not** the anti-pattern above. There the options were
*verdicts over a group*; here **each option is one finding**, and checking F-7 while leaving
F-8 is exactly the per-decision granularity the anti-pattern destroys.

Use it only for a run of **P2 / P3 findings**. P0 and P1 always get their own card, where the
scenario, the trade-off and the recommendation have room to be read.

- **The context still goes in the chat** — one `📖 F-N` chunk per finding, with its scenario,
  exactly as §8 and §10 require. The card carries the *switch*, never the reasoning.
- **Each option is one line: `Approve F-N (recommended)`.** Its description names what the
  finding is, in plain words. Never a compressed `before → after`, never a truncated rationale:
  a trimmed half-sentence in a checkbox is unreadable, which is the failure this replaces.
- **Say what unchecked means, in the question text, every time.** Unchecked leaves the finding
  **open for a later round — it is never a Drop.** To drop one, the person says so in "Other".
- **Four findings per card, maximum** — a card takes 2–4 options. Eleven P3s are three cards,
  not one; never silently leave seven out.

````text
📖 F-7 — … full chunk, scenario first, in the chat message …
📖 F-8 — … full chunk …
📖 F-9 — … full chunk …

…then, in the same turn, ONE card:

[Q-P3] Three P3 findings (see 📖 F-7, F-8, F-9 above). Check each one to approve.
       Anything left unchecked stays OPEN for a later round — it is not dropped.
       To drop one, say so in Other.
  ☐ Approve F-7 (recommended)  — the lint-suppression comment misstates what it blocks
  ☐ Approve F-8 (recommended)  — the CSS check matches by substring, so it passes wrongly
  ☐ Approve F-9 (recommended)  — the "settings were reset" toast fires when nothing changed
````

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
  **The scenario** (what the person is doing, and what they see go wrong — §10) /
  **What's wrong** (concrete, with a line / section ref) /
  **Before → After** (the current text and its exact replacement, *shown* — or a worked
  example when there is no "before" yet; §9) /
  **Proposed fix** (the specific change, in words) /
  **Why it works** (why that change resolves it).
- **Carry the reviewer's confidence next to the severity, expanded** — in the chunk header and
  in the question text, everywhere severity already goes. The engines emit it on every finding;
  observed values are 100 / 75 / 50. It is a document-local number (§3), so never ship it bare:
  - **100** — the reviewer confirmed it against the source.
  - **75** — inferred from reading the code. Likely, unproven.
  - **50** — a suspicion worth checking, not a finding to act on as it stands (§1 spikes these).

  Measured across 42 artifacts and 504 findings: 19% are 100, **63% are 75**, 18% are 50 — and
  a P1 never drops to 50. So the risk is not in the severe findings; it is the large middle band
  that reads as settled when it was only inferred. Confidence is the reviewer's own score at
  raise time: if your own spike or the verify step confirmed it, say so rather than leaving the
  person to wonder which it is.
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

- **Prose, copy, or a rewritten block** → one fence carrying both sides, each labelled with
  its source ref (two separate fences are fine; what matters is that the labels line up and
  the sides sit adjacent, so the eye can do the diffing):

  ```text
  Before (SKILL.md:149):  **Proposed fix** (the specific change)
  After:                  **Proposed fix** (the specific change, showing the After)
  ```

- **A one-token change** → inline, no fence: `lap: 3` → `lap: 4`.
- **A table row, or a cell inside one** → **never fence the row's source.** The pipes are
  carriage, not content: a `|`-delimited line wrapped inside a monospace fence is the least
  readable form the change can take, and it makes the person re-table it in their head. Choose
  by how many rows changed:
  - **One row** → name the table and the row, then show only the sentences that changed, as
    labelled prose. A prose cell is prose; render it as prose.
  - **Two or more rows** → one **rendered** markdown table with `Before` and `After` columns —
    rendered, never fenced — so the cells sit side by side.

  ```text
  ❌ the row's source, fenced — the pipes become noise and the sentence wraps into mush
     | **Start handshake** | learned start lead L (median of the first 3 readings after
     Play). If the synth is slower (L > 0) the **media start is delayed by L**. If the …

  ✅ name the row; show only what changed
     §6.2 → the "Start handshake" row, on what happens when the synth is slower:
     Before:  the synth starts L earlier in the song.
     After:   the synth starts L earlier in the song — but never past the target; a
              positive per-speed offset is caught up after the first beat by a faster
              nudge (≤ 8%).
  ```

**Empty sides are stated, never left blank** — `Before: (absent — no such section today)` for a
pure addition, `After: (removed)` for a deletion. A blank side reads as an oversight; a labelled
empty one is information.

**Keep the picker self-sufficient (§11):** put a ≤ 60-character `before → after` in the option's
own description, so the choice stays decidable once the chunk has scrolled away — e.g.
*"`Proposed fix` prose → prose + the shown After"*.

**Size guard — count the UNCHANGED lines, not the total.** Never trim a change the person needs
in full: if twenty lines genuinely changed, show twenty, because a collapsed block they cannot
follow is worse than a long one they can. What must never appear is text that did *not* change —
the rest of the cell, the untouched rows beside the edited one, the body of the function around
the edited line. Every line you show is either changed, or the ~1 line of context that makes a
changed line legible.

- **Long because the change is long** → keep it whole, and put a one-line summary of what
  changed above it, so the person can read the detail or take the summary and move on.
- **Long because unchanged text rode along** → cut the unchanged text. This is the usual cause,
  and it is what makes a long block unreadable rather than merely long.
- **Past ~12 changed lines**, stop and ask whether this is still one fix. If it has become a
  rewrite, say so: show the representative hunk, say how many other sites match, and split the
  finding when they differ.

## 10. Ground it — open every finding with the scenario

§9 shows what *changes*. The scenario shows what is *at stake*, and it comes **first**: nobody
can weigh a fix until they know what goes wrong without it. Write it for a reader who has never
opened the file, does not know the subsystem, and was not in the review.

**The scenario is a short second-person walk-through of the failure as a human meets it** —
what they were doing, what they would see, and why that is bad. Not the mechanism and not the
code; those follow, under their own labels.

- **Second person, present tense, inside the product.** "You open Settings and type `100`…" —
  not "the handler fires on every keystroke".
- **Concrete beats general.** A number, a screen, a click. *"You typed three characters and
  restarted the song three times"* lands where *"causes redundant reloads"* does not.
- **Name the damage in the person's own terms** — lost work, a wrong number, a silent failure,
  a test that passes when it should have caught this.
- **Ground it in a real incident when one exists** — *"this is not hypothetical; it shipped
  once"* turns a worry into evidence. Never invent one.
- **No jargon inside the scenario.** If a term is unavoidable, expand it in a *Terms first*
  line above the findings (§3), never mid-story.

```text
❌ mechanism-first — only decidable by someone who already knows the subsystem
   The restore path gates enums and numbers but not text, so an invalid stored font throws
   in fillFromJson and the reset flag stays false.

✅ scenario-first — the same finding, decidable by anyone
   **The scenario.** You spend ten minutes setting the app up how you like it — a readable
   font, a colour you picked, zoom at 120%. Next morning you open it and *everything* is
   back to factory defaults. No message, no warning. Twenty settings gone, because one of
   them was saved in a form the engine will not accept.
```

**Carry it into the options.** The scenario pays off a second time in the `Drop` description:
say what keeps happening if the person declines — *"Discard it. One bad stored value keeps
wiping every other setting, silently, on every visit."* That is what keeps the picker decidable
on its own (§11) once the chunk has scrolled away.

**Where it goes:** first, above *What's wrong*, in every finding chunk (§8) and every decision
message (§12). A finding with no scenario is a fix nobody can weigh.

## 11. Send the picker in the SAME turn — never strand it

- Write the chunks, then emit the `AskUserQuestion` tool call **in the same turn**. Ending the
  turn after the chunks hands control back and the promised picker never fires — the single
  most common failure.
- Keep the **picker self-sufficient**: its question + option text must be decidable even if the
  lead-in is visually hidden on some clients. The chunks add depth, not the essentials.
- Never split the chunks and the picker across two turns.

## 12. One decision, one self-contained message — and never a file

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
- **Any path you DO print must resolve for the person.** When you name a file — in a chunk, an
  option, or a resume command — give the **absolute** path in a code block, naming the worktree
  that actually holds it. A repo-relative `docs/plans/<doc>.md` is a fragment, not a location:
  it resolves against whatever checkout the reader has open, and in a worktree-per-task repo
  that is usually one where the file does not exist. Relative is safe **only** for a file in
  the reader's own current checkout. Observed 2026-09-30: a triage half handed over
  `docs/plans/<doc>.md` from a session whose cwd was a different worktree than the document's;
  the person went looking and found nothing. Build the absolute form from where the file *is*,
  not from your own cwd — being absolute is not enough if it names the wrong worktree.
- **Never create a file in order to ask a question.** No scratch `context.md`, no
  `questions.md`, no "I wrote it up, go read it". Put the context in the chat message. A
  picker overlay that covers the message text is *not* a reason to write a file — it is the
  reason the picker must be self-sufficient (§11): question and option text carry the
  essentials, the chunk carries the depth.
  *(Not this: the loop's `findings.json` handoff between the review and triage halves. That is
  state you write for yourself across invocations — never an artifact handed to the person.)*

**The shape that works** — per decision, in one message, with the picker in that same turn:

1. **The scenario** — what goes wrong for the person, in their terms, before any mechanism (§10).
2. **Today** — what the code or doc does right now, with the relevant source text quoted inline.
3. **Before → After** — the change *shown*: a diff fence, or two labelled fences for prose (§9).
4. **Pros / cons** — a short table across the options (§7) whenever there is more than one.
5. **The trade-off** — one line naming the axis the choice actually turns on.
6. **Recommendation** — the pick, why, and what would flip it.

````text
📖 F-3 (finding 3 of 6) — the retry helper hides the error it failed on

**The scenario.** A user reports "it just says it failed". You open the logs to find out why
the upload died — and there is nothing: no host, no status, no timeout. The one call that knew
what went wrong threw it away, so every failure in this path looks identical.

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

## 13. No ghost references

- If a question says `(see 📖 F-X)`, the chunk `📖 F-X` MUST exist **in the same message** as
  the question (§12) — never in an earlier one the person has to scroll back for.
- **❌ Wrong:** referencing a chunk you never wrote — the person has nothing to read, asks for
  context, and you loop re-issuing the same lean question thinking they want format help.
- **✅ Correct:** the chunk sits in the same message as the question that references it.
- **Self-check:** if you are about to write `(see 📖 X)`, re-read *this* message — is the
  chunk actually in it? If not, write it here, before the `AskUserQuestion` call.

## 14. Skills and subagents do not suspend this

The moment control returns to you after any `Skill` invocation or `Agent` dispatch, the **next
decision is a picker again** — never a numbered prose "confirm before I …" list. Report-style
skills and subagents may return prose; that is their output, not your way of asking the person.

## 15. "Other" is a side channel

The person sometimes types new, unrelated context into a picker's **"Other"** box because it
lands faster than a separate message. Treat "Other" content as **potentially-real content**,
not merely a custom answer to that one question.

## 16. Confirm before saving memories

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
| "The context is in my earlier message / in the plan doc." | One decision = one message. Quote the source inline (§12). |
| "The overlay hides the text — I'll write it to a file." | Never a file to ask a question. Chat message + self-sufficient picker (§12). |
| "The restore path gates enums but not text." | Mechanism-first. Open with what breaks for the person (§10). |
| "They'll know what this subsystem does." | Assume they have never opened the file. Scenario first, jargon expanded (§10). |
| "I'll ask them which approach would work." | If you can run it, run it. Spike first, ask with the result (§1). |
| "Shall I rename this confusing variable?" | Ambiguity-only fixes need no approval. Make it, say you did (§1). |
| "F-6 (P2) — apply?" with no confidence shown | 63% of findings are only 75% sure. Show it next to severity (§8). |
| "conf=50, but it reads plausible, so I'll ask." | 50 is a suspicion, not a finding. Spike it or label it (§1). |
| "\| **Start handshake** \| learned start lead L…" in a fence | Table source fenced. Name the row, show the changed sentences (§9). |
| "That's 16 lines, I'll trim it to 12." | Cut the UNCHANGED lines, never the change itself (§9). |
| "I'll record a private detail for context." | Never. Generic, neutral, zero personal data. |
