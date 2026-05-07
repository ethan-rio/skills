---
name: youtube-summary
description: Summarise a YouTube video from its auto-generated transcript into a structured markdown note (core question, key ideas, one-liner takeaway) alongside the full cleaned transcript. Use when the user gives a YouTube URL and asks to summarise, extract ideas from, or take notes on a video, or runs /youtube-summary.
when_to_use: User provides a YouTube URL and wants a written summary without watching.
argument-hint: <youtube-url>
allowed-tools: Bash Read Write
---

# youtube-summary

Turn a YouTube URL into a structured markdown summary plus the full cleaned transcript. Claude runs the deterministic pipeline (download subs, clean VTT, extract metadata) then writes both files directly using its own reasoning — no external model runner.

## Arguments

`$ARGUMENTS` = one or more `<youtube-url>` values. Multiple URLs → loop.

## Output layout

All output lands under the current working directory:

```
$PWD/youtube-summary/
└── <sanitized-video-title>/
    ├── summary.md       # Structured summary (core question, key ideas, one-liner)
    └── transcript.md    # Full cleaned transcript with metadata header
```

- `youtube-summary/` is created in `$PWD` if missing.
- `<sanitized-video-title>/` is created from the video title if missing. If it already exists from a prior run, overwrite the files inside.
- No date prefix, no user-named paths. Works the same in any repo.

## Dependencies

Check once at start. If missing, stop and tell the user how to install:

```bash
command -v yt-dlp >/dev/null || { echo "Install: uv tool install yt-dlp  (or: pipx install yt-dlp)"; exit 1; }
```

`jq` is NOT required — use `yt-dlp --print` for metadata.

## Workflow

### 1. Fetch, clean, and write transcript — ALL in ONE bash call

Shell variables do not persist across Bash tool invocations. Split this across multiple bash calls and you will hit: empty `$TITLE`, lost `$TMPDIR`, or wrong `$OUT_DIR`. Run the whole script below in a single Bash call. Substitute `<URL>` with the user's URL, and `<CLEAN_VTT_PY>` with the absolute path to `scripts/clean_vtt.py` inside this skill directory.

```bash
set -euo pipefail
URL="<URL>"
CLEAN_VTT_PY="<absolute-path-to-scripts/clean_vtt.py>"

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Download subs + auto-subs. Prefer English (manual or auto-translated), but fall
# back to any available track so non-English videos still work. Claude can read
# most languages — surface the language in the summary if it isn't English.
yt-dlp \
  --write-sub --write-auto-sub --sub-lang "en.*,en,all" \
  --skip-download \
  --output "$TMPDIR/%(title)s.%(ext)s" \
  "$URL" 2>&1 | tail -5

# Prefer processed en.vtt, then any en variant, then the original-language track,
# then anything. Skip raw en-orig.vtt (untranslated auto track in source lang
# tagged as English) when a cleaner en.vtt exists.
VTT=$(find "$TMPDIR" -name '*.en.vtt' ! -name '*.en-orig.vtt' | head -1)
[ -z "$VTT" ] && VTT=$(find "$TMPDIR" -name '*.en*.vtt' | head -1)
[ -z "$VTT" ] && VTT=$(find "$TMPDIR" -name '*-orig.vtt' | head -1)
[ -z "$VTT" ] && VTT=$(find "$TMPDIR" -name '*.vtt' | head -1)

# Extract language tag from the filename (e.g. "Title.vi.vtt" -> "vi").
SUB_LANG=$(basename "$VTT" .vtt | awk -F. '{print $NF}')

if [ -z "$VTT" ]; then
  echo "ERROR: no subtitles found. Video may not have captions." >&2
  exit 1
fi

TITLE=$(yt-dlp --print "%(title)s" --skip-download "$URL" 2>/dev/null)
CHANNEL=$(yt-dlp --print "%(channel,uploader|Unknown)s" --skip-download "$URL" 2>/dev/null)
DURATION=$(yt-dlp --print "%(duration_string)s" --skip-download "$URL" 2>/dev/null)

# Clean the VTT
python3 "$CLEAN_VTT_PY" < "$VTT" > "$TMPDIR/cleaned.txt"

# Sanitise title: ASCII-safe dir name, collapse spaces, trim, truncate.
SAFE_TITLE=$(printf '%s' "$TITLE" | sed 's/[^a-zA-Z0-9 _-]//g' | sed 's/  */ /g' | sed 's/^ *//;s/ *$//' | cut -c1-100)

OUT_DIR="$PWD/youtube-summary/$SAFE_TITLE"
mkdir -p "$OUT_DIR"

# Write transcript.md via bash (avoids Write tool token limits for long videos)
{
  printf '# %s -- Transcript\n\n' "$TITLE"
  printf '**Source:** %s\n' "$URL"
  printf '**Channel:** %s\n' "$CHANNEL"
  printf '**Duration:** %s\n' "$DURATION"
  printf '**Subtitle language:** %s\n\n---\n\n' "$SUB_LANG"
  cat "$TMPDIR/cleaned.txt"
} > "$OUT_DIR/transcript.md"

# Emit values Claude needs for the next step, on stdout in a parseable form
echo "OUT_DIR=$OUT_DIR"
echo "TITLE=$TITLE"
echo "CHANNEL=$CHANNEL"
echo "DURATION=$DURATION"
echo "CLEANED=$TMPDIR/cleaned.txt"
echo "SUB_LANG=$SUB_LANG"
```

