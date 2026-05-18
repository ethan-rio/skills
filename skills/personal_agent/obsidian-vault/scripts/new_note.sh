#!/usr/bin/env bash
# new_note.sh — canonical note creator for the personal_agent skill set.
# Reads OBSIDIAN_VAULT (or its default) and writes a frontmatter-correct .md
# file under either $VAULT/Inbox/ (for type=inbox) or $VAULT/ (otherwise).
# Prints the absolute path of the created note on stdout. No other output.
#
# See ../SKILL.md for the contract.

set -euo pipefail

VAULT="${OBSIDIAN_VAULT:-/Users/ethanphan/Documents/my-obsidian-v1}"

usage() {
  cat <<EOF >&2
usage: new_note.sh --type <inbox|source|wiki|index>
                   [--kind <article|video|pdf|voice|quick-note|manual>]
                   [--title <Title in Title Case>]
                   [--slug <kebab-case-slug>]
                   [--source-url <url>]
                   [--tags <comma,separated>]
                   [--status <raw|curated|synthesized>]
                   [--body-file <path>]
                   [--body-stdin]
                   [--force]
EOF
  exit 2
}

TYPE=""
KIND=""
TITLE=""
SLUG=""
SOURCE_URL=""
TAGS=""
STATUS=""
BODY_FILE=""
BODY_STDIN=0
FORCE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --type) TYPE="$2"; shift 2 ;;
    --kind) KIND="$2"; shift 2 ;;
    --title) TITLE="$2"; shift 2 ;;
    --slug) SLUG="$2"; shift 2 ;;
    --source-url) SOURCE_URL="$2"; shift 2 ;;
    --tags) TAGS="$2"; shift 2 ;;
    --status) STATUS="$2"; shift 2 ;;
    --body-file) BODY_FILE="$2"; shift 2 ;;
    --body-stdin) BODY_STDIN=1; shift ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage ;;
    *) echo "ERROR: unknown arg $1" >&2; usage ;;
  esac
done

[ -d "$VAULT" ] || { echo "ERROR: OBSIDIAN_VAULT not found at $VAULT" >&2; exit 1; }
[ -n "$TYPE" ] || { echo "ERROR: --type is required" >&2; usage; }

case "$TYPE" in
  inbox|source|wiki|index) ;;
  *) echo "ERROR: --type must be one of inbox|source|wiki|index" >&2; exit 1 ;;
esac

# Default status by type if not explicitly given.
if [ -z "$STATUS" ]; then
  case "$TYPE" in
    inbox) STATUS="raw" ;;
    source) STATUS="curated" ;;
    wiki) STATUS="synthesized" ;;
    index) STATUS="curated" ;;
  esac
fi

# Slugify helper: ASCII-safe kebab-case, max 60 chars.
slugify() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed 's/[^a-z0-9 _-]//g' \
    | sed 's/[ _]\+/-/g' \
    | sed 's/-\+/-/g' \
    | sed 's/^-//;s/-$//' \
    | cut -c1-60
}

# Compute filename and target dir.
NOW_DATE="$(date -u +%Y-%m-%d)"
NOW_TS="$(date -u +%Y-%m-%dT%H-%M)"
NOW_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

case "$TYPE" in
  inbox)
    TARGET_DIR="$VAULT/Inbox"
    mkdir -p "$TARGET_DIR"
    [ -n "$KIND" ] || { echo "ERROR: --kind is required for type=inbox" >&2; exit 1; }
    case "$KIND" in
      article) PREFIX="Article" ;;
      video)   PREFIX="Video" ;;
      pdf)     PREFIX="PDF" ;;
      voice)   PREFIX="Voice" ;;
      quick-note) PREFIX="Note" ;;
      manual)  PREFIX="Manual" ;;
      *) echo "ERROR: unknown --kind $KIND" >&2; exit 1 ;;
    esac
    if [ "$KIND" = "quick-note" ] && [ -z "$SLUG" ] && [ -z "$TITLE" ]; then
      # Quick notes may have no title at all — date+ts is enough.
      FILENAME="${PREFIX} -- ${NOW_TS}.md"
    elif [ "$KIND" = "voice" ]; then
      [ -n "$SLUG" ] || SLUG="$(slugify "${TITLE:-voice}")"
      FILENAME="${PREFIX} -- ${NOW_TS} -- ${SLUG}.md"
    else
      [ -n "$SLUG" ] || SLUG="$(slugify "${TITLE:-untitled}")"
      FILENAME="${PREFIX} -- ${NOW_DATE} -- ${SLUG}.md"
    fi
    ;;
  source|wiki)
    TARGET_DIR="$VAULT"
    [ -n "$TITLE" ] || { echo "ERROR: --title is required for type=$TYPE" >&2; exit 1; }
    PREFIX="$(echo "$TYPE" | sed 's/.*/\u&/')"  # source -> Source, wiki -> Wiki
    FILENAME="${PREFIX} -- ${TITLE}.md"
    ;;
  index)
    TARGET_DIR="$VAULT"
    [ -n "$TITLE" ] || { echo "ERROR: --title is required for type=index" >&2; exit 1; }
    case "$TITLE" in
      *' Index') FILENAME="${TITLE}.md" ;;
      *) FILENAME="${TITLE} Index.md" ;;
    esac
    ;;
esac

OUT="$TARGET_DIR/$FILENAME"

if [ -e "$OUT" ] && [ "$FORCE" -eq 0 ]; then
  echo "ERROR: file exists: $OUT (re-slug or pass --force)" >&2
  exit 1
fi

# Build tags YAML list
if [ -n "$TAGS" ]; then
  TAGS_YAML="[$(echo "$TAGS" | sed 's/,/, /g')]"
else
  TAGS_YAML="[]"
fi

# Body content
if [ "$BODY_STDIN" -eq 1 ]; then
  BODY="$(cat)"
elif [ -n "$BODY_FILE" ]; then
  [ -r "$BODY_FILE" ] || { echo "ERROR: cannot read --body-file $BODY_FILE" >&2; exit 1; }
  BODY="$(cat "$BODY_FILE")"
else
  BODY=""
fi

# Ensure body has a Related section.
case "$BODY" in
  *"## Related"*) ;;
  *)
    if [ -n "$BODY" ]; then
      BODY="${BODY}

## Related
"
    else
      BODY="## Related
"
    fi
    ;;
esac

# Compose frontmatter and write.
{
  echo "---"
  echo "type: $TYPE"
  echo "status: $STATUS"
  echo "captured_at: $NOW_ISO"
  [ -n "$KIND" ]       && echo "source_kind: $KIND"
  [ -n "$SOURCE_URL" ] && echo "source_url: $SOURCE_URL"
  echo "tags: $TAGS_YAML"
  echo "graph_id: null"
  echo "---"
  echo
  echo "$BODY"
} > "$OUT"

# Print absolute path. ONLY stdout.
echo "$OUT"
