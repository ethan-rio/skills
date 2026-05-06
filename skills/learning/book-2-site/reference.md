# book-2-site — Reference

Deep spec. Loaded only when the agent needs it.

---

## 1. `data.js` schema

Every generated site's `data.js` sets `window.BOOK` to an object with this shape:

```js
window.BOOK = {
  schemaVersion: 1,              // increment only on breaking changes
  meta: {
    title: "...",                // book title
    subtitle: "...",             // optional
    authors: "...",              // "Author1 & Author2"
    year: 2000,                  // publication year (int or null)
    genre: "...",                // free text: "technical / philosophy / narrative / tutorial / ..."
    slug: "...",                 // matches folder name
  },

  // --- CORE VIEWS (always present) ---

  summary: {
    // Free-form ordered sequence of sections. Renderer handles each by `.type`.
    // See "Section types library" below for supported types.
    sections: [ /* {type, title, ...}, ... */ ]
  },

  values: {
    // 6–15 book-specific themes
    intro: "...",
    themes: [
      {
        id: "craft",
        title: "Craft",
        subtitle: "...",
        color: "#ffb547",         // any valid CSS color
        quotes: [
          { text: "...", src: "Tip 1", context: "..." },  // context is optional
          ...
        ]
      },
      ...
    ]
  },

  // Quotes live in a separate file (quotes.js). See "quotes.js" below.

  map: {
    primary: "concept-dependency", // id of the archetype shown by default
    archetypes: [
      {
        id: "concept-dependency",
        label: "Concept Dependency",
        description: "...",        // 1 sentence, shown in UI
        nodes: [
          {
            id: "dry",
            label: "DRY",
            tag: "Principle",       // category label shown in inspector
            tagline: "...",         // 1 sentence
            group: 2,               // integer for color-grouping (e.g. chapter #)
            core: true,             // optional; if true, special styling
            topic: "summary-..."    // optional; id of a Summary section or topic for drill-in
          },
          ...
        ],
        edges: [
          { from: "dry", to: "orth", label: "reinforces", strong: true },
          ...
        ],
        groups: [                   // optional legend; mapped to node.group
          { id: 1, label: "Philosophy", color: "#ffb547" },
          ...
        ]
      },
      /* additional archetypes: timeline, process-flow, etc. */
    ]
  },

  // --- READ VIEW (always present) ---

  // Structured view of the book's chapters/sections for the Read tab.
  read: {
    chapters: [
      {
        id: "ch-1",
        num: 1,
        title: "...",
        intro: "...",               // HTML allowed; escape user-input carefully
        color: "#ffb547",           // optional; matches a Values theme or a chapter palette
        topics: [
          {
            id: "1-1",
            num: 1,
            title: "...",
            hook: "...",             // 1-sentence summary
            why: "...",              // HTML allowed
            how: ["...", ...],       // array of string bullets
            example: { bad: "...", good: "..." }, // optional before/after
            antiPatterns: ["...", ...],           // optional
            tipRefs: [3, 4]                       // optional; references into tips view
          }
        ]
      }
    ]
  },

  // --- CONDITIONAL VIEWS (omit if not applicable) ---

  tips: [
    { n: 1, text: "...", topic: "1-1" },  // short aphorism + topic id
    ...
  ],

  quiz: [
    {
      q: "...",
      opts: ["...", "...", ...],
      correct: 2,                   // index of correct option
      explain: "..."                // why
    },
    ...
  ],

  scenarios: [
    {
      title: "...",
      desc: "...",                  // the situation
      applies: ["1-1", "2-8"],      // topic ids the scenario relates to
      verdict: "..."                // HTML allowed; how this book's ideas apply
    },
    ...
  ]
};
```

**Schema discipline:**
- Never rename or remove fields. Add new ones optionally.
- When adding a new section type or archetype, the runtime's unknown-section handler shows a placeholder automatically — no immediate breakage.

---

## 2. `quotes.js` schema

Separate file so users can add/edit/delete quotes without touching book content:

