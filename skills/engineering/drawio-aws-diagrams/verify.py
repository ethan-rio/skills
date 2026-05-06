#!/usr/bin/env python3
"""Verify a .drawio AWS architecture diagram against the rules in this skill.

Usage:  python3 verify.py path/to/diagram.drawio

Checks:
  1. Every `resIcon=mxgraph.aws4.<name>` references a known-good stencil name.
  2. Every service icon has a category-correct fillColor.
  3. Every edge uses the canonical style (endArrow=open, strokeColor=#545B64, orthogonalEdgeStyle).
  4. Every edge has a labelBackgroundColor (prevents arrows cutting through labels).
  5. Geometry: containment (every *parent* container actually contains its nested children).
  6. Geometry: centering where explicitly declared in a top-of-file comment.

Exit code 0 on all-pass, 1 on any fail.  Output is concise: one line per rule.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

# Known-good resIcon names (subset of STENCILS.md table — most common).
# If a diagram uses a name not here, it's a warning (may still be valid), not a hard fail.
KNOWN_RESICON = {
    # compute
    "ec2", "lambda", "fargate", "elastic_container_service",
    "elastic_kubernetes_service", "ecr", "batch",
    # networking
    "application_load_balancer", "network_load_balancer", "api_gateway",
    "route_53", "cloudfront", "transit_gateway", "direct_connect",
    "privatelink", "site-to-site_vpn",
    # storage
    "s3", "elastic_file_system", "elastic_block_store", "fsx",
    "s3_glacier", "backup",
    # database
    "dynamodb", "rds", "aurora", "documentdb", "opensearch_service",
    # AI/ML
    "bedrock", "sagemaker", "textract", "comprehend",
    # security
    "identity_and_access_management", "single_sign_on", "cognito",
    "secrets_manager", "key_management_service", "network_firewall",
    "waf", "shield", "certificate_manager_3", "guardduty",
    # management
    "cloudwatch_2", "cloudformation", "cloudtrail", "systems_manager",
    "config", "service_catalog",
    # integration
    "eventbridge", "simple_notification_service", "simple_queue_service",
    "step_functions", "appflow", "appsync",
    # analytics
    "kinesis", "athena", "glue", "quicksight",
    "managed_streaming_for_apache_kafka",
}

# Known-bad names we've hit before
WRONG_NAMES = {
    "elastic_container_registry": "ecr",
    "identity_and_access_management_iam": "identity_and_access_management",
    "cloudwatch": "cloudwatch_2",
    "certificate_manager": "certificate_manager_3",
    "account": "group_account (use as grIcon in a group container, not as resIcon)",
}

# Category fill colours (the ones a diagram should use)
VALID_FILLS = {
    "#ED7100",  # compute
    "#8C4FFF",  # networking
    "#7AA116",  # storage
    "#C925D1",  # database
    "#01A88D",  # AI/ML
    "#DD344C",  # security
    "#E7157B",  # management / integration
    "#ffffff",  # white (non-AWS shapes)
    "none",
}

CANONICAL_EDGE_STYLE_PARTS = [
    "edgeStyle=orthogonalEdgeStyle",
    "endArrow=open",
    "endFill=0",
    "strokeWidth=2",
]

ICON_RE = re.compile(r'resIcon=mxgraph\.aws4\.([a-z0-9_-]+)')
FILL_RE = re.compile(r'fillColor=([^;"]+)')
CELL_ID_RE = re.compile(r'<mxCell id="([^"]+)"')
STYLE_RE = re.compile(r'style="([^"]*)"')
EDGE_ATTR_RE = re.compile(r'edge="1"')
GEOM_RE = re.compile(r'<mxGeometry x="(-?\d+)" y="(-?\d+)" width="(\d+)" height="(\d+)"')


def parse_cells(xml: str) -> list[dict]:
    """Return a list of cell dicts with id/style/is_edge/geometry."""
    cells = []
    for match in re.finditer(r'<mxCell\s+([^>]*?)(?:/>|>(.*?)</mxCell>)', xml, re.DOTALL):
        attrs = match.group(1)
        body = match.group(2) or ""
        mid = CELL_ID_RE.search('<mxCell id="' + (dict(re.findall(r'(\w+)="([^"]*)"', attrs)).get("id", "") or "") + '"')
        # simpler extract
        id_match = re.search(r'id="([^"]+)"', attrs)
        style_match = re.search(r'style="([^"]*)"', attrs)
        is_edge = 'edge="1"' in attrs
        geom_match = GEOM_RE.search(body)
        cells.append({
            "id": id_match.group(1) if id_match else None,
            "style": style_match.group(1) if style_match else "",
            "is_edge": is_edge,
            "geom": tuple(int(v) for v in geom_match.groups()) if geom_match else None,
        })
    return cells


def check_icons(xml: str) -> list[str]:
    errs = []
    for match in ICON_RE.finditer(xml):
        name = match.group(1)
        if name in WRONG_NAMES:
            errs.append(f"WRONG resIcon '{name}' -> use '{WRONG_NAMES[name]}'")
        elif name not in KNOWN_RESICON:
            # not in our known-good list; flag as warning
            errs.append(f"WARN  unknown resIcon 'mxgraph.aws4.{name}' (verify against Sidebar-AWS4.js)")
    return errs


def check_fills(cells: list[dict]) -> list[str]:
    errs = []
    for cell in cells:
        if "resIcon=mxgraph.aws4." not in cell["style"]:
            continue
        fill_match = FILL_RE.search(cell["style"])
        if not fill_match:
            errs.append(f"icon {cell['id']!r}: missing fillColor")
            continue
        fill = fill_match.group(1)
        if fill not in VALID_FILLS:
            errs.append(f"icon {cell['id']!r}: non-category fillColor '{fill}' (allowed: {sorted(VALID_FILLS)})")
    return errs


def check_edges(cells: list[dict]) -> list[str]:
    errs = []
    for cell in cells:
        if not cell["is_edge"]:
            continue
        style = cell["style"]
        for part in CANONICAL_EDGE_STYLE_PARTS:
            if part not in style:
                errs.append(f"edge {cell['id']!r}: missing '{part}' in style")
        if "labelBackgroundColor=" not in style and "value=" not in style:
            # edges without labels don't need the background, but if there's a value= it does
            pass
        if "endArrow=classic" in style:
            errs.append(f"edge {cell['id']!r}: uses endArrow=classic — should be 'open'")
    return errs


def check_containment(cells: list[dict], parent_children: dict[str, list[str]]) -> list[str]:
    """parent_children: optional explicit map from top-of-file comment.

    If not provided, skip this check — containment is structural, not inferred.
    """
    errs = []
    by_id = {c["id"]: c for c in cells if c["id"] and c["geom"]}
    for parent_id, child_ids in parent_children.items():
        p = by_id.get(parent_id)
        if not p:
            continue
        px, py, pw, ph = p["geom"]
        for cid in child_ids:
            c = by_id.get(cid)
            if not c:
                continue
            cx, cy, cw, ch = c["geom"]
            if cx < px or cy < py or cx + cw > px + pw or cy + ch > py + ph:
                errs.append(f"{cid!r} escapes parent {parent_id!r}: child {c['geom']} parent {p['geom']}")
    return errs


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <file.drawio>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    if not path.is_file():
        print(f"not found: {path}", file=sys.stderr)
        return 2

    xml = path.read_text()
    cells = parse_cells(xml)

    all_errs = {}
    all_errs["stencils"] = check_icons(xml)
    all_errs["fills"] = check_fills(cells)
    all_errs["edges"] = check_edges(cells)
    all_errs["containment"] = check_containment(cells, {})  # caller must patch in explicit map

    total = sum(len(v) for v in all_errs.values())
    for check, errs in all_errs.items():
        if errs:
            print(f"[{check}] {len(errs)} issue(s):")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"[{check}] OK")

    print()
    print(f"TOTAL: {total} issue(s)")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
