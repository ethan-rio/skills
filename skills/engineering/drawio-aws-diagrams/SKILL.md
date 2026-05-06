---
name: drawio-aws-diagrams
description: Author professional AWS architecture diagrams as .drawio XML on the first attempt. Use when creating, editing, or auditing any .drawio / diagrams.net file that uses AWS service icons, especially when a reference image or AWS Architecture Icon convention is in play. Pre-loads the 17 most-used stencil names, official fill colours, container hierarchy rules, edge style, and a deterministic grid layout that avoids the usual iteration loops.
---

# draw.io AWS Diagrams

**Rigid skill.** Diagrams drift fast without discipline. Follow the checklists in order.

## Quick rule — before you write any `.drawio` XML

1. Ask the user: "Do you have a reference diagram to match, or should I use AWS default layout conventions?"
2. If a reference exists: read it first, extract layout (zones, bands, swim-lanes), note which icons appear.
3. Pick stencils from [STENCILS.md](STENCILS.md) — **never invent a name**. If a service is not in the table, run one WebFetch against `https://github.com/jgraph/drawio/blob/dev/src/main/webapp/js/diagramly/sidebar/Sidebar-AWS4.js` to verify, then add it to the table.
4. Draft math on paper first (grid constants, column x-positions, row y-positions). Self-document as a top-of-file HTML comment.
5. Write the XML once. Verify containment + centering with the script in [verify.py](verify.py). Only then show the user.

## Workflows

### Workflow A — new diagram from scratch

Checklist:
- [ ] Canvas chosen (1800×1300 works for most multi-tier AWS diagrams — use that unless a reference forces a different size)
- [ ] Grid constants declared in a top-of-file HTML `<!-- ... -->` comment (ICON, GUTTER, column x, row y)
- [ ] AWS container hierarchy followed (see [CONVENTIONS.md](CONVENTIONS.md) §2)
- [ ] Every service icon's `resIcon=` + `fillColor=` looked up in [STENCILS.md](STENCILS.md) — **do not guess**
- [ ] Canonical edge style applied to every edge (see [CONVENTIONS.md](CONVENTIONS.md) §3) — `strokeColor=#545B64;endArrow=open;endFill=0;strokeWidth=2;edgeStyle=orthogonalEdgeStyle;labelBackgroundColor=#ffffff`
- [ ] `labelBackgroundColor=#ffffff` on every edge label and service icon label
- [ ] Ran `python3 verify.py <file>` and got all-pass
- [ ] Diagram has a mermaid fallback inline in the surrounding markdown for GitHub-preview compatibility

### Workflow B — editing an existing `.drawio` file

- [ ] First pass: read the file and list every `shape=mxgraph.aws4.*` / `resIcon=...` reference. Cross-check against [STENCILS.md](STENCILS.md). Report mismatches to the user before editing.
- [ ] Preserve the existing grid constants in the comment. If the grid is undocumented, extract + document before changing anything.
- [ ] Run `verify.py` before and after. Report the delta.

### Workflow C — reference-driven layout

When the user provides a reference image (JPG/SVG/screenshot):

1. Read the image.
2. Describe the layout out loud in ≤10 bullets: *"top band X, left strip Y, vertical divider band Z..."*
3. Map each zone to a coloured pastel fill from the [palette](CONVENTIONS.md#colour-palette).
4. Draft math constants. Grid cells align to the reference's implicit columns.
5. Author XML. Verify. Show.

## Red flags — stop immediately

- "Let me just use `mxgraph.aws4.service_name`" — **NO**. Check the table.
- Overriding `fillColor` on an AWS service icon to a colour different from the category colour — **NO**. AWS icons have baked-in category colours; overriding is a Rule 9 violation.
- Using `endArrow=classic` or default bezier — **NO**. Canonical style is `endArrow=open;endFill=0;edgeStyle=orthogonalEdgeStyle`.
- Nesting AWS Cloud → VPC with no Region between — **NO**. Order is Cloud > Region > VPC > AZ > Subnet.
- Skipping `labelBackgroundColor=#ffffff` — **NO**. Edges will cut through labels.
- Authoring coordinates ad-hoc (`x=471, y=240, x=473, y=245`...) — **NO**. Declare grid constants first.

## Reference files

- [STENCILS.md](STENCILS.md) — the `resIcon=` + `fillColor=` lookup table (41 services)
- [CONVENTIONS.md](CONVENTIONS.md) — container hierarchy, colours, edge style, grid math patterns
- [verify.py](verify.py) — Python script: containment, centering, colour compliance checks