```js
window.QUOTES = [
  { text: "...", src: "Tip 1" },       // bare quote; src is attribution
  ...
];
```

Keep quotes short (1–2 sentences max). Attribution-only — no elaboration (use Values themes for that).

Typical size: 60–120 quotes for a 300-page book. Include:
- Any numbered tips/rules the book defines
- Memorable lines from prose (1 per ~5 pages)
- Cited epigraphs and quoted authorities

---

## 3. Section types library (for `summary.sections`)

The runtime renders each section based on `type`. Available types:

| type | fields | renders as |
|---|---|---|
| `prose` | `title`, `body` (HTML ok), `tone?` | Paragraph block |
| `list` | `title`, `items: string[]`, `ordered?` | Bulleted/numbered list |
| `cards` | `title`, `note?`, `cards: [{icon?, name, desc}]` | Grid of small cards |
| `timeline` | `title`, `events: [{date, label, body}]` | Vertical timeline |
| `steps` | `title`, `steps: [{num, title, body}]` | Numbered procedural flow |
| `comparison` | `title`, `left: {label, body}`, `right: {label, body}` | Two-column compare |
| `quote-list` | `title`, `quotes: [{text, src}]` | Small quotes strip |
| `definitions` | `title`, `items: [{term, def}]` | Glossary |
| `people` | `title`, `people: [{name, role, body}]` | Character cards |
| `principles` | `title`, `note?`, `items: [{name, line, refs?: number[]}]` | Labeled principle cards with tip refs |
| `table` | `title`, `headers: string[]`, `rows: string[][]` | Data table |
| `callout` | `title`, `tone: "info"|"warn"|"ok"`, `body` | Colored callout box |

Pick whichever types fit the book. A typical Summary has 4–7 sections of varied types.

---

## 4. Map archetype rubric

Pick the **primary** archetype based on the book's dominant structure. Offer 1–2 alternates the book *also* supports.

| Archetype | id | When primary |
|---|---|---|
| Concept Dependency | `concept-dependency` | Technical/philosophical books with interrelated principles (Pragmatic Programmer, Clean Code, Design Patterns) |
| Timeline / Chronology | `timeline` | History, biography, civilizational narratives (Sapiens, Guns Germs & Steel) |
| Character / Relationship | `characters` | Fiction, memoir, political narratives |
| Argument Tree | `argument-tree` | Philosophical polemics, academic arguments |
| Process / Method Flow | `process-flow` | How-to books, methodologies (Lean Startup, GTD) |
| Taxonomy / Category | `taxonomy` | Reference books, classification systems (Gang of Four patterns, diagnostic manuals) |
| Tutorial Dependency | `tutorial-dependency` | Learn-by-doing books where concepts build on prior concepts (Teach Yourself X, textbooks) |

If none fit, invent a new archetype. Give it a short `id`, a human label, a 1-sentence description. The renderer is generic — it just draws nodes + edges.

---

## 5. View-inclusion rubric

**Always include:** `read`, `summary`, `values`, `map`.

**Conditional — decide per rubric:**

| View | Include when |
|---|---|
| `tips` | Book contains enumerated axioms/laws/rules (numbered or clearly listed, ≥10 distinct items) |
| `quiz` | Book has objectively testable facts or principles. Skip for pure narrative/fiction/memoir/poetry |
| `scenarios` | Book's ideas are case-applicable (engineering, management, self-help, psychology-applied). Skip for pure history/narrative/reference |

When you skip a conditional view, log the reason in `plan.md` and omit the field from `data.js` entirely (do not set to `[]`).

---

## 6. Non-PDF extraction procedure

For `.epub`, `.md`, `.txt`, `.docx`, `.html`, or folders:

1. **Research** the best current Python library via WebSearch. Verify via the package's official docs.
2. **Check install**: `python3 -c "import <pkg>"`. If missing:
3. **Install**: `pip install <pkg>`. If network fails, report the manual install command to the user and abort.
4. **Extract** to plain text + extract embedded figures to `.booksite/state/figures/` where applicable.
5. Save same output shape as `scripts/extract.py` produces (so the rest of the pipeline is format-agnostic).

