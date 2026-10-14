# spec-triage-loop

A Claude Code plugin with three skills, one of which needs nothing else installed.

**`triage`** is that one. It makes every decision an agent puts to you a *picker*, with the
context established first and **shown** — a `Before → After` or a worked example, never a bare
description. It is not code-specific and has no dependencies.

**`doc-review-loop`** and **`code-review-loop`** run a document or a diff through
`review → verify → triage → apply → re-review` **until it is clean**. These two do compose
existing skills rather than re-implementing them, so they need other plugins installed.

A session-start hook re-surfaces the discipline each session, so it is there without you
loading it by hand.

## The three skills, and what each needs

| Skill | What it does | Requires |
|-------|--------------|----------|
| **`triage`** | Turns every decision into a picker with the context shown first | **nothing** |
| **`doc-review-loop`** | Reviews a doc until clean | `compound-engineering` |
| **`code-review-loop`** | Reviews a diff until clean | `compound-engineering` **and** `superpowers` |

The two loops resolve those skills by name and fail the moment they run without them:

```text
/plugin install compound-engineering@compound-engineering-plugin
/plugin install superpowers@claude-plugins-official
```

(`superpowers` supplies code-scoped verification, which is why the document loop does not
use it.)

## Install

**As a plugin** — the full thing, including the session-start hook:

```text
/plugin marketplace add leocaseiro/spec-triage-loop
/plugin install spec-triage-loop@spec-triage-loop
```

It installs at user scope, so it is available in every project with no per-project setup.

**With the [skills CLI](https://skills.sh)** — skills only, no hook:

```bash
npx skills add leocaseiro/spec-triage-loop                       # pick interactively
npx skills add leocaseiro/spec-triage-loop --skill triage -g     # just the standalone one
```

Two differences worth knowing before you choose:

- **No session-start hook.** The hook is a plugin feature. Installed as skills, nothing
  re-surfaces the discipline each session — you load `triage` yourself, or your agent does
  when its description matches.
- **The loops still need the two plugins above,** because `compound-engineering:ce-doc-review`
  is a plugin-qualified name that the skills CLI cannot install. Each loop also says to load
  `triage` as `Skill("triage")` when there is no `spec-triage-loop:` namespace.

`triage` has no such caveats: it is self-contained, references no other file, and behaves
identically whichever way you install it.

## What you get

Three skills plus a session-start hook.

- **`triage`** — the asking discipline. Every decision is put to you as a picker with the
  context established first, never a prose "answer 1-4" — and the context is *shown*: each
  finding and each option carries a `Before → After` or a worked example, never a bare
  description. Governs review walk-throughs and any multi-option question.
- **`doc-review-loop`** — review any document (spec, plan, design, RFC) until clean. Wraps
  `compound-engineering:ce-doc-review` in headless mode, verifies each finding, triages it
  with you, applies your decisions, and re-reviews until nothing actionable remains.
- **`code-review-loop`** — review any diff until clean. Wraps
  `compound-engineering:ce-code-review` in agent mode (report-only), verifies findings with
  `superpowers:receiving-code-review`, triages, applies, and re-reviews.

Each lap runs as **two invocations** — a review half that writes a findings artifact and
stops, then a triage half that reads it. Triage is the judgment-heavy step, so it starts on a
clean context instead of inheriting the review's machinery.

The **hook** re-injects the triage rule and a pointer to the two loops at the start of each
session (`startup` / `clear` / `compact`), so the workflow is present without you loading it
by hand.

## How it composes

The loops do not re-implement review or model-tiering — they **compose** two existing skill
families through the Skill tool by plugin-qualified name (`compound-engineering:…`,
`superpowers:…`). The loop shape is written once in `skills/_shared/review-loop.md`; each
loop skill only binds its five parameters — which review skill, which mode, the exit signal,
the verify check, and where loop state is stored. The bound is real: the loop halts at a lap
cap, or when a lap makes no progress, so "until clean" is never open-ended.

Each loop folder also carries a **generated copy** of that file, because `npx skills add`
installs skill folders only and `skills/_shared/` is not one — a loop installed that way
would otherwise lose the file its first instruction tells it to read, with no error at
install time. `scripts/sync-shared.py` writes the copies and `--check` fails CI if they
drift. Edit the source, never a copy.

## Measuring whether it lands

`scripts/picker-audit.py` reads Claude Code transcripts and scores every `AskUserQuestion`
picker: did it carry a `Before → After`, a pros/cons table, a named trade-off, a
recommendation — and was the `triage` skill loaded in that session at all. Read-only.

```bash
scripts/picker-audit.py <project>              # per-session table
scripts/picker-audit.py <project> --by-skill   # loaded vs not loaded
scripts/picker-audit.py <project> --monthly    # trend over months
scripts/picker-audit.py <project> --dump 2     # one picker in full
```

`<project>` is a substring of a directory under `~/.claude/projects`; omit it to scan all.
It exists because the discipline degrades silently. Measured 2026-10-14 across 1,128
pickers in 126 sessions: sessions that had loaded the skill named the trade-off in 40% of
their pickers against 8% in sessions that had not, and carried a `Before → After` in 45%
against 4%. No other visible difference between the two groups.

## Depth

- Design + rationale — [`docs/specs/2026-07-20-spec-triage-loop-plugin.md`](docs/specs/2026-07-20-spec-triage-loop-plugin.md)
- Implementation plan — [`docs/plans/2026-07-20-spec-triage-loop-plugin-plan.md`](docs/plans/2026-07-20-spec-triage-loop-plugin-plan.md)
- Deferred to v1.1 (nothing dropped, each with its reason) — [`TODO.md`](TODO.md)

MIT.
