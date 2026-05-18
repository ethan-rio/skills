---
name: curate
description: Review Inbox/ items and promote them to root as Source -- ...md, or merge / discard / retag. The curation gate. Use when the user runs /curate or asks to triage the inbox.
when_to_use: User runs `/curate` (interactive review of Inbox/), OR asks "what's in my inbox / triage my inbox / clean up the inbox", OR daily-review surfaces inbox items needing attention.
argument-hint: [--all | --kind <article|video|...> | <inbox-filename>]
allowed-tools: Read Bash Write Edit AskUserQuestion
---

# curate

Vivian's curation gate. Inbox items don't graduate to the canonical vault automatically — a human (or human-supervised pass) decides what becomes a `Source -- ...md` at root, what gets merged into an existing source, and what gets discarded.

## When to use

- `/curate` slash command — interactive review.
- User asks to "triage the inbox" or "clean up Inbox".
- Bulk mode: `curate --kind article` reviews all article inbox items.
- Targeted mode: `curate "Article -- 2026-05-18 -- the-bitter-lesson.md"` for a single item.

## Inputs / outputs

- **Input:** none, `--all`, `--kind <kind>`, or a specific inbox filename.
- **Output:** for each item, one of:
  - **promote** — moved to `$VAULT/Source -- <Title>.md`, frontmatter `type: source`, `status: curated`.
  - **merge** — content appended to an existing `Source -- ...md`; inbox file removed.
  - **retag** — frontmatter updated; file stays in inbox.
  - **discard** — inbox file removed.

## Vault contract

See [obsidian-vault](../obsidian-vault/SKILL.md).

## Workflow

```bash
set -euo pipefail
VAULT="${OBSIDIAN_VAULT:-/Users/ethanphan/Documents/my-obsidian-v1}"
[ -d "$VAULT/Inbox" ] || { echo "Inbox is empty or missing — nothing to curate."; exit 0; }

# 1. Pick targets
case "${1:-}" in
  ""|--all) TARGETS=$(ls -1 "$VAULT/Inbox/"*.md 2>/dev/null) ;;
  --kind)
    case "$2" in
      article) PREFIX="Article" ;;
      video)   PREFIX="Video" ;;
      pdf)     PREFIX="PDF" ;;
      voice)   PREFIX="Voice" ;;
      quick-note) PREFIX="Note" ;;
      *) echo "ERROR: unknown kind $2" >&2; exit 1 ;;
    esac
    TARGETS=$(ls -1 "$VAULT/Inbox/$PREFIX -- "*.md 2>/dev/null) ;;
  *) TARGETS="$VAULT/Inbox/$1" ;;
esac

[ -n "$TARGETS" ] || { echo "No matching inbox items."; exit 0; }
```

For each target, the agent should:

1. **Read** the inbox note.
2. **Summarise** to the user (one or two lines) — title, source, key claim.
3. **Ask** (via AskUserQuestion) what to do:
   - **Promote** to a new `Source -- <Title>.md` (offer a default title; let user override).
   - **Merge** into an existing source (LLM picks the most plausible candidate via vault scan).
   - **Retag / edit metadata** only.
   - **Discard.**
   - **Skip** (leave as-is, move on).

4. **Apply** the chosen action:

### Promote

```bash
SRC="$VAULT/Inbox/Article -- 2026-05-18 -- the-bitter-lesson.md"
TITLE="The Bitter Lesson"   # from user
DEST="$VAULT/Source -- $TITLE.md"

# Strip the inbox-only frontmatter fields and rewrite as type=source, status=curated.
# Use yq if available; otherwise sed/awk.
python3 - "$SRC" "$DEST" "$TITLE" <<'PY'
import sys, datetime, re
src, dest, title = sys.argv[1:]
with open(src) as f: text = f.read()
# split frontmatter
m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.DOTALL)
fm, body = (m.group(1), m.group(2)) if m else ("", text)
# parse fm naively (line-based; YAML libs may be unavailable on hermes)
fields = {}
for line in fm.splitlines():
    if ":" in line:
        k, v = line.split(":", 1)
        fields[k.strip()] = v.strip()
fields["type"] = "source"
fields["status"] = "curated"
fields["curated_at"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
new_fm = "\n".join(f"{k}: {v}" for k, v in fields.items())
with open(dest, "w") as f:
    f.write(f"---\n{new_fm}\n---\n\n# {title}\n\n{body.lstrip()}")
PY
rm "$SRC"
echo "PROMOTED: $DEST"
```

### Merge

Append to an existing `Source -- ...md`:

```bash
TARGET="$VAULT/Source -- The Bitter Lesson.md"
{
  echo
  echo "---"
  echo
  echo "## Additional capture — $(date -u +%Y-%m-%d)"
  echo
  # Strip the inbox frontmatter; keep only the body
  awk 'BEGIN{fm=0} /^---$/{fm++; next} fm==2{print}' "$SRC"
} >> "$TARGET"
rm "$SRC"
```

### Retag

Edit frontmatter in place via the same Python helper, only mutating `tags:` / `status:` fields.

### Discard

```bash
rm "$SRC"
```

## Confirmation

For each item, surface a one-line outcome:

```
[1/4] Article -- the-bitter-lesson  →  PROMOTED to Source -- The Bitter Lesson.md
[2/4] Note -- groceries-thought    →  DISCARDED
[3/4] Voice -- meeting-thoughts    →  RETAGGED (added: foreign-policy)
[4/4] Article -- vivian-talk       →  MERGED into Source -- Singapore AI Strategy.md
```

## Heuristics for autonomous mode (future)

When extending to a non-interactive cron variant:

- **Auto-discard** quick-notes older than 14 days that have never been edited.
- **Auto-suggest merge** when an inbox item's `source_url` host or title strongly overlaps with an existing `Source -- ...md` (Levenshtein on titles, exact host match on URLs).
- **Never auto-promote** without confirmation — promotion is the curation gate.

## Failure modes

- **Filename collision on promote** — append a `(2)` suffix or ask the user to pick a different title.
- **Merge target ambiguous** — LLM offers top 3 candidates; user picks.
- **Inbox note missing required frontmatter** — fall back to file-level mtime + filename for metadata, but warn the user.
