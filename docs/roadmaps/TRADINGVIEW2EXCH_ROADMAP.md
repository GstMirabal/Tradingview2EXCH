# Global Roadmap: Tradingview2EXCH

**Last Updated Sprint**: #004
**Last Updated Date**: 2026-10-26

The single forward-looking plan for this repository (`agents.md §0 Hierarchy`:
`roadmaps/` is the Future). Completed work is summarized here only as a pointer;
its record is the Master Ledger (`CHANGELOG.md`) and each sprint's `SPRINT_LOG.md`.

---

## 1. Completed

| Sprint | Stack / Layer | Outcome | Record |
| :--- | :--- | :--- | :--- |
| #000 | global / onboarding | Scenario C reverse engineering; legacy tree flagged | `docs/active_state.json` `onboarding` |
| #001 | backend / remediation | Legacy unauthenticated project deleted; leaked `SECRET_KEY` purged from history | `CHANGELOG.md` Sprint #001 |
| #002 | backend / re-audit | Independent re-audit before publishing; CI and community files | `CHANGELOG.md` Sprint #002 |
| #003 | backend / hardening | Ten-finding audit; rejected orders retryable; `LIVE_TRADING` replaces `DEBUG` | `docs/sprints/003-backend-hardening/SPRINT_LOG.md` |
| #004 | backend / dependencies | 13 Dependabot alerts closed; `.agents` pinned to `v4.39.1` | `docs/sprints/004-backend-dependencies/SPRINT_LOG.md` |

---

## 2. Queue

Ordered by risk. Each item names its source and its done-criterion.

| # | Item | Source | Done when |
| :--- | :--- | :--- | :--- |
| 1 | Resolve the required check `Analyze (python)` that CodeQL default setup never reports on dependency-only PRs | Sprint #004 KI-004-1 | A Dependabot PR that changes only `requirements.txt` reaches `mergeStateStatus: CLEAN` without `--admin` |
| 2 | Dependabot PR #26: Django `6.0.8` → `6.1.2`, DRF `3.18.3`, `drf-yasg`, `asgiref` | Dependabot, 2026-10-26 | PR merged with suite green, or closed with the reason recorded |
| 3 | Dependabot PR #27: ten tooling and runtime bumps, including `ruff 0.17.2` and `gunicorn 26.2.0` | Dependabot, 2026-10-26 | PR merged with suite green, or closed with the reason recorded |
| 4 | Replace the deprecated `pythonjsonlogger.jsonlogger` import with `pythonjsonlogger.json` | Sprint #004 Tester gate | `pytest` reports 0 warnings |
| 5 | Resolve the `docs-freshness-check` finding `C4 Level 3 required for: backend/core` — write the Level 3 section or record why it does not apply | Sprint #004 close | `make -f .agents/Makefile docs-freshness-check` prints no `WARN` |
