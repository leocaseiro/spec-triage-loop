# spec-triage-loop

One hook re-surfaces a review discipline at the start of every session; two loops review any
document or diff **until it is clean**. It is a Claude Code plugin that makes
`review → verify → triage → apply → re-review` the default review workflow — by composing
existing skills (superpowers + compound-engineering) rather than re-implementing them.

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
  context established first, never a prose "answer 1-4". Governs review walk-throughs and any
  multi-option question.
- **`doc-review-loop`** — review any document (spec, plan, design, RFC) until clean. Wraps
  `compound-engineering:ce-doc-review` in headless mode, verifies each finding, triages it
  with you, applies your decisions, and re-reviews until nothing actionable remains.
- **`code-review-loop`** — review any diff until clean. Wraps
  `compound-engineering:ce-code-review` in agent mode (report-only), verifies findings with
  `superpowers:receiving-code-review`, triages, applies, and re-reviews.

The **hook** re-injects the triage rule and a pointer to the two loops at the start of each
session (`startup` / `clear` / `compact`), so the workflow is present without you loading it
by hand.

## How it composes

The loops do not re-implement review or model-tiering — they **compose** two existing skill
families through the Skill tool by plugin-qualified name (`compound-engineering:…`,
`superpowers:…`). The loop shape lives once in `skills/_shared/review-loop.md`; each loop
skill only binds its four parameters — which review skill, which mode, the exit signal, and
the verify check. The bound is real: the loop halts at a lap cap, or when a lap makes no
progress, so "until clean" is never open-ended.

## Depth

- Design + rationale — [`docs/specs/2026-07-20-spec-triage-loop-plugin.md`](docs/specs/2026-07-20-spec-triage-loop-plugin.md)
- Implementation plan — [`docs/plans/2026-07-20-spec-triage-loop-plugin-plan.md`](docs/plans/2026-07-20-spec-triage-loop-plugin-plan.md)
- Deferred to v1.1 (nothing dropped, each with its reason) — [`TODO.md`](TODO.md)

MIT.
