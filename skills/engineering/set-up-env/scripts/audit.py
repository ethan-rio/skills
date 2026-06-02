#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit a repository against the AI Services / BNE Data Engineering standards.

Read-only. Makes no changes. This is the single source of truth shared by the
`set-up-env` and `check-setup-against-standards` skills — including the registry
of OPTIONAL components the agent asks the user about.

Standards derive from the team Confluence "6. Developer Guidelines" and the
`rio-tinto/dna-bne-project-template` repo. See ../STANDARDS.md for rationale.

Optional components (dev container, docker, notebooks, etc.) can be opted out per
repo. Opt-outs live in `.setup-env.toml` at the repo root and surface as SKIP —
never as a fake PASS. Core components (uv, ruff/mypy, src/tests, data policy)
cannot be skipped.

Usage:
    uv run audit.py [PATH] [--format text|json] [--quiet]
    uv run audit.py --list-components [--format text|json]

    PATH               Repo root to audit (default: current directory).
    --format           "text" (default) or "json".
    --quiet            Suppress the text summary footer.
    --list-components  Print the optional-component registry and exit. The agent
                       uses this to know what to ask the user.

Config (`.setup-env.toml` at repo root, all keys optional, default = enabled):
    [components]
    devcontainer = false
    notebooks = false

Exit codes:
    0   All active checks passed (SKIPs ignored).
    1   At least one WARN, no FAIL.
    2   At least one FAIL.
    3   Usage / runtime error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path

PASS, WARN, FAIL, SKIP = "PASS", "WARN", "FAIL", "SKIP"

CONFIG_FILENAME = ".setup-env.toml"

# --- Optional component registry (THE source of truth the agent queries) -----
# key -> (label, default-enabled, one-line description shown to the user)
COMPONENTS: dict[str, dict] = {
    "devcontainer": {
        "label": "Dev Container",
        "default": True,
        "description": ".devcontainer/devcontainer.json. Skip if you don't use dev containers.",
    },
    "docker": {
        "label": "Docker",
        "default": True,
        "description": "docker/ with Dockerfile + .dockerignore for containerisation.",
    },
    "infrastructure": {
        "label": "Infrastructure (IaC)",
        "default": True,
        "description": "infrastructure/{aws,azure,others}/ for Bicep/CloudFormation templates.",
    },
    "pipelines": {
        "label": "CI/CD pipelines",
        "default": True,
        "description": "pipelines/{aws,azure,others}/ for deployment pipelines.",
    },
    "notebooks": {
        "label": "Notebooks",
        "default": True,
        "description": "notebooks/ for Jupyter work. Also requires the nbqa tool. Skip for pure-script projects.",
    },
    "models": {
        "label": "Models",
        "default": True,
        "description": "models/ for ML model code and artifacts. Skip for non-ML projects.",
    },
    "github_pr": {
        "label": "GitHub PR template",
        "default": True,
        "description": ".github/pull_request_template.md. Skip if the repo isn't on GitHub.",
    },
}

# --- Deterministic recommendation engine ------------------------------------
# Detecting which optional components a repo "wants" is MECHANICAL, so it lives
# here (same answer every run) — not in agent-improvised `find`/`ls` calls. The
# agent presents these recommendations; the user makes the final choice.
#
# Each detector returns (recommend, reason):
#   recommend = True  -> a positive signal was found (pre-select it)
#   recommend = False -> a clear negative signal (don't pre-select)
#   recommend = None  -> no signal; fall back to the component's `default`
# "No signal" is its own category on purpose: an empty repo must yield identical,
# explainable output, never a coin-flip.

# File-extension / path globs that signal a component is in use.
SIGNAL_GLOBS = {
    "docker": ["**/Dockerfile", "**/*.dockerfile", "**/docker-compose*.y*ml"],
    "infrastructure": ["**/*.tf", "**/*.bicep", "**/*.cfn.y*ml",
                       "**/cloudformation*.y*ml", "**/template.y*ml"],
    "pipelines": ["**/azure-pipelines*.y*ml", ".github/workflows/*.y*ml",
                  "**/*.pipeline.y*ml"],
    "notebooks": ["**/*.ipynb"],
    "models": ["**/*.pt", "**/*.pkl", "**/*.h5", "**/*.onnx", "**/*.joblib",
               "**/*.safetensors"],
}


def _has_any(root: Path, globs: list[str]) -> bool:
    for pat in globs:
        for p in root.glob(pat):
            if ".git/" in str(p.relative_to(root)).replace("\\", "/") + "/":
                continue
            return True
    return False


