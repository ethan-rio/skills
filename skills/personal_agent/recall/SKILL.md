---
name: recall
description: Answer a question by querying the Honcho graph plus semantic search over vault notes, returning a grounded answer with [[wikilink]] citations. Use when the user asks a question that should be answered from their own captured material rather than from the model's pretraining.
when_to_use: User asks a factual or interpretive question and the harness should answer from the vault rather than freelance, OR runs `/ask <question>`, OR says "what do we know about X / according to my notes / from what I've captured".
argument-hint: <question>
allowed-tools: Read Bash Write
---

# recall

The query side of the second brain. Vivian's "if I need a fact or a factoid, I can get it anywhere" — implemented as graph + semantic search over your own captured material, with citations.

## Status

**Contract is fixed; full implementation requires the Honcho schema and the embedding pipeline.** Until then, the prototype variant uses the JSON-on-disk graph (see [extract-graph](../extract-graph/SKILL.md)) and grep-based search over vault notes. That's enough to validate end-to-end.

## When to use

- `/ask <question>` slash command.
- User phrases a question and wants a *grounded* answer (your own notes), not a fresh LLM answer.
- User says "what do we know about X" / "according to my notes".

## When NOT to use

- General factual questions where the LLM's pretraining is fine ("what's the capital of France"). Recall is for **your captured material**, not Wikipedia.
- The skill should fail loudly when the vault has no relevant material rather than silently fall back to pretraining.

## Inputs / outputs

- **Input:** `$ARGUMENTS = <question>`.
- **Output:** answer text + a `Sources:` block listing `[[wikilinks]]` actually consulted.

## Vault contract

See [obsidian-vault](../obsidian-vault/SKILL.md).

## Workflow (prototype — graph + grep)

```bash
set -euo pipefail
VAULT="${OBSIDIAN_VAULT:-/Users/ethanphan/Documents/my-obsidian-v1}"
Q="$ARGUMENTS"

# 1. Pull keywords from the question (LLM does this in conversation; this is a sketch).
# 2. Search wiki + source notes by keyword.
HITS=$(grep -rli --include='Wiki -- *.md' --include='Source -- *.md' -E "$(echo "$Q" | tr ' ' '|')" "$VAULT" 2>/dev/null || true)

[ -n "$HITS" ] || { echo "No vault material relevant to: $Q" >&2; exit 0; }

# 3. The agent reads the top-N hits and composes an answer with citations.
echo "$HITS" | head -10
```

The LLM (the host model) then:

1. Reads each hit via the Read tool.
2. Composes an answer **grounded in those notes only** — every claim citable to a `[[Wiki -- ...]]` or `[[Source -- ...]]`.
3. If the notes don't cover the question, **says so** rather than improvising. Suggests which ingest-* skill the user should run.

## Workflow (full — graph-aware)

When the Honcho graph is wired:

1. **Embed** the question with the same model used for source notes.
2. **Retrieve** top-K nodes by cosine similarity from Honcho.
3. **Expand** to 1-2 hop neighbourhood — pull edges (causal/temporal/semantic) for context.
4. **Rerank** by a graph-aware score (semantic similarity × edge weight × recency).
5. **Compose** the answer. Cite by graph_id → resolve to vault note via frontmatter.

## Output shape

```markdown
**Answer:** <2-4 paragraphs grounded in the cited sources.>

**Sources:**
- [[Source -- The Bitter Lesson]] — provided the framing on scale vs. structure.
- [[Wiki -- Tool Assembly]] — synthesized concept note this answer leans on.
- [[Source -- Vivian Balakrishnan -- Building a Second Brain]] — direct quote on curation.

**Caveats:**
- The vault has no source material on subtopic X; the answer above does not address it.
```

## Confirmation

The answer itself is the confirmation. Surface to the user; if they're on Telegram, the wikilinks won't render but they're still scannable.

## Failure modes

- **No relevant material** — say so. Suggest which ingest-* skill to run. Do NOT freelance.
- **Conflicting sources** — surface the conflict explicitly. Don't pick a side silently.
- **Honcho unreachable** — fall back to grep-only mode and warn the user that semantic search is degraded.

## Disciplines

This skill is the **integrity check** for the whole second brain. If `recall` lies, the system has no value.

- **Cite or skip.** No claim without a `[[wikilink]]` to a vault note.
- **Quotes when contested.** When the answer is interpretive, quote the source directly.
- **Don't hallucinate adjacency.** If two notes don't actually link in the graph, don't claim they do.
