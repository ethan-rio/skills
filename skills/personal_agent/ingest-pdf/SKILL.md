---
name: ingest-pdf
description: Extract text from a PDF (paper, book, report) into the Obsidian Inbox. Use when the user attaches a PDF, runs /pdf <path>, or shares a URL ending in .pdf.
when_to_use: User attaches a .pdf file in Telegram, OR runs `/pdf <path-or-url>`, OR pastes a URL ending in `.pdf`, OR says "ingest this paper / read this PDF".
argument-hint: <local-path-or-url>
allowed-tools: Bash Read Write
---

# ingest-pdf

PDF (local file or URL) → text-extracted markdown → `Inbox/PDF -- YYYY-MM-DD -- <slug>.md`.

## When to use

- PDF attached in chat / available at a local path.
- URL ends in `.pdf`.
- `/pdf <path-or-url>` slash command.
- User says "ingest this paper".

## Inputs / outputs

- **Input:** `$ARGUMENTS` is either an absolute local path or a URL.
- **Output:** absolute path of inbox note on stdout.
- **Vault file:** `$OBSIDIAN_VAULT/Inbox/PDF -- YYYY-MM-DD -- <slug>.md`

## Vault contract

See [obsidian-vault](../obsidian-vault/SKILL.md).

## Dependencies

One of:

- **`pdftotext`** (poppler-utils) — `brew install poppler`. Lightweight, fast, decent for text-heavy PDFs. **Recommended default.**
- **`pypdf`** (Python) — `pip install pypdf`. Falls back when pdftotext fails.

Plus: `curl` (for URL inputs).

## Workflow

```bash
set -euo pipefail
INPUT="$ARGUMENTS"
NEW_NOTE="$(dirname "$0")/../obsidian-vault/scripts/new_note.sh"
TMPDIR=$(mktemp -d); trap 'rm -rf "$TMPDIR"' EXIT

# 1. Resolve to a local path
case "$INPUT" in
  http*://*)
    PDF="$TMPDIR/source.pdf"
    curl -sSL --max-filesize 50M -o "$PDF" "$INPUT"
    SOURCE_URL="$INPUT"
    ;;
  *)
    [ -r "$INPUT" ] || { echo "ERROR: cannot read $INPUT" >&2; exit 1; }
    PDF="$INPUT"
    SOURCE_URL=""
    ;;
esac

# 2. Extract text
if command -v pdftotext >/dev/null; then
  pdftotext -layout "$PDF" "$TMPDIR/text.txt"
elif python3 -c 'import pypdf' 2>/dev/null; then
  python3 -c "
import sys, pypdf
r = pypdf.PdfReader(sys.argv[1])
print('\n\n'.join(p.extract_text() or '' for p in r.pages))
" "$PDF" > "$TMPDIR/text.txt"
else
  echo "ERROR: install pdftotext (brew install poppler) or pypdf (pip install pypdf)" >&2
  exit 1
fi

# 3. Get a title
# Try PDF metadata first; fall back to first non-empty line.
if command -v pdfinfo >/dev/null; then
  TITLE=$(pdfinfo "$PDF" 2>/dev/null | awk -F': +' '/^Title/{print $2; exit}')
fi
[ -n "${TITLE:-}" ] || \
  TITLE=$(awk 'NF{print; exit}' "$TMPDIR/text.txt" | cut -c1-80)
[ -n "$TITLE" ] || TITLE="Untitled PDF"

# 4. Compose body. Truncate to a sane size for inbox; the LLM can re-read full text from PDF if needed.
WORDS=$(wc -w < "$TMPDIR/text.txt")
BODY_FILE="$TMPDIR/body.md"
{
  echo "# $TITLE"
  echo
  echo "**Source:** ${SOURCE_URL:-$INPUT}"
  echo "**Word count:** $WORDS"
  echo
  echo "---"
  echo
  # First 5000 words inline. If you need the full text, re-run pdftotext.
  awk 'NF' "$TMPDIR/text.txt" | head -c 40000
  echo
  echo
  echo "(truncated; full text at \`${SOURCE_URL:-$INPUT}\`)"
} > "$BODY_FILE"

# 5. Slugify
SLUG=$(printf '%s' "$TITLE" | tr '[:upper:]' '[:lower:]' \
  | sed 's/[^a-z0-9 _-]//g; s/[ _]\+/-/g; s/-\+/-/g; s/^-//; s/-$//' \
  | cut -c1-60)
[ -n "$SLUG" ] || SLUG="pdf"

# 6. File it
ARGS=( --type inbox --kind pdf --title "$TITLE" --slug "$SLUG" --body-file "$BODY_FILE" )
[ -n "$SOURCE_URL" ] && ARGS+=( --source-url "$SOURCE_URL" )
"$NEW_NOTE" "${ARGS[@]}"
```

## Confirmation

```
Saved to Inbox: PDF -- 2026-05-18 -- attention-is-all-you-need.md  (8420 words, 11 pages)
```

## Failure modes

- **Encrypted / password-protected PDF** — surface error; don't auto-prompt for password from a chat channel.
- **Image-only / scanned PDF** — `pdftotext` returns ~0 words. Surface that and suggest OCR (`ocrmypdf`) as a manual escape.
- **Huge PDF (>50MB)** — `curl --max-filesize` aborts; tell the user to download manually and pass a local path.
- **Garbled text** (multi-column papers) — `pdftotext -layout` helps but isn't perfect. Note that downstream skills (`extract-graph`, `synthesize-wiki`) should be tolerant.
