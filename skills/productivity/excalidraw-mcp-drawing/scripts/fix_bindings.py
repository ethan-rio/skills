#!/usr/bin/env python3
"""
Fix arrow bindings in an .excalidraw file.

Excalidraw treats an arrow as "attached" (moves with its shape) only if the
arrow has startBinding/endBinding AND the target shape's boundElements array
contains a reverse pointer to the arrow. Files authored by hand or by older
tools often miss the reverse pointer, or miss `focus`/`gap` on the binding
itself. This script patches both so the file round-trips cleanly.

Usage:
    python3 fix_bindings.py path/to/diagram.excalidraw
"""

import json
import sys
from pathlib import Path


def fix(path: Path) -> int:
    data = json.loads(path.read_text())
    by_id = {e["id"]: e for e in data["elements"]}
    changed = 0

    for el in data["elements"]:
        if el.get("type") not in ("arrow", "line"):
            continue
        for key in ("startBinding", "endBinding"):
            binding = el.get(key)
            if not isinstance(binding, dict):
                continue
            # Fill in Excalidraw's required pinning fields if missing
            if "focus" not in binding:
                binding["focus"] = 0
                changed += 1
            if "gap" not in binding:
                binding["gap"] = 1
                changed += 1

            target = by_id.get(binding.get("elementId"))
            if not target:
                continue
            bound = target.setdefault("boundElements", [])
            if not any(
                isinstance(x, dict) and x.get("id") == el["id"] for x in bound
            ):
                bound.append({"id": el["id"], "type": "arrow"})
                changed += 1

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return changed


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: fix_bindings.py <path-to-.excalidraw>", file=sys.stderr)
        return 1
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"not found: {path}", file=sys.stderr)
        return 1
    n = fix(path)
    print(f"{path}: {n} binding field(s) patched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
