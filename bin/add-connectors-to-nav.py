#!/usr/bin/env python3
"""
Insert connector groups into docs.json nav for every connector directory that
has files on disk but no nav entry. Companion to
generate_connector_docs.py in the platform repo, which writes the files but
does not touch this repo's docs.json.

    python bin/add-connectors-to-nav.py --dry-run
    python bin/add-connectors-to-nav.py --apply

Category -> nav group mapping matches the manifest `category:` field (see
--platform). Three categories have no existing docs.json group and are
created: Cloud Platforms, Version Control, Collaboration.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_JSON = ROOT / "docs.json"
CARDS_DIR = ROOT / "nerve-centre" / "kpi-cards"

# AIOS category -> exact docs.json category group label.
CATEGORY_TO_GROUP = {
    "Content & Docs": "Content & Docs",
    "Cloud Platforms": "Cloud Platforms",       # new
    "Databases": "Databases",
    "Ecommerce": "E-commerce Platforms",
    "Notifications": "Notifications",
    "Payments": "Payments",
    "Version Control": "Version Control",       # new
    "Analytics": "Analytics",
    "Collaboration": "Collaboration",           # new
    "Project Management": "Project Management",
}

# Where a brand-new category group is inserted, relative to the existing
# "KPI Cards" pages list - kept adjacent to a related group rather than
# appended at the end, so the nav reads in a sensible order.
NEW_GROUP_AFTER = {
    "Cloud Platforms": "Databases",
    "Version Control": "Content & Docs",
    "Collaboration": "Project Management",
}


def find_group(node, want):
    if isinstance(node, dict):
        if node.get("group") == want:
            return node
        for v in node.values():
            r = find_group(v, want)
            if r is not None:
                return r
    elif isinstance(node, list):
        for x in node:
            r = find_group(x, want)
            if r is not None:
                return r
    return None


def find_parent_list_containing(node, target):
    """Find the `pages` list that directly contains `target` (by identity)."""
    if isinstance(node, dict):
        for v in node.values():
            r = find_parent_list_containing(v, target)
            if r is not None:
                return r
    elif isinstance(node, list):
        if any(x is target for x in node):
            return node
        for x in node:
            r = find_parent_list_containing(x, target)
            if r is not None:
                return r
    return None


def connector_pages(slug):
    d = CARDS_DIR / slug
    names = sorted(p.stem for p in d.glob("*.mdx"))
    ordered = []
    for special in ("index", "audit", "sentiment"):
        if special in names:
            ordered.append(special)
            names.remove(special)
    ordered.extend(sorted(names))
    return [f"nerve-centre/kpi-cards/{slug}/{n}" for n in ordered]


def main():
    if "--dry-run" not in sys.argv and "--apply" not in sys.argv:
        print(__doc__)
        return 1
    apply = "--apply" in sys.argv

    doc = json.loads(DOCS_JSON.read_text(encoding="utf-8"))
    kpi_cards = find_group(doc["navigation"], "KPI Cards")

    # Which connector dirs already have a nav group (by slug match on any
    # page ref inside it), vs which are missing entirely.
    all_refs = set()

    def collect(node):
        if isinstance(node, dict):
            for v in node.values():
                collect(v)
        elif isinstance(node, list):
            for x in node:
                if isinstance(x, str):
                    all_refs.add(x)
                else:
                    collect(x)

    collect(doc["navigation"])

    present_slugs = {r.split("/")[2] for r in all_refs if r.startswith("nerve-centre/kpi-cards/") and len(r.split("/")) > 2}
    disk_slugs = {d.name for d in CARDS_DIR.iterdir() if d.is_dir()} - {"concepts"}
    missing_slugs = sorted(disk_slugs - present_slugs)

    print(f"connector dirs on disk: {len(disk_slugs)}, already in nav: {len(present_slugs & disk_slugs)}, missing: {len(missing_slugs)}")

    import yaml
    man_dir = Path(r"c:\Users\Susant\Desktop\AgenticWorkflow\Agentic-workflow-SSO-LOGIN\config\vortex_mind\manifests")

    additions = {}  # group label -> list of connector-group dicts to add
    for slug in missing_slugs:
        key = slug.replace("-", "_")
        man_path = man_dir / f"{key}.yaml"
        if not man_path.is_file():
            print(f"  SKIP {slug}: no manifest at {man_path}")
            continue
        manifest = yaml.safe_load(man_path.read_text(encoding="utf-8"))
        category = manifest.get("category", "")
        group_label = CATEGORY_TO_GROUP.get(category)
        if not group_label:
            print(f"  SKIP {slug}: unmapped category {category!r}")
            continue
        display = manifest.get("display_name", key)
        conn_group = {"group": display, "pages": connector_pages(slug)}
        additions.setdefault(group_label, []).append(conn_group)

    for label, groups in additions.items():
        print(f"{label}: +{len(groups)} connector group(s) -> {[g['group'] for g in groups]}")

    if not apply:
        print("\ndry run, nothing written. re-run with --apply")
        return 0

    for label, groups in additions.items():
        existing = find_group(kpi_cards, label)
        if existing is not None:
            existing.setdefault("pages", [])
            existing["pages"].extend(groups)
            existing["pages"].sort(key=lambda g: g["group"] if isinstance(g, dict) else g)
            continue

        # New category group. Insert after NEW_GROUP_AFTER[label] if that
        # anchor exists in kpi_cards["pages"], else append at the end.
        new_group = {"group": label, "pages": sorted(groups, key=lambda g: g["group"])}
        anchor = NEW_GROUP_AFTER.get(label)
        idx = len(kpi_cards["pages"])
        if anchor:
            for i, g in enumerate(kpi_cards["pages"]):
                if isinstance(g, dict) and g.get("group") == anchor:
                    idx = i + 1
                    break
        kpi_cards["pages"].insert(idx, new_group)

    DOCS_JSON.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\napplied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
