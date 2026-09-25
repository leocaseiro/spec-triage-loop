# spec-triage-loop

One hook re-surfaces a review discipline at the start of every session; two loops review any
document or diff **until it is clean**. It is a Claude Code plugin that makes
`review → verify → triage → apply → re-review` the default review workflow — by composing
existing skills (superpowers + compound-engineering) rather than re-implementing them.

## Requirements

Both loops compose skills from two other plugins. Install them first, or the loops fail on an
unresolvable skill name the moment they run:

```text
/plugin install superpowers@claude-plugins-official
/plugin install compound-engineering@compound-engineering-plugin
```

`triage` on its own has no dependencies.

## Install

From any machine with Claude Code:

```text
/plugin marketplace add leocaseiro/spec-triage-loop
/plugin install spec-triage-loop@spec-triage-loop
```

It installs at user scope, so it is available in every project with no per-project setup.

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
`superpowers:…`). The loop shape lives once in `skills/_shared/review-loop.md`; each loop
skill only binds its five parameters — which review skill, which mode, the exit signal, the
verify check, and where loop state is stored. The bound is real: the loop halts at a lap cap,
or when a lap makes no progress, so "until clean" is never open-ended.

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
It exists because the discipline degrades silently: measured on 2026-09-19 across 89
pickers, sessions that loaded the skill named the trade-off in 40% of pickers and sessions
that did not in 4%, with no other visible difference.

## Depth

- Design + rationale — [`docs/specs/2026-07-20-spec-triage-loop-plugin.md`](docs/specs/2026-07-20-spec-triage-loop-plugin.md)
- Implementation plan — [`docs/plans/2026-07-20-spec-triage-loop-plugin-plan.md`](docs/plans/2026-07-20-spec-triage-loop-plugin-plan.md)
- Deferred to v1.1 (nothing dropped, each with its reason) — [`TODO.md`](TODO.md)

MIT.
