#!/usr/bin/env python3
"""Audit AskUserQuestion pickers in Claude Code transcripts.

Measures whether the triage discipline is actually landing: does each picker
carry a Before -> After, a pros/cons table, a named trade-off, a recommendation
-- and was the `triage` skill loaded in that session at all.

Built after the 2026-09-19 investigation, which found the depth rules collapse
when the skill is not loaded (trade-off naming 40% -> 2%).

USAGE
  scripts/picker-audit.py notation-hero                 # per-session table
  scripts/picker-audit.py notation-hero --monthly       # trend over months
  scripts/picker-audit.py notation-hero --by-skill      # loaded vs not loaded
  scripts/picker-audit.py notation-hero --since 2026-09-14
  scripts/picker-audit.py notation-hero --dump 2        # print picker #2 of the
                                                        #   newest session, in full
PROJECT is a substring matched against ~/.claude/projects/<dir>; omit it to scan
every project. Read-only -- it never writes to a transcript.

GOTCHA that broke the first three attempts: Claude Code writes each content
block as its own JSONL record, so a turn's text and its tool_use are SEPARATE
records sharing a `requestId`. Grouping per record makes every picker look like
it had no lead-in text. Group by requestId (see `turns()`).
"""
import argparse, collections, json, os, re, sys

PROJECTS = os.path.expanduser("~/.claude/projects")
# Claude Code mangles a project's cwd into its directory name: /Users/me/Sites/app
# becomes -Users-me-Sites-app. Strip whatever THIS user's home maps to, so a label
# names the project rather than the machine it happened to be measured on.
HOME_SLUG = os.path.expanduser("~").replace("/", "-")


def load(path):
    out = []
    try:
        fh = open(path, errors="replace")
    except OSError:
        return out
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def turns(recs):
    """Group assistant records into turns by requestId, preserving order."""
    order, by_rid = [], {}
    for r in recs:
        if r.get("type") != "assistant" or r.get("isSidechain"):
            continue
        rid = r.get("requestId") or r.get("uuid")
        if rid not in by_rid:
            by_rid[rid] = {"ts": r.get("timestamp", ""), "text": [], "pickers": []}
            order.append(rid)
        t = by_rid[rid]
        for b in (r.get("message") or {}).get("content") or []:
            if b.get("type") == "text":
                t["text"].append(b.get("text", ""))
            elif b.get("type") == "tool_use" and b.get("name") == "AskUserQuestion":
                t["pickers"].append(b.get("input", {}))
    return [by_rid[r] for r in order]


def metrics(s):
    return dict(
        chars=len(s),
        bare=len(s) < 40,
        chunk=bool(re.search(r"📖|(?<![A-Za-z])F-\d", s)),
        diff="```diff" in s,
        table=bool(re.search(r"^\s*\|.*\|.*\|", s, re.M)),
        before=bool(re.search(r"(?i)\*\*before|before\s*(→|->)|before\s*\(", s)),
        tradeoff=bool(re.search(r"(?i)trade-?off", s)),
        rec=bool(re.search(r"(?i)recommend", s)),
    )


FIELDS = ("bare", "chunk", "diff", "table", "before", "tradeoff", "rec")


def scan(path):
    recs = load(path)
    if not recs:
        return None
    items = []
    for t in turns(recs):
        if t["pickers"]:
            items.append({"ts": t["ts"], "text": "\n".join(t["text"]).strip(),
                          "qs": t["pickers"]})
    if not items:
        return None
    skills = []
    for r in recs:
        if r.get("type") != "assistant":
            continue
        for b in (r.get("message") or {}).get("content") or []:
            if b.get("type") == "tool_use" and b.get("name") == "Skill":
                s = (b.get("input") or {}).get("skill", "")
                if s:
                    skills.append(s)
    return dict(
        path=path,
        date=next((r.get("timestamp") for r in recs if r.get("timestamp")), "")[:10],
        model=next(((r.get("message") or {}).get("model")
                    for r in recs if (r.get("message") or {}).get("model")), "?"),
        worktree=os.path.basename(os.path.dirname(path)),
        items=items,
        skills=skills,
        triage_loaded=any(s.split(":")[-1] == "triage" for s in skills),
    )