Preferred libraries (subject to change; verify current):
- `.epub` → `ebooklib` + `beautifulsoup4`
- `.docx` → `python-docx`
- `.html` → `beautifulsoup4`
- `.md` / `.txt` → stdlib
- folder of `.md` / `.txt` → concat alphabetically

---

## 7. Scanned / image-only PDFs

If `measure.py` reports `class: scanned` (chars_per_page < 100), skip pypdf text extraction entirely. Instead:

1. Render every page as PNG at 200 DPI using `pymupdf` (`fitz`). Install if missing.
2. Read each PNG via the Read tool (Claude Vision).
3. The "extracted text" is Claude's visual reading of the pages — both text and figures.

This produces higher fidelity than OCR, since Claude understands diagrams semantically.

---

## 8. Chunked-read procedure (default for all sizes)

`extract.py` always splits output into `chunks/chunk-NNN.txt` (≤80 pages or ≤200KB each) plus `chunks/manifest.json`. The Read tool rejects files larger than 256KB, so reading `extracted.txt` whole is not a viable path for most books — always go chunk-by-chunk.

For each chunk:
- Read via Read tool.
- Immediately write structured notes to `.booksite/state/notes/chunk-NNN.json`:
  ```json
  {
    "pages": "1-80",
    "summary": "...",
    "key_concepts": [...],
    "quotes": [{text, src}, ...],
    "map_nodes": [{id, label, tag, tagline, connections: [...]}],
    "values_hints": [...]
  }
  ```
- Do **not** re-Read the chunk file; the notes are now the canonical memory.

After all chunks noted, synthesise `data.js` and `quotes.js` from the union of notes, not from the raw text. This keeps context usage bounded (≈ number-of-chunks × note-size) instead of scaling linearly with the book.

---

## 9. Resume

The SHA-256 of the source PDF is saved to `.booksite/state/source.sha256` on first extract. On every invocation:

1. Compute current PDF's SHA-256.
2. If matches the saved hash AND `.booksite/state/extracted.txt` exists:
   - **Skip Phase 2 extraction.** Use cached text and figures.
3. If `.booksite/state/plan.md` exists:
   - **Re-use the prior plan** (same archetypes, themes, view decisions). This ensures regeneration is idempotent.
4. If `--fresh` flag passed: delete `.booksite/state/` entirely.

---

## 10. Quality rubric — MANDATORY minimums

**These are not suggestions. Every generated site must meet them.** If a generated field falls below the minimum, the self-review phase (§11) must raise it before the site is considered complete.

### 10.0 Scaling by book length

The per-row minimums in §10.1–§10.6 are the **base** floor, calibrated for ~300-page trade books. They scale sub-linearly with page count — fidelity, not volume, is the goal.

| Pages | Scale factor | Notes |
|---|---|---|
| ≤ 400 | 1.0× | Base rubric applies as written. |
| 400 – 800 | 1.25× | Apply to quote counts and map-node counts. |
| 800 – 1300 | 1.5× | Cover 20–24 representative chapters in depth; list the rest under a "Reference-only" section in Summary. |
| > 1300 | 1.5× (hard-capped) | Same as above. Do not generate encyclopedic coverage of every chapter. |

**Hard caps regardless of size** — beyond these, extra volume is noise:
- Quotes: 150 total
- Map primary nodes: 24
- Topics per chapter: 6

Document your page count and the scale factor you applied in `plan.md`.

### 10.1 Topic depth (each topic in `read.chapters[].topics[]`)

