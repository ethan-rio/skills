---
name: book-2-site
description: Convert a book (PDF or other format) into an interactive learning website with adaptive Summary, Values, Quotes, Map, and more. Reads the entire book into context, then generates a bespoke site in `interactive_learning/<slug>/`. Use when the user wants to study a book deeply or asks to "book-2-site" a file.
when_to_use: User runs `/book-2-site <path-to-book>` or asks to turn a book PDF/EPUB/MD into a study website.
argument-hint: <path-to-book-file>
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch
---

# book-2-site

Read an entire book and generate a bespoke interactive learning site.

## Arguments

`$ARGUMENTS` = absolute or relative path to the book file (PDF preferred; other formats handled by runtime research).

## Output

`<parent-of-book>/interactive_learning/<slug>/`

Where `<slug>` is the book's filename without the extension, lowercased, spaces → dashes, unsafe chars stripped.

Shared runtime (HTML shell, CSS, JS renderer) lives at `<parent-of-book>/interactive_learning/_runtime/` — one copy per library, refreshed from `~/.claude/skills/book-2-site/runtime/` on each run.

Per-book files are only `index.html` (~20 lines, sources `../_runtime/`), `data.js`, `quotes.js`.

## Workflow — follow these phases in order

### Phase 1 — Measure

Run `python3 ${CLAUDE_SKILL_DIR}/scripts/measure.py "$ARGUMENTS"`. It prints JSON with `pages`, `chars`, `est_tokens`, `chars_per_page`, `class` (`small`/`medium`/`large`/`oversized`/`scanned`).

Branch on `class`:
- **`small` / `medium` / `large`**: proceed to Phase 2. Chunked read is the default regardless of class — the extractor always emits `chunks/`.
- **`oversized`** (>2M tokens): abort with clear message.
- **`scanned`** (<100 chars/page): switch to vision-based extraction (see `reference.md`).

### Phase 2 — Extract & Chunked Read

Run `python3 ${CLAUDE_SKILL_DIR}/scripts/extract.py "$ARGUMENTS" "<output-dir>/.booksite/state/"`.

The script bootstraps a venv on first run. It creates or augments `requirements.txt` with the packages it needs (`pypdf`, `pymupdf`) and installs them. No system-wide pip calls.

**Venv location — important for the agent:** `_venv.py` anchors the venv at Python's `cwd()`, which is whatever directory Bash is in when `measure.py` / `extract.py` is invoked. That means **the venv lands in the user's current working directory at invocation time**, not in the skill directory and not in the output directory.

Practical rules:
- Do NOT `cd` to a different directory before running the scripts. Run them from whatever directory the user invoked the skill in (usually where their book file lives or a parent of it).
- Invoke with absolute paths to the book and state dir — e.g. `python3 ${CLAUDE_SKILL_DIR}/scripts/extract.py "<absolute-book-path>" "<absolute-state-dir>"` — so cwd doesn't need to change.
- On repeat runs from the *same* directory, the existing `.venv` is reused automatically (fast).
- On runs from a *different* directory, a fresh `.venv` is created there. That's intentional — each project gets its own.
- If the user already has a `requirements.txt` in that folder, the bootstrap appends missing entries rather than overwriting it; existing pins are untouched.

This writes:
- `.booksite/state/chunks/chunk-NNN.txt` — page-bounded chunks (≤80 pages or ≤200KB each, always Read-tool friendly)
- `.booksite/state/chunks/manifest.json` — `[{id, pages, chars, bytes, file}, ...]`
- `.booksite/state/extracted.txt` — full plain text (reference copy, do NOT Read directly for books >200KB)
- `.booksite/state/figures/` — rendered page images for pages with figures (if any)
- `.booksite/state/source.sha256` — used for resume detection
- `.booksite/state/meta.json` — pages, size, `chunk_count`, detected structure

**Read chunk by chunk, not the whole book at once.** The extracted.txt is there as a reference but will exceed the Read tool's 256KB limit for any non-trivial book.

For each chunk in `manifest.json`:
1. Read the chunk file.
2. Immediately write structured notes to `.booksite/state/notes/chunk-NNN.json`:
   ```json
   { "pages": "1-80",
     "summary": "...",
     "key_concepts": [...],
     "quotes": [{"text": "...", "src": "Ch X, p. N"}, ...],
     "map_hints": [{"id": "...", "label": "...", "tag": "...", "tagline": "..."}],
     "values_hints": [...] }
   ```
3. Do **not** re-Read the chunk. The notes are now your canonical memory.

After all chunks noted, synthesise `data.js` and `quotes.js` from the union of notes.

For non-PDF formats, consult `reference.md` → "Non-PDF extraction" for the research-and-install procedure.

### Phase 3 — Plan (internal)

After reading, write a private plan to `<output-dir>/.booksite/state/plan.md` capturing:
- Book type (technical / philosophical / narrative / tutorial / …)
- Thesis in one sentence
- Which views apply (always: Read, Summary, Values, Quotes, Map; conditional: Tips, Quiz, Scenarios — decide per rubric in `reference.md`)
- Primary Map archetype + alternate archetypes (see `reference.md`)
- Values theme list (6–15, book-specific names)
- Section types to use in Summary (pick from the section library — see `reference.md`)

