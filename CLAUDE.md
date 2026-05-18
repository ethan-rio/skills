# Repo conventions for `ethan-skills`

Skills are organized into bucket folders under `skills/`:

- `engineering/` — daily code work
- `productivity/` — daily non-code workflow tools
- `learning/` — turn external content into active understanding
- `personal_agent/` — second-brain ingest, synthesis, recall (hermes-shaped, agent-agnostic)
- `personal/` — tied to my own setup, not promoted
- `goose/` — placeholder for skills targeting the [Goose](https://block.github.io/goose/) framework

## Inclusion rules

- Every skill in `engineering/`, `productivity/`, `learning/`, or `personal_agent/` **must**:
  - Appear in the top-level `README.md` under its bucket
  - Appear in `.claude-plugin/plugin.json` `skills` array
  - Appear in its bucket's `README.md` with a one-line description
- Skills in `personal/` **must not** appear in the top-level `README.md` or
  `plugin.json`.
- Each skill name in a README must link to its `SKILL.md`.

## Vendored skills

Some skills in `productivity/` are vendored from
[`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT). They
carry an HTML-comment attribution block at the top of `SKILL.md`:

```markdown
<!--
Vendored from https://github.com/mattpocock/skills (MIT).
Copyright (c) Matt Pocock. Modifications by ethan-rio tracked in this repo's git history.
-->
```

On substantial modification, append `Modified by ethan-rio: <one-line summary>.`
to the same comment block. Never remove the attribution.

## Install path

Distributed via the [`skills` CLI](https://skills.sh):

```bash
npx skills@latest add ethan-rio/skills
```

Works for public and private GitHub repos — the CLI uses existing git
credentials for private access. No Claude Code marketplace manifest
(`.claude-plugin/marketplace.json`) is shipped; the repo is a plugin,
not a marketplace.