def recommend_components(root: Path) -> dict[str, dict]:
    """Deterministically recommend include/skip per optional component."""
    disabled = load_disabled(root)
    has_git = (root / ".git").exists()
    # GitHub remote detection from .git/config (deterministic, no network).
    on_github = False
    cfg = root / ".git" / "config"
    if cfg.is_file():
        on_github = "github.com" in cfg.read_text(encoding="utf-8", errors="ignore").lower()

    out: dict[str, dict] = {}
    for key, meta in COMPONENTS.items():
        # A prior opt-out in .setup-env.toml always wins — honour the user.
        if key in disabled:
            out[key] = {"recommend": False, "reason": "previously opted out (.setup-env.toml)",
                        "signal": "config"}
            continue

        rec: bool | None = None
        reason = ""
        if key in SIGNAL_GLOBS:
            if _has_any(root, SIGNAL_GLOBS[key]):
                rec, reason = True, f"found {meta['label'].lower()} files in the repo"
            else:
                rec, reason = False, f"no {meta['label'].lower()} files detected"
        elif key == "github_pr":
            if has_git and on_github:
                rec, reason = True, "git remote is on GitHub"
            elif has_git and not on_github:
                rec, reason = False, "git remote is not GitHub"
            else:
                rec, reason = None, "no git remote yet"
        elif key == "devcontainer":
            # No reliable code signal; defer to the documented default.
            rec, reason = None, "no signal — team baseline"

        if rec is None:
            rec = meta["default"]
            reason = reason or "no signal — using default"
            signal = "default"
        else:
            signal = "detected"
        out[key] = {"recommend": rec, "reason": reason, "signal": signal}
    return out


# Core requirements (never skippable).
REQUIRED_DEV_TOOLS = ["ruff", "mypy"]  # nbqa added only if notebooks enabled.
CORE_DIRS = ["config", "data", "data/raw", "data/processed", "docs",
             "reports", "scripts", "src", "tests"]
CORE_FILES = [".gitignore", ".gitattributes", ".env.sample", "README.md",
              "SECURITY.md", "CONTRIBUTING.md", "LICENSE", "Makefile",
              "data/README.md"]
GITIGNORE_DATA_RULES = ["data/**", "!data/README.md", "!data/**/*sample*",
                        "!data/**/*mock*", "!data/**/*schema*"]


@dataclass
class Check:
    category: str
    name: str
    status: str
    detail: str
    remediation: str = ""
    component: str | None = None  # None = core; else an optional-component key.


@dataclass
class Report:
    root: str
    disabled: set[str] = field(default_factory=set)
    checks: list[Check] = field(default_factory=list)

    def add(self, category: str, name: str, status: str, detail: str,
            remediation: str = "", component: str | None = None) -> None:
        # An opted-out component's checks become SKIP, never run for real status.
        if component and component in self.disabled:
            status, detail = SKIP, "opted out (.setup-env.toml)"
            remediation = ""
        self.checks.append(Check(category, name, status, detail, remediation, component))

    @property
    def worst(self) -> str:
        live = [c.status for c in self.checks if c.status != SKIP]
        if FAIL in live:
            return FAIL
        if WARN in live:
            return WARN
        return PASS


def _read_toml(path: Path) -> dict | None:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        return None


def load_disabled(root: Path) -> set[str]:
    """Read opted-out component keys from `.setup-env.toml` (missing = none)."""
    data = _read_toml(root / CONFIG_FILENAME)
    if not data:
        return set()
    comps = data.get("components", {})
    return {k for k in COMPONENTS if comps.get(k) is False}


# --- Check groups ------------------------------------------------------------


