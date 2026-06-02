---
name: check-setup-against-standards
description: Audit an existing repository against the AI Services / BNE Data Engineering standards and report discrepancies — dev container, uv + uv.lock, ruff/mypy/nbqa config, required folder structure, data .gitignore policy, PR template. Read-only; makes no changes. Use when the user runs /check-my-setup-against-standards, asks "is my setup compliant / correct / up to standard?", "check my repo against the guidelines", or wants a gap report before a review.
allowed-tools: Bash(uv run*), Read
---

# check-setup-against-standards

Read-only audit of a repo against the team's **Developer Guidelines**. Reports
every gap with severity and a remediation hint. **Makes no changes** — to fix the
gaps, hand off to the `set-up-env` skill (`/set-up-env`).

This skill shares its checker and canonical standard with `set-up-env`:
[`../set-up-env/scripts/audit.py`](../set-up-env/scripts/audit.py) and
[`../set-up-env/STANDARDS.md`](../set-up-env/STANDARDS.md). Both skills are in the
`engineering` bucket and install together, so the sibling path resolves.

## Workflow

1. **Pick the target** — current directory by default, or a path the user names.

2. **Run the audit** (read-only, structured output):
   ```bash
   uv run ../set-up-env/scripts/audit.py <target> --format json
   ```
   If the sibling path doesn't resolve (skill installed standalone), locate the
   `set-up-env` skill directory and run its `scripts/audit.py`; if it isn't
   installed, tell the user to install `set-up-env` from the same bucket.

3. **Report the gaps.** Group by category (Environment, Tooling, Structure, Git
   hygiene). Lead with `FAIL`s, then `WARN`s. For each, give the one-line detail
   and the remediation. End with the pass/warn/fail tally and the overall result.

4. **Offer the fix.** If anything is non-PASS, point the user to `/set-up-env`,
   which scaffolds the missing pieces (with a confirmation step). Do **not** fix
   anything here.

## Interpreting results

- **FAIL** — a hard standard is unmet (missing dependency manifest, no `uv.lock`,
  missing dev tool, unpinned `requirements.txt`). Blocks "compliant".
- **WARN** — recommended/context-dependent: a missing scaffoldable dir/file, an
  empty `devcontainer.json` placeholder, line-length ≠ 100, no remote.
- Exit code mirrors severity: `0` clean, `1` warnings only, `2` at least one fail.

## Scope

Checks only what's mechanically verifiable from files. Process standards (PR
approval flow, code-review checklist, unit/integration-test coverage targets)
are **not** audited here — note them as manual-review items. See
[`../set-up-env/STANDARDS.md`](../set-up-env/STANDARDS.md) §5.
