#!/usr/bin/env python3
"""
Guard against the drift classes that accumulated before the 24 Jul 26 cleanup.

Run it before opening a docs PR:

    python bin/check-docs.py

Optionally point it at the platform repo to also check connector parity, which
is the check that catches "we shipped a connector and never documented it" and
"we deleted a connector and left the pages behind":

    python bin/check-docs.py --platform ../Agentic-workflow-SSO-LOGIN

Checks, in order:

  1. docs.json parses and every page it references exists on disk.
  2. Every .mdx on disk is referenced in docs.json (orphan pages).
  3. No hardcoded catalogue totals. Counts change every time a connector ships,
     so no page may state an exact connector or card total. Say "over 7,000
     cards" and "more than 200 connectors" instead.
  4. No em dashes or en dashes.
  5. With --platform: every connector directory maps to a real manifest, and
     every manifest has a connector directory.

Exit code is non-zero if any check fails, so it can gate CI.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_JSON = ROOT / "docs.json"
CARDS_DIR = ROOT / "nerve-centre" / "kpi-cards"

# Slugs that legitimately have no manifest, with the reason. Keep this list
# short and justified; it is not a dumping ground for drift.
ALLOWED_NO_MANIFEST = {
    "concepts": "shared concept pages, not a connector",
}

# Connectors with a manifest that deliberately have no docs yet. Empty on
# purpose: add a slug here only with a ticket reference.
ALLOWED_NO_DOCS: dict[str, str] = {}

# Only catalogue-WIDE totals are policed. Per-connector counts ("BigCommerce
# tracks 115 cards") are generator-maintained, informative, and out of scope:
# hence the four-digit floor on cards and three-digit floor on connectors,
# which is the scale only a catalogue total reaches.
COUNT_PATTERNS = [
    (re.compile(r"\b\d{1,3},\d{3}\s*\+?\s*(?:KPI\s+|live\s+)?cards?\b", re.I), "exact catalogue card total"),
    (re.compile(r"\b\d{1,3},\d{3}\s*\+?\s*(?:KPI\s+)?(?:pulses|metrics)\b", re.I), "exact catalogue card total"),
    (re.compile(r"\b\d{1,3},\d{3}-card\b", re.I), "exact catalogue card total"),
    (re.compile(r"\b\d{3}\s*\+?\s*(?:connectors?|integrations?|data sources?)\b", re.I), "exact connector total"),
    (re.compile(r"\b\d+\s+connector types\b", re.I), "exact connector-type count"),
]
# An approximator immediately before the number makes it durable and allowed:
# "over 200 connectors", "more than 7,000 cards".
APPROX_BEFORE = re.compile(r"(?:over|more than|about|around|upwards of|beyond)\s*\**\s*$", re.I)
# A range is describing one workspace, not the catalogue: "200 to 1,500 cards".
RANGE_BEFORE = re.compile(r"(?:to|and|between)\s*\**\s*$", re.I)
# Product names that contain a number and are not counts.
PRODUCT_NOISE = re.compile(r"(?:Dynamics|Office|Microsoft)\s*$", re.I)

DASHES = re.compile("[—–]")


def nav_pages(doc):
    """Every page ref anywhere in the nav tree."""
    out = set()

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                if isinstance(v, str):
                    out.add(v)
                else:
                    walk(v)

    walk(doc.get("navigation", {}))
    return out


def main():
    platform = None
    if "--platform" in sys.argv:
        platform = Path(sys.argv[sys.argv.index("--platform") + 1]).resolve()

    failures = []

    try:
        doc = json.loads(DOCS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"FAIL docs.json does not parse: {e}")
        return 1
    print("ok   docs.json parses")

    refs = nav_pages(doc)
    on_disk = {
        str(p.relative_to(ROOT).with_suffix("")).replace("\\", "/")
        for p in ROOT.rglob("*.mdx")
        if ".git" not in p.parts
    }

    dangling = sorted(r for r in refs if r not in on_disk)
    if dangling:
        failures.append(f"{len(dangling)} nav refs point at missing files")
        print(f"FAIL {len(dangling)} nav refs have no file:")
        for d in dangling[:15]:
            print(f"       {d}")
    else:
        print(f"ok   all {len(refs)} nav refs resolve to a file")

    # Mintlify serves the root index implicitly, so it is never listed in nav.
    orphans = sorted(p for p in on_disk if p not in refs and p != "index")
    if orphans:
        failures.append(f"{len(orphans)} pages not in nav")
        print(f"FAIL {len(orphans)} pages exist but are not in docs.json nav:")
        for o in orphans[:15]:
            print(f"       {o}")
    else:
        print(f"ok   no orphan pages")

    count_hits = []
    dash_hits = []
    for p in sorted(ROOT.rglob("*.mdx")):
        if ".git" in p.parts:
            continue
        rel = p.relative_to(ROOT).as_posix()
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for pat, why in COUNT_PATTERNS:
                for m in pat.finditer(line):
                    before = line[max(0, m.start() - 30):m.start()]
                    if (APPROX_BEFORE.search(before)
                            or RANGE_BEFORE.search(before)
                            or PRODUCT_NOISE.search(before)):
                        continue
                    count_hits.append((rel, i, why, m.group(0).strip()))
            if DASHES.search(line):
                dash_hits.append((rel, i))

    # Individual card pages are full of tables with real figures (revenue rows,
    # SKU counts). Only prose, connector index and concept pages are policed,
    # since that is where catalogue totals get quoted.
    count_hits = [
        h for h in count_hits
        if "/kpi-cards/" not in h[0] or h[0].endswith("/index.mdx") or "/concepts/" in h[0]
    ]

    if count_hits:
        failures.append(f"{len(count_hits)} hardcoded catalogue totals")
        print(f"FAIL {len(count_hits)} hardcoded totals (use 'over N' phrasing instead):")
        for rel, i, why, txt in count_hits[:20]:
            print(f"       {rel}:{i}  {why}: \"{txt}\"")
    else:
        print("ok   no hardcoded catalogue totals")

    # The pre-existing backlog (915 lines across 185 files as of 24 Jul 26)
    # was swept clean in bin/dash-sweep.py. This now gates, so nothing new
    # can creep back in.
    if dash_hits:
        failures.append(f"{len(dash_hits)} em/en dashes")
        files = sorted({r for r, _ in dash_hits})
        print(f"FAIL {len(dash_hits)} lines contain an em dash or en dash, across {len(files)} files:")
        for rel, i in dash_hits[:15]:
            print(f"       {rel}:{i}")
    else:
        print("ok   no em dashes or en dashes")

    if platform:
        man_dir = platform / "config" / "vortex_mind" / "manifests"
        if not man_dir.is_dir():
            print(f"skip connector parity, no manifests at {man_dir}")
        else:
            manifests = {p.stem.replace("_", "-") for p in man_dir.glob("*.yaml")}
            docdirs = {d.name for d in CARDS_DIR.iterdir() if d.is_dir()}

            no_manifest = sorted(docdirs - manifests - set(ALLOWED_NO_MANIFEST))
            no_docs = sorted(manifests - docdirs - set(ALLOWED_NO_DOCS))

            if no_manifest:
                failures.append(f"{len(no_manifest)} doc dirs with no manifest")
                print(f"FAIL {len(no_manifest)} connector doc dirs have no manifest:")
                print("       " + ", ".join(no_manifest))
            else:
                print(f"ok   every connector doc dir maps to a manifest")

            if no_docs:
                print(f"WARN {len(no_docs)} manifests have no docs directory:")
                print("       " + ", ".join(no_docs))
            else:
                print(f"ok   every manifest has a docs directory")

    print()
    if failures:
        print("FAILED: " + "; ".join(failures))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