### Phase 4 — Generate (staged, resumable)

Do not emit `data.js` in a single monolithic Write. Stage it so an interruption loses at most one chapter's worth of output.

1. **Skeleton.** Write `data.js` with `meta`, `values`, `map`, `summary`, optional `tips`/`quiz`/`scenarios`, and an empty `read: { chapters: [] }`. Write `quotes.js` in full.
2. **Progress file.** Write `.booksite/state/progress.json`: `{ "phase": "chapters", "total": N, "done": [] }`.
3. **Per chapter.** For each chapter: generate its object, Edit `data.js` to append it inside `chapters: [ ... ]`, update `progress.json.done`. One chapter = one Edit.
4. **Index.** After all chapters written, generate `index.html` from `runtime/template.html`.

On resume: read `progress.json`; skip any chapter id already in `done[]`. This makes mid-generation interruptions cheap.

**Before moving on, every field must meet the minimums in `reference.md` §10 (Quality rubric).** The rubric is the floor — see §10.0 for scaling rules on long books.

### Phase 5 — Self-review (MANDATORY — do not skip)

**This phase is required. A site is not done until self-review passes.**

1. Re-Read the just-written `data.js` and `quotes.js` via the Read tool.
2. Walk through the rubric in `reference.md` §10, counting passes/failures per row.
3. Write the audit to `<output-dir>/.booksite/state/self-review.md` using the template in `reference.md` §11.2.
4. If the audit has any ⚠ NEEDS-REVISION rows, **edit the affected fields in `data.js` / `quotes.js` until every row passes** (see §11.4 for common revision patterns). Re-audit after revision.
5. Do not proceed to Phase 6 until `self-review.md` ends with `Overall: PASS`.

Exceptions are allowed only when the book genuinely cannot meet a rubric row (e.g., no code in a philosophy book → no `example` field). Document exceptions in the `Justified exceptions` section of `self-review.md`.

### Phase 6 — Install runtime

Copy `${CLAUDE_SKILL_DIR}/runtime/{app.js,styles.css}` to `<parent>/interactive_learning/_runtime/`. Overwrite existing files (that's the point — shared runtime stays current).

### Phase 7 — Log & report

Write progress/actions to `<output-dir>/.booksite/log.txt` as you go. At the end, print a summary:
```
✓ Site generated at <output-dir>/index.html
  Views: Summary, Values, Quotes, Map (+ Tips / Quiz / Scenarios if applicable)
  Read X pages, Y figures, Z quotes curated
  Open with: xdg-open "<output-dir>/index.html"
```

## Resume

Three levels of resume, checked in order on each invocation:

1. **Extraction cache** — if `.booksite/state/source.sha256` matches the source file, skip Phase 2; the existing `chunks/` and `extracted.txt` are reused.
2. **Notes cache** — if `.booksite/state/notes/chunk-NNN.json` exists for every chunk in `manifest.json`, skip chunked-read; go straight to Phase 3 with the notes as your memory.
3. **Generation progress** — if `.booksite/state/progress.json` exists, read it and resume chapter-by-chapter generation from `done[]`. Skip chapters already present.

If the user passes `--fresh`, delete `.booksite/state/` first.

## Failure handling

- PDF extraction returns thin text (<100 chars/page) → auto-fallback to vision on every page.
- Missing Python package → handled automatically by `scripts/_venv.py` (creates `./.venv` in the current working directory, ensures `./requirements.txt` has the needed packages, installs, re-execs). If `python3 -m venv` itself fails, surface the error to the user.
- Vision call transient error → retry 3× with backoff.
- Any unrecoverable error → friendly message + full stack in `.booksite/log.txt`.

## References

- `reference.md` — schema for `data.js`, section-type library, Map archetype rubric, view-inclusion rubric, non-PDF extraction procedure, chunked-read procedure
- `runtime/template.html` — the HTML shim each generated site uses
- `runtime/app.js`, `runtime/styles.css` — the shared schema-tolerant renderer
- `scripts/measure.py`, `scripts/extract.py` — Python helpers

## Quality bar

The whole value of this skill is **fidelity to the specific book**. Generic summaries are failure. The Values themes, Summary sections, and Map archetype must reflect what *this book* is about, not a template.

Two discipline layers enforce this:

1. **`reference.md` §10 — mandatory minimums.** Every field has a quantitative floor (chars/bullets/quotes/nodes/edges). No generated site skips it on the grounds of "this book is different". Exceptions require written justification.

2. **`reference.md` §11 — self-review phase.** After generating, Claude re-reads its own output, scores it against §10, writes `self-review.md`, and revises gaps until every row passes. This is a required phase in the workflow, not optional.

The first pass of generation is often thin (it matches the structure, not the depth). The self-review loop is what raises quality to a consistent bar. **Do not skip self-review.**
