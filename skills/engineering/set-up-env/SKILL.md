---
name: set-up-env
description: Set up or scaffold a repository to the AI Services / BNE Data Engineering standards — uv + uv.lock, ruff/mypy code-quality config, folder structure, data-directory .gitignore policy, and optional components (dev container, docker, notebooks, infrastructure, CI/CD, models, PR template) that the agent asks the user about. Use when the user runs /set-up-env, starts a new Rio data/AI project, onboards an existing repo to team standards, or asks to "set up the environment" / "scaffold this repo" / "make this repo compliant".
disable-model-invocation: true
allowed-tools: Bash(uv run*), Bash(bash*), Bash(git clone*), Bash(git init*), Read, Edit, Write
---

# set-up-env

Brings a repository into line with the team's **Developer Guidelines** (see
[STANDARDS.md](STANDARDS.md)). This skill **mutates the repo**, so it only runs
when the user invokes it explicitly, **adapts to which components the user wants**,
and **always shows a plan before writing anything**.

The standard — including which components are optional — is encoded in
`scripts/audit.py` (the same checker `check-setup-against-standards` uses) and
applied by `scripts/scaffold.sh`. Don't hardcode the component list from this
prose; query the script so the skill stays the source of truth.

## Workflow

1. **Confirm the target.** Default to the current working directory. If the user
   named a path, use it. State which repo you're about to modify.

2. **Audit current state** (read-only):
   ```bash
   uv run scripts/audit.py <target> --format json
   ```
   Parse the JSON. Note every `FAIL` and `WARN`, and any existing `disabled`
   components (a prior `.setup-env.toml`) — default the checklist to those.

3. **Get the deterministic component recommendation.** Do **not** hand-roll
   `find`/`ls` scans to guess which components apply — that drifts run to run.
   The script does the detection mechanically and reproducibly:
   ```bash
   uv run scripts/audit.py <target> --recommend --format json
   ```
   For each optional component this returns `recommend` (true/false), a `reason`,
   and a `signal` (`detected` = found real files / git remote; `default` = no
   signal, fell back to the team baseline; `config` = honouring a prior
   `.setup-env.toml`). **Core** items (uv, ruff/mypy, src/tests, data policy) are
   never optional — don't offer to skip them.

4. **Ask the user, adaptively.** Present the optional components as
   `AskUserQuestion` **multi-select** questions (selected = include), seeded by
   step 3's recommendation — select the ones with `recommend: true`, and quote
   the `reason` so the user sees *why*. You are presenting the script's verdict,
   not inventing your own; the user's answer is the final authority.
   **`AskUserQuestion` allows at most 4 options per question**, and there are
   more than 4 optional components — so split them across **multiple multi-select
   questions in a single `AskUserQuestion` call** (the tool takes up to 4
   questions at once; group e.g. "infra/ops" and "project type"). Do **not** try
   to put all components in one question — it will error.

5. **Preview** with a dry run, passing `--skip <key>` for every unchecked
   component:
   ```bash
   bash scripts/scaffold.sh --target <target> --dry-run --skip devcontainer --skip notebooks
   ```

6. **Show the plan and get explicit confirmation.** Summarise what will be
   created, what's being skipped (and that the skips get recorded in
   `.setup-env.toml` so future audits won't flag them), and what you can't fix
   automatically (e.g. populating an empty `devcontainer.json` from
   `demo-devcontainer-analytics`). **Wait for the user to say go.**

7. **Apply** (only after confirmation), same `--skip` flags:
   ```bash
   bash scripts/scaffold.sh --target <target> --skip devcontainer --skip notebooks
   ```
   Idempotent; never overwrites existing files. If the template repo is
   unreachable, add `--no-clone` for a minimal skeleton.

8. **Verify and report.** Re-run the audit:
   ```bash
   uv run scripts/audit.py <target>
   ```
   Show the before/after delta. Opted-out components appear as `SKIP`, not
   discrepancies. List remaining `WARN`/`FAIL` items needing manual work
   (devcontainer content, real `pyproject.toml`/`Makefile`/`uv.lock` if stubs
   were used, LICENSE/README content).

## Rules

- **Adapt, don't dictate.** Always run step 3–4. Never scaffold optional
  components without asking, and never skip a **core** component.
- **Honour prior choices.** If `.setup-env.toml` already opts something out,
  carry it into the checklist defaults rather than silently re-enabling it.
- **Never overwrite.** The scaffold only fills gaps. If a file exists, leave it.
- **Never invent compliance.** If a stub can't satisfy a hard rule (e.g. no real
  `pyproject.toml` without the template), say so plainly — don't fake a PASS.
- **Confirmation is mandatory** before step 7. This skill is opt-in by design.
- Run scripts from this skill's directory so relative paths resolve. The scripts
  use `uv run` (PEP 723 inline metadata) — no separate install needed.

## What's out of scope

Process standards (PR approval flow, code-review checklist, unit/integration-test
coverage targets) are **not** auto-applied — they live in review, not in files.
Surface them as guidance only. See [STANDARDS.md](STANDARDS.md) §5.
