# ethan-skills

My personal agent skills for Claude Code (and other `SKILL.md`-aware agents) —
tools I use every day for AWS / data engineering, deep learning from external
material, and staying aligned with coding agents.

No unifying thesis yet. Five clusters have emerged from daily use:

- **Engineering** — disciplined work in complex technical environments
  (AWS architecture diagrams, testing your grasp of a codebase).
- **Learning** — turn passive external content into active understanding
  (books into interactive sites, YouTube into structured notes).
- **Personal agent** — second-brain skills for a Telegram-first PKM agent:
  ingest raw resources, curate, extract into a graph, synthesize wiki notes,
  recall on demand. Inspired by [Vivian Balakrishnan's Building a 'Second Brain'
  talk](https://www.youtube.com/watch?v=t-4a20_iYhg).
- **Productivity** — stay aligned with your agent before writing code
  (grilling sessions, PRDs, skill authoring). Vendored from
  [`mattpocock/skills`](https://github.com/mattpocock/skills).
- **HTML** — push Claude toward HTML as the working surface (specs, diagrams,
  dashboards, throwaway editors) instead of long-form markdown when HTML is
  the better medium. Vendored from
  [`f-labs-io/agent-html-skills`](https://github.com/f-labs-io/agent-html-skills).

## Install

Install via the [`skills` CLI](https://skills.sh) — works for public and
private repos (the CLI uses your existing git credentials: SSH key,
`GITHUB_TOKEN`, or `gh auth token`):

```bash
npx skills@latest add ethan-rio/skills
```

Pick the skills and agents you want when prompted. Selected skills are
copied into `~/.claude/skills/` (or the equivalent location for other
agents).

## Skills

### Engineering

- **[drawio-aws-diagrams](./skills/engineering/drawio-aws-diagrams/SKILL.md)** — Author professional AWS architecture diagrams as `.drawio` XML on the first attempt.
- **[prove-it](./skills/engineering/prove-it/SKILL.md)** — Test your understanding of the current project through adaptive questioning.

_Vendored from [mattpocock/skills](https://github.com/mattpocock/skills):_

- **[diagnose](./skills/engineering/diagnose/SKILL.md)** — Disciplined diagnosis loop for hard bugs and performance regressions.
- **[improve-codebase-architecture](./skills/engineering/improve-codebase-architecture/SKILL.md)** — Find deepening opportunities in a codebase; consolidate tightly-coupled modules.
- **[tdd](./skills/engineering/tdd/SKILL.md)** — Test-driven development with a red-green-refactor loop.
- **[zoom-out](./skills/engineering/zoom-out/SKILL.md)** — Tell the agent to zoom out and give broader context on an unfamiliar section of code.

### Learning

- **[book-2-site](./skills/learning/book-2-site/SKILL.md)** — Convert a book into an interactive learning website.
- **[youtube-summary](./skills/learning/youtube-summary/SKILL.md)** — Summarise a YouTube video from its transcript into a structured markdown note.

### Personal agent

Hermes-shaped second-brain skills, agent-agnostic. See [`skills/personal_agent/README.md`](./skills/personal_agent/README.md) for the full bucket.

_Foundation:_

- **[obsidian-vault](./skills/personal_agent/obsidian-vault/SKILL.md)** — vault contract (path, layout, frontmatter, linking) every other personal-agent skill assumes.

_Ingest (raw input → Inbox/):_

- **[ingest-quick-note](./skills/personal_agent/ingest-quick-note/SKILL.md)** — capture a short text thought.
- **[ingest-article](./skills/personal_agent/ingest-article/SKILL.md)** — scrape a web article (Firecrawl) into the Inbox.
- **[ingest-youtube](./skills/personal_agent/ingest-youtube/SKILL.md)** — wrap `youtube-summary` and file into the Inbox.
- **[ingest-pdf](./skills/personal_agent/ingest-pdf/SKILL.md)** — extract text from a PDF into the Inbox.
- **[ingest-voice-note](./skills/personal_agent/ingest-voice-note/SKILL.md)** — Whisper-transcribe a voice message.

_Process (Inbox → graph + wiki):_

- **[curate](./skills/personal_agent/curate/SKILL.md)** — review Inbox items and promote to root as `Source -- ...md`.
- **[extract-graph](./skills/personal_agent/extract-graph/SKILL.md)** — extract entity-relation triples (causal/temporal/semantic) into the Honcho graph.
- **[synthesize-wiki](./skills/personal_agent/synthesize-wiki/SKILL.md)** — generate a `Wiki -- <Topic>.md` note from a topic + graph subset.

_Navigate:_

- **[update-index](./skills/personal_agent/update-index/SKILL.md)** — inject `[[wikilinks]]` to new wikis into the right `<Topic> Index.md` MOC notes.
- **[recall](./skills/personal_agent/recall/SKILL.md)** — answer questions from the vault with `[[wikilink]]` citations.
- **[daily-review](./skills/personal_agent/daily-review/SKILL.md)** — daily housekeeping digest (inbox debt, broken links, ripe topics).

### HTML

Vendored from [f-labs-io/agent-html-skills](https://github.com/f-labs-io/agent-html-skills) (MIT). See [`skills/html/README.md`](./skills/html/README.md) for the full bucket and [`skills/html/ATTRIBUTION.md`](./skills/html/ATTRIBUTION.md) for the per-bucket attribution.

_Specs &amp; planning:_

- **[html-spec-planning](./skills/html/html-spec-planning/SKILL.md)** — specs, RFCs, implementation plans, exploration.
- **[html-code-review](./skills/html/html-code-review/SKILL.md)** — PR explainers, refactor risk maps, codebase tours.
- **[html-architecture-diagrams](./skills/html/html-architecture-diagrams/SKILL.md)** — system maps, deployment topologies.

_Exploration &amp; comparison:_

- **[html-brainstorm-grid](./skills/html/html-brainstorm-grid/SKILL.md)** — N-variant comparison grids when exploring options.
- **[html-comparison-matrix](./skills/html/html-comparison-matrix/SKILL.md)** — weighted decision matrices for named candidates.
- **[html-data-explorer](./skills/html/html-data-explorer/SKILL.md)** — filterable tables, faceted search, log viewers.

_Design:_

- **[html-design-prototypes](./skills/html/html-design-prototypes/SKILL.md)** — component design, animation tuning, design systems.
- **[html-design-tokens](./skills/html/html-design-tokens/SKILL.md)** — color/type/spacing token showcases.

_Diagrams &amp; data shapes:_

- **[html-erd-explorer](./skills/html/html-erd-explorer/SKILL.md)** — database schema visualizations.
- **[html-svg-diagrams](./skills/html/html-svg-diagrams/SKILL.md)** — flowcharts, sequence diagrams, state machines.
- **[html-mind-map](./skills/html/html-mind-map/SKILL.md)** — branching concept maps that send the tree back.

_Communication:_

- **[html-research-reports](./skills/html/html-research-reports/SKILL.md)** — multi-source research synthesis, status reports, incidents.
- **[html-slideshow-deck](./skills/html/html-slideshow-deck/SKILL.md)** — keyboard-navigable presentation decks.

_Throwaway editors &amp; tuners:_

- **[html-interactive-playground](./skills/html/html-interactive-playground/SKILL.md)** — sliders/knobs for tuning parameters.
- **[html-throwaway-editor](./skills/html/html-throwaway-editor/SKILL.md)** — one-off editors that send results back to Claude.
- **[html-timeline-roadmap](./skills/html/html-timeline-roadmap/SKILL.md)** — gantt / roadmap / timeline views.

_Infrastructure (the receiver that closes the click → Claude loop):_

- **[html-skills-listen](./skills/html/html-skills-listen/SKILL.md)** — sets up the per-session local receiver and Monitor for interactive artifacts.
- **[html-skills-stop](./skills/html/html-skills-stop/SKILL.md)** — tears down the receiver when work is done.

### Productivity

- **[excalidraw-mcp-drawing](./skills/productivity/excalidraw-mcp-drawing/SKILL.md)** — Draw high-quality diagrams on an Excalidraw canvas via the excalidraw-mcp server and save them to disk correctly.

_Vendored from [mattpocock/skills](https://github.com/mattpocock/skills):_

- **[grill-me](./skills/productivity/grill-me/SKILL.md)** — Get relentlessly interviewed about a plan or design until every branch is resolved.
- **[grill-with-docs](./skills/productivity/grill-with-docs/SKILL.md)** — Grilling session that challenges your plan against the existing domain model and updates docs inline.
- **[to-prd](./skills/productivity/to-prd/SKILL.md)** — Turn the current conversation context into a PRD.
- **[write-a-skill](./skills/productivity/write-a-skill/SKILL.md)** — Create new agent skills with proper structure and progressive disclosure.

## Credits

Several skills in `engineering/` and `productivity/` are vendored from
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT). Each vendored
`SKILL.md` carries an attribution comment at the top.

The entire `html/` bucket is vendored from
[f-labs-io/agent-html-skills](https://github.com/f-labs-io/agent-html-skills) (MIT).
Bucket-level attribution lives in [`skills/html/ATTRIBUTION.md`](./skills/html/ATTRIBUTION.md)
rather than per-file blocks, since the whole bucket has the same upstream.

Modifications, if any, are tracked in this repo's git history. See
[`LICENSE`](./LICENSE) for the full third-party notice.

## License

MIT. See [`LICENSE`](./LICENSE).
