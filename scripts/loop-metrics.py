#!/usr/bin/env python3
"""Re-measure the two numbers the skill and the shared loop assert.

Both are cited as fact in skills/_shared/review-loop.md and skills/triage/SKILL.md,
and both say "re-measure before changing this". This is how.

  scripts/loop-metrics.py context <project-substring>
      Peak context per session from ~/.claude/projects transcripts, and the
      marginal cost per finding across one session's picker rounds. Backs the
      12-finding triage cap (measured 2026-09-26: entered triage at 149,680
      tokens, ~17,900 per finding, 21 findings reached 472k untroubled).

  scripts/loop-metrics.py confidence <repo-path>
      Confidence distribution across that repo's .spec-triage-loop artifacts.
      Backs §8 (measured 2026-10-08 over 42 artifacts / 504 findings:
      19% at 100, 63% at 75, 18% at 50; P1 never drops to 50).
"""
import collections, glob, json, os, sys


def load(path):
    out = []
    try:
        fh = open(path, errors="replace")
    except OSError:
        return out
    with fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def context(project):
    rows = []
    for p in glob.glob(os.path.expanduser(f"~/.claude/projects/*{project}*/*.jsonl")):
        recs = load(p)
        date = next((r.get("timestamp") for r in recs if r.get("timestamp")), "")[:10]
        if not date:
            continue
        peak = out = 0
        marks = []
        for r in recs:
            if r.get("type") != "assistant":
                continue
            u = (r.get("message") or {}).get("usage") or {}
            ctx = ((u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)
                   + (u.get("cache_creation_input_tokens") or 0))
            if ctx:
                peak = max(peak, ctx)
            out += u.get("output_tokens") or 0
            for b in (r.get("message") or {}).get("content") or []:
                if b.get("type") == "tool_use" and b.get("name") == "AskUserQuestion":
                    nq = len([q for q in b["input"].get("questions", [])
                              if "Q-add" not in q.get("question", "")])
                    marks.append((ctx or peak, nq))
        if peak:
            rows.append((date, os.path.basename(os.path.dirname(p))[-28:], peak, out, marks))
    rows.sort()
    print(f"{'date':12}{'worktree':30}{'peakCtx':>10}{'outTok':>10}{'pickers':>8}")
    for d, w, pk, o, m in rows:
        print(f"{d:12}{w:30}{pk:>10,}{o:>10,}{len(m):>8}")
    if rows:
        pks = sorted(r[2] for r in rows)
        print(f"\nsessions={len(rows)}  medianPeak={pks[len(pks)//2]:,}  maxPeak={max(pks):,}")
    best = max(rows, key=lambda r: len(r[4]), default=None)
    if best and len(best[4]) > 1:
        m = best[4]
        span = m[-1][0] - m[0][0]
        fin = sum(n for _, n in m[1:])
        print(f"\nper-finding slope, longest walk ({best[0]} {best[1]}):")
        print(f"  entered at {m[0][0]:,} -> {m[-1][0]:,} over {sum(n for _,n in m)} findings")
        if fin:
            print(f"  ~{span//fin:,} tokens per finding after the first round")


def confidence(repo):
    vals = collections.Counter()
    bysev = collections.defaultdict(collections.Counter)
    files = 0
    # os.walk, not glob: glob's ** skips dot-directories, and the artifacts live
    # under .claude/worktrees/*/.spec-triage-loop/.
    paths = []
    for root, _dirs, names in os.walk(repo):
        if ".spec-triage-loop" in root.split(os.sep) and "findings.json" in names:
            paths.append(os.path.join(root, "findings.json"))
    for p in paths:
        try:
            d = json.load(open(p))
        except Exception:
            continue
        got = False
        for v in d.values():
            if isinstance(v, list) and v and isinstance(v[0], dict) and "confidence" in v[0]:
                got = True
                for f in v:
                    vals[f.get("confidence")] += 1
                    bysev[str(f.get("severity"))][f.get("confidence")] += 1
        files += 1 if got else 0
    total = sum(vals.values())
    print(f"artifacts carrying confidence: {files}   findings: {total}")
    if not total:
        return
    for k, n in sorted(vals.items(), key=lambda x: -(x[0] or 0)):
        print(f"  conf {str(k):>4}: {n:>4}  ({100*n//total}%)")
    print("\nby severity:")
    for s in sorted(bysev):
        row = bysev[s]
        cells = "  ".join(f"{k}:{n}" for k, n in sorted(row.items(), key=lambda x: -(x[0] or 0)))
        print(f"  {s:4} total={sum(row.values()):>4}   {cells}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("context", "confidence"):
        sys.exit(__doc__)
    (context if sys.argv[1] == "context" else confidence)(sys.argv[2])
