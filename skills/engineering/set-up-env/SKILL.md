---
name: set-up-env
description: Set up or scaffold a repository to the AI Services / BNE Data Engineering standards — dev container, uv + uv.lock, ruff/mypy/nbqa code-quality config, the required folder structure, data-directory .gitignore policy, and PR template. Use when the user runs /set-up-env, starts a new Rio data/AI project, onboards an existing repo to team standards, or asks to "set up the environment" / "scaffold this repo" / "make this repo compliant".
disable-model-invocation: true
allowed-tools: Bash(uv run*), Bash(bash*), Bash(git clone*), Bash(git init*), Read, Edit, Write
---

# set-up-env

Brings a repository into line with the team's **Developer Guidelines** (see
[STANDARDS.md](STANDARDS.md)). This skill **mutates the repo**, so it only runs
when the user invokes it explicitly, and it **always audits and shows a plan
before writing anything**.

The standard is encoded in `scripts/audit.py` (the same checker the
`check-setup-against-standards` skill uses) and applied by `scripts/scaffold.sh`.

## Workflow

1. **Confirm the target.** Default to the current working directory. If the user
   named a path, use it. State which repo you're about to modify.

2. **Audit current state** (read-only):
   ```bash
   uv run scripts/audit.py <target> --format json
   ```
   Parse the JSON. Note every `FAIL` and `WARN`.

3. **Preview the changes** with a dry run:
   ```bash
   bash scripts/scaffold.sh --target <target> --dry-run
   ```

4. **Show the plan and get explicit confirmation.** Summarise what will be
   created (dirs, files, where they come from — template clone vs. stubs) and
   what the audit can't fix automatically (e.g. you must populate the empty
   `devcontainer.json` from `demo-devcontainer-analytics`). **Wait for the user
   to say go.** Do not write before confirmation.

5. **Apply** (only after confirmation):
   ```bash
   bash scripts/scaffold.sh --target <target>
   ```
   The script is idempotent and never overwrites existing files. If the team
   template repo is unreachable, add `--no-clone` to build a minimal skeleton.

6. **Verify and report.** Re-run the audit:
   ```bash
   uv run scripts/audit.py <target>
   ```
   Show the before/after delta. List remaining `WARN`/`FAIL` items the user must
   handle manually (devcontainer content, real `pyproject.toml`/`Makefile`/`uv.lock`
   if stubs were used, LICENSE choice, README content).

## Rules

- **Never overwrite.** The scaffold only fills gaps. If a file exists, leave it.
- **Never invent compliance.** If a stub can't satisfy a hard rule (e.g. no real
  `pyproject.toml` without the template), say so plainly — don't fake a PASS.
- **Confirmation is mandatory** before step 5. This skill is opt-in by design.
- Run scripts from this skill's directory so relative paths resolve. The scripts
  use `uv run` (PEP 723 inline metadata) — no separate install needed.

## What's out of scope

Process standards (PR approval flow, code-review checklist, unit/integration-test
coverage targets) are **not** auto-applied — they live in review, not in files.
Surface them as guidance only. See [STANDARDS.md](STANDARDS.md) §5.
