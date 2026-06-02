#!/usr/bin/env bash
# Scaffold a repository to the AI Services / BNE Data Engineering standards.
#
# Idempotent and non-destructive: it only CREATES things that are missing and
# never overwrites an existing file. Safe to re-run. Agent-safe: no interactive
# prompts, all input via flags.
#
# Happy path clones rio-tinto/dna-bne-project-template and copies its missing
# pieces in. If that repo is unreachable, falls back to creating the directory
# skeleton + .gitkeep files from scratch (--no-clone forces this).
#
# Usage:
#   scaffold.sh [--target DIR] [--dry-run] [--no-clone] [--help]
#
#   --target DIR   Repo root to scaffold (default: current directory).
#   --dry-run      Print actions without making changes.
#   --no-clone     Skip cloning the template; build skeleton from scratch.
#   --help         Show this message.
#
# Exit codes:
#   0  Success (changes made, or nothing to do).
#   2  A required action failed.
#   3  Usage error.
set -euo pipefail

TARGET="."
DRY_RUN=0
NO_CLONE=0
TEMPLATE_REPO="https://github.com/rio-tinto/dna-bne-project-template.git"

REQUIRED_DIRS=(config data data/raw data/processed docker docs \
  infrastructure infrastructure/aws infrastructure/azure infrastructure/others \
  models notebooks pipelines pipelines/aws pipelines/azure pipelines/others \
  reports reports/figures scripts src src/app_config tests \
  .devcontainer .github)

usage() { sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; }

log()  { printf '%s\n' "$*"; }
act()  { if [[ $DRY_RUN -eq 1 ]]; then log "[dry-run] $*"; else log "  + $*"; fi; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:?--target needs a value}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --no-clone) NO_CLONE=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 3 ;;
  esac
done

[[ -d "$TARGET" ]] || { echo "error: not a directory: $TARGET" >&2; exit 3; }
TARGET="$(cd "$TARGET" && pwd)"
log "Scaffolding: $TARGET"
[[ $DRY_RUN -eq 1 ]] && log "(dry-run: no changes will be written)"

# mkdir -p the dir if missing, drop a .gitkeep when it ends up empty.
ensure_dir() {
  local d="$TARGET/$1"
  if [[ ! -d "$d" ]]; then
    act "mkdir $1/"
    [[ $DRY_RUN -eq 0 ]] && mkdir -p "$d"
  fi
  if [[ $DRY_RUN -eq 0 && -d "$d" && -z "$(ls -A "$d" 2>/dev/null)" ]]; then
    touch "$d/.gitkeep"
  fi
}

# Copy SRC->DEST only if DEST is missing. Never overwrite.
copy_missing() {
  local src="$1" rel="$2" dest="$TARGET/$2"
  [[ -e "$dest" ]] && return 0
  [[ -e "$src" ]] || return 0
  act "add $rel (from template)"
  if [[ $DRY_RUN -eq 0 ]]; then
    mkdir -p "$(dirname "$dest")"
    cp -R "$src" "$dest"
  fi
}

# 1. Directory skeleton (always, cheap, idempotent).
for d in "${REQUIRED_DIRS[@]}"; do ensure_dir "$d"; done

# 2. Files: prefer the template, fall back to minimal stubs.
TMP=""
cleanup() { [[ -n "$TMP" && -d "$TMP" ]] && rm -rf "$TMP"; }
trap cleanup EXIT

CLONED=0
if [[ $NO_CLONE -eq 0 ]]; then
  TMP="$(mktemp -d)"
  if git clone --depth 1 "$TEMPLATE_REPO" "$TMP/tmpl" >/dev/null 2>&1; then
    CLONED=1
    log "Template cloned; copying any missing files."
  else
    log "Template unreachable; falling back to from-scratch stubs."
  fi
fi

TEMPLATE_FILES=(
  .gitignore .gitattributes .env.sample README.md SECURITY.md
  CONTRIBUTING.md LICENSE Makefile pyproject.toml uv.lock
  data/README.md docker/Dockerfile docker/.dockerignore
  .devcontainer/devcontainer.json .github/pull_request_template.md
  docs/CODE_QUALITY_SETUP_GUIDE.md scripts/code_quality_notebook_analyser.py
)

if [[ $CLONED -eq 1 ]]; then
  for f in "${TEMPLATE_FILES[@]}"; do copy_missing "$TMP/tmpl/$f" "$f"; done
else
  # From-scratch minimal stubs so an audit's hard FAILs become satisfiable.
  stub() {
    local rel="$1" body="$2" dest="$TARGET/$1"
    [[ -e "$dest" ]] && return 0
    act "add $rel (stub)"
    if [[ $DRY_RUN -eq 0 ]]; then
      mkdir -p "$(dirname "$dest")"
      printf '%s\n' "$body" > "$dest"
    fi
  }
  stub README.md "# Project"
  stub SECURITY.md "# Security Policy"
  stub CONTRIBUTING.md "# Contributing"
  stub .env.sample ""
  stub .gitattributes ""
  stub data/README.md "# Data\nDocument data source, owner, and storage here."
  stub data/raw/raw-sample.csv "id,value"
  stub .devcontainer/devcontainer.json ""
  stub .gitignore "$(printf 'data/**\n!data/README.md\n!data/raw/\n!data/processed/\n!data/**/*sample*\n!data/**/*mock*\n!data/**/*schema*\n.venv\n__pycache__/\n.ruff_cache/\n.mypy_cache/\n.ipynb_checkpoints\n')"
  log "NOTE: from-scratch stubs are minimal. Adopt the real template files"
  log "      (pyproject.toml, Makefile, uv.lock, PR template) when reachable."
fi

log "Done. Run the audit to confirm: uv run scripts/audit.py \"$TARGET\""
exit 0
