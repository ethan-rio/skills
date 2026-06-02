#!/usr/bin/env bash
# Scaffold a repository to the AI Services / BNE Data Engineering standards.
#
# Idempotent and non-destructive: only CREATES missing things, never overwrites.
# Safe to re-run. Agent-safe: no interactive prompts, all input via flags.
#
# Optional components can be skipped with repeated --skip flags. Skipped
# components are recorded in .setup-env.toml so later audits report them as
# SKIP (opted out) rather than as discrepancies. Valid keys (see audit.py
# --list-components): devcontainer docker infrastructure pipelines notebooks
# models github_pr
#
# Happy path clones rio-tinto/dna-bne-project-template and copies missing pieces.
# If unreachable (or --no-clone), builds the skeleton from scratch.
#
# Usage:
#   scaffold.sh [--target DIR] [--skip KEY]... [--dry-run] [--no-clone] [--help]
#
#   --target DIR   Repo root to scaffold (default: current directory).
#   --skip KEY     Opt out of an optional component (repeatable).
#   --dry-run      Print actions without making changes.
#   --no-clone     Skip cloning the template; build skeleton from scratch.
#   --help         Show this message.
#
# Exit codes: 0 success · 2 action failed · 3 usage error.
set -euo pipefail

TARGET="."
DRY_RUN=0
NO_CLONE=0
SKIP=()
TEMPLATE_REPO="https://github.com/rio-tinto/dna-bne-project-template.git"
VALID_KEYS=(devcontainer docker infrastructure pipelines notebooks models github_pr)

usage() { sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; }
log()  { printf '%s\n' "$*"; }
act()  { if [[ $DRY_RUN -eq 1 ]]; then log "[dry-run] $*"; else log "  + $*"; fi; }
has_skip() { local k; for k in "${SKIP[@]:-}"; do [[ "$k" == "$1" ]] && return 0; done; return 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:?--target needs a value}"; shift 2 ;;
    --skip)   SKIP+=("${2:?--skip needs a key}"); shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --no-clone) NO_CLONE=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 3 ;;
  esac
done

# Validate skip keys against the known registry.
for k in "${SKIP[@]:-}"; do
  [[ -z "$k" ]] && continue
  ok=0; for v in "${VALID_KEYS[@]}"; do [[ "$v" == "$k" ]] && ok=1; done
  [[ $ok -eq 1 ]] || { echo "error: unknown --skip key: $k (valid: ${VALID_KEYS[*]})" >&2; exit 3; }
done

[[ -d "$TARGET" ]] || { echo "error: not a directory: $TARGET" >&2; exit 3; }
TARGET="$(cd "$TARGET" && pwd)"
log "Scaffolding: $TARGET"
[[ ${#SKIP[@]} -gt 0 ]] && log "Opting out: ${SKIP[*]}"
[[ $DRY_RUN -eq 1 ]] && log "(dry-run: no changes will be written)"

# Core dirs always created; optional dirs gated by their component key.
CORE_DIRS=(config data data/raw data/processed docs reports scripts src src/app_config tests)
declare -A OPTIONAL_DIRS=(
  [docker]="docker"
  [infrastructure]="infrastructure infrastructure/aws infrastructure/azure infrastructure/others"
  [pipelines]="pipelines pipelines/aws pipelines/azure pipelines/others"
  [notebooks]="notebooks"
  [models]="models"
  [devcontainer]=".devcontainer"
  [github_pr]=".github"
)

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

# 1. Directories.
for d in "${CORE_DIRS[@]}"; do ensure_dir "$d"; done
for key in "${!OPTIONAL_DIRS[@]}"; do
  has_skip "$key" && continue
  for d in ${OPTIONAL_DIRS[$key]}; do ensure_dir "$d"; done
done

# 2. Files from template (or stubs).
TMP=""
cleanup() { [[ -n "$TMP" && -d "$TMP" ]] && rm -rf "$TMP"; }
trap cleanup EXIT

CLONED=0
if [[ $NO_CLONE -eq 0 ]]; then
  TMP="$(mktemp -d)"
  if git clone --depth 1 "$TEMPLATE_REPO" "$TMP/tmpl" >/dev/null 2>&1; then
    CLONED=1; log "Template cloned; copying any missing files."
  else
    log "Template unreachable; falling back to from-scratch stubs."
  fi
fi

# Core files (always) and optional files (gated).
CORE_FILES=(.gitignore .gitattributes .env.sample README.md SECURITY.md
  CONTRIBUTING.md LICENSE Makefile pyproject.toml uv.lock data/README.md
  docs/CODE_QUALITY_SETUP_GUIDE.md scripts/code_quality_notebook_analyser.py)
declare -A OPTIONAL_FILES=(
  [docker]="docker/Dockerfile docker/.dockerignore"
  [devcontainer]=".devcontainer/devcontainer.json"
  [github_pr]=".github/pull_request_template.md"
)

if [[ $CLONED -eq 1 ]]; then
  for f in "${CORE_FILES[@]}"; do copy_missing "$TMP/tmpl/$f" "$f"; done
  for key in "${!OPTIONAL_FILES[@]}"; do
    has_skip "$key" && continue
    for f in ${OPTIONAL_FILES[$key]}; do copy_missing "$TMP/tmpl/$f" "$f"; done
  done
else
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
  stub .gitignore "$(printf 'data/**\n!data/README.md\n!data/raw/\n!data/processed/\n!data/**/*sample*\n!data/**/*mock*\n!data/**/*schema*\n.venv\n__pycache__/\n.ruff_cache/\n.mypy_cache/\n.ipynb_checkpoints\n')"
  has_skip devcontainer || stub .devcontainer/devcontainer.json ""
  log "NOTE: from-scratch stubs are minimal. Adopt the real template files"
  log "      (pyproject.toml, Makefile, uv.lock, PR template) when reachable."
fi

# 3. Personalise the project name (the template ships name = "dna-bne-project-template").
#    Idempotent: only rewrites while the name is still the template default, so a
#    user's real name is never clobbered on re-run.
PYPROJECT="$TARGET/pyproject.toml"
if [[ -f "$PYPROJECT" ]] && grep -q '^name = "dna-bne-project-template"' "$PYPROJECT"; then
  # Derive a PEP 503-ish name from the target directory: lowercase, non-alnum → '-'.
  proj="$(basename "$TARGET" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
  [[ -z "$proj" ]] && proj="project"
  act "set pyproject.toml name = \"$proj\" (was template default)"
  if [[ $DRY_RUN -eq 0 ]]; then
    sed -i "s/^name = \"dna-bne-project-template\"/name = \"$proj\"/" "$PYPROJECT"
  fi
fi

# 4. Record opt-outs so future audits honour them.
if [[ ${#SKIP[@]} -gt 0 ]]; then
  conf="$TARGET/.setup-env.toml"
  act "write .setup-env.toml (opt-outs)"
  if [[ $DRY_RUN -eq 0 ]]; then
    {
      echo "# Component selections for the set-up-env / check-setup-against-standards skills."
      echo "# false = opted out (audit reports SKIP instead of a discrepancy)."
      echo "[components]"
      for k in "${SKIP[@]}"; do echo "$k = false"; done
    } > "$conf"
  fi
fi

log "Done. Run the audit to confirm: uv run scripts/audit.py \"$TARGET\""
exit 0