def check_environment(root: Path, rep: Report) -> None:
    cat = "Environment"

    devc = root / ".devcontainer" / "devcontainer.json"
    if devc.is_file():
        empty = devc.stat().st_size == 0
        rep.add(cat, "Dev Container present", WARN if empty else PASS,
                ".devcontainer/devcontainer.json exists"
                + (" but is empty (placeholder)" if empty else ""),
                "Populate from rio-tinto/demo-devcontainer-analytics" if empty else "",
                component="devcontainer")
    else:
        rep.add(cat, "Dev Container present", FAIL,
                "No .devcontainer/devcontainer.json",
                "Create .devcontainer/devcontainer.json (see demo-devcontainer-analytics)",
                component="devcontainer")

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

    proj_name = data.get("project", {}).get("name", "")
    is_template = proj_name == "dna-bne-project-template"
    rep.add(cat, "Project name personalised", WARN if is_template else PASS,
            f'name = "{proj_name}"' + (" (still the template default)" if is_template else ""),
            "Rename the project in pyproject.toml to your repo" if is_template else "")

    declared = " ".join(str(v) for v in _all_dep_strings(data)).lower()
    for tool in REQUIRED_DEV_TOOLS:
        present = tool in declared
        rep.add(cat, f"{tool} declared", PASS if present else FAIL,
                f"{tool} {'found' if present else 'missing'} in dependency groups",
                "" if present else f"Add {tool} to the dev dependency group")
    # nbqa is only required when notebooks are in play.
    nbqa_present = "nbqa" in declared
    rep.add(cat, "nbqa declared", PASS if nbqa_present else FAIL,
            f"nbqa {'found' if nbqa_present else 'missing'} in dependency groups",
            "" if nbqa_present else "Add nbqa to the dev dependency group (for notebook linting)",
            component="notebooks")

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
            "" if from_banned else "Ban from-imports via [tool.ruff.lint.flake8-tidy-imports.banned-api]")

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
    # Core dirs (always required).
    for d in CORE_DIRS:
        ok = (root / d).is_dir()
        rep.add(cat, f"dir {d}/", PASS if ok else WARN, "present" if ok else "missing",
                "" if ok else f"Create {d}/ (add .gitkeep if empty)")
    # Optional dirs, each tied to a component.
    optional_dirs = {
        "docker": ["docker"],
        "infrastructure": ["infrastructure"],
        "pipelines": ["pipelines"],
        "notebooks": ["notebooks"],
        "models": ["models"],
    }
    for comp, dirs in optional_dirs.items():
        for d in dirs:
            ok = (root / d).is_dir()
            rep.add(cat, f"dir {d}/", PASS if ok else WARN, "present" if ok else "missing",
                    "" if ok else f"Create {d}/ (add .gitkeep if empty)", component=comp)

    for f in CORE_FILES:
        ok = (root / f).is_file()
        rep.add(cat, f"file {f}", PASS if ok else WARN, "present" if ok else "missing",
                "" if ok else f"Add {f} from dna-bne-project-template")
    pr = ".github/pull_request_template.md"
    ok = (root / pr).is_file()
    rep.add(cat, f"file {pr}", PASS if ok else WARN, "present" if ok else "missing",
            "" if ok else f"Add {pr} from dna-bne-project-template", component="github_pr")

    data_dir = root / "data"
    if data_dir.is_dir():
        has_sample = any(re.search(r"(sample|mock|schema)", p.name, re.I)
                         for p in data_dir.rglob("*") if p.is_file())
        rep.add(cat, "data sample/mock/schema file", PASS if has_sample else WARN,
                "found" if has_sample else "none found under data/",
                "" if has_sample else "Add e.g. data/raw/raw-sample.csv")


def check_gitignore(root: Path, rep: Report) -> None:
    cat = "Git hygiene"
    gi = root / ".gitignore"
    if not gi.is_file():
        rep.add(cat, ".gitignore data policy", FAIL, "No .gitignore",
                "Add .gitignore with the data/** policy block")
    else:
        text = gi.read_text(encoding="utf-8", errors="ignore")
        missing = [r for r in GITIGNORE_DATA_RULES if r not in text]
        rep.add(cat, ".gitignore data policy", PASS if not missing else WARN,
                "all data rules present" if not missing else f"missing rules: {', '.join(missing)}",
                "" if not missing else "Add the data/** ignore block from the template")

    git_dir = root / ".git"
    rep.add(cat, "Is a git repository", PASS if git_dir.exists() else WARN,
            "yes" if git_dir.exists() else "no .git directory",
            "" if git_dir.exists() else "Run `git init` and set up a remote")


