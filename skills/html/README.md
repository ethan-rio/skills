# HTML

Bundled HTML-output skills. Vendored from
[`f-labs-io/agent-html-skills`](https://github.com/f-labs-io/agent-html-skills)
(MIT) — see [ATTRIBUTION.md](./ATTRIBUTION.md).

These skills push Claude toward HTML as the working surface (specs,
diagrams, dashboards, throwaway editors) instead of long-form markdown
when HTML is the better medium. Six of them are interactive — the
result of a click is delivered back to Claude as a session
notification (server mode) or via clipboard (fallback).

## Skills

### Specs &amp; planning

- [html-spec-planning](./html-spec-planning/SKILL.md) — specs, RFCs, implementation plans, exploration
- [html-code-review](./html-code-review/SKILL.md) — PR explainers, refactor risk maps, codebase tours
- [html-architecture-diagrams](./html-architecture-diagrams/SKILL.md) — system maps, deployment topologies

### Exploration &amp; comparison

- [html-brainstorm-grid](./html-brainstorm-grid/SKILL.md) — N-variant comparison grids when exploring options *(interactive)*
- [html-comparison-matrix](./html-comparison-matrix/SKILL.md) — weighted decision matrices for named candidates *(interactive)*
- [html-data-explorer](./html-data-explorer/SKILL.md) — filterable tables, faceted search, log viewers

### Design

- [html-design-prototypes](./html-design-prototypes/SKILL.md) — component design, animation tuning, design systems *(interactive)*
- [html-design-tokens](./html-design-tokens/SKILL.md) — color/type/spacing token showcases

### Diagrams &amp; data shapes

- [html-erd-explorer](./html-erd-explorer/SKILL.md) — database schema visualizations
- [html-svg-diagrams](./html-svg-diagrams/SKILL.md) — flowcharts, sequence diagrams, state machines
- [html-mind-map](./html-mind-map/SKILL.md) — branching concept maps that send the tree back *(interactive)*

### Communication

- [html-research-reports](./html-research-reports/SKILL.md) — multi-source research synthesis, status reports, incidents
- [html-slideshow-deck](./html-slideshow-deck/SKILL.md) — keyboard-navigable presentation decks

### Throwaway editors &amp; tuners

- [html-interactive-playground](./html-interactive-playground/SKILL.md) — sliders/knobs for tuning parameters *(interactive)*
- [html-throwaway-editor](./html-throwaway-editor/SKILL.md) — one-off editors that send results back to Claude *(interactive)*
- [html-timeline-roadmap](./html-timeline-roadmap/SKILL.md) — gantt / roadmap / timeline views

### Infrastructure

- [html-skills-listen](./html-skills-listen/SKILL.md) — sets up the per-session local receiver for interactive artifacts
- [html-skills-stop](./html-skills-stop/SKILL.md) — tears down the receiver when work is done

## How the interactive skills work

Each interactive artifact ships a `Submit` button. With
`html-skills-listen` armed, the click POSTs JSON to a per-session
localhost receiver and arrives in Claude as a notification. Without
it, the same button copies JSON to the clipboard for paste-back.
Either way the artifacts work — server mode just removes the paste.

Companion gallery (the original by Thariq Shihipar):
[thariqs.github.io/html-effectiveness](https://thariqs.github.io/html-effectiveness/).
Background reading:
["Using Claude Code: The unreasonable effectiveness of HTML"](https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html).
