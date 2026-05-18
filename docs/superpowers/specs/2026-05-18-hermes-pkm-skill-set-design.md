# Hermes PKM Skill Set — Design

**Date:** 2026-05-18
**Author:** Ethan (with Claude assistance)
**Status:** Approved for scaffolding

## Background

Hermes is Ethan's Telegram-first personal agent at `~/.hermes/` — a multi-channel harness with Honcho memory, STT/TTS, and the GSD plugin already installed. It is sophisticated in infrastructure but barebone in *PKM skill content*: it does not yet know how to ingest raw resources, extract structure, or synthesize wiki-style understanding into Obsidian.

This spec defines a **set of 12 portable skills** distributed via [`ethan-rio/skills`](https://github.com/ethan-rio/skills) so that `npx skills@latest add ethan-rio/skills` makes hermes (and any other agent — Claude Code, Goose, etc.) PKM-capable.

## Influences

- **Vivian Balakrishnan, "Building a 'Second Brain'"** ([video](https://www.youtube.com/watch?v=t-4a20_iYhg)) — the architecture: Mnemon graph as memory store, Obsidian as the read/UX surface, Karpathy-style LLM-supervised wiki generation. *"I have curated the stuff I put in"* — there is an explicit curation gate.
- **Andy Matuschak, [Evergreen Notes](https://notes.andymatuschak.org/Evergreen_notes)** — atomic, concept-oriented, densely linked. Notes flow inbox → literature → permanent. Avoid hierarchical taxonomies.
- **Tiago Forte, [PARA](https://fortelabs.com/blog/para/)** — actionability over subject. (Adopted only as a *frame*; PARA itself doesn't fit a study/synthesis vault.)
- **Matt Pocock's [`obsidian-vault` skill](https://github.com/mattpocock/skills/blob/main/skills/personal/obsidian-vault/SKILL.md)** — flat root + Title Case + index notes. Used as the starting template for the foundation skill.

## Goals

1. **Cover the full PKM loop** — ingest → curate → extract → synthesize → recall.
2. **Be agent-agnostic** — every skill is a standard `SKILL.md`. Hermes loads them; Claude Code loads them; Goose loads them.
3. **Hermes-aware in vocabulary** — "When to use" sections name Telegram triggers, voice triggers, etc. so hermes can route naturally.
4. **Vivian-faithful end state** — Obsidian is the surface; Honcho graph is the store. Skills assume that direction even if today's reality is transitional.

## Non-goals

- We do **not** decide the Honcho graph schema in this spec. Skills that touch the graph (`extract-graph`, `synthesize-wiki`, `recall`) declare a *contract* — what their helper script should do — and leave the script TODO until the schema is locked.
- We do **not** implement Telegram dispatch (that lives in the hermes harness, not a skill).
- We do **not** ship Whisper / firecrawl / yt-dlp — they are dependencies, declared and checked at runtime, installed once by the user.

## The vault contract

All skills in the set assume the following layout. This is the **foundation** — every other skill cross-links to `obsidian-vault`.

### Path

`OBSIDIAN_VAULT` env var, default `/Users/ethanphan/Documents/my-obsidian-v1/`. Skills fail-fast with a clear message if the path is missing.

### Layout (Vivian-faithful + transitional Inbox)

```
$OBSIDIAN_VAULT/
├── Inbox/                       # Raw agent dumps. Transitional — deletable once Honcho is canonical.
│   ├── Article -- 2026-05-18 -- <slug>.md
│   ├── Video -- 2026-05-18 -- <slug>.md
│   ├── Voice -- 2026-05-18T14-22 -- <slug>.md
│   ├── Note -- 2026-05-18T14-22.md
│   └── PDF -- 2026-05-18 -- <slug>.md
├── Source -- <Title>.md         # Curated source notes (promoted from Inbox/)
├── Wiki -- <Title>.md           # Synthesized concept notes (Karpathy pattern)
└── <Topic> Index.md             # Maps of Content / index notes
```

### Filename rules

- **Title Case** for human-authored titles; kebab-case slugs for machine-generated.
- **Filename prefixes** (`Article -- `, `Video -- `, `Source -- `, `Wiki -- `) are the *type* signal — duplicated in frontmatter for query reliability but visible in file lists too.
- **Inbox filenames carry an ISO date** (`-- YYYY-MM-DD`) for chronological sort.
- **Index notes** end in ` Index.md` (e.g., `Singapore Foreign Policy Index.md`). Pure list of `[[wikilinks]]`.

### Frontmatter (YAML)

```yaml
---
type: inbox | source | wiki | index
status: raw | curated | synthesized
captured_at: 2026-05-18T22:39:00Z
source_url: https://...           # if applicable
source_kind: article | video | pdf | voice | quick-note | manual
tags: [foreign-policy, singapore]
graph_id: <honcho-node-id>        # populated by extract-graph
---
```

### Linking

- Every note ends with a `## Related` section listing `[[wikilinks]]`.
- Index notes are pure `[[wikilink]]` lists, optionally with H2 sub-groupings.

## The skill set (12)

### Foundation (1)

| # | Skill | Purpose |
|---|---|---|
| 1 | `obsidian-vault` | Encodes the vault contract above. Cross-linked by every other skill. Ships `scripts/new_note.sh` (creates a frontmatter-correct note) used by all ingest skills. |

### Ingest — raw input → `Inbox/` (5)

| # | Skill | Trigger | Output |
|---|---|---|---|
| 2 | `ingest-quick-note` | Plain text msg / `/note <text>` | `Inbox/Note -- ...md` |
| 3 | `ingest-article` | URL pasted / `/clip <url>` | `Inbox/Article -- ...md` |
| 4 | `ingest-youtube` | YouTube URL / `/yt <url>` — wraps `youtube-summary` | `Inbox/Video -- ...md` |
| 5 | `ingest-pdf` | PDF attached / `/pdf <path>` | `Inbox/PDF -- ...md` |
| 6 | `ingest-voice-note` | Voice msg from Telegram | `Inbox/Voice -- ...md` |

### Process — Inbox → graph + wiki (3)

| # | Skill | Purpose |
|---|---|---|
| 7 | `curate` | Review `Inbox/`, promote to root as `Source -- ...md` (or merge / discard / retag). Vivian's curation gate. |
| 8 | `extract-graph` | Source/Wiki note → entity-relation triples (causal/temporal/semantic) → Honcho graph. |
| 9 | `synthesize-wiki` | Topic + graph subset → `Wiki -- ...md`. Karpathy's LLM-supervised wiki pattern. |

### Navigate (3)

| # | Skill | Purpose |
|---|---|---|
| 10 | `update-index` | New Wiki → wikilinks injected into the right `... Index.md` MOCs. |
| 11 | `recall` | Question → graph + semantic search → answer with citations. |
| 12 | `daily-review` | Cron-style: surface inbox, broken links, orphan notes, suggested merges. |

## SKILL.md shape

Every skill in the set follows this body structure:

1. **Vendoring/attribution** (only if adapted from mattpocock/skills) — HTML comment per repo convention.
2. **`When to use`** — trigger phrases + invocation forms (e.g. `/yt <url>`, voice msg, file attached). Hermes uses this to route.
3. **`Inputs / outputs`** — explicit. What it reads, what it writes, what env it expects.
4. **`Vault contract`** — one-line link to `obsidian-vault` skill rather than re-stating.
5. **`Workflow`** — bash recipes / pseudo-steps, copy-paste-runnable.
6. **`Failure modes`** — what to do when yt-dlp/FIRECRAWL_API_KEY/`OBSIDIAN_VAULT`/Honcho is missing.

## Bucket and registration

- **Bucket:** `skills/personal_agent/` — sibling to `engineering/`, `learning/`, `productivity/`, `personal/`.
- **Registration policy:** follows the *public* convention — every skill registered in `plugin.json`, top-level `README.md`, and a new `skills/personal_agent/README.md`.
- **CLAUDE.md update:** add `personal_agent/` to the bucket list:
  > `personal_agent/` — second-brain ingest, synthesis, recall (hermes-shaped, but agent-agnostic).
- **No vendoring**: all 12 skills are net-new in this repo. (`obsidian-vault` is *inspired by* mattpocock's but rewritten end-to-end for the new vault contract — no attribution comment required.)

## Depth this session

- **Scaffold all 12 SKILL.md files** with thorough, runnable content.
- **Ship `obsidian-vault` complete**, including `scripts/new_note.sh`.
- **Ship the simple ingest skills** (`ingest-quick-note`, `ingest-youtube`, `ingest-article`) with full bash workflows.
- **Ship Honcho-touching skills** (`extract-graph`, `synthesize-wiki`, `recall`) with helper-script *contracts* but TODO implementations — unblocked by graph schema decision.
- **Update plugin.json + READMEs + CLAUDE.md.**

Helper scripts requiring undecided schema decisions are deferred to follow-up sessions.

## Order of follow-up implementation

When ready to flesh out the TODO scripts:

1. `ingest-quick-note` — smallest end-to-end loop; validates the vault contract + `new_note.sh`.
2. `ingest-youtube` — proves the wrap-existing-skill pattern.
3. `ingest-article` — adds firecrawl dependency, proves API-key handling.
4. `ingest-voice-note` — adds Whisper, proves binary-input handling.
5. `ingest-pdf` — adds pdftotext / pypdf.
6. `curate` — first interactive skill.
7. Decide Honcho schema (separate spec).
8. `extract-graph` → `synthesize-wiki` → `recall`.
9. `update-index` → `daily-review`.

## Open questions (deferred)

- **Honcho graph schema** — node types (Person/Place/Concept/Event/Document?), edge types beyond Vivian's three (causal/temporal/semantic)? Needs its own spec.
- **Telegram routing** — slash commands first, NL routing later; lives in hermes harness, not in skills.
- **Whisper local vs cloud** — affects `ingest-voice-note` dependency footprint.
- **Curation: human-in-the-loop vs autonomous** — `curate` defaults to interactive; cron variant possible later.