def discover(project, since):
    if not os.path.isdir(PROJECTS):
        sys.exit(f"no transcripts directory at {PROJECTS}")
    out = []
    for d in os.listdir(PROJECTS):
        if project and project not in d:
            continue
        full = os.path.join(PROJECTS, d)
        if not os.path.isdir(full):
            continue
        for f in os.listdir(full):
            if f.endswith(".jsonl"):
                out.append(os.path.join(full, f))
    sessions = [s for s in (scan(p) for p in out) if s]
    if since:
        sessions = [s for s in sessions if s["date"] >= since]
    return sorted(sessions, key=lambda s: s["date"])


def pct(counter, n, field):
    return f"{100 * counter[field] // n}%" if n else "-"


def tally(sessions):
    c = collections.Counter()
    n = 0
    chars = 0
    for s in sessions:
        for it in s["items"]:
            m = metrics(it["text"])
            n += 1
            chars += m["chars"]
            for f in FIELDS:
                c[f] += bool(m[f])
    return c, n, chars


def short(wt):
    return wt.replace(HOME_SLUG, "").replace("--claude-worktrees-", "/").lstrip("-")[-30:]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?", default="",
                    help="substring of the project dir under ~/.claude/projects")
    ap.add_argument("--since", metavar="YYYY-MM-DD", help="only sessions on/after this date")
    ap.add_argument("--monthly", action="store_true", help="aggregate by month")
    ap.add_argument("--by-skill", action="store_true",
                    help="aggregate by whether the triage skill was loaded")
    ap.add_argument("--dump", type=int, metavar="N",
                    help="print picker N of the newest session in full (1-based)")
    a = ap.parse_args()

    sessions = discover(a.project, a.since)
    if not sessions:
        sys.exit("no sessions with pickers matched")

    if a.dump:
        s = sessions[-1]
        if a.dump > len(s["items"]):
            sys.exit(f"newest session has {len(s['items'])} picker(s)")
        it = s["items"][a.dump - 1]
        print(f"# {s['date']}  {short(s['worktree'])}  picker {a.dump}/{len(s['items'])}")
        print(f"# triage skill loaded: {s['triage_loaded']}")
        print(f"# skills: {', '.join(s['skills']) or '(none)'}\n")
        print(f"--- SAME-TURN TEXT ({len(it['text'])} chars) ---")
        print(it["text"] or "(empty)")
        print("\n--- PICKER ---")
        for q in it["qs"]:
            for sub in q.get("questions", []):
                print(" Q:", sub.get("question", ""))
                for o in sub.get("options", []):
                    print(f"    - {o.get('label','')} :: {o.get('description','')}")
        return

    hdr = f"{'':2}{'pickers':>8}{'bare':>6}{'chunk':>7}{'diff':>6}{'table':>7}{'before':>8}{'tradeoff':>10}{'rec':>5}{'avgChars':>10}"

    if a.monthly or a.by_skill:
        if a.monthly:
            groups = collections.OrderedDict()
            for s in sessions:
                groups.setdefault(s["date"][:7], []).append(s)
            width = 9
        else:
            groups = collections.OrderedDict([
                ("LOADED", [s for s in sessions if s["triage_loaded"]]),
                ("not loaded", [s for s in sessions if not s["triage_loaded"]]),
            ])
            width = 12
        print(f"{'group':{width}}{hdr}")
        for k, g in groups.items():
            c, n, chars = tally(g)
            if not n:
                print(f"{k:{width}}  (no pickers)")
                continue
            cells = "".join(f"{pct(c,n,f):>{w}}" for f, w in
                            zip(FIELDS, (6, 7, 6, 7, 8, 10, 5)))
            print(f"{k:{width}}{'':2}{n:>8}{cells}{chars//n:>10}   ({len(g)} sessions)")
        return

    print(f"{'date':12}{'worktree':32}{'triage?':9}{'pk':>4}{'diff':>6}{'before':>8}{'trdoff':>8}{'avgC':>8}")
    for s in sessions:
        c, n, chars = tally([s])
        print(f"{s['date']:12}{short(s['worktree']):32}"
              f"{'LOADED' if s['triage_loaded'] else '-':9}"
              f"{n:>4}{c['diff']:>6}{c['before']:>8}{c['tradeoff']:>8}{chars//n:>8}")
    c, n, chars = tally(sessions)
    print(f"\n{'TOTAL':12}{'':32}{'':9}{n:>4}"
          f"{pct(c,n,'diff'):>6}{pct(c,n,'before'):>8}{pct(c,n,'tradeoff'):>8}{chars//n:>8}")


if __name__ == "__main__":
    main()
