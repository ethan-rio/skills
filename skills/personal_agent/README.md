# Personal agent

Skills for a personal second-brain agent — ingest raw resources, curate, extract structure into a graph memory, synthesize wiki notes, and recall on demand. Hermes-shaped but agent-agnostic: every skill is a standard `SKILL.md` and works in Claude Code, Goose, or any `SKILL.md`-aware host.

Inspired by Vivian Balakrishnan's [Building a 'Second Brain'](https://www.youtube.com/watch?v=t-4a20_iYhg) talk — graph as memory, Obsidian as surface, Karpathy-style LLM-supervised wiki generation. Design lives at [`docs/superpowers/specs/2026-05-18-hermes-pkm-skill-set-design.md`](../../docs/superpowers/specs/2026-05-18-hermes-pkm-skill-set-design.md).

## Foundation

- **[obsidian-vault](./obsidian-vault/SKILL.md)** — the vault contract every other skill in this bucket assumes. Ships `scripts/new_note.sh` as the canonical note creator.

## Ingest

- **[ingest-quick-note](./ingest-quick-note/SKILL.md)** — capture a short text thought into the Obsidian Inbox.
- **[ingest-article](./ingest-article/SKILL.md)** — scrape a web article (Firecrawl) into the Inbox as clean markdown.
- **[ingest-youtube](./ingest-youtube/SKILL.md)** — wrap `youtube-summary` and file the output into the Inbox.
- **[ingest-pdf](./ingest-pdf/SKILL.md)** — extract text from a PDF into the Inbox.
- **[ingest-voice-note](./ingest-voice-note/SKILL.md)** — transcribe a voice message with Whisper and file the transcript.

## Process

- **[curate](./curate/SKILL.md)** — review Inbox/ items and promote to root as `Source -- ...md`, or merge / discard / retag.
- **[extract-graph](./extract-graph/SKILL.md)** — extract entity-relation triples (causal/temporal/semantic) from a note into the Honcho graph.
- **[synthesize-wiki](./synthesize-wiki/SKILL.md)** — generate a `Wiki -- <Topic>.md` from a topic and the relevant graph subset.

## Navigate

- **[update-index](./update-index/SKILL.md)** — inject `[[wikilinks]]` to a new wiki into the appropriate `<Topic> Index.md` MOC notes.
- **[recall](./recall/SKILL.md)** — answer a question by querying the graph + semantic search, with `[[wikilink]]` citations.
- **[daily-review](./daily-review/SKILL.md)** — daily housekeeping: inbox debt, broken links, orphan wikis, ripe topics.
