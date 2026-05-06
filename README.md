# ethan-skills

My personal agent skills for Claude Code (and other `SKILL.md`-aware agents) —
tools I use every day for AWS / data engineering, deep learning from external
material, and staying aligned with coding agents.

No unifying thesis yet. Three clusters have emerged from daily use:

- **Engineering** — disciplined work in complex technical environments
  (AWS architecture diagrams, testing your grasp of a codebase).
- **Learning** — turn passive external content into active understanding
  (books into interactive sites, YouTube into structured notes).
- **Productivity** — stay aligned with your agent before writing code
  (grilling sessions, PRDs, skill authoring). Vendored from
  [`mattpocock/skills`](https://github.com/mattpocock/skills).

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

### Productivity _(vendored from [mattpocock/skills](https://github.com/mattpocock/skills))_

- **[grill-me](./skills/productivity/grill-me/SKILL.md)** — Get relentlessly interviewed about a plan or design until every branch is resolved.
- **[grill-with-docs](./skills/productivity/grill-with-docs/SKILL.md)** — Grilling session that challenges your plan against the existing domain model and updates docs inline.
- **[to-prd](./skills/productivity/to-prd/SKILL.md)** — Turn the current conversation context into a PRD.
- **[write-a-skill](./skills/productivity/write-a-skill/SKILL.md)** — Create new agent skills with proper structure and progressive disclosure.

## Credits

Several skills in `engineering/` and `productivity/` are vendored from
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT). Each vendored
`SKILL.md` carries an attribution comment at the top. Modifications, if any,
are tracked in this repo's git history. See [`LICENSE`](./LICENSE) for the
full third-party notice.

## License

MIT. See [`LICENSE`](./LICENSE).
