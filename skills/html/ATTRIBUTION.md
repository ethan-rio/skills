# Attribution

The skills in this bucket are vendored from
[`f-labs-io/agent-html-skills`](https://github.com/f-labs-io/agent-html-skills)
(MIT). Copyright © 2026 Fiverr Labs.

## Source

Upstream layout (see upstream repo's `plugins/html-skills/`):

```
plugins/html-skills/
├── assets/submit-handler.js   ← inlined by the 6 interactive skills
└── skills/<skill-name>/SKILL.md
```

Vendored here under `skills/html/` with one folder per skill. The 6
interactive skills carry their own copy of `submit-handler.js` (inlined
into the artifact at generation time per the upstream contract); the
two infrastructure skills (`html-skills-listen`, `html-skills-stop`)
also bring their `server.js` + `scripts/` payloads.

## Skills covered

All 18 skills in `skills/html/` are vendored from upstream:

- 16 content skills — `html-architecture-diagrams`, `html-brainstorm-grid`,
  `html-code-review`, `html-comparison-matrix`, `html-data-explorer`,
  `html-design-prototypes`, `html-design-tokens`, `html-erd-explorer`,
  `html-interactive-playground`, `html-mind-map`, `html-research-reports`,
  `html-slideshow-deck`, `html-spec-planning`, `html-svg-diagrams`,
  `html-throwaway-editor`, `html-timeline-roadmap`
- 2 infrastructure skills — `html-skills-listen`, `html-skills-stop`

## Modifications

None at vendoring time. Substantive modifications going forward should
be tracked in this repo's git history; if a single skill diverges
significantly, append a note here:

```
- html-<name>: <one-line summary of modification> (commit <sha>)
```

## License

MIT — same as upstream. The full license text accompanies the upstream
repository at https://github.com/f-labs-io/agent-html-skills/blob/main/LICENSE.