Capture `OUT_DIR`, `TITLE`, `CHANNEL`, `DURATION`, `SUB_LANG`, and the cleaned-transcript path from the stdout of that call.

Error cases (fail fast with clear message):
- Output contains `CERTIFICATE_VERIFY_FAILED` → corporate proxy/ZScaler. Suggest `--no-check-certificates` flag or adding it to `~/.config/yt-dlp/config`.
- `ERROR: no subtitles found` → video has no captions. Mention Whisper as a manual escape hatch but do not automate.

### 2. Read the cleaned transcript

Use the Read tool on the `CLEANED` path emitted above. Read the whole thing — do not skim. Large transcripts may need multiple Read calls with offset/limit.

### 3. Write `summary.md`

Use the Write tool to create `$OUT_DIR/summary.md` with this exact structure (ASCII only — `--` for em dashes, straight quotes):

```
# <Video Title>

**Source:** <url>
**Channel:** <channel>
**Duration:** <from yt-dlp, or approximate from transcript length if missing>

## Core question

<Central thesis of the video, 1-2 sentences.>

## Key ideas

1. **<Bold label>.** <2-3 sentences with specific examples, arguments, or data points from the video.>
2. **<Bold label>.** <...>
...

## One-liner takeaway

<Single sentence capturing the most important insight.>
```

Aim for 300-600 words total. Focus on the actual ideas and arguments — not a description of what the video covers.

### 4. Report

Print both paths (`summary.md` and `transcript.md`). Done.

## Batch mode

If `$ARGUMENTS` contains multiple URLs, process them sequentially. Each video gets its own subfolder under `$PWD/youtube-summary/` based on its title.

## Known bounds

- Videos up to ~3 hours (~30k words cleaned transcript) fit comfortably in context.
- Non-English videos: the sub-lang filter prefers English (manual or auto-translated) but falls back to any available track (`all`). `SUB_LANG` on stdout tells you which language was picked. Write the summary in English regardless of source language, and note the source language in the header (e.g. `**Subtitle language:** vi`). If the language is one Claude cannot read confidently, stop and tell the user rather than guessing.
- Re-running the skill on the same URL in the same `$PWD` overwrites the previous `summary.md` and `transcript.md` for that title. That's intentional — it lets you regenerate summaries as your reading priorities change.
