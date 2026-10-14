#!/usr/bin/env python3
"""Keep each review loop's copy of the shared loop in sync with its source.

`skills/_shared/review-loop.md` is the single source of truth for the loop
shape. It is not a skill -- the directory has no SKILL.md -- so
`npx skills add` skips it entirely, and a loop installed that way loses the
very file its step 1 tells it to read. Nothing warns you: the installer
reports success and the skill fails later, at use time.

So each loop carries a generated copy inside its own skill folder. Both
install paths deliver that: the plugin ships the whole repo, and the skills
CLI copies a skill folder whole, subdirectories included. The copies are
generated and must never be hand-edited -- edit the source and re-run this.

  scripts/sync-shared.py           # write the copies
  scripts/sync-shared.py --check   # exit 1 if they have drifted (CI)
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "skills/_shared/review-loop.md"
TARGETS = [ROOT / "skills/doc-review-loop/review-loop.md",
           ROOT / "skills/code-review-loop/review-loop.md"]

BANNER = ("<!-- GENERATED from skills/_shared/review-loop.md -- do not edit.\n"
          "     Run scripts/sync-shared.py after changing the source.\n"
          "     This copy exists because `npx skills add` installs skill folders\n"
          "     only, and skills/_shared/ is not one. -->\n\n")


def expected() -> str:
    return BANNER + SOURCE.read_text()


def main() -> int:
    check = "--check" in sys.argv
    if not SOURCE.exists():
        print(f"missing source: {SOURCE}", file=sys.stderr)
        return 2

    want, drifted = expected(), []
    for t in TARGETS:
        rel = t.relative_to(ROOT)
        if t.exists() and t.read_text() == want:
            print(f"  ok       {rel}")
            continue
        if check:
            drifted.append(rel)
            print(f"  DRIFTED  {rel}")
        else:
            t.write_text(want)
            print(f"  written  {rel}")

    if drifted:
        print(f"\n{len(drifted)} copy/copies out of sync with "
              f"{SOURCE.relative_to(ROOT)}.\nRun: scripts/sync-shared.py",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
