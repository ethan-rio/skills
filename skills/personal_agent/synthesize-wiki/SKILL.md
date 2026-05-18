---
name: synthesize-wiki
description: Generate a Wiki -- <Topic>.md note from a topic and the relevant graph subset, following Andrej Karpathy's LLM-supervised wiki generation pattern. Output is concept-oriented, atomic, densely linked. Use when the user asks for a wiki on a topic or daily-review identifies a topic with enough graph density to warrant one.
when_to_use: User runs `/wiki <topic>`, OR asks "write me a wiki on X / synthesize what we know about X / draft a concept note on X", OR `daily-review` flags a topic with sufficient graph density.
argument-hint: <topic>
allowed-tools: Read Bash Write Edit
---

# synthesize-wiki

Topic + relevant graph subset → atomic, concept-oriented wiki note at `$VAULT/Wiki -- <Title>.md`.

## Status

**Contract is fixed; full implementation is gated on the Honcho schema decision.** Until then, this skill operates against the JSON-on-disk prototype graph (see [extract-graph](../extract-graph/SKILL.md)).

## When to use

- `/wiki <topic>` — synthesize a wiki on demand.
- User says "write me a wiki on X" or "what do we know about X — pull it together".
- Auto-trigger from `daily-review` when a topic has ≥ N source notes / ≥ M graph edges (threshold tunable).

## Inputs / outputs

- **Input:** `$ARGUMENTS = <topic phrase>`.
- **Output:** absolute path of new wiki note on stdout.
- **Vault file:** `$VAULT/Wiki -- <Title>.md` (Title in Title Case derived from topic).
- **Graph side effect:** the new wiki note becomes a graph node itself — pipe into [extract-graph](../extract-graph/SKILL.md) after writing.

## Vault contract

See [obsidian-vault](../obsidian-vault/SKILL.md). Frontmatter: `type: wiki`, `status: synthesized`.

## The Karpathy pattern

> "LLM-supervised wiki generation"

Inputs are the *grounded source material* (curated source notes + their extracted triples), not the LLM's pretraining knowledge. The LLM's job is to **structure, not invent**. Every claim in the wiki should trace back via wikilink to a `Source -- ...md` in the vault.

Key disciplines:

1. **Atomic.** One concept per wiki note. If the topic spans multiple concepts, write multiple wiki notes and link them.
2. **Concept-oriented, not source-oriented.** A wiki on "tool assembly" is a concept note, not a summary of Vivian's video. The video is a `[[Source -- ...]]` referenced from the wiki.
3. **Densely linked.** Every claim links to a source note (`[[Source -- The Bitter Lesson]]`), every related concept links to its wiki (`[[Wiki -- Decentralization]]`), every relevant index sits in `## Related`.
4. **Grounded only.** If the graph doesn't have evidence for a claim, do NOT include the claim. Note the gap explicitly: "(no source notes yet on subtopic Y; capture more before extending here)".

## Workflow (prototype variant)

```bash
set -euo pipefail
VAULT="${OBSIDIAN_VAULT:-/Users/ethanphan/Documents/my-obsidian-v1}"
TOPIC="$ARGUMENTS"
NEW_NOTE="$(dirname "$0")/../obsidian-vault/scripts/new_note.sh"
TMPDIR=$(mktemp -d); trap 'rm -rf "$TMPDIR"' EXIT

# 1. Resolve topic → graph subset
# Prototype: search source notes by keyword + tag.
# Real impl: query Honcho for nodes whose label matches TOPIC, gather 1-2 hop neighborhood.
grep -rli --include='Source -- *.md' --include='Wiki -- *.md' \
  -F "$TOPIC" "$VAULT" > "$TMPDIR/sources.txt" || true

[ -s "$TMPDIR/sources.txt" ] || { echo "No source material found for topic: $TOPIC. Run more ingest-* skills first." >&2; exit 1; }
```

The agent then:

2. **Reads each source note** referenced in `sources.txt`.
3. **Drafts a wiki** following the structure below.
4. **Verifies** every paragraph cites a `[[Source -- ...]]` link.
5. **Writes** via `new_note.sh --type wiki --title "$TITLE" --body-file ...`.
6. **Hooks `extract-graph`** to mirror the new wiki note into the graph.

## Wiki structure

```markdown
# <Title in Title Case>

> One-sentence definition of the concept.

## What it is

2-4 paragraphs grounding the concept. Every claim links to a `[[Source -- ...]]`.

## Why it matters

What does this concept enable / prevent / explain? Cite evidence.

## Related concepts

- `[[Wiki -- Adjacent Concept 1]]` — one-line on the relationship.
- `[[Wiki -- Adjacent Concept 2]]` — one-line on the relationship.

## Open questions

- Genuinely open questions surfaced from the source material — not LLM hallucinations.

## Sources

- `[[Source -- ...]]` — one-line on what this source contributes.
- `[[Source -- ...]]`

## Related

- `[[<Topic> Index]]` — auto-injected by [update-index](../update-index/SKILL.md).
```

## After writing

1. Pipe the new path through [update-index](../update-index/SKILL.md) so the relevant `... Index.md` MOC notes pick up a `[[Wiki -- ...]]` link.
2. Pipe through [extract-graph](../extract-graph/SKILL.md) so the wiki becomes a graph node and its links become semantic edges.

## Confirmation

```
Wrote: Wiki -- Tool Assembly.md  (cites 4 sources, links 3 wikis)
```

## Failure modes

- **No source material on topic** — fail loudly with `"No source material found for <topic>. Capture sources first."`. Do NOT generate a wiki from pretraining knowledge.
- **Topic too broad** — ask the user to narrow. "Tool assembly" yes; "AI" no.
- **Insufficient graph density** — when fewer than 3 source notes touch the topic, surface a draft but mark `status: synthesized-thin` and remind the user that more capture would deepen the wiki.