| Field | Minimum | Guidance |
|---|---|---|
| `hook` | one vivid sentence, ≤ 140 chars | No "this topic discusses…" filler. Lead with the insight. |
| `why` | ≥ 2 sentences, ≥ 180 chars, must reference book specifics | Cite pages, authors the book cites, concrete examples from the text. No generic platitudes. |
| `how` | ≥ 4 bullets, each actionable | "Do X" or "Avoid Y", not "consider…". |
| `example` | REQUIRED if the book has code, formulas, diagrams, or step-by-step procedures | `{bad, good}` shape. For code books: before/after snippets. For method books: anti-pattern vs. pragmatic scenario. Only omit for pure-prose books (fiction, philosophy) where no example form applies. |
| `antiPatterns` | REQUIRED: ≥ 2 book-specific pitfalls | Must be things the book explicitly warns against OR natural misreadings. Not generic "don't be lazy". |
| `tipRefs` | REQUIRED if `tips` view exists AND this topic relates to tips | Array of tip numbers. Links the Read view to the Tips view. |

### 10.2 Values view

| Field | Minimum | Guidance |
|---|---|---|
| `themes` count | 6–12 | Fewer than 6 is too thin; more than 12 overwhelms. |
| `quotes` per theme | **≥ 3**, target 4–5, max 6 | 2 quotes per theme produces a visually sparse gallery. The first is the "lead" (rendered large); needs siblings. |
| `text` | Verbatim from book OR verbatim-style paraphrase with marker | If paraphrased, mark in `context`: "paraphrased from Ch 5". |
| `src` | Exact: chapter number, tip/verse number, or "Ch X, p. NN" | Never empty. |
| `context` | 1 sentence on where this appears / why it matters | Gives the quote's home in the book. |

### 10.3 Summary sections

| Field | Minimum | Guidance |
|---|---|---|
| Sections count | ≥ 4, target 5–7 | A 1–2 section Summary is a stub. |
| Section types variety | ≥ 3 distinct types | All `prose` sections is a weak summary. Mix `prose` + `cards`/`steps`/`principles`/`timeline`/`comparison`. |
| Every `prose.body` | ≥ 400 chars | Real paragraphs, not sentences. |
| Every `cards` / `principles` section | ≥ 4 cards | Fewer feels trimmed. |
| Thesis | Explicit as `thesis: {title, body}` OR first prose section clearly marked as thesis | Must capture the book's one-line core argument. |

### 10.4 Quotes (`quotes.js`)

| Field | Minimum | Guidance |
|---|---|---|
| Total count | ≥ 1 per ~5 pages of book | e.g. 350-page book → ≥ 70 curated quotes. |
| Unique sources | ≥ √(quote count) | Diverse attribution. 100 quotes all from Ch 1 fails. |
| All numbered tips/laws/rules | MUST be included as quotes | If the book has Tip 1…N, all N appear here. |
| Epigraphs the author cites | Include as quotes with attribution to the cited author | e.g. Emerson, Wittgenstein, etc. |
| No paraphrasing silently | Verbatim text; if cleaned for line-breaks, keep the content exact | |

### 10.5 Map archetypes

| Field | Minimum | Guidance |
|---|---|---|
| Primary archetype `nodes` | ≥ 10 | Fewer than 10 makes the map look empty. |
| Primary archetype `edges` | ≥ 1.2 × nodes | Enough to show real structure. |
| Every node has `tag`, `tagline`, `group` | All three | Inspector panel needs them to look populated. |
| Alternate archetypes | ≥ 1 (ideally 2) | Q3 decision: primary + alternates. |
| Every edge has `label` | Not just `from`/`to` | Named relationships ("enables", "implies"). |
| `core: true` on at least one node | Yes | Gives the renderer a visual anchor. |

### 10.6 Conditional views

| View | Include when | Exclude when |
|---|---|---|
| `tips` | Book has enumerated axioms/laws/rules (≥10 distinct items) | Narrative / memoir / fiction / poetry |
| `quiz` | Book has objectively testable facts or principles (target 10–15 questions) | Pure narrative / fiction |
| `scenarios` | Book's ideas are case-applicable (engineering, management, self-help, psychology-applied) | Pure history / narrative / reference |

When including `tips`, generate ≥ 15 if the book supports it. When including `quiz`, generate ≥ 10.
When including `scenarios`, generate ≥ 6.

### 10.7 Anti-patterns — a site is BAD when

