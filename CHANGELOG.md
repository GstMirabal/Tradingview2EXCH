# Changelog

All notable changes to Tradingview2EXCH. This file is the **Master Ledger** (agents.md §0): every Sprint Closeout appends its sprint entry under `[Unreleased]`; every deployment seals that section as `[vX.Y.Z] - date` immediately before tagging.

Format: [Keep a Changelog](https://keepachangelog.com/) · Versioning: [SemVer](https://semver.org/).

> Jurisdiction note: framework changes live in `.agents/CHANGELOG.md`, never here. When the `.agents` pin is updated, this ledger records only the bump (e.g. `chore(deps): pin .agents to v4.2.1 #000`).

## [Unreleased]

### Added
- Adopted Token-Optimized Agent Pipeline governance (`.agents` v4.2.1) — onboarding scenario: C (mature project, no prior docs, zero prior agentic traces; Full Reverse Engineering per `standardization_workflow.md` Phase 6). Physical `docs/` topology scaffolded, `docs/active_state.json` seeded as Zero Coordinate, `docs/0_SYSTEM_OVERVIEW.md` materialized. #000

## [v0.0.0-legacy] - 2026-07-27
_Seed entry: audited state of the project at governance adoption (Scenario C — summarized, not itemized line-by-line)._

- Backend-only Django trading webhook relay: TradingView alerts -> `Webhook_Receiver` -> `Binance_Connector` -> Binance API, under `backend/config/` (settings, urls) and `backend/apps/` (`core`, `Binance_Connector`, `Webhook_Receiver`).
- Prior undocumented history migrated the project onto a Django-Pro template, introduced a Service Layer, and hardened security (commit `6cd4c32`), followed by ruff linting fixes and explicit `.env` loading in `manage.py` (commit `f5ea84d`), predating this governance adoption.
- **Known cleanup candidate (flagged, not actioned)**: root-level `Binance_Connector/` and `Webhook_Receiver/` directories are pre-migration duplicates of the now-active `backend/apps/` versions — confirmed dead code, not referenced in `settings.py`/`urls.py`. Left in place pending an explicit human deletion decision; tracked as `legacy_flags` in `docs/active_state.json`.
- Containerization present at `docker/DockerFile` + `docker-compose.yml`; app-level runtime config at root `config.toml` (distinct from Django settings).
