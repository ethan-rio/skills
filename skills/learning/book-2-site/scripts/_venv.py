"""Bootstrap a .venv in the current working directory for skill scripts.

Call `ensure_venv()` at the very top of any script that needs third-party
packages. If the current interpreter is not `./.venv/bin/python`, this
function creates the venv (if missing), ensures `./requirements.txt` exists,
installs it, and re-execs the caller using the venv python.

Design:
- venv lives at <cwd>/.venv.
- requirements.txt lives at <cwd>/requirements.txt; created with sensible
  defaults if missing (pypdf, pymupdf). If it already exists, it is left
  alone — but any missing book-2-site deps are appended.
- Uses only stdlib so it can run on any python3.
"""
from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path

CWD = Path.cwd()
VENV_DIR = CWD / ".venv"
REQ_FILE = CWD / "requirements.txt"
REQUIRED_PKGS = ["pypdf", "pymupdf"]


def _venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _stamp() -> Path:
    return VENV_DIR / ".requirements.stamp"


def _reqs_hash() -> str:
    if not REQ_FILE.exists():
        return ""
    return str(REQ_FILE.stat().st_mtime_ns)


def ensure_venv() -> None:
    """Ensure we're running inside the skill venv with requirements installed.

    Re-execs the current script with the venv python if not already. No-op
    if already inside the venv and requirements are up to date.
    """
    vpy = _venv_python()
    running_in_venv = Path(sys.executable).resolve() == vpy.resolve() if vpy.exists() else False

    if not vpy.exists():
        print(f"[book-2-site] Creating venv at {VENV_DIR}", file=sys.stderr)
        venv.EnvBuilder(with_pip=True, clear=False, upgrade_deps=False).create(str(VENV_DIR))

    if REQ_FILE.exists():
        existing = REQ_FILE.read_text(encoding="utf-8")
        existing_names = {
            line.strip().split("=")[0].split(">")[0].split("<")[0].split("[")[0].lower()
            for line in existing.splitlines()
            if line.strip() and not line.strip().startswith("#")
        }
        additions = [p for p in REQUIRED_PKGS if p.lower() not in existing_names]
        if additions:
            with REQ_FILE.open("a", encoding="utf-8") as f:
                if not existing.endswith("\n"):
                    f.write("\n")
                for pkg in additions:
                    f.write(f"{pkg}\n")
    else:
        REQ_FILE.write_text("pypdf>=4.0\npymupdf>=1.24\n", encoding="utf-8")

    stamp = _stamp()
    current = _reqs_hash()
    needs_install = not stamp.exists() or stamp.read_text().strip() != current
    if needs_install:
        print(f"[book-2-site] Installing {REQ_FILE.name}", file=sys.stderr)
        subprocess.check_call(
            [str(vpy), "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
             "-r", str(REQ_FILE)],
        )
        stamp.write_text(current, encoding="utf-8")

    if not running_in_venv:
        os.execv(str(vpy), [str(vpy), *sys.argv])
