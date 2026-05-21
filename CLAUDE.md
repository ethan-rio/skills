# Repo conventions for `ethan-skills`

Skills are organized into bucket folders under `skills/`:

- `engineering/` — daily code work
- `productivity/` — daily non-code workflow tools
- `learning/` — turn external content into active understanding
- `personal_agent/` — second-brain ingest, synthesis, recall (hermes-shaped, agent-agnostic)
- `html/` — bundled HTML-output skills (vendored from [`f-labs-io/agent-html-skills`](https://github.com/f-labs-io/agent-html-skills), MIT)
- `personal/` — tied to my own setup, not promoted
- `goose/` — placeholder for skills targeting the [Goose](https://block.github.io/goose/) framework

## Inclusion rules

- Every skill in `engineering/`, `productivity/`, `learning/`, `personal_agent/`, or `html/` **must**:
  - Appear in the top-level `README.md` under its bucket
  - Appear in `.claude-plugin/marketplace.json` under the matching bucket plugin
  - Appear in its bucket's `README.md` with a one-line description
- Skills in `personal/` **must not** appear in the top-level `README.md` or
  `marketplace.json`.
- Each skill name in a README must link to its `SKILL.md`.

## Manifest layout

This repo uses `.claude-plugin/marketplace.json` (NOT a single `plugin.json`)
so the [`skills` CLI](https://skills.sh) groups skills by bucket in its
interactive picker:

```
Select skills to install
│  ◻ Engineering
│  │ ◻ diagnose
│  │ ◻ ...
│  ◻ Personal Agent
│  │ ◻ ingest-quick-note
│  │ ◻ ...
```

One plugin per bucket. Plugin names are kebab-case (`personal-agent`); the CLI
title-cases them for display (`Personal Agent`). When adding a new bucket,
add a new plugin entry to `marketplace.json` AND register the bucket in the
list above.

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
