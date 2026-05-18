---
name: ingest-youtube
description: Ingest a YouTube video into the Obsidian Inbox by reusing the youtube-summary skill. Produces a structured summary + full transcript filed as Inbox/Video -- YYYY-MM-DD -- <slug>.md. Use when a YouTube URL is shared.
when_to_use: User pastes a YouTube URL (youtube.com or youtu.be), OR runs `/yt <url>`, OR says "summarise this video / save this talk / take notes on this video".
argument-hint: <youtube-url>
allowed-tools: Bash Read Write Skill
---

# ingest-youtube

Wraps the existing `youtube-summary` skill and files its output into the Obsidian Inbox using the vault contract.

## When to use

- YouTube URL shared (`youtube.com/watch?v=...`, `youtu.be/...`, or YouTube Shorts).
- `/yt <url>` slash command.
- User explicitly asks for a video summary.

## Inputs / outputs

- **Input:** `$ARGUMENTS = <youtube-url>`
- **Output:** absolute path of inbox note + (optional) attached transcript path
- **Vault file:** `$OBSIDIAN_VAULT/Inbox/Video -- YYYY-MM-DD -- <slug>.md`

## Vault contract

See [obsidian-vault](../obsidian-vault/SKILL.md).

## Dependencies

Inherits from `youtube-summary`:

- `yt-dlp` — `brew install yt-dlp` or `uv tool install yt-dlp`.
- `python3` — for the VTT cleaner.

Plus: standard vault helper.

## Workflow

This skill **delegates** transcript fetch + summary to the existing `learning/youtube-summary` skill, then files the output into the Inbox.

### Option A — invoke `youtube-summary` then re-file (recommended)

```bash
set -euo pipefail
URL="$ARGUMENTS"
NEW_NOTE="$(dirname "$0")/../obsidian-vault/scripts/new_note.sh"

# 1. Run the existing youtube-summary skill in a tmp scratch dir.
SCRATCH=$(mktemp -d); trap 'rm -rf "$SCRATCH"' EXIT
( cd "$SCRATCH" && claude --skill youtube-summary "$URL" )
# ^ adapt to whatever invocation form the host agent uses;
# in Claude Code interactive mode, the LLM invokes the Skill tool directly.

# 2. Find the produced summary + transcript.
SUMMARY_DIR=$(find "$SCRATCH/youtube-summary" -mindepth 1 -maxdepth 1 -type d | head -1)
[ -d "$SUMMARY_DIR" ] || { echo "ERROR: youtube-summary produced no output" >&2; exit 1; }
SUMMARY_MD="$SUMMARY_DIR/summary.md"
TRANSCRIPT_MD="$SUMMARY_DIR/transcript.md"
TITLE=$(basename "$SUMMARY_DIR")

# 3. Compose body: summary on top, transcript collapsed below.
BODY_FILE="$SCRATCH/body.md"
{
  cat "$SUMMARY_MD"
  echo
  echo "---"
  echo
  echo "<details><summary>Full transcript</summary>"
  echo
  cat "$TRANSCRIPT_MD"
  echo
  echo "</details>"
} > "$BODY_FILE"

# 4. Slugify title
SLUG=$(printf '%s' "$TITLE" | tr '[:upper:]' '[:lower:]' \
  | sed 's/[^a-z0-9 _-]//g; s/[ _]\+/-/g; s/-\+/-/g; s/^-//; s/-$//' \
  | cut -c1-60)

# 5. File it
"$NEW_NOTE" \
  --type inbox --kind video \
  --title "$TITLE" --slug "$SLUG" \
  --source-url "$URL" \
  --body-file "$BODY_FILE"
```

### Option B — inline the youtube-summary pipeline

If invoking another skill from this one is awkward in your harness, copy the bash pipeline from `learning/youtube-summary/SKILL.md` directly. Keep the cleaner script reference pointing at `../../learning/youtube-summary/scripts/clean_vtt.py` so it stays DRY.

## Confirmation

```
Saved to Inbox: Video -- 2026-05-18 -- vivians-second-brain-talk.md  (22:28, 2733 words)
```

Surface duration + transcript word count — useful signal of whether the video is worth a follow-up listen.

## Failure modes

- **No subtitles** — yt-dlp errors. Surface to user; suggest manual Whisper transcription. Do NOT auto-Whisper a 2-hour video without consent.
- **Non-English captions** — `youtube-summary` handles this; SUB_LANG is captured. Note source language in the inbox note.
- **Age-gated / private video** — surface error verbatim. Don't retry.

## Why a thin wrapper

`youtube-summary` already does the hard part (download, clean VTT, structured summary). This skill exists only to enforce the **vault contract** — filename prefix, frontmatter, Inbox path. Without it, ingestion would land in `$PWD/youtube-summary/...` instead of the vault.
