# Task Scope — Sprint 004 (dependency security and framework pin)

Phase 4.3 of `workflows/pipeline_workflow.md`. `jurisdictional_lock` and
`no_interference` are enforced by reading this table: one physical file per unit,
and no file held by two units in progress at the same time.

| # | File | Operation | Risk | Assignee | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `requirements.txt` | merge PR #22 (remote squash) | low | `devops_agent` | ✅ `4eaf86a` |
| 2 | `requirements.txt` | merge PR #23 (remote squash) | medium | `devops_agent` | ✅ `7bfc82f` |
| 3 | `requirements.txt` | merge PR #18 (remote squash) | low | `devops_agent` | ✅ `95a2e63` |
| 4 | `requirements.txt` | merge PR #13 (remote squash) | medium | `devops_agent` | ✅ `f93a8e0` |
| 5 | `.agents` | checkout tag `v4.39.1` | low | `devops_agent` | ✅ `e222bd8` |
| 6 | `docs/0_SYSTEM_OVERVIEW.md` | modify | low | `doc_orchestrator` | ✅ `f5ea9f4` |

Units 1-4 share `requirements.txt` and were executed strictly in sequence: each
started only after `main` CI on the previous squash commit was observed green
(`RA-13`), so no two were ever in progress together.
