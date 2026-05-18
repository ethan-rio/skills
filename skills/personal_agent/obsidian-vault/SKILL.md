---
name: obsidian-vault
description: Vault contract for the personal-agent skill set — encodes path, layout, filename rules, frontmatter, and linking conventions for Obsidian. Every other personal_agent skill cross-links to this one. Ships scripts/new_note.sh as the canonical note-creation helper.
when_to_use: Read this when working with any other personal_agent skill, or when the user asks how the vault is structured. Helper script (scripts/new_note.sh) is invoked by every ingest-* skill.
allowed-tools: Read Bash Write
---

# obsidian-vault

The contract every other `personal_agent` skill assumes. Read this first.

## Vault path

`OBSIDIAN_VAULT` env var, default `/Users/ethanphan/Documents/my-obsidian-v1/`.

If unset and the default does not exist, **fail fast** with:

```
ERROR: OBSIDIAN_VAULT is not set and the default path does not exist.
       Set it: export OBSIDIAN_VAULT=/path/to/your/vault
```

Resolve once at the top of every skill that reads/writes the vault:

```bash
VAULT="${OBSIDIAN_VAULT:-/Users/ethanphan/Documents/my-obsidian-v1}"
[ -d "$VAULT" ] || { echo "ERROR: OBSIDIAN_VAULT not found at $VAULT" >&2; exit 1; }
```

## Layout

```
$VAULT/
├── Inbox/                       # Raw agent dumps. Transitional.
│   ├── Article -- 2026-05-18 -- <slug>.md
│   ├── Video -- 2026-05-18 -- <slug>.md
│   ├── Voice -- 2026-05-18T14-22 -- <slug>.md
│   ├── Note -- 2026-05-18T14-22.md
│   └── PDF -- 2026-05-18 -- <slug>.md
├── Source -- <Title>.md         # Curated source notes
├── Wiki -- <Title>.md           # Synthesized concept notes
└── <Topic> Index.md             # Maps of Content
```

`Inbox/` is **transitional** — it exists because the Honcho graph isn't yet the canonical store. When the graph is wired, raw ingest can write straight to the graph and `Inbox/` becomes deletable. Skills that read `Inbox/` must tolerate it being empty or missing.

## Filename rules

- **Inbox files** carry a type prefix and ISO date:
  - `Article -- 2026-05-18 -- the-bitter-lesson.md`
  - `Video -- 2026-05-18 -- vivian-second-brain.md`
  - `Voice -- 2026-05-18T14-22 -- groceries-thought.md` (HH-MM appended for sub-day uniqueness)
  - `Note -- 2026-05-18T14-22.md` (no slug — quick captures may have no title yet)
  - `PDF -- 2026-05-18 -- attention-is-all-you-need.md`
- **Curated source notes** at root: `Source -- <Title in Title Case>.md`
- **Wiki notes** at root: `Wiki -- <Title in Title Case>.md`
- **Index notes** at root: `<Topic> Index.md` — e.g. `Singapore Foreign Policy Index.md`. Always end in ` Index.md` (with the space).

Slugs in inbox filenames are **kebab-case**, ASCII-only, max 60 chars. Generated from the source title or first line of the body.

## Frontmatter

YAML, required on every note. Minimum:

```yaml
---
type: inbox | source | wiki | index
status: raw | curated | synthesized
captured_at: 2026-05-18T22:39:00Z
source_url: https://...
source_kind: article | video | pdf | voice | quick-note | manual
tags: [foreign-policy, singapore]
graph_id: <honcho-node-id>
---
```

- `type` and `status` are **required**.
- `captured_at` is **required**, ISO 8601 UTC.
- `source_url` and `source_kind` are required for ingest skills (omit for hand-written wiki/index notes).
- `tags` defaults to `[]`.
- `graph_id` is populated by `extract-graph` once the note is mirrored into Honcho.

## Linking

- Every note ends with a `## Related` H2 followed by a list of `[[wikilinks]]`. Empty if none.
- **Index notes** are pure `[[wikilink]]` lists; H2 sub-groupings are allowed but optional.
- Wikilinks reference *display names without the type prefix* — Obsidian resolves by full filename, but link text reads naturally:
  - File: `Wiki -- Tool Assembly.md`
  - Link: `[[Wiki -- Tool Assembly|Tool Assembly]]`

## The `new_note.sh` helper

`scripts/new_note.sh` is the **only** sanctioned way to create notes from a skill. It enforces filename rules, writes valid frontmatter, and prints the absolute path on stdout.

### Usage

```bash
NEW_NOTE="$(dirname "$0")/../obsidian-vault/scripts/new_note.sh"

# From an ingest skill (Inbox/), with all metadata
"$NEW_NOTE" \
  --type inbox \
  --kind article \
  --title "The Bitter Lesson" \
  --slug "the-bitter-lesson" \
  --source-url "https://..." \
  --tags "ai,scaling" \
  --body-file /tmp/article-body.md

# From a wiki synthesis skill (root)
"$NEW_NOTE" \
  --type wiki \
  --title "Tool Assembly" \
  --tags "ai,workflow" \
  --body-file /tmp/wiki-body.md
```

### Contract

- Reads `OBSIDIAN_VAULT` (with the default fallback above).
- Determines target directory from `--type` (`inbox` → `$VAULT/Inbox/`, anything else → `$VAULT/`).
- Builds filename from prefix + ISO date (for inbox) + slug or title.
- If a file with that name already exists, **fails** with non-zero exit unless `--force` is set. Skills should re-slug rather than force.
- Writes frontmatter then `--body-file` content.
- Appends a `## Related` H2 with empty list if not already present in the body.
- Prints the absolute path on stdout. That's the only stdout output.

### Where it lives

`skills/personal_agent/obsidian-vault/scripts/new_note.sh` — every other skill in the set calls it via relative path computed from its own SKILL.md location.

## Conventions cross-reference

| You want to | See skill |
|---|---|
| Add raw ingest to the vault | `ingest-quick-note`, `ingest-article`, `ingest-youtube`, `ingest-pdf`, `ingest-voice-note` |
| Promote inbox → root | `curate` |
| Get a note into the Honcho graph | `extract-graph` |
| Generate a Wiki from the graph | `synthesize-wiki` |
| Update Index/MOC notes | `update-index` |
| Ask a question of the vault | `recall` |
| Daily housekeeping | `daily-review` |
