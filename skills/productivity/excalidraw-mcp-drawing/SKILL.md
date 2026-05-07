---
name: excalidraw-mcp-drawing
description: Draw high-quality diagrams on an Excalidraw canvas via the excalidraw-mcp server, and save them to disk correctly. Use when the user asks to draw, diagram, sketch, mind-map, flowchart, decision matrix, architecture, timeline, or illustrate anything on Excalidraw, or when exporting a live canvas to an `.excalidraw` file. Covers diagram-type selection (flow vs mind map vs tree vs matrix), shape semantics, arrow-to-shape binding pitfalls, palettes per diagram type, pre-draw planning, and the two-way `boundElements` requirement for saved files.
---

# excalidraw-mcp-drawing

How to produce clean, attached, movable diagrams through the `excalidraw-mcp` server, and how to save them so arrows survive a round-trip.

## Before you draw — the 4 hard rules

1. **Ensure a connection first.** Before any drawing tool, confirm you're connected to a room. If any tool returns `Not connected. Call connect() first.`, or the user hasn't provided a collab URL in this conversation, **stop and ask the user for the Excalidraw collab URL** (format: `https://excalidraw.com/#room=<id>,<key>`). Do not guess URLs, do not reuse URLs from other conversations, do not proceed without one. Once you have it, call `connect` and continue.

2. **Always call `get_scene` first** when adding to a non-empty canvas. Existing elements have IDs and positions you need to avoid overlapping. Skipping this is the #1 cause of collisions.

3. **Pre-assign `id` on every shape that an arrow will point to**, in the same `draw_elements` call. Arrows reference shapes by ID via `startBinding.elementId` / `endBinding.elementId` — auto-generated UUIDs won't be known at the time you author the arrow.

4. **Plan the full layout before the first tool call.** Sketch positions (x, y, width, height) for all shapes and the routing of all arrows on paper or in your head. Partial drawing followed by "I'll figure arrows out later" produces overlaps and re-work.

## Arrow binding — the subtle part

For an arrow to *truly attach* (move with the shape when the shape is dragged), three things must all be true:

- Arrow has `startBinding` and/or `endBinding` with `elementId` + `fixedPoint`.
- `fixedPoint` is **normalised**: `[0..1, 0..1]`, top-left of the shape is `[0,0]`, bottom-right is `[1,1]`. Not pixel coords.
- The target shape's `boundElements` array includes `{id: <arrow-id>, type: "arrow"}`.

The `excalidraw-mcp` server adds the reverse pointer (bullet 3) automatically on `draw_elements`. If you're writing arrows any other way (e.g. to an `.excalidraw` file directly), **you must write both sides yourself** — Excalidraw treats a one-sided binding as loose-proximity, not attached.

**Minimal pinned arrow:**

```json
{
  "type": "arrow",
  "x": 100, "y": 100,
  "points": [[0, 0], [200, 50]],
  "strokeColor": "#64748B",
  "endArrowhead": "arrow",
  "startBinding": { "elementId": "source-id", "fixedPoint": [1, 0.5] },
  "endBinding":   { "elementId": "target-id", "fixedPoint": [0, 0.5] }
}
```

The server auto-fills `focus: 0, gap: 1`. If you're writing the file directly, add those fields yourself.

## Choose the diagram type *before* you pick a palette

A mind map is only one shape of diagram, and forcing every piece of content into a hub-and-spoke layout hides relationships that matter. **Before drawing, ask: what is the content actually *doing*?** Then pick the structure that makes that shape visible.

| Content shape | Best diagram | When to use |
|---|---|---|
| A set of independent ideas clustered around one question | **Mind map / radial** | Talk/essay with a central thesis and 6-12 roughly peer-level ideas. |
| Steps in a pipeline, decisions flowing forward | **Flowchart / left-to-right** | How a system processes input, request lifecycle, ETL pipeline. |
| A process with branches and merges | **Swimlane or BPMN-lite** | Multi-actor workflows (user / service / DB). Swimlanes per actor, boxes per step. |
| A hierarchy or decomposition | **Tree (top-down)** | Org chart, type hierarchy, breakdown of a concept into sub-concepts. |
| Before vs. after, option A vs. option B | **Side-by-side comparison** | Migration docs, design options, trade-off tables rendered visually. |
| A small number of overlapping sets | **Venn / overlapping rectangles** | Intersection of concerns, Venn of capabilities. |
| Events on a time axis | **Timeline / horizontal strip** | Roadmap, project phases, historical narrative. |
| A spectrum or 2-axis trade-off | **2D matrix / quadrant** | Impact-vs-effort, urgency-vs-importance, Gartner-style. |
| Components and their connections, no clear hierarchy | **Graph / network** | System architecture where nodes interact bidirectionally. |
| Layered architecture (presentation / logic / data) | **Stacked horizontal bands** | 3-tier or 7-layer diagrams, AWS architecture with VPC/subnet/service layering. |

**Rule of thumb:** if the content has a clear *direction* (steps, time, causation), don't use a mind map — use a flow. If the content has a clear *hierarchy*, use a tree. A mind map is the default only when ideas are peer-level and tied by a shared question, not by causal order.

**Be creative where it helps legibility, rigid where it helps correctness.** Vary shape (rectangle for things, ellipse for states, diamond for decisions), colour (categories), and layout (radial vs. linear vs. grid) to communicate structure — not for decoration. A reader should be able to read the *type* of relationship from the diagram without reading the labels.

### Shape semantics

