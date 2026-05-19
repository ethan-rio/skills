---
name: ingest-quick-note
description: Capture a short text thought into the Obsidian Inbox. Smallest end-to-end ingest skill — text in, frontmatter-correct .md out. Use when the user types a freeform thought, runs /note <text>, or sends a Telegram text message that isn't a URL or file.
when_to_use: Plain text message arrives via Telegram or chat, OR user types `/note <text>`, OR user says "save this thought / capture this / quick note - ...". Default fallback when no other ingest skill matches.
argument-hint: <free text>
allowed-tools: Bash Write
---

# ingest-quick-note

Smallest possible ingest. Text → `Inbox/Note -- <ISO-ts>.md`. Validates the vault contract end-to-end.

## When to use

- User sends plain text (no URL, no file) and the harness has no better skill to dispatch.
- User explicitly invokes `/note <text>` or "save this: ...".
- A voice note has already been transcribed by `ingest-voice-note` — that skill handles its own filing; this one is for *typed* captures.

## Inputs / outputs

- **Input:** `$ARGUMENTS` is the raw text body. May contain newlines.
- **Output:** absolute path of the new note, printed on stdout.
- **Vault file:** `$OBSIDIAN_VAULT/Inbox/Note -- YYYY-MM-DDTHH-MM.md` (no slug — quick captures often have no title).

## Vault contract

See [obsidian-vault](../obsidian-vault/SKILL.md). The helper at `obsidian-vault/scripts/new_note.sh` enforces filename, frontmatter, and `## Related` structure.

## Workflow

```bash
NEW_NOTE="$(dirname "$0")/../obsidian-vault/scripts/new_note.sh"
# When invoked from Claude Code, substitute the absolute path:
#   /Users/ethanphan/Projects/skills/skills/personal_agent/obsidian-vault/scripts/new_note.sh

BODY="$ARGUMENTS"

# If the first non-empty line looks like a title (short, no terminal punctuation),
# extract a slug from it; otherwise leave the note untitled.
FIRST_LINE=$(printf '%s\n' "$BODY" | awk 'NF{print; exit}')
SLUG=""
if [ "${#FIRST_LINE}" -le 60 ] && ! echo "$FIRST_LINE" | grep -qE '[.!?]$'; then
  SLUG=$(printf '%s' "$FIRST_LINE" | tr '[:upper:]' '[:lower:]' \
    | sed 's/[^a-z0-9 _-]//g; s/[ _]\+/-/g; s/-\+/-/g; s/^-//; s/-$//' \
    | cut -c1-60)
fi

if [ -n "$SLUG" ]; then
  printf '%s' "$BODY" | "$NEW_NOTE" \
    --type inbox --kind quick-note \
    --title "$FIRST_LINE" --slug "$SLUG" \
    --body-stdin
else
  printf '%s' "$BODY" | "$NEW_NOTE" \
    --type inbox --kind quick-note \
    --body-stdin
fi
```

The script prints the absolute path on stdout. If hermes is the caller, reply to the user with that path or with a short confirmation.

## Telegram dispatch hint (for hermes)

```
/note Singapore won't be at the frontier of model dev — Vivian
```

…dispatches with `$ARGUMENTS = "Singapore won't be at the frontier of model dev — Vivian"`.

A bare text message with no command should also dispatch here as a fallback.

## Failure modes

- **Vault missing** — `new_note.sh` exits 1 with a clear message. Surface verbatim to the user.
- **Empty body** — fail with `ERROR: empty note body, nothing captured` and do not write a file.
- **Filename collision** — `new_note.sh` will fail; very rare for `Note -- HH-MM` since the timestamp has minute resolution. If it happens, append a counter suffix to the slug and retry.

## Confirmation

After successful write, surface to the user:

```
Saved to Inbox: Note -- 2026-05-18T14-22.md
```

Path is enough — the user can open Obsidian and see it.
