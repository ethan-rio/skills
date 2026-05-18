---
name: extract-graph
description: Extract entity-relation triples (causal, temporal, semantic) from a Source or Wiki note into the Honcho graph memory store. Mirrors Vivian's Mnemon pattern. Skill ships a contract; helper script implementation depends on Honcho schema decisions deferred to a follow-up spec.
when_to_use: After `curate` promotes an inbox note to `Source -- ...md`, OR explicitly via `/graph <note-name>`, OR as a hook after `synthesize-wiki` to reflect new wiki nodes back into the graph.
argument-hint: <vault-relative-note-path>
allowed-tools: Read Bash Write
---

# extract-graph

Note → entity-relation triples → Honcho graph. The bridge from human-readable Obsidian to machine-traversable memory.

## Status

**Contract is fixed; helper script implementation is TODO** until the Honcho graph schema is decided. See [open questions in the spec](../../../docs/superpowers/specs/2026-05-18-hermes-pkm-skill-set-design.md). This SKILL.md describes what the script must do so downstream skills (`synthesize-wiki`, `recall`) can be written against a stable contract.

## When to use

- Hook on `curate` promote: every new `Source -- ...md` should be reflected into the graph.
- Hook on `synthesize-wiki`: a new wiki note becomes a graph node too (concept-level).
- Manual: `/graph <note-name>` to re-extract after editing a note.

## Inputs / outputs

- **Input:** `$ARGUMENTS = <vault-relative path>` (e.g. `Source -- The Bitter Lesson.md` or `Inbox/Article -- 2026-05-18 -- ....md`).
- **Output (stdout):** JSON summary — `{nodes_added: N, edges_added: M, graph_id: "..."}`.
- **Side effect:** updates the note's frontmatter to set `graph_id: <honcho-node-id>`.

## Vault contract

See [obsidian-vault](../obsidian-vault/SKILL.md).

## Triple shape

Following Vivian's three edge types:

```jsonc
{
  "node": {
    "id": "n_<uuid>",
    "label": "...",                 // human-readable
    "kind": "person|place|concept|event|document|claim",
    "source_note": "Source -- ....md",  // the vault note this node was extracted from
    "captured_at": "2026-05-18T..."
  },
  "edges": [
    { "from": "n_a", "to": "n_b", "kind": "causal",   "label": "causes",        "weight": 0.8, "evidence": "<quote>" },
    { "from": "n_a", "to": "n_b", "kind": "temporal", "label": "preceded by",   "weight": 1.0, "evidence": "<quote>" },
    { "from": "n_a", "to": "n_b", "kind": "semantic", "label": "is a kind of",  "weight": 0.6, "evidence": "<quote>" }
  ]
}
```

- `kind` on edges is the **mandatory** Vivian taxonomy (causal / temporal / semantic).
- `label` on edges is a free-form natural-language predicate ("causes", "is a kind of", "preceded by", "contradicts").
- `evidence` quotes the source text the LLM relied on — required for `recall` to cite back.
- `weight` ∈ [0, 1] = LLM's confidence.

## Helper script contract

`scripts/extract_graph.py` (TODO) must:

1. **Read** the vault note at `$ARGUMENTS`.
2. **Prompt an LLM** with a clear extraction template (system prompt: "extract entities and edges following the schema; ground every edge in a direct quote from the text"). Use Claude (the host model) for this.
3. **Validate** the LLM output against the schema. Reject + retry if malformed.
4. **Deduplicate** against existing Honcho nodes — entity resolution by normalized label + kind. Reuse `node.id` if a match is found within similarity threshold.
5. **Write** new nodes + edges to Honcho via its client API.
6. **Patch** the source note's frontmatter with `graph_id: <root-node-id>` for the document itself.
7. **Emit** the JSON summary on stdout.

The script must be **idempotent** — re-running on the same note should not duplicate triples; it should detect overlaps and either skip or update with the latest evidence.

## Honcho schema dependencies (deferred)

Before this script can be implemented, the following must be decided in a separate spec:

- **Honcho node identity** — UUID? content-hash? graph-database native id?
- **Storage backend** — Honcho's session/message model directly, or a side-car graph DB (kuzu / neo4j / sqlite + edges table) referenced from Honcho?
- **Embedding model** — for semantic-edge generation and entity resolution. Local (Ollama) or cloud?
- **Refresh policy** — when a source note is edited, do we re-extract from scratch or diff?

Until those land, downstream skills (`synthesize-wiki`, `recall`) should treat this skill's output as a **mock**: store triples as JSON files under `$VAULT/.graph/` and operate on those for prototyping. That gives you an end-to-end loop without committing to a schema.

## Workflow (prototype variant — JSON-on-disk)

```bash
set -euo pipefail
VAULT="${OBSIDIAN_VAULT:-/Users/ethanphan/Documents/my-obsidian-v1}"
NOTE="$VAULT/$ARGUMENTS"
[ -r "$NOTE" ] || { echo "ERROR: cannot read $NOTE" >&2; exit 1; }

GRAPH_DIR="$VAULT/.graph"
mkdir -p "$GRAPH_DIR/nodes" "$GRAPH_DIR/edges"

# Have the LLM read $NOTE and produce a triples JSON. Pseudo-call:
#   claude run --skill extract-graph-prompt --input "$NOTE" --output "$GRAPH_DIR/staging.json"
# Then dedupe + write per-node/edge files keyed by id, append to a running edges.jsonl.

# Until extract_graph.py exists, this skill is invoked by the LLM directly:
# the LLM reads the note via Read tool, emits triples in conversation, then
# calls Write to persist them under .graph/.
```

## Failure modes

- **Honcho unreachable** — fall back to JSON-on-disk under `$VAULT/.graph/` and surface a warning.
- **LLM produces malformed JSON** — retry once with a stricter prompt; on second failure, surface the raw output and skip rather than write garbage.
- **Note has no extractable entities** — emit `{nodes_added: 0, edges_added: 0}` and don't error.

## See also

- [synthesize-wiki](../synthesize-wiki/SKILL.md) — consumes the graph to produce wiki notes.
- [recall](../recall/SKILL.md) — queries the graph.
- [Vivian's video](https://www.youtube.com/watch?v=t-4a20_iYhg) — the inspiration. He runs Mnemon for this layer.
