#!/usr/bin/env python3
"""Extract a book's text (and optionally page images for figures) to a state dir.

Usage: extract.py <source-path> <state-dir>

Writes:
  <state-dir>/extracted.txt        — full plain text with page markers
  <state-dir>/source.sha256        — SHA-256 of source file
  <state-dir>/meta.json            — {pages, chars, figures_extracted, format, slug}
  <state-dir>/figures/page-NNN.png — high-DPI renders of pages with embedded images

Only re-extracts if source hash differs. Idempotent.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _venv import ensure_venv  # noqa: E402

ensure_venv()

# Chunking targets. The Read tool has TWO limits — ~256KB bytes AND ~25K tokens
# (≈ 90KB for prose, less for code-heavy text). Token limit is the binding one.
# Keep chunks ≤80KB to stay single-Read even for token-dense books.
CHUNK_MAX_BYTES = 80_000
CHUNK_MAX_PAGES = 40


def write_chunks(state_dir: Path, pages_text: list[str]) -> list[dict]:
    """Split per-page text into chunks bounded by CHUNK_MAX_BYTES / CHUNK_MAX_PAGES.

    pages_text[i] is the full text of page i+1 (including a ===PAGE N=== marker).
    Returns a manifest list of {id, pages, chars, bytes, file}.
    """
    chunks_dir = state_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    # Wipe any stale chunks from a prior run with different boundaries.
    for old in chunks_dir.glob("chunk-*.txt"):
        old.unlink()

    manifest = []
    buf: list[str] = []
    buf_bytes = 0
    first_page = 1
    chunk_id = 1

    def flush(last_page: int):
        nonlocal buf, buf_bytes, first_page, chunk_id
        if not buf:
            return
        body = "".join(buf)
        fname = f"chunk-{chunk_id:03d}.txt"
        (chunks_dir / fname).write_text(body, encoding="utf-8")
        manifest.append({
            "id": chunk_id,
            "pages": f"{first_page}-{last_page}",
            "chars": len(body),
            "bytes": len(body.encode("utf-8")),
            "file": f"chunks/{fname}",
        })
        chunk_id += 1
        buf = []
        buf_bytes = 0
        first_page = last_page + 1

    for i, page_text in enumerate(pages_text, start=1):
        page_bytes = len(page_text.encode("utf-8"))
        if buf and (buf_bytes + page_bytes > CHUNK_MAX_BYTES or (i - first_page) >= CHUNK_MAX_PAGES):
            flush(i - 1)
        buf.append(page_text)
        buf_bytes += page_bytes
    flush(len(pages_text))

    (chunks_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "book"


def page_has_image(page) -> bool:
    """Detect embedded XObjects on a PDF page."""
    try:
        resources = page.get("/Resources")
        if not resources:
            return False
        xobjects = resources.get("/XObject") if hasattr(resources, "get") else None
        if not xobjects:
            return False
        # any XObject marked as Image
        for name in xobjects.keys():
            obj = xobjects[name]
            subtype = obj.get("/Subtype") if hasattr(obj, "get") else None
            if str(subtype) == "/Image":
                return True
    except Exception:
        pass
    return False


def extract_pdf(source: Path, state_dir: Path) -> dict:
    from pypdf import PdfReader  # type: ignore

    reader = PdfReader(str(source))
    pages = len(reader.pages)
    figures_dir = state_dir / "figures"
    full_text_parts = []     # for extracted.txt (whole-book convenience copy)
    pages_text: list[str] = []  # for chunking (one entry per page)
    image_pages = []

    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        page_block = f"\n===PAGE {i}===\n{text}"
        full_text_parts.append(page_block)
        pages_text.append(page_block)
        if page_has_image(page):
            image_pages.append(i)

    (state_dir / "extracted.txt").write_text("".join(full_text_parts), encoding="utf-8")
    manifest = write_chunks(state_dir, pages_text)

    # Render image-bearing pages via pymupdf (fitz) if available.
    figures_extracted = 0
    if image_pages:
        try:
            import fitz  # type: ignore
            figures_dir.mkdir(parents=True, exist_ok=True)
            doc = fitz.open(str(source))
            # Cap at 60 figures so we don't blow up small books or generate 500 PNGs
            for pnum in image_pages[:60]:
                try:
                    pix = doc[pnum - 1].get_pixmap(dpi=160)
                    pix.save(str(figures_dir / f"page-{pnum:03d}.png"))
                    figures_extracted += 1
                except Exception:
                    pass
            doc.close()
        except ImportError:
            # pymupdf not installed — skip rendering. Text is still extracted.
            pass

    return {
        "format": "pdf",
        "pages": pages,
        "chars": sum(len(p) for p in full_text_parts),
        "figures_extracted": figures_extracted,
        "image_pages_detected": len(image_pages),
        "chunk_count": len(manifest),
    }


def _pseudo_pages(content: str) -> list[str]:
    """Split text into ~3000-char pseudo-pages so chunking logic applies uniformly."""
    step = 3000
    out = []
    for i in range(0, len(content), step):
        pnum = i // step + 1
        out.append(f"\n===PAGE {pnum}===\n{content[i:i+step]}")
    return out or ["\n===PAGE 1===\n"]


def extract_text_like(source: Path, state_dir: Path) -> dict:
    content = source.read_text(encoding="utf-8", errors="replace")
    (state_dir / "extracted.txt").write_text(content, encoding="utf-8")
    pages_text = _pseudo_pages(content)
    manifest = write_chunks(state_dir, pages_text)
    return {
        "format": source.suffix.lstrip("."),
        "pages": len(pages_text),
        "chars": len(content),
        "figures_extracted": 0,
        "image_pages_detected": 0,
        "chunk_count": len(manifest),
    }


def extract_folder(source: Path, state_dir: Path) -> dict:
    files = sorted([p for p in source.rglob("*") if p.suffix.lower() in (".md", ".txt")])
    content = []
    for f in files:
        content.append(f"\n===FILE {f.relative_to(source)}===\n")
        try:
            content.append(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            pass
    joined = "".join(content)
    (state_dir / "extracted.txt").write_text(joined, encoding="utf-8")
    pages_text = _pseudo_pages(joined)
    manifest = write_chunks(state_dir, pages_text)
    return {
        "format": "folder",
        "files": len(files),
        "pages": len(pages_text),
        "chars": len(joined),
        "figures_extracted": 0,
        "image_pages_detected": 0,
        "chunk_count": len(manifest),
    }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "usage: extract.py <source> <state-dir>"}))
        sys.exit(1)

    source = Path(os.path.expanduser(sys.argv[1])).resolve()
    state_dir = Path(os.path.expanduser(sys.argv[2])).resolve()

    if not source.exists():
        print(json.dumps({"error": f"source not found: {source}"}))
        sys.exit(1)

    state_dir.mkdir(parents=True, exist_ok=True)

    # Hash / resume check
    current_hash = sha256_of(source) if source.is_file() else "folder-" + str(int(source.stat().st_mtime))
    hash_file = state_dir / "source.sha256"
    meta_file = state_dir / "meta.json"
    extracted_file = state_dir / "extracted.txt"

    if (
        hash_file.exists()
        and hash_file.read_text().strip() == current_hash
        and extracted_file.exists()
        and meta_file.exists()
    ):
        meta = json.loads(meta_file.read_text())
        meta["resumed"] = True
        print(json.dumps(meta, indent=2))
        return

    # Fresh extraction
    if source.is_dir():
        stats = extract_folder(source, state_dir)
    else:
        ext = source.suffix.lower()
        if ext == ".pdf":
            stats = extract_pdf(source, state_dir)
        elif ext in (".txt", ".md"):
            stats = extract_text_like(source, state_dir)
        else:
            print(json.dumps({
                "error": f"format {ext} not handled by extract.py",
                "hint": "agent should research and install an extractor (see reference.md)",
            }))
            sys.exit(2)

    hash_file.write_text(current_hash)
    slug = slugify(source.stem if source.is_file() else source.name)
    meta = {
        "source": str(source),
        "slug": slug,
        "resumed": False,
        **stats,
    }
    meta_file.write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
