# AWS Diagram Conventions

## 1. Container hierarchy (strict)

Nest containers in this order. Skipping a level is wrong.

```
AWS Cloud
  Region
    VPC
      Availability Zone
        Subnet (public or private)
          Security Group
            Service
```

Exceptions:
- Single-region diagram: omit AWS Cloud. Region is the outermost AWS container.
- Service outside a VPC (S3, DynamoDB, ECR, Secrets Manager, CloudWatch): place inside Region but outside VPC.
- Logical groupings (ECS Cluster, Auto Scaling Group, Bedrock AgentCore): use group containers with an orange or grey dashed border. They nest inside an AZ or VPC depending on placement.

Official style attributes per container — see [STENCILS.md](STENCILS.md) § Group container.

**Essential flags on every group container:** `container=1;collapsible=0;recursiveResize=0`. Without `recursiveResize=0`, resizing the outer container resizes every child.

## 2. Colour palette

### Service icons — use the category colour only

Never override `fillColor` to a custom colour. The table in STENCILS.md gives the mandatory category colour for every service. Using a different colour misleads: blue-on-ALB means "networking", pink-on-ALB means "management" — AWS viewers read colour semantically.

<a id="colour-palette"></a>
### Zone fills (pastel tints) for visual separation

| Zone purpose | `fillColor=` | `strokeColor=` |
|---|---|---|
| Network / Security / Compliance | `#E8EEF5` | `#4A6785` |
| Supporting Services | `#F0F4FA` | `#4A6785` |
| Managed Storage / Data | `#F5EFFB` | `#8B5CF6` |
| External / Corporate Network | `#DBEAFE` | `#3B82F6` |
| Private Network Connectivity band | `#334155` (dark strip, white text) | — |
| Guardrails / Bedrock highlight | `#FCE7F3` | `#EC4899` |
| AgentCore Runtime | `#F4F6F9` | `#545B64` (dashed) |

All zone fills are used at full opacity with pastel tones — no transparency needed. Contrast is provided by the `strokeColor` accent.

### Text

- Body text: `#232F3E` (AWS almost-black) or `#1E293B`
- Secondary text / subtitles: `#545B64`
- Zone labels coloured to match their zone's stroke

## 3. Edge style (canonical — used in every official AWS template)

Every edge in every AWS architecture template uses **exactly one** style. Memorise it.

```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#545B64;endArrow=open;endFill=0;fontSize=11;labelBackgroundColor=#ffffff;
```

Points:
- **`endArrow=open;endFill=0`** is the open/unfilled chevron. NOT `classic`.
- **`strokeColor=#545B64`** is the default arrow colour. Override only for semantic emphasis (e.g. `#EC4899` for a delegated-identity DAX call).
- **`labelBackgroundColor=#ffffff`** — mandatory on every edge. Prevents arrows cutting through label text.
- **`orthogonalEdgeStyle`** — not `curved=1`, not default bezier.
- **Waypoints** — when an edge crosses a container, add an explicit `<Array as="points">` with 1–2 `<mxPoint>` entries to route it through a clear lane. Common lanes: 20–40 px inside the edge-of-page margin, or dedicated vertical lanes between column groups.

### Entry/exit pinning

For edges between specific points on shapes, set `exitX/Y/Dx/Dy` + `entryX/Y/Dx/Dy` so the edge always anchors at that location regardless of rerouting. Values:

| Side | `X` | `Y` |
|---|---|---|
| top | 0.5 | 0 |
| right | 1 | 0.5 |
| bottom | 0.5 | 1 |
| left | 0 | 0.5 |

Corners use combinations (e.g. top-right `1, 0`).

## 4. Icon size and label position

- Service icons: **78×78** (measured from 152/159 occurrences in official templates). If extreme density is needed (storage grid of 8+), drop to **68×68** uniformly.
- Label: `verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize=12;fontStyle=0` (not bold).
- Line breaks in label values: use `&#xa;` (XML newline entity), not `\n`.
- Labels never inside the icon, never to the side.

## 5. Grid math — deterministic layout

Declare grid constants in an HTML comment at the top of the `.drawio` file. Every `<mxGeometry>` x/y/width/height must be expressible from those constants. Example:

```xml
<!--
  Grid:
    MARGIN=40, ICON=78, ROW_PITCH=140, GUTTER=40
    Canvas 1800×1300

  COL_EXT   x=40   w=240  (external actors)
  COL_VPC   x=320  w=880  (VPC)
  COL_ST    x=1220 w=520  (storage strip)

  Region container x=40 y=110 w=1720 h=900
    VPC     x=320 y=340 w=880 h=640
      AZ    x=340 y=380 w=840 h=580

  Storage grid:
    col_x = [1280, 1560]   row_y = [240, 400, 560, 720]
-->
```

### Centering a child in a container

```
child.x = container.x + (container.width - child.width) / 2
```

Always integer. If the container's inner width is odd and the icon is 78, round to the nearest 10 so the icon sits on the grid.

### Verification

After writing the XML, run:

```bash
python3 ~/.claude/skills/drawio-aws-diagrams/verify.py <file.drawio>
```

The script checks: containment, centering, stencil name validity, fill colour compliance, edge style consistency, label-background presence.

## 6. Reference-matching workflow

When the user provides a reference image:

1. **Extract layout structure first**, not icons:
   - How many horizontal bands / vertical strips?
   - Where is the divider band?
   - Where are external actors (top-left vs bottom)?
   - Are there coloured zone fills?
2. **List the icons in the reference** — one by one, left-to-right, top-to-bottom.
3. **Map to stencils** via STENCILS.md.
4. **Draft grid constants** that produce that layout.
5. **Write XML once.** Then verify.

Do not author incrementally. Incremental authoring produces drift (measured: 4 iterations average without this skill, 1 iteration with).

## 7. Known traps (don't repeat these)

| Trap | Fix |
|---|---|
| `shape=mxgraph.aws4.<name>` on a service icon | Use `shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.<name>` |
| Override `fillColor` to match a brand colour | Use only the category colour in STENCILS.md |
| Drop AZ between VPC and subnet | Insert an AZ container with `grIcon=group_az;dashed=1;verticalAlign=bottom` |
| Use `endArrow=classic` | Use `endArrow=open;endFill=0` |
| Put icon labels inside the icon or to the right | Below the icon via `verticalLabelPosition=bottom` |
| Centre a Bedrock AgentCore region in its own coloured box | Use a grey dashed logical group — there is no official Bedrock container |
| Write coordinates ad-hoc from memory | Declare grid constants first in the top-of-file comment |
