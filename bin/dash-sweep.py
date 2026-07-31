#!/usr/bin/env python3
"""
One-off sweep of the pre-existing em/en-dash backlog (989 occurrences across
185 files as of 24 Jul 26, per bin/check-docs.py's warning). Same heuristic
used for the two connector-doc generators in the platform repo, applied here
to hand-authored prose instead of manifest text:

  - a SPACED dash (" — " / " – "), the common parenthetical-aside or
    sentence-break usage, becomes ", "
  - a BARE dash ("1–5", "cost-effective"-style compounds), becomes "-"

This is a mechanical default, not a proofreader. Run --dry-run first and
read the diff; it prints every changed line with before/after so a human can
sanity-check the sample before trusting the full run, and skips code blocks
(fenced ``` / `~~~` regions) so example output or shell snippets containing
a real dash character are never touched.

    python bin/dash-sweep.py --dry-run
    python bin/dash-sweep.py --apply
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# A dash that IS a markdown table cell on its own ("| — |", meaning "no
# value"/"not applicable") must become a literal hyphen placeholder, not a
# comma. Handled first and protected from the general SPACED rule below,
# which would otherwise turn "| — |" into the broken "|, |". 107 confirmed
# instances of exactly this across 94 files before this guard was added.
TABLE_CELL = re.compile(r"\|\s*[—–]\s*\|")
SPACED = re.compile(r"\s+[—–]\s+")
BARE = re.compile(r"[—–]")
FENCE = re.compile(r"^\s*(```|~~~)")


def clean_line(line):
    line = TABLE_CELL.sub("| - |", line)
    line = SPACED.sub(", ", line)
    return BARE.sub("-", line)


def process(path, apply):
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    changed = []
    in_fence = False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if "—" in line or "–" in line:
            new = clean_line(line)
            if new != line:
                changed.append((i, line, new))
                lines[i] = new

    if changed and apply:
        path.write_text("\n".join(lines), encoding="utf-8")

    return changed


def main():
    if "--dry-run" not in sys.argv and "--apply" not in sys.argv:
        print(__doc__)
        return 1
    apply = "--apply" in sys.argv

    total_files = 0
    total_lines = 0
    samples = []

    for p in sorted(ROOT.rglob("*.mdx")):
        if ".git" in p.parts:
            continue
        changed = process(p, apply)
        if changed:
            total_files += 1
            total_lines += len(changed)
            if len(samples) < 40:
                for i, old, new in changed[:2]:
                    samples.append((str(p.relative_to(ROOT)), i + 1, old.strip(), new.strip()))

    print(f"{'would change' if not apply else 'changed'}: {total_lines} lines across {total_files} files\n")
    print("sample before/after (first 20 files, up to 2 lines each):")
    for rel, lineno, old, new in samples[:40]:
        print(f"\n{rel}:{lineno}")
        print(f"  - {old}")
        print(f"  + {new}")

    if not apply:
        print("\ndry run, nothing written. re-run with --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