def check_docs_consistency(root: Path, rep: Report) -> None:
    """Surface doc drift for the agent's sanitisation step (detect, don't fix).

    If a component was opted out but the README still documents its directory,
    flag it. The fix (pruning the tree, rewording prose) is the agent's
    sanitisation job — judgment-laden, so not automated here. This check is the
    deterministic backstop that verifies the agent actually did it.
    """
    cat = "Docs consistency"
    readme = root / "README.md"
    if not rep.disabled or not readme.is_file():
        return
    text = readme.read_text(encoding="utf-8", errors="ignore").lower()
    # Directory token each optional component owns (mirrors the scaffold).
    comp_dir = {"devcontainer": ".devcontainer", "docker": "docker",
                "infrastructure": "infrastructure", "pipelines": "pipelines",
                "notebooks": "notebooks", "models": "models", "github_pr": ".github"}
    stale = sorted(d for k in rep.disabled
                   if (d := comp_dir.get(k)) and re.search(rf"(^|\W){re.escape(d)}/", text, re.M))
    rep.add(cat, "README matches selected components", PASS if not stale else WARN,
            "no opted-out components referenced" if not stale
            else f"README still references opted-out: {', '.join(stale)}",
            "" if not stale else "Sanitise README: remove/reword the opted-out entries")


CHECK_GROUPS = [check_environment, check_tooling, check_structure,
                check_gitignore, check_docs_consistency]


def build_report(root: Path) -> Report:
    rep = Report(root=str(root), disabled=load_disabled(root))
    for group in CHECK_GROUPS:
        group(root, rep)
    return rep


# --- Rendering ---------------------------------------------------------------


def render_text(rep: Report, quiet: bool) -> str:
    icons = {PASS: "✓", WARN: "▲", FAIL: "✗", SKIP: "·"}
    lines = [f"Auditing: {rep.root}"]
    if rep.disabled:
        lines.append(f"Opted out: {', '.join(sorted(rep.disabled))}")
    lines.append("")
    current = None
    for c in rep.checks:
        if c.category != current:
            lines.append(f"  {c.category}")
            current = c.category
        lines.append(f"    {icons[c.status]} {c.name}: {c.detail}")
        if c.status in (WARN, FAIL) and c.remediation:
            lines.append(f"        → {c.remediation}")
    if not quiet:
        n = {s: sum(1 for c in rep.checks if c.status == s) for s in (PASS, WARN, FAIL, SKIP)}
        lines += ["", f"Summary: {n[PASS]} pass, {n[WARN]} warn, {n[FAIL]} fail, "
                  f"{n[SKIP]} skipped → {rep.worst}"]
    return "\n".join(lines)


def list_components(fmt: str) -> str:
    if fmt == "json":
        return json.dumps({"components": COMPONENTS}, indent=2)
    rows = ["Optional components (the agent should ask the user about these):", ""]
    for key, meta in COMPONENTS.items():
        default = "on" if meta["default"] else "off"
        rows.append(f"  {key}  [{default} by default]  — {meta['label']}")
        rows.append(f"      {meta['description']}")
    rows += ["", "Core (never optional): uv + pyproject + uv.lock, ruff + mypy,",
             "  src/ tests/ docs/ config/ scripts/ data/, data .gitignore policy,",
             "  README/SECURITY/CONTRIBUTING/LICENSE/Makefile/.env.sample."]
    return "\n".join(rows)


def render_recommendations(root: Path, fmt: str) -> str:
    recs = recommend_components(root)
    if fmt == "json":
        return json.dumps(
            {"root": str(root),
             "recommendations": {
                 k: {**recs[k], "label": COMPONENTS[k]["label"],
                     "description": COMPONENTS[k]["description"]}
                 for k in COMPONENTS}}, indent=2)
    rows = [f"Recommended components for: {root}",
            "(deterministic from repo signals; the user decides)", ""]
    for key, meta in COMPONENTS.items():
        r = recs[key]
        mark = "include" if r["recommend"] else "skip   "
        tag = "" if r["signal"] == "detected" else f"  [{r['signal']}]"
        rows.append(f"  {mark}  {meta['label']}{tag} — {r['reason']}")
    return "\n".join(rows)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Audit a repo against team standards.")
    ap.add_argument("path", nargs="?", default=".", help="Repo root (default: .)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--list-components", action="store_true",
                    help="Print the optional-component registry and exit.")
    ap.add_argument("--recommend", action="store_true",
                    help="Deterministically recommend components from repo signals and exit.")
    args = ap.parse_args(argv)

    if args.list_components:
        print(list_components(args.format))
        return 0

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 3

    if args.recommend:
        print(render_recommendations(root, args.format))
        return 0

    rep = build_report(root)

    if args.format == "json":
        print(json.dumps(
            {"root": rep.root, "result": rep.worst,
             "disabled": sorted(rep.disabled),
             "checks": [asdict(c) for c in rep.checks]}, indent=2))
    else:
        print(render_text(rep, args.quiet))

    return {PASS: 0, WARN: 1, FAIL: 2}[rep.worst]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
