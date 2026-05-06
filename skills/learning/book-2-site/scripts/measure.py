#!/usr/bin/env python3
"""Measure a book file's extractability, size, and shape.

Prints JSON to stdout with:
    pages, chars, est_tokens, chars_per_page, class, notes

class ∈ {small, medium, large, oversized, scanned, non-pdf-error}
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _venv import ensure_venv  # noqa: E402

ensure_venv()


def classify(chars: int, pages: int) -> tuple[str, str]:
    """Return (class, human-readable note)."""
    if pages == 0:
        return "error", "zero pages"
    cpp = chars / pages
    if cpp < 100:
        return "scanned", f"only {cpp:.0f} chars/page — likely scanned PDF, use vision"
    tokens = chars / 4
    if tokens > 2_000_000:
        return "oversized", f"{tokens/1e6:.1f}M tokens exceeds 2M limit — skill cannot handle"
    if tokens > 800_000:
        return "large", f"{tokens/1e6:.1f}M tokens — use chunked-read with external notes"
    if tokens > 400_000:
        return "medium", f"{tokens/1e3:.0f}K tokens — single-read, warn margin"
    return "small", f"{tokens/1e3:.0f}K tokens — fits comfortably"


def measure_pdf(path: Path) -> dict:
    from pypdf import PdfReader  # type: ignore

    reader = PdfReader(str(path))
    pages = len(reader.pages)
    # Sample 5 pages evenly for char-per-page estimate (faster than full extraction)
    sample_indices = [0, pages // 4, pages // 2, 3 * pages // 4, pages - 1] if pages > 4 else list(range(pages))
    sample_chars = 0
    sample_count = 0
    for i in sample_indices:
        try:
            text = reader.pages[i].extract_text() or ""
            sample_chars += len(text)
            sample_count += 1
        except Exception:
            pass
    avg_cpp = sample_chars / max(1, sample_count)
    est_chars = int(avg_cpp * pages)
    est_tokens = int(est_chars / 4)
    klass, note = classify(est_chars, pages)
    return {
        "format": "pdf",
        "pages": pages,
        "chars": est_chars,
        "est_tokens": est_tokens,
        "chars_per_page": int(avg_cpp),
        "class": klass,
        "note": note,
        "file_size_mb": round(path.stat().st_size / (1024 * 1024), 2),
    }


def measure_text(path: Path) -> dict:
    """Plain text / markdown — straightforward."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": f"cannot read: {e}"}
    chars = len(content)
    # For text files, estimate "pages" as chars/3000 (a typical page)
    pages = max(1, chars // 3000)
    klass, note = classify(chars, pages)
    return {
        "format": path.suffix.lstrip("."),
        "pages": pages,
        "chars": chars,
        "est_tokens": chars // 4,
        "chars_per_page": chars // pages,
        "class": klass,
        "note": note,
        "file_size_mb": round(path.stat().st_size / (1024 * 1024), 2),
    }


def measure_folder(path: Path) -> dict:
    """Concatenate all .md/.txt files in folder alphabetically."""
    files = sorted([p for p in path.rglob("*") if p.suffix.lower() in (".md", ".txt")])
    if not files:
        return {"error": f"no .md or .txt files under {path}"}
    total_chars = 0
    for f in files:
        try:
            total_chars += len(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            pass
    pages = max(1, total_chars // 3000)
    klass, note = classify(total_chars, pages)
    return {
        "format": "folder",
        "files": len(files),
        "pages": pages,
        "chars": total_chars,
        "est_tokens": total_chars // 4,
        "chars_per_page": total_chars // pages,
        "class": klass,
        "note": note,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: measure.py <path-to-book>"}))
        sys.exit(1)
    path = Path(os.path.expanduser(sys.argv[1])).resolve()
    if not path.exists():
        print(json.dumps({"error": f"file not found: {path}"}))
        sys.exit(1)
    if path.is_dir():
        result = measure_folder(path)
    else:
        ext = path.suffix.lower()
        if ext == ".pdf":
            result = measure_pdf(path)
        elif ext in (".txt", ".md"):
            result = measure_text(path)
        else:
            result = {
                "format": ext.lstrip("."),
                "class": "non-pdf-needs-research",
                "note": f"Format {ext} requires agent to research and install an extractor.",
                "file_size_mb": round(path.stat().st_size / (1024 * 1024), 2),
            }
    result["path"] = str(path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
