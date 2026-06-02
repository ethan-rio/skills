#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit a repository against the AI Services / BNE Data Engineering standards.

Read-only. Makes no changes. This is the single source of truth shared by the
`set-up-env` and `check-setup-against-standards` skills.

Standards are derived from the team Confluence "6. Developer Guidelines" and the
`rio-tinto/dna-bne-project-template` repository. See ../STANDARDS.md for the
human-readable rationale and Confluence links.

Usage:
    uv run audit.py [PATH] [--format text|json] [--quiet]

    PATH         Repository root to audit (default: current directory).
    --format     Output format. "text" (default, human table) or "json".
    --quiet      Suppress the text summary footer (text format only).

Exit codes:
    0   All checks passed (no FAIL, no WARN).
    1   At least one WARN, but no FAIL.
    2   At least one FAIL (a hard standard is unmet).
    3   Usage / runtime error (bad path, bad args).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Severity ordering for exit-code resolution.
PASS, WARN, FAIL = "PASS", "WARN", "FAIL"

# Required top-level directories (from "How to Structure Your Repository").
REQUIRED_DIRS = [
    "config", "data", "data/raw", "data/processed", "docker", "docs",
    "infrastructure", "models", "notebooks", "pipelines", "reports",
    "scripts", "src", "tests",
]

# Required top-level files.
REQUIRED_FILES = [
    ".gitignore", ".gitattributes", ".env.sample", "README.md", "SECURITY.md",
    "CONTRIBUTING.md", "LICENSE", "Makefile", "data/README.md",
    ".github/pull_request_template.md",
]

# Dev tooling that must be declared as dependencies (code-quality standard).
REQUIRED_DEV_TOOLS = ["ruff", "mypy", "nbqa"]

# Lines the .gitignore must contain for the data-directory policy.
GITIGNORE_DATA_RULES = [
    "data/**",
    "!data/README.md",
    "!data/**/*sample*",
    "!data/**/*mock*",
    "!data/**/*schema*",
]


@dataclass
class Check:
    """One audited standard."""

    category: str
    name: str
    status: str  # PASS | WARN | FAIL
    detail: str
    remediation: str = ""


@dataclass
class Report:
    root: str
    checks: list[Check] = field(default_factory=list)

    def add(self, *args, **kwargs) -> None:
        self.checks.append(Check(*args, **kwargs))

    @property
    def worst(self) -> str:
        if any(c.status == FAIL for c in self.checks):
            return FAIL
        if any(c.status == WARN for c in self.checks):
            return WARN
        return PASS


def _read_toml(path: Path) -> dict | None:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        return None


# --- Individual check groups -------------------------------------------------


def check_environment(root: Path, rep: Report) -> None:
    cat = "Environment"

    devc = root / ".devcontainer" / "devcontainer.json"
    if devc.is_file():
        # The template ships an empty placeholder; presence is the standard,
        # content is filled from demo-devcontainer-analytics.
        empty = devc.stat().st_size == 0
        rep.add(cat, "Dev Container present", WARN if empty else PASS,
                ".devcontainer/devcontainer.json exists"
                + (" but is empty (placeholder)" if empty else ""),
                "Populate from rio-tinto/demo-devcontainer-analytics" if empty else "")
    else:
        rep.add(cat, "Dev Container present", FAIL,
                "No .devcontainer/devcontainer.json",
                "Create .devcontainer/devcontainer.json (see demo-devcontainer-analytics)")

    pyproject = root / "pyproject.toml"
    reqs = root / "requirements.txt"
    if pyproject.is_file():
        rep.add(cat, "Dependency manifest", PASS, "pyproject.toml present")
    elif reqs.is_file():
        pinned = _requirements_pinned(reqs)
        rep.add(cat, "Dependency manifest", PASS if pinned else FAIL,
                "requirements.txt present" + ("" if pinned else " with unpinned packages"),
                "" if pinned else "Pin every package (e.g. package==1.2.3)")
    else:
        rep.add(cat, "Dependency manifest", FAIL, "No pyproject.toml or requirements.txt",
                "Add pyproject.toml (preferred) defining dependencies")

    lock = root / "uv.lock"
    rep.add(cat, "uv lockfile committed", PASS if lock.is_file() else FAIL,
            "uv.lock present" if lock.is_file() else "No uv.lock",
            "" if lock.is_file() else "Run `uv sync` and commit the generated uv.lock")


def _requirements_pinned(path: Path) -> bool:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    for raw in lines:
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        if "==" not in line:
            return False
    return True


