---
name: daily-review
description: Daily housekeeping pass over the vault — surface inbox items needing curation, broken wikilinks, orphan wikis, suggested merges, and graph-density topics ripe for a wiki. Designed to run on cron and post a digest to Telegram.
when_to_use: Cron-fired daily (suggested 7am local), OR user runs `/review` interactively, OR after a long ingest burst the user wants a "what's new" digest.
argument-hint: [--digest-only]
allowed-tools: Read Bash Write
---

# daily-review

The compounding-interest skill. Without something running daily, an agent-driven vault accumulates entropy faster than a human one.

## What it surfaces

1. **Inbox debt** — items >7 days old that still have `status: raw`. Promote, merge, or discard.
2. **Broken wikilinks** — `[[Wiki -- X]]` references where `Wiki -- X.md` doesn't exist. Either create the wiki or fix the link.
3. **Orphan wikis** — wikis with no inbound links from any index. Pipe through [update-index](../update-index/SKILL.md).
4. **Untagged wikis** — wikis with empty `tags: []`. Suggest tags from body content.
5. **Topics ripe for a wiki** — clusters of source notes (≥3) sharing tags but with no synthesizing wiki. Offer to fire [synthesize-wiki](../synthesize-wiki/SKILL.md).
6. **Stale wikis** — wikis older than 30 days whose source notes have grown. Suggest re-synthesis.

## When to use

- **Cron** — once a day. Hermes has a `cron/` directory; wire this there.
- **`/review`** — interactive, on demand.
- **`--digest-only`** — produces only the Telegram digest, doesn't perform any actions.

## Inputs / outputs

- **Input:** none, or `--digest-only`.
- **Output:** stdout = digest text suitable for Telegram (≤4096 chars, markdown-light).
- **Side effects:** none in `--digest-only`. Otherwise: queues actions for the user to confirm; does NOT auto-curate or auto-synthesize.

## Vault contract

See [obsidian-vault](../obsidian-vault/SKILL.md).

## Workflow

```bash
set -euo pipefail
VAULT="${OBSIDIAN_VAULT:-/Users/ethanphan/Documents/my-obsidian-v1}"
DIGEST_ONLY=0
[ "${1:-}" = "--digest-only" ] && DIGEST_ONLY=1

NOW=$(date -u +%s)
WEEK_AGO=$((NOW - 7*86400))
MONTH_AGO=$((NOW - 30*86400))

# --- 1. Inbox debt ---
INBOX_OLD=()
if [ -d "$VAULT/Inbox" ]; then
  while IFS= read -r f; do
    MTIME=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f")
    [ "$MTIME" -lt "$WEEK_AGO" ] && INBOX_OLD+=("$f")
  done < <(find "$VAULT/Inbox" -name '*.md' -type f)
fi

# --- 2. Broken wikilinks ---
BROKEN=()
while IFS= read -r link; do
  TARGET=$(echo "$link" | sed 's/^.*\[\[//; s/[|].*//; s/]].*$//')
  [ -f "$VAULT/$TARGET.md" ] || BROKEN+=("$link")
done < <(grep -rho --include='*.md' -E '\[\[[^]]+\]\]' "$VAULT" | sort -u)

# --- 3. Orphan wikis ---
ORPHANS=()
while IFS= read -r wiki; do
  WIKI_BASE=$(basename "$wiki" .md)
  if ! grep -rqF --include='*Index.md' "[[${WIKI_BASE}" "$VAULT"; then
    ORPHANS+=("$wiki")
  fi
done < <(find "$VAULT" -maxdepth 1 -name 'Wiki -- *.md')

# --- 4. Untagged wikis ---
UNTAGGED=()
while IFS= read -r wiki; do
  TAGS=$(awk 'BEGIN{fm=0} /^---$/{fm++; next} fm==1 && /^tags:/{print}' "$wiki" | sed 's/.*\[//; s/\].*//')
  TAGS_TRIMMED=$(echo "$TAGS" | tr -d '[:space:]')
  [ -z "$TAGS_TRIMMED" ] && UNTAGGED+=("$wiki")
done < <(find "$VAULT" -maxdepth 1 -name 'Wiki -- *.md')

# --- 5. Wiki-ripe topic clusters --- (LLM does the actual clustering; bash just lists tags)
CLUSTERS=$(grep -rh --include='Source -- *.md' --include='Inbox/*.md' '^tags:' "$VAULT" 2>/dev/null \
  | sed 's/.*\[//; s/\].*//' | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' \
  | grep -v '^$' | sort | uniq -c | awk '$1 >= 3' | sort -rn)

# --- Compose digest ---
{
  echo "*Daily review — $(date +%Y-%m-%d)*"
  echo
  echo "*Inbox debt* (>7 days, status=raw): ${#INBOX_OLD[@]}"
  for f in "${INBOX_OLD[@]:0:5}"; do echo "  - \`$(basename "$f")\`"; done
  [ "${#INBOX_OLD[@]}" -gt 5 ] && echo "  - …and $((${#INBOX_OLD[@]} - 5)) more"
  echo
  echo "*Broken wikilinks*: ${#BROKEN[@]}"
  for l in "${BROKEN[@]:0:5}"; do echo "  - $l"; done
  echo
  echo "*Orphan wikis* (not in any index): ${#ORPHANS[@]}"
  for f in "${ORPHANS[@]:0:5}"; do echo "  - \`$(basename "$f")\`"; done
  echo
  echo "*Untagged wikis*: ${#UNTAGGED[@]}"
  for f in "${UNTAGGED[@]:0:5}"; do echo "  - \`$(basename "$f")\`"; done
  echo
  echo "*Topic clusters ripe for a wiki* (≥3 sources):"
  echo "$CLUSTERS" | head -5 | awk '{printf "  - %s (%d notes)\n", $2, $1}'
} > /tmp/hermes-digest.md

cat /tmp/hermes-digest.md

[ "$DIGEST_ONLY" -eq 1 ] && exit 0

# --- Queue actions for user confirmation (non-digest mode) ---
# In hermes, post the digest to Telegram and offer "/curate" / "/wiki <topic>"
# follow-up commands. Do NOT auto-act.
```

## Cron wiring (hermes)

In `~/.hermes/cron/`, add an entry firing daily at 07:00 local:

```yaml
- name: daily-review
  cron: "0 7 * * *"
  command: claude --skill daily-review --digest-only
  post_to: telegram://Ethan
```

(Adapt to whatever syntax the hermes cron config uses.)

## Confirmation

The digest IS the output. Telegram-friendly: ≤4096 chars, markdown-light formatting, hero numbers up top, top-5 of each category as a sample.

## Failure modes

- **Empty vault** — say so cheerfully: "Vault is empty. Capture some material with `/clip` or `/yt`."
- **Vault missing** — `obsidian-vault` contract handles it; surface verbatim.
- **Digest >4096 chars** — truncate to top-5 per section. The user can drill in via `/curate` or `/review --section inbox`.

## Why daily

Knowledge systems compound only when curated. Without a daily nudge, raw inbox notes pile up, links rot, and the vault stops being a second brain — it becomes a junk drawer.