- **Rectangle** — a thing, noun, component, card of content.
- **Ellipse** — a state, phase, or soft grouping.
- **Diamond** — a decision point (yes/no, branch).
- **Frame** — a logical grouping that stays together when items inside are rearranged (use for swimlanes, layered architectures, zones).
- **Arrow** — directed relationship (flow, causes, depends on). Direction matters.
- **Line** (no arrowhead) — undirected association.

Pick shapes based on *what the element represents*, not aesthetic preference.

## Palettes by diagram type

The palette below is the **mind map default**. For other diagram types, pick a palette that matches the structure:

| Role | Fill | Stroke |
|---|---|---|
| Problem framing | `#FEF3C7` | `#D97706` (amber) |
| Personal answers / "why" | `#D1FAE5` | `#059669` (green) |
| Structural opportunities | `#DBEAFE` | `#2563EB` (blue) |
| Unsolved frontiers / risks | `#EDE9FE` | `#7C3AED` (purple) |
| Central node | `#1E293B` fill, `#FFFFFF` text | `#1E293B` |
| Takeaway / summary bar | `#F1F5F9` | `#64748B` |

Pick one role per node and stick to it. Arrows inherit their source node's stroke colour.

**For flowcharts / pipelines:** one stroke colour for the happy path (blue `#2563EB`), a second for error / fallback paths (red `#DC2626` fill `#FEE2E2`), neutral grey for context boxes.

**For comparison / before-after:** green `#059669` + `#D1FAE5` for the recommended / after side; amber `#D97706` + `#FEF3C7` for the current / before side; keep both sides perfectly aligned vertically.

**For architecture / layered:** use a frame per layer with a very light background tint (`#F8FAFC`, `#F1F5F9`, `#E2E8F0` top to bottom), components as white-fill rectangles inside. No colour on components unless colour carries meaning (e.g. region, owner).

**For timelines:** one horizontal axis line, milestones as ellipses above/below, colour only used to mark delivered (green) vs planned (amber) vs blocked (red).

When in doubt, fewer colours read as more intentional. Greys + one accent often beats a full rainbow.

## Containers, never bare text

Every card, section, or labelled group MUST be a `rectangle` (or `ellipse` / `diamond` / `frame`) with `width` and `height`, and the label goes inside via the `label` property or a separate `text` element positioned within the box. Standalone text is only for titles and annotations — never for content cards.

## Spacing defaults

- ≥ 80px horizontal gap between shapes (room for arrow + label).
- ≥ 120px vertical gap between rows (room for annotations).
- Arrow labels are unbound text — place them adjacent to the arrow, never on the arrow or over content.
- If an arrow would cross another shape, route it with an L or Z: `points: [[0,0],[dx,0],[dx,dy]]`.

## Saving to a file — fix bindings on export

When exporting a live canvas to an `.excalidraw` file, the arrows on the server have the correct bindings, but if you reconstruct the JSON manually (or round-trip through an older tool) the reverse pointer is often missing.

Run this after writing the file:

```python
import json, sys
path = sys.argv[1]
with open(path) as f: data = json.load(f)
by_id = {e["id"]: e for e in data["elements"]}
for e in data["elements"]:
    if e.get("type") not in ("arrow", "line"): continue
    for key in ("startBinding", "endBinding"):
        b = e.get(key)
        if not isinstance(b, dict): continue
        b.setdefault("focus", 0)
        b.setdefault("gap", 1)
        target = by_id.get(b.get("elementId"))
        if not target: continue
        be = target.setdefault("boundElements", [])
        if not any(x.get("id") == e["id"] for x in be if isinstance(x, dict)):
            be.append({"id": e["id"], "type": "arrow"})
with open(path, "w") as f: json.dump(data, f, indent=2, ensure_ascii=False)
```

Save as `scripts/fix_bindings.py` alongside this skill and invoke as `python3 scripts/fix_bindings.py <path-to-.excalidraw>`.

## Pre-flight checklist

Before the first `draw_elements` call:

- [ ] Collab URL is in this conversation. If not, **ask the user** before any tool call.
- [ ] `connect` has been called (or a previous call in this session confirmed the connection).
- [ ] Canvas state checked via `get_scene`, or confirmed empty.
- [ ] **Diagram type chosen** to match the content's actual shape (flow? tree? mind map? matrix?), not defaulted to mind map. Briefly justify the choice (one sentence) before drawing.
- [ ] Shape semantics respected — rectangles for things, ellipses for states, diamonds for decisions.
- [ ] Every shape that an arrow will reference has a pre-assigned string `id`.
- [ ] Layout positions calculated for all shapes (not drawn incrementally).
- [ ] Each node has a role from the palette above (if it's a mind map).
- [ ] Arrow routing sketched — no arrow crosses a shape.
- [ ] Labels live *inside* rectangles, not as floating text.

## Common failures and their causes

| Symptom | Cause | Fix |
|---|---|---|
| Arrow endpoint free, doesn't follow shape | Only one side bound, or `focus`/`gap` missing | Bind both ends; let server set focus/gap, or set them manually |
| Arrow width/height = 0 on server response | `points` given as placeholder like `[[0,0],[100,0]]` without real coords | Use real absolute `x,y` and real relative `points` |
| Shapes overlap after drawing | Skipped `get_scene` on non-empty canvas | Always inspect first; calculate offsets from existing bounds |
| Text label white-on-white | Label placed on light container; server only auto-inverts on dark | Set `strokeColor` explicitly, or use `label` inside the shape |
| Saved `.excalidraw` file loses arrow attachment when reopened | Rectangles' `boundElements` missing reverse pointer | Run the `fix_bindings.py` snippet above |
