#!/usr/bin/env python3
"""
One-off surgery for the connector cleanup (see DOCS_CLEANUP_CHECKLIST.md Batch A).

Removes stale connector groups from docs.json, renames three connector slugs to
match their manifest key, and adds redirects for every path that moves or goes
away. Run with --dry-run first; it prints exactly what it would touch and
changes nothing.

    python bin/connector-nav-surgery.py --dry-run
    python bin/connector-nav-surgery.py --apply
"""
import json
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_JSON = ROOT / "docs.json"
CARDS_DIR = ROOT / "nerve-centre" / "kpi-cards"
PREFIX = "nerve-centre/kpi-cards/"

# Connectors present in neither config/vortex_mind/manifests/ nor the connector
# seeders in the Laravel repo, verified 24 Jul 26.
DELETE = [
    "aircall", "app-dynamics", "bluesnap", "bugsnag", "chargebee", "checkout-com",
    "dialpad", "dynatrace", "eway", "fastly", "gocardless", "heap", "helcim",
    "kissmetrics", "logrocket", "looker", "lucidchart", "mailgun", "miro",
    "mode-analytics", "moosend", "mural", "nuvei", "omnisend", "postmark",
    "raygun", "recharge", "recurly", "ringcentral", "rollbar", "sparkpost",
    "stax-payments", "tableau", "vonage",
]

# Same connector, different slug. docs slug -> manifest-derived slug.
RENAME = {
    "brevo-sendinblue": "brevo",
    "customerio-api": "customer-io",
    "wrike-api": "wrike",
}

# Duplicate directory whose content is folded into another. Deleted, redirected
# at the connector level to the survivor.
MERGE = {"mixpanel-b": "mixpanel"}


def load():
    return json.loads(DOCS_JSON.read_text(encoding="utf-8"))


def group_slug(node):
    """If this group's page refs all belong to one connector, return its slug."""
    if not isinstance(node, dict):
        return None
    pages = node.get("pages")
    if not isinstance(pages, list):
        return None
    slugs = set()
    for p in pages:
        if not isinstance(p, str) or not p.startswith(PREFIX):
            return None
        rest = p[len(PREFIX):]
        if "/" not in rest:
            return None
        slugs.add(rest.split("/", 1)[0])
    return slugs.pop() if len(slugs) == 1 else None


def prune_and_rename(node, removed, renamed):
    """Walk the whole nav tree. Drop groups belonging to DELETE/MERGE slugs and
    rewrite page refs for RENAME slugs. Prunes wherever a list of children
    appears (Mintlify nests groups inside `pages`), and descends through every
    other container so nothing is missed regardless of nesting depth."""
    if isinstance(node, dict):
        for key, value in list(node.items()):
            if isinstance(value, list):
                kept = []
                for child in value:
                    slug = group_slug(child)
                    if slug and (slug in DELETE or slug in MERGE):
                        removed.append(slug)
                        continue
                    if isinstance(child, str) and child.startswith(PREFIX):
                        rest = child[len(PREFIX):]
                        s = rest.split("/", 1)[0]
                        if s in DELETE or s in MERGE:
                            removed.append(s)
                            continue
                        if s in RENAME:
                            child = PREFIX + RENAME[s] + rest[len(s):]
                            renamed.append(s)
                    prune_and_rename(child, removed, renamed)
                    kept.append(child)
                node[key] = kept
            elif isinstance(value, dict):
                prune_and_rename(value, removed, renamed)
    elif isinstance(node, list):
        for child in node:
            prune_and_rename(child, removed, renamed)


def build_redirects(existing):
    """A connector-level redirect per moved/removed slug. Removed connectors
    point at the connector index so an old inbound link still lands somewhere
    useful rather than 404ing."""
    have = {r.get("source") for r in existing}
    out = []
    for slug in DELETE:
        src = f"/{PREFIX}{slug}/:slug*"
        if src not in have:
            out.append({"source": src, "destination": "/nerve-centre/connectors"})
    for old, new in {**RENAME, **MERGE}.items():
        src = f"/{PREFIX}{old}/:slug*"
        if src not in have:
            out.append({"source": src, "destination": f"/{PREFIX}{new}/:slug*"})
    return out


def main():
    if "--dry-run" not in sys.argv and "--apply" not in sys.argv:
        print(__doc__)
        return 1
    apply = "--apply" in sys.argv

    doc = load()
    before = json.dumps(doc)

    removed, renamed = [], []
    prune_and_rename(doc["navigation"], removed, renamed)
    new_redirects = build_redirects(doc.get("redirects", []))

    print(f"nav groups/pages removed : {len(removed)} refs across {len(set(removed))} connectors")
    print(f"page refs rewritten      : {len(renamed)} refs across {len(set(renamed))} connectors")
    print(f"redirects to add         : {len(new_redirects)}")

    print("\ndirectories to delete:")
    for s in DELETE + list(MERGE):
        d = CARDS_DIR / s
        n = len(list(d.glob("*.mdx"))) if d.is_dir() else 0
        print(f"   {'ok ' if d.is_dir() else 'MISSING'} {s:18s} {n:4d} pages")

    print("\ndirectories to rename:")
    for old, new in RENAME.items():
        src, dst = CARDS_DIR / old, CARDS_DIR / new
        state = "ok" if src.is_dir() and not dst.exists() else "CHECK"
        n = len(list(src.glob("*.mdx"))) if src.is_dir() else 0
        print(f"   {state:7s} {old:18s} -> {new:18s} {n:4d} pages")

    if not apply:
        print("\ndry run, nothing written. re-run with --apply")
        return 0

    for s in DELETE + list(MERGE):
        d = CARDS_DIR / s
        if d.is_dir():
            shutil.rmtree(d)
    for old, new in RENAME.items():
        src, dst = CARDS_DIR / old, CARDS_DIR / new
        if src.is_dir() and not dst.exists():
            src.rename(dst)

    doc.setdefault("redirects", []).extend(new_redirects)
    DOCS_JSON.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\napplied. docs.json rewritten ({len(before)} -> {DOCS_JSON.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
