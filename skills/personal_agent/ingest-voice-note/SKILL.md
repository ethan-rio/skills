---
name: ingest-voice-note
description: Transcribe a voice message (Telegram OGG/Opus, m4a, mp3, wav) with Whisper and file the transcript into the Obsidian Inbox. Use when the user sends a voice message.
when_to_use: User sends a voice/audio message via Telegram, OR runs `/voice <audio-path>`, OR a transcription has been requested for an existing audio file.
argument-hint: <audio-file-path>
allowed-tools: Bash Read Write
---

# ingest-voice-note

Audio file → Whisper transcription → `Inbox/Voice -- YYYY-MM-DDTHH-MM -- <slug>.md`.

## When to use

- Telegram voice message arrives — hermes downloads the OGG/Opus file and dispatches here with the local path.
- User runs `/voice <path>`.
- Existing audio file needs transcription.

## Inputs / outputs

- **Input:** `$ARGUMENTS = <absolute path to audio file>`. Supported: `.ogg`, `.opus`, `.m4a`, `.mp3`, `.wav`, `.flac`.
- **Output:** absolute path of inbox note on stdout.
- **Vault file:** `$OBSIDIAN_VAULT/Inbox/Voice -- YYYY-MM-DDTHH-MM -- <slug>.md`

## Vault contract

See [obsidian-vault](../obsidian-vault/SKILL.md).

## Dependencies — pick one

### Local Whisper (recommended for privacy)

- **`whisper.cpp`** — `brew install whisper-cpp`. Fast on Apple Silicon. Models live at `~/.cache/whisper.cpp/`.
- **OR `openai-whisper` (Python)** — `pip install -U openai-whisper`. Heavier; uses PyTorch.

### Cloud Whisper (recommended for transient quick-notes; faster)

- **OpenAI API** — `OPENAI_API_KEY` set; `pip install openai` or use `curl` directly.

Pick **one** strategy and bake it into your hermes config. Voice notes are often sensitive; **prefer local** unless you've explicitly opted into cloud.

Plus: `ffmpeg` for format conversion (`brew install ffmpeg`).

## Workflow (whisper.cpp variant)

```bash
set -euo pipefail
AUDIO="$ARGUMENTS"
[ -r "$AUDIO" ] || { echo "ERROR: cannot read $AUDIO" >&2; exit 1; }

NEW_NOTE="$(dirname "$0")/../obsidian-vault/scripts/new_note.sh"
TMPDIR=$(mktemp -d); trap 'rm -rf "$TMPDIR"' EXIT

# 1. Convert to 16kHz mono WAV — what whisper.cpp expects.
WAV="$TMPDIR/audio.wav"
ffmpeg -loglevel error -y -i "$AUDIO" -ar 16000 -ac 1 -c:a pcm_s16le "$WAV"

# 2. Transcribe.
MODEL="${WHISPER_MODEL:-$HOME/.cache/whisper.cpp/ggml-base.en.bin}"
[ -r "$MODEL" ] || { echo "ERROR: whisper model not found at $MODEL. Run 'bash $(brew --prefix)/share/whisper-cpp/models/download-ggml-model.sh base.en'" >&2; exit 1; }

whisper-cli -m "$MODEL" -f "$WAV" -otxt -of "$TMPDIR/transcript" >/dev/null
TRANSCRIPT="$TMPDIR/transcript.txt"
[ -s "$TRANSCRIPT" ] || { echo "ERROR: empty transcript" >&2; exit 1; }

# 3. Build a title slug from the first ~60 chars of the transcript.
FIRST_LINE=$(awk 'NF{print; exit}' "$TRANSCRIPT")
SLUG=$(printf '%s' "$FIRST_LINE" | tr '[:upper:]' '[:lower:]' \
  | sed 's/[^a-z0-9 _-]//g; s/[ _]\+/-/g; s/-\+/-/g; s/^-//; s/-$//' \
  | cut -c1-60)
[ -n "$SLUG" ] || SLUG="voice"

DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO" 2>/dev/null | awk '{printf "%d:%02d", $1/60, int($1)%60}')

# 4. Compose body
BODY_FILE="$TMPDIR/body.md"
{
  echo "# Voice note — ${FIRST_LINE:0:80}"
  echo
  echo "**Duration:** ${DURATION:-unknown}"
  echo "**Source file:** $AUDIO"
  echo
  echo "---"
  echo
  cat "$TRANSCRIPT"
} > "$BODY_FILE"

# 5. File it
"$NEW_NOTE" \
  --type inbox --kind voice \
  --title "${FIRST_LINE:0:80}" --slug "$SLUG" \
  --body-file "$BODY_FILE"
```

## Workflow (OpenAI cloud variant)

```bash
RESPONSE=$(curl -sS https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F model=whisper-1 \
  -F response_format=text \
  -F file="@$AUDIO")
echo "$RESPONSE" > "$TMPDIR/transcript.txt"
# … same composition steps
```

## Confirmation

```
Saved to Inbox: Voice -- 2026-05-18T14-22 -- meeting-thoughts-on-singapore.md  (1:42)
```

## Failure modes

- **Unsupported codec** — `ffmpeg` will tell you. Surface that.
- **Empty transcript** — likely silence or noise; do NOT write an empty inbox note.
- **Cloud API key missing** — surface clearly. Don't fall back to local without explicit opt-in (different privacy posture).
- **Very long audio (>30 min)** — chunk to avoid Whisper memory blowups; whisper.cpp handles long files but slow. Surface duration to the user before starting if practical.

## Privacy note

Voice notes are often the most personal input. The default for hermes should be **local Whisper**. If using cloud Whisper, consider redacting voice notes before storing them long-term, or marking the inbox note `tags: [private]` so downstream skills can filter.
