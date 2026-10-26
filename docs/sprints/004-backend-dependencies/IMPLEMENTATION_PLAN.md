# Implementation Plan: Sprint 004 — Dependency security and framework pin

**Canonical path**: `docs/sprints/004-backend-dependencies/IMPLEMENTATION_PLAN.md`
**Branch**: `ai-sprint/004` · **Base**: `main` at `79a9531`
**Status**: `EXECUTING`

---

## Context

Two independent debts found by `/agents:start` on 2026-10-26:

1. The `.agents` submodule was pinned at `v4.3.0-5-g763fe54`, 40 tags behind
   `v4.39.1` (`git -C .agents tag --sort=-v:refname | awk '/^v4\.3\.0$/{exit} {print}' | wc -l`).
2. Dependabot reported 13 open alerts against `requirements.txt` — 1 critical,
   7 high, 5 medium (`gh api 'repos/{owner}/{repo}/dependabot/alerts?state=open' --jq length`).

| Package | Alerts | Minimum safe version | Pinned at base |
| :--- | :--- | :--- | :--- |
| `certifi` | 1 critical (GHSA-6q48-6c7w-9gw2) | `2026.10.19` | `2026.7.22` |
| `djangorestframework` | 3 high, 2 medium | `3.18.2` | `3.17.1` |
| `Django` | 1 high, 1 medium | `6.0.8` | `6.0.7` |
| `sqlparse` | 3 high, 2 medium | `0.6.0` | `0.5.5` |

Done when: `gh api 'repos/{owner}/{repo}/dependabot/alerts?state=open' --jq length` returns `0`, and `git -C .agents describe --tags` returns `v4.39.1`.

---

## Design

- **Merge the four single-package Dependabot PRs (#22, #23, #18, #13), not the group PRs.**
  Group PR #19 stops DRF at `3.18.1`, which leaves 3 high alerts open, and moves
  Django to `6.1.1`, a minor upgrade outside the scope of a security fix. Group PR
  #21 pins `certifi==2026.10.18`, which is still vulnerable and would revert #22.
- **Merge one at a time, observing `main` CI before the next** (`RA-13`).
- **Merge with `--admin`.** Branch protection on `main` requires `Analyze (python)`;
  CodeQL default setup skips pull requests that change only `requirements.txt`,
  so that check never reports and the PRs stay `BLOCKED`. The three other required
  checks pass on every PR. `enforce_admins` is `false`. Human authorization for
  these merges outside `deployment_workflow.md` was given in chat on 2026-10-26.

---

## Work

| # | File | Operation | Risk | Assignee (proposed) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `requirements.txt` | modify — PR #22 `certifi` | low | `principal_agent` | ⏳ |
| 2 | `requirements.txt` | modify — PR #23 `djangorestframework` | medium | `principal_agent` | ⏳ |
| 3 | `requirements.txt` | modify — PR #18 `Django` | low | `principal_agent` | ⏳ |
| 4 | `requirements.txt` | modify — PR #13 `sqlparse` | medium | `principal_agent` | ⏳ |
| 5 | `.agents` (submodule pointer) | modify — pin `v4.39.1` | low | `devops_agent` | ⏳ |
| 6 | `docs/0_SYSTEM_OVERVIEW.md` | modify — correct pin version | low | `doc_orchestrator` | ⏳ |

---

## Dependencies

None. The sprint raises versions of existing dependencies and adds none.

---

## Mechanisms

None proposed.

---

## Cost

| Field | Value | Reproduce |
| :--- | :--- | :--- |
| Delegation | `native` | `docs/active_state.json` |
| Work units | 6 | Count of rows in Work table |
| Subagents dispatched | 0 | — |
| Prior session ratio | n/a | No prior measured transcript for this host |

---

## Tests

| Check | Fails against the current tree? | Observed at base |
| :--- | :--- | :--- |
| Dependabot open alert count is `0` | **Yes** — this is the defect | `13` on 2026-10-26 |
| `ci / Lint and tests` on each PR | **No** — regression to protect | `success` on #22, #23, #18, #13 |

---

## Verification

| Command | Expected | Dry run | Positive control |
| :--- | :--- | :--- | :--- |
| `gh api 'repos/{owner}/{repo}/dependabot/alerts?state=open' --jq length` | `0` | `13` (defect present) | The base run returned `13` |
| `gh api repos/{owner}/{repo}/commits/main/check-runs --jq '.check_runs[].conclusion'` | `success` on every run | run at close — depends on merges | — |
| `git -C .agents describe --tags` | `v4.39.1` | `v4.39.1` | Base returned `v4.3.0-5-g763fe54` |

---

## Documentary impact (T5)

| Artefacto | Qué cambia |
| :--- | :--- |
| `CHANGELOG.md` | Entrada Sprint #004: pin bump y fixes de seguridad |
| `docs/0_SYSTEM_OVERVIEW.md` | Versión del pin corregida |
| `docs/active_state.json` | `current_sprint` → 4 |

---

## Out of scope

| Exclusion | Why, and where it goes instead |
| :--- | :--- |
| PR #19 (Django 6.1, drf-yasg) | Minor upgrade, not a security fix. Rebased by Dependabot after this sprint; next sprint decides. |
| PR #21 (everything-else group) | Must not land while it pins `certifi` below `2026.10.19`. Rebased by Dependabot; next sprint decides. |
| CodeQL skipping dependency-only PRs | Branch-protection design question; recorded as a follow-up for the next sprint. |

---

## Abort criterion

Any required check on `main` concludes `failure` after a merge: stop merging, revert that squash commit, and reopen planning.

---

## Approval — `triple_lock` lock 1

| Field | Value |
| :--- | :--- |
| **Approved by** | GstMirabal (chat, "ok") |
| **Date** | 2026-10-26 |
| **Plan commit at approval** | this commit |
| **Remaining locks** | Active Sprint · QA + Tester verdicts · Human OK at close |

*Phase 5 is a single attended human authorization. It MUST NOT be wrapped inside an
unattended `/loop` (`workflows/pipeline_workflow.md`, `rules/loop_governance.md`).
Any `/loop` this sprint does run — Phases 6-8 only — is governed by
`scripts/loop_guard.py start`, which fails closed.*
