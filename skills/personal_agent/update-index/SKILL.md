---
name: update-index
description: After a Wiki note is written or updated, inject a [[wikilink]] to it into the appropriate <Topic> Index.md (Map of Content) notes. Keeps human-navigable indexes in sync with the wiki layer. Use as a post-hook of synthesize-wiki, or manually.
when_to_use: After `synthesize-wiki` produces a new wiki note (auto-hook), OR user runs `/index <wiki-name>` to re-link an orphaned wiki, OR `daily-review` flags wikis missing from any index.
argument-hint: <wiki-note-name>
allowed-tools: Read Edit Bash AskUserQuestion
---

# update-index

Wiki notes are the concept layer; index notes (MOCs) are the navigation layer. When a wiki lands, the relevant indexes should learn about it.

## When to use

- **Auto-hook** of [synthesize-wiki](../synthesize-wiki/SKILL.md). Fire-and-forget after every wiki write.
- User runs `/index <Wiki -- ...>` to retrofit a wiki that's missing from indexes.
- `daily-review` surfaces wikis with no inbound index link.

## Inputs / outputs

- **Input:** `$ARGUMENTS = <wiki note filename>` (e.g. `Wiki -- Tool Assembly.md`).
- **Output (stdout):** list of indexes updated, one per line.
- **Side effect:** appends `[[Wiki -- Tool Assembly|Tool Assembly]]` lines to relevant `<Topic> Index.md` files. Creates new indexes when the wiki's tags suggest one is needed.

## Vault contract

See [obsidian-vault](../obsidian-vault/SKILL.md). Index notes are pure `[[wikilink]]` lists, optionally with H2 sub-groupings.

## How indexes are picked

Two signals:

1. **Tags.** The wiki's frontmatter `tags: [foreign-policy, singapore]` → look for `Foreign Policy Index.md`, `Singapore Index.md`. Create them if they don't exist.
2. **Cross-links.** If the wiki body links to other wikis whose own indexes are known, add the new wiki to those indexes too.

When ambiguous (no tags, no cross-links, no obvious topic), **ask** which index to add it to via AskUserQuestion. Don't silently strand the wiki.

## Workflow

```bash
set -euo pipefail
VAULT="${OBSIDIAN_VAULT:-/Users/ethanphan/Documents/my-obsidian-v1}"
WIKI="$ARGUMENTS"
WIKI_PATH="$VAULT/$WIKI"
[ -r "$WIKI_PATH" ] || { echo "ERROR: $WIKI not found in vault" >&2; exit 1; }

# 1. Read tags from frontmatter
TAGS=$(awk 'BEGIN{fm=0} /^---$/{fm++; next} fm==1 && /^tags:/{
  sub(/^tags:[[:space:]]*\[/,""); sub(/\][[:space:]]*$/,""); print
}' "$WIKI_PATH" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$')

# 2. Convert tags to index filenames
# foreign-policy -> Foreign Policy Index.md
INDEXES=()
while IFS= read -r tag; do
  [ -z "$tag" ] && continue
  TITLE=$(echo "$tag" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++)$i=toupper(substr($i,1,1)) substr($i,2)}1')
  INDEXES+=("$VAULT/$TITLE Index.md")
done <<< "$TAGS"

# 3. Extract title for the wikilink display text
WIKI_TITLE=$(echo "$WIKI" | sed 's/^Wiki -- //; s/\.md$//')

LINE="- [[${WIKI%.md}|${WIKI_TITLE}]]"

# 4. For each index, append the link if not already present.
for IDX in "${INDEXES[@]}"; do
  if [ ! -f "$IDX" ]; then
    # Create new index
    INDEX_TITLE=$(basename "$IDX" .md)
    cat > "$IDX" <<EOF
---
type: index
status: curated
captured_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
tags: []
---

# $INDEX_TITLE

$LINE

EOF
    echo "CREATED: $IDX"
  elif ! grep -qF "[[${WIKI%.md}" "$IDX"; then
    printf '%s\n' "$LINE" >> "$IDX"
    echo "UPDATED: $IDX"
  fi
done
```

## Cross-link inference (extension)

After the tag pass, scan the wiki body for `[[Wiki -- ...]]` links. For each linked wiki, find which indexes already reference it. Offer to add this new wiki to those same indexes.

This implements LYT's MOC philosophy: indexes evolve organically as concepts cluster.

## Confirmation

```
update-index: 2 indexes touched
  CREATED: Tool Assembly Index.md
  UPDATED: Singapore Foreign Policy Index.md
```

## Failure modes

- **No tags + no cross-links** — fall back to AskUserQuestion: "Which index should `Wiki -- X` go under? (existing options listed)". Don't strand the wiki silently.
- **Index file is huge / has subgroupings** — append at the end; let the user manually re-organize subgroups. Better to over-flat than to misplace under a wrong H2.
- **Race condition (two skills updating same index)** — `update-index` is idempotent (`grep -qF` check), so concurrent writes converge to the same final state.
