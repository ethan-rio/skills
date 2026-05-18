---
name: ingest-article
description: Scrape a web article (blog, news, docs page) into the Obsidian Inbox as clean markdown. Uses Firecrawl for JS-rendered pages. Use when the user pastes a non-YouTube URL or runs /clip <url>.
when_to_use: User shares a URL pointing to an article/blog/docs page (anything that isn't a YouTube video, PDF, or pure media file), OR runs `/clip <url>`, OR says "save this article / clip this / read it later".
argument-hint: <url>
allowed-tools: Bash Read Write
---

# ingest-article

URL → cleaned markdown article → `Inbox/Article -- YYYY-MM-DD -- <slug>.md`.

## When to use

- User pastes a URL in a chat message and expects it filed.
- User runs `/clip <url>` from Telegram or CLI.
- User says "save this for later" with a URL.
- **Skip if** URL host is `youtube.com` / `youtu.be` (route to [ingest-youtube](../ingest-youtube/SKILL.md)) or the URL ends in `.pdf` (route to [ingest-pdf](../ingest-pdf/SKILL.md)).

## Inputs / outputs

- **Input:** `$ARGUMENTS = <url>`
- **Output:** absolute path of new note on stdout
- **Vault file:** `$OBSIDIAN_VAULT/Inbox/Article -- YYYY-MM-DD -- <slug>.md`

## Vault contract

See [obsidian-vault](../obsidian-vault/SKILL.md).

## Dependencies

- `firecrawl` CLI **OR** the `firecrawl:firecrawl-scrape` skill, plus a `FIRECRAWL_API_KEY` env var.
- `jq` for parsing scrape output.

Fail fast if missing:

```bash
command -v firecrawl >/dev/null 2>&1 || \
  { echo "ERROR: firecrawl CLI not installed. Install via 'npm i -g firecrawl' and set FIRECRAWL_API_KEY." >&2; exit 1; }
[ -n "${FIRECRAWL_API_KEY:-}" ] || \
  { echo "ERROR: FIRECRAWL_API_KEY not set." >&2; exit 1; }
command -v jq >/dev/null || { echo "ERROR: jq required. brew install jq" >&2; exit 1; }
```

## Workflow

```bash
set -euo pipefail
URL="$ARGUMENTS"
NEW_NOTE="$(dirname "$0")/../obsidian-vault/scripts/new_note.sh"

# 1. Skip-out routing
case "$URL" in
  *youtube.com/*|*youtu.be/*)
    echo "ROUTE: ingest-youtube $URL" >&2; exit 0 ;;
  *.pdf)
    echo "ROUTE: ingest-pdf $URL" >&2; exit 0 ;;
esac

# 2. Scrape via firecrawl
TMPDIR=$(mktemp -d); trap 'rm -rf "$TMPDIR"' EXIT
firecrawl scrape "$URL" --formats markdown -o "$TMPDIR/page.json" --json >/dev/null

TITLE=$(jq -r '.data.metadata.title // .data.metadata.ogTitle // "Untitled"' "$TMPDIR/page.json")
DESC=$(jq -r  '.data.metadata.description // .data.metadata.ogDescription // ""' "$TMPDIR/page.json")
SITE=$(jq -r  '.data.metadata.sourceURL // .data.metadata.url // ""' "$TMPDIR/page.json")
MD=$(jq -r    '.data.markdown' "$TMPDIR/page.json")

[ -n "$MD" ] && [ "$MD" != "null" ] || { echo "ERROR: empty markdown returned from firecrawl" >&2; exit 1; }

# 3. Compose body
BODY_FILE="$TMPDIR/body.md"
{
  echo "# ${TITLE}"
  echo
  [ -n "$DESC" ] && [ "$DESC" != "null" ] && { echo "> $DESC"; echo; }
  echo "**Source:** ${SITE:-$URL}"
  echo
  echo "---"
  echo
  echo "$MD"
} > "$BODY_FILE"

# 4. Slugify
SLUG=$(printf '%s' "$TITLE" | tr '[:upper:]' '[:lower:]' \
  | sed 's/[^a-z0-9 _-]//g; s/[ _]\+/-/g; s/-\+/-/g; s/^-//; s/-$//' \
  | cut -c1-60)
[ -n "$SLUG" ] || SLUG="article"

# 5. File it
"$NEW_NOTE" \
  --type inbox --kind article \
  --title "$TITLE" --slug "$SLUG" \
  --source-url "$URL" \
  --body-file "$BODY_FILE"
```

## Confirmation

After successful write, reply with:

```
Clipped: Article -- 2026-05-18 -- the-bitter-lesson.md  (1842 words)
```

Word count is a useful signal — surface it if the harness can compute it.

## Failure modes

- **Firecrawl 4xx (paywall, login wall)** — try `firecrawl:firecrawl-instruct` for an interactive session, or `mini-browser` as fallback. Do NOT silently produce an empty note.
- **No markdown returned** — fail loudly. Don't write empty inbox stubs.
- **JS-heavy page that returned only a skeleton** — escalate to `firecrawl:firecrawl-instruct`.