- Fields are filler: "key ideas include leadership, vision, and teamwork".
- Map nodes are vague concepts the book doesn't actually develop.
- Quotes are paraphrases silently presented as verbatim.
- Summary reads like the book's Wikipedia page instead of the book itself.
- Every topic has the same shape of `why` and `how` with no examples or anti-patterns.
- Values themes are generic ("Craft / Learning / Perseverance") rather than book-specific.
- Quiz questions test generic knowledge, not what *this book* argues.

---

## 11. Self-review phase — MANDATORY before declaring done

**This is a required phase. Do not skip it.** After writing `data.js` and `quotes.js`, Claude MUST:

### 11.1 Re-read own output

Read the freshly-written `data.js` and `quotes.js` via the Read tool. This is not busywork — seeing your own output with fresh eyes surfaces thinness that was invisible during generation.

**For books >500 pages:** `data.js` may exceed the Read tool's 256KB limit. In that case: Read `quotes.js` in full, read `data.js` in two passes (first half then second half by line offset), and sample 5 chapters at random for full topic-depth audit. Values, Map, and Summary must still be audited in full.

### 11.2 Score against §10 rubric

Walk through every rubric row in §10. For each rubric, count how many items in the generated data pass or fail the minimum.

Write the review to `<output-dir>/.booksite/state/self-review.md` with this shape:

```markdown
# Self-review — <book slug>

## Topic depth (§10.1)
- Total topics: N
- ✓ `hook` below 140 chars: N/N
- ⚠ `why` below 180 chars: K topics → [list topic ids]
- ⚠ `how` below 4 bullets: K topics → [list topic ids]
- ⚠ Missing `example` (required for this book type): K topics
- ⚠ Missing `antiPatterns`: K topics
- ⚠ Missing `tipRefs`: K topics

## Values (§10.2)
- Themes: N (target 6–12: ✓/⚠)
- Themes with < 3 quotes: K → [list theme ids]
- Missing `context`: K quotes

## Summary (§10.3)
- Sections: N (target ≥ 4: ✓/⚠)
- Section type diversity: K distinct types (target ≥ 3: ✓/⚠)
- `prose.body` shorter than 400 chars: K sections

## Quotes (§10.4)
- Total: N, target ≥ (book_pages / 5): ✓/⚠
- Unique sources: K, target ≥ sqrt(N): ✓/⚠

## Map (§10.5)
- Primary nodes: N (target ≥ 10: ✓/⚠)
- Edges per node ratio: R (target ≥ 1.2: ✓/⚠)
- Nodes missing tag/tagline/group: K
- Alternate archetypes: N (target ≥ 1: ✓/⚠)

## Verdict
Overall: PASS / NEEDS-REVISION
If NEEDS-REVISION: list the specific gaps to fix.
```

### 11.3 Revise if NEEDS-REVISION

If any rubric row fails, **revise the affected fields in `data.js` / `quotes.js` directly** until the review passes. Do not write the final log entry or print the "✓ Site generated" message until the self-review is PASS.

### 11.4 Common revision patterns

- **Thin `why`** → re-open the chapter's extracted text (still cached in `.booksite/state/extracted.txt`), pull a specific example or cited authority, expand.
- **Missing `example`** → find the chapter's code snippets or worked procedure, split into bad/good or before/after form.
- **Missing `antiPatterns`** → the book's warnings/cautions always exist; the "common mistakes" section or "what not to do" hints are gold.
- **Values theme with only 2 quotes** → scan the chapter for more quotable lines; cited authorities, aphorisms, memorable formulations.
- **Thin Map** → traverse the extracted text for concepts you skipped. Every chapter likely adds 2-3 nodes.

### 11.5 When revision is impossible

If the book genuinely doesn't support a rubric requirement (e.g., pure-prose philosophy has no `example` code), document the exception in `self-review.md` under a "Justified exceptions" section. Narrative books may genuinely lack testable content, so the `quiz` view is omitted; that's not a failure — it's correct per §10.6.

The rubric is a floor for books that *can* meet it, not a procrustean bed.
