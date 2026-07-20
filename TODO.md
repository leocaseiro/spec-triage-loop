# spec-triage-loop — backlog

Nothing here is dropped — it is deferred, on purpose, with the reason. Revisit
before calling the project done.

## Staged to v1.1 (cut from v1 to prove the core loop first — Q-V1SIZE 2026-07-20)

- **`before-pr` skill** — the 15-step sequencer (brainstorm → … → merge). Deferred
  because the two loops + hook deliver the always-on review value on their own; the
  full sequence is additive. Add once the loops are dogfooded and stable.
- **`handoff` skill** — loop-aware session-resume doc. Its justification was
  `before-pr`'s context length; with `before-pr` staged, it loses its v1 reason.
  Add when a real multi-session run demonstrates the need.
- **Delta vocabulary** (`## ADDED / MODIFIED / REMOVED Requirements`) as a docs
  convention — a per-lap change record. Nice-to-have, not required for the loop.
- **Tier 3 (read-from-disk + skip-lists) + `bin/resolve-skill`** — the version
  resolver ships nothing in v1 (no v1 consumer). Reintroduce together with tier 3,
  only when a composed skill provably won't defer.

## Open findings to revisit (from the 2026-07-20 ce-doc-review)

- **Always-on vs the mechanism.** The SessionStart hook fires at
  `startup|clear|compact`, not every turn, and carries a lossy ~8-line summary — so
  "always-on" is really "re-surfaced at session start." v1 softens the claim to match;
  revisit whether to strengthen the mechanism (re-assert on a recurring trigger, or
  force-load the full triage skill). Also: the matcher omits `resume` — a resumed
  session may not re-inject the rule.
- **"Auto-current" cuts both ways.** Tier-1 auto-currency is the delivery path for an
  upstream reformat that breaks any prose-output parse the loop depends on. Future:
  add a format-drift smoke check that runs a composed review skill against a fixture
  and asserts the exit signal still parses.
- **`resolve-skill` reads an undocumented schema.** `installed_plugins.json` is
  internal Claude Code state (`"version": 2`). When tier 3 is built, assert that shape
  and fall back to Skill-tool resolution if it differs.
- **Cross-plugin invocation evidence.** Was "n=1" at spec time; the 2026-07-20 dogfood
  added more data points (this session invoked `superpowers:brainstorming` and
  `compound-engineering:ce-doc-review` cross-plugin, the latter nested with subagents).
  Still worth an explicit falsification test on a second machine before v1 ships.

## Product-lens advisories (noted, not actioned — Q-V1SIZE chose trim over document)

- Maintenance budget for tracking two upstream skill families — set a ceiling.
- Public-repo framing: lead the README with the simple "one hook makes review
  always-on" story; keep the machinery as depth.
- Opportunity cost vs the AWS/product job-hunt focus — keep this a means, not a sink.

## Deferred questions for the plan stage

- Model-tiering delivery: ship an `agents/` definition with `model:` frontmatter, or
  pass a per-dispatch model when composing superpowers' executor? (D-1 chose "configure
  superpowers' existing Model Selection" — pin the mechanism at plan time.)
- Loop-termination when only P2/P3 are applied but findings remain — pin the exact
  predicate (leans on the lap cap + manual override for now).

## Deferred during build (2026-07-20)

- **Cross-platform hook wrapper.** v1's `hooks/hooks.json` calls `hooks/session-start`
  directly (Unix-only). superpowers ships a polyglot `hooks/run-hook.cmd` so the same hook
  also runs on Windows (Git-Bash). Deferred per Simplicity-First — v1 is a macOS-only,
  prove-the-core release. Wire it in before advertising Windows support; pattern to copy:
  `superpowers/6.1.1/hooks/run-hook.cmd` + set `"command"` to `"…/run-hook.cmd session-start"`.