def check_tooling(root: Path, rep: Report) -> None:
    cat = "Tooling"
    data = _read_toml(root / "pyproject.toml")
    if data is None:
        rep.add(cat, "Code-quality config", FAIL, "No readable pyproject.toml",
                "Adopt pyproject.toml from dna-bne-project-template")
        return

    # Dev dependency groups can live in [dependency-groups] or [tool.uv].
    declared = " ".join(str(v) for v in _all_dep_strings(data)).lower()
    for tool in REQUIRED_DEV_TOOLS:
        present = tool in declared
        rep.add(cat, f"{tool} declared", PASS if present else FAIL,
                f"{tool} {'found' if present else 'missing'} in dependency groups",
                "" if present else f"Add {tool} to the dev dependency group")

    ruff = data.get("tool", {}).get("ruff", {})
    line_len = ruff.get("line-length")
    rep.add(cat, "Ruff line-length = 100", PASS if line_len == 100 else WARN,
            f"line-length = {line_len!r}",
            "Set [tool.ruff] line-length = 100" if line_len != 100 else "")

    banned = (ruff.get("lint", {}).get("flake8-tidy-imports", {})
              .get("banned-api", {}))
    from_banned = "from" in banned
    rep.add(cat, "Absolute imports enforced", PASS if from_banned else WARN,
            "from-imports banned" if from_banned else "from-imports not banned",
            "" if from_banned else 'Ban from-imports via [tool.ruff.lint.flake8-tidy-imports.banned-api]')

    mk = root / "Makefile"
    has_cq = mk.is_file() and "check_code_quality" in mk.read_text(encoding="utf-8", errors="ignore")
    rep.add(cat, "Makefile code-quality target", PASS if has_cq else WARN,
            "check_code_quality target found" if has_cq else "No check_code_quality target",
            "" if has_cq else "Copy the Makefile from dna-bne-project-template")


def _all_dep_strings(data: dict) -> list[str]:
    out: list[str] = []
    out += data.get("project", {}).get("dependencies", []) or []
    for group in (data.get("dependency-groups", {}) or {}).values():
        if isinstance(group, list):
            out += [g for g in group if isinstance(g, str)]
    uv = data.get("tool", {}).get("uv", {})
    out += uv.get("dev-dependencies", []) or []
    return out


def check_structure(root: Path, rep: Report) -> None:
    cat = "Structure"
    for d in REQUIRED_DIRS:
        ok = (root / d).is_dir()
        rep.add(cat, f"dir {d}/", PASS if ok else WARN,
                "present" if ok else "missing",
                "" if ok else f"Create {d}/ (add .gitkeep if empty)")
    for f in REQUIRED_FILES:
        ok = (root / f).is_file()
        sev = PASS if ok else WARN
        rep.add(cat, f"file {f}", sev, "present" if ok else "missing",
                "" if ok else f"Add {f} from dna-bne-project-template")

    # At least one sample/mock/schema file under data/.
    data_dir = root / "data"
    if data_dir.is_dir():
        has_sample = any(
            re.search(r"(sample|mock|schema)", p.name, re.I)
            for p in data_dir.rglob("*") if p.is_file()
        )
        rep.add(cat, "data sample/mock/schema file", PASS if has_sample else WARN,
                "found" if has_sample else "none found under data/",
                "" if has_sample else "Add e.g. data/raw/raw-sample.csv")


def check_gitignore(root: Path, rep: Report) -> None:
    cat = "Git hygiene"
    gi = root / ".gitignore"
    if not gi.is_file():
        rep.add(cat, ".gitignore data policy", FAIL, "No .gitignore",
                "Add .gitignore with the data/** policy block")
        return
    text = gi.read_text(encoding="utf-8", errors="ignore")
    missing = [r for r in GITIGNORE_DATA_RULES if r not in text]
    rep.add(cat, ".gitignore data policy", PASS if not missing else WARN,
            "all data rules present" if not missing else f"missing rules: {', '.join(missing)}",
            "" if not missing else "Add the data/** ignore block from the template")

    git_dir = root / ".git"
    rep.add(cat, "Is a git repository", PASS if git_dir.exists() else WARN,
            "yes" if git_dir.exists() else "no .git directory",
            "" if git_dir.exists() else "Run `git init` and set up a remote")


CHECK_GROUPS = [check_environment, check_tooling, check_structure, check_gitignore]


def build_report(root: Path) -> Report:
    rep = Report(root=str(root))
    for group in CHECK_GROUPS:
        group(root, rep)
    return rep


# --- Rendering ---------------------------------------------------------------


def render_text(rep: Report, quiet: bool) -> str:
    icons = {PASS: "✓", WARN: "▲", FAIL: "✗"}
    lines: list[str] = [f"Auditing: {rep.root}", ""]
    current = None
    for c in rep.checks:
        if c.category != current:
            lines.append(f"  {c.category}")
            current = c.category
        line = f"    {icons[c.status]} {c.name}: {c.detail}"
        lines.append(line)
        if c.status != PASS and c.remediation:
            lines.append(f"        → {c.remediation}")
    if not quiet:
        n = {s: sum(1 for c in rep.checks if c.status == s) for s in (PASS, WARN, FAIL)}
        lines += ["", f"Summary: {n[PASS]} pass, {n[WARN]} warn, {n[FAIL]} fail "
                  f"→ {rep.worst}"]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Audit a repo against team standards.")
    ap.add_argument("path", nargs="?", default=".", help="Repo root (default: .)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 3

    rep = build_report(root)

    if args.format == "json":
        print(json.dumps(
            {"root": rep.root, "result": rep.worst,
             "checks": [asdict(c) for c in rep.checks]},
            indent=2))
    else:
        print(render_text(rep, args.quiet))

    return {PASS: 0, WARN: 1, FAIL: 2}[rep.worst]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
