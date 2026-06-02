# AI Services / BNE Data Engineering — Environment & Repo Standards

Canonical, machine-checkable summary of the team's **Developer Guidelines**.
Both `set-up-env` and `check-setup-against-standards` read this file; `scripts/audit.py`
is its executable form. Keep the two in sync — if a rule changes here, change the check.

> Source of truth: Confluence space **AIS → 6. Developer Guidelines** (Diátaxis-structured)
> and the reference repo [`rio-tinto/dna-bne-project-template`](https://github.com/rio-tinto/dna-bne-project-template).
> When in doubt, the template repo wins for *structure*; Confluence wins for *intent*.

Severity convention used by the audit:

- **FAIL** — a hard standard is unmet (blocks "compliant").
- **WARN** — recommended but context-dependent, or a placeholder needing content.
- **PASS** — meets the standard.
- **SKIP** — an *optional* component the repo opted out of (recorded in
  `.setup-env.toml`). Reported transparently; never counted as pass or fail.

## Deterministic vs. dynamic (the dividing line)

Anything that must give the **same answer every run** lives in the scripts;
genuine **judgment, user choice, and one-off cleanup** live in the agent. Rule
of thumb: a script when drift would change *what gets built* or *how it's
measured*; an agent instruction when it's cosmetic clean-up of just-created
resources that mixes mechanical edits with prose and placeholders. (We tried a
`prune_readme.py` for README cleanup and removed it — it could prune the
structure tree but not honestly reword the surrounding prose, which is exactly
the judgment a script shouldn't fake.)

| Concern | Deterministic (scripts) | Dynamic (agent) |
|---|---|---|
| Does a file / dir / config exist & meet the standard? | `audit.py` | |
| Component registry + which are core vs optional | `audit.py --list-components` | |
| **Detecting repo signals → recommending components** | `audit.py --recommend` | |
| Create dirs, copy template, write `.setup-env.toml`, set project name | `scaffold.sh` | |
| **Sanitise created files** (prune README tree, reword prose, placeholders) | | agent (step 8) |
| Detect README still references an opted-out component | `audit.py` (Docs consistency) | |
| *Which* components to actually include (the decision) | | user via `AskUserQuestion` |
| Whether to `git init` a nested repo, fill boilerplate | | agent judgment |
| Present plan, confirm, narrate before/after | | agent |

`--recommend` detection rules (mechanical, reproducible): `docker` ← Dockerfile /
compose; `infrastructure` ← `*.tf`/`*.bicep`/CloudFormation; `pipelines` ←
azure-pipelines / `.github/workflows`; `notebooks` ← `*.ipynb`; `models` ←
`*.pt/.pkl/.h5/.onnx/.joblib/.safetensors`; `github_pr` ← git remote on GitHub.
No signal → the component's documented `default`. A prior `.setup-env.toml`
opt-out always wins.

## Core vs. optional components

Not every team uses every component (e.g. some devs don't use dev containers).
`set-up-env` asks the user which optional components to include; the choice is
saved to `.setup-env.toml` and honoured by both skills across sessions.
`audit.py --list-components` is the canonical registry.

- **Core (never skippable):** uv + `pyproject.toml` + `uv.lock`, ruff + mypy,
  `src/ tests/ docs/ config/ scripts/ data/`, the data `.gitignore` policy + a
  sample file, and `README/SECURITY/CONTRIBUTING/LICENSE/Makefile/.env.sample`.
- **Optional (agent asks):** `devcontainer`, `docker`, `infrastructure`,
  `pipelines`, `notebooks` (which also gates the **nbqa** tool), `models`,
  `github_pr`.

`.setup-env.toml` format:

```toml
[components]
devcontainer = false   # opted out → audit reports SKIP, scaffold won't create it
notebooks = false      # also drops the nbqa tooling requirement
```

---

## 1. Development environment (hard requirements)

| Standard | Rule | Severity if missing |
|---|---|---|
| Dev Container | `.devcontainer/devcontainer.json` must exist. Content is filled from [`demo-devcontainer-analytics`](https://github.com/rio-tinto/demo-devcontainer-analytics). | FAIL (absent) / WARN (empty placeholder) |
| Dependency manager | Use **uv**. A `pyproject.toml` (preferred) or `requirements.txt` must define dependencies. | FAIL |
| Lockfile | `uv.lock` must be committed for reproducibility. | FAIL |
| Pinning | If using `requirements.txt`, every package is version-pinned (`pkg==1.2.3`). | FAIL (unpinned) |

## 2. Code-quality tooling

Configured via `pyproject.toml` + `Makefile`, adopted from the template.

- Dev dependency group declares **ruff**, **mypy**, **nbqa** (FAIL if any missing).
- `[tool.ruff] line-length = 100` (team adaptation of PEP 8's 79) — WARN otherwise.
- Absolute imports enforced: `[tool.ruff.lint.flake8-tidy-imports.banned-api]` bans `from`-imports — WARN otherwise.
- `Makefile` exposes a `check_code_quality` target (ruff check → isort → format → mypy) — WARN otherwise.
- PEP 257 docstrings (`[tool.ruff.lint.pydocstyle] convention = "pep257"`).

## 3. Repository structure

Top-level layout from "How to Structure Your Repository". Missing dirs/files are **WARN**
(scaffoldable), except where they break a hard rule.

Required directories: `config/ data/ data/raw/ data/processed/ docker/ docs/
infrastructure/ models/ notebooks/ pipelines/ reports/ scripts/ src/ tests/`

Required files: `.gitignore .gitattributes .env.sample README.md SECURITY.md
CONTRIBUTING.md LICENSE Makefile data/README.md .github/pull_request_template.md`

Data directory policy:
- **Never commit full datasets.** Only files whose names contain `sample`, `mock`, or `schema` (files, not folders).
- At least one such file must exist (e.g. `data/raw/raw-sample.csv`).
- `.gitignore` must contain the `data/**` allow-list block (see template).

## 4. Git hygiene (reference — not all auto-checkable)

- One branch per ticket; branch name contains the ticket number; `exploratory/` prefix for EDA.
- Trunk-based: feature → `main`; releases from long-lived release branches; tags `rc-*` (UAT), `release-*` (prod).
- **Conventional commits**: `<type>[scope]: <description>`. Types include `feat fix refactor chore config infra cfn cicd exp wip test perf style docs log revert`.
- Clear notebook outputs and review the diff before committing.

## 5. Out of scope for automated setup

Process standards that live in review, not in files — surfaced as guidance, never auto-applied:
PR process (≥1 approver, author merges, small focused PRs), code-review checklist,
unit-test R-S-D-C-R triggers + stage coverage targets (POC→Production, ≥80% line / ≥60% branch),
integration-test selection. See Confluence for these.

---

## Confluence index (for deep links)

- `[S] How to Meet Project Environment Standards` — §1
- `[S] How to Set Up Your Development Environment (Dev Containers and uv)` — §1
- `How to Set Up ruff, nbQA and mypy` / `[S] How to Apply Our Python Code Style` — §2
- `[S] How to Structure Your Repository` — §3
- `[S] How to Use Git for Team Collaboration` — §4
- `[S] How to Create and Complete a Pull Request`, `[S] How to Conduct a Code Review`,
  `[S] When to Write Unit Tests`, `[S] When to Write an Integration Test` — §5
