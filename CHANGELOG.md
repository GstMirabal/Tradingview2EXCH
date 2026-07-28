# Changelog

All notable changes to Tradingview2EXCH. This file is the **Master Ledger** (agents.md §0): every Sprint Closeout appends its sprint entry under `[Unreleased]`; every deployment seals that section as `[vX.Y.Z] - date` immediately before tagging.

Format: [Keep a Changelog](https://keepachangelog.com/) · Versioning: [SemVer](https://semver.org/).

> Jurisdiction note: framework changes live in `.agents/CHANGELOG.md`, never here. When the `.agents` pin is updated, this ledger records only the bump (e.g. `chore(deps): pin .agents to v4.2.1 #000`).

## [Unreleased]

### Sprint #001 — Full security & quality remediation

#### Fixed
- **Production could not start at all**: `settings.py` used pre-4.0 `django-csp` syntax (`CSP_DEFAULT_SRC`), which the installed `django-csp==4.0` treats as a hard system-check `Error`, blocking Django whenever `DEBUG=False`. Migrated to `CONTENT_SECURITY_POLICY`.
- **Docker/production deploy booted the wrong, unauthenticated project**: `entrypoint.sh`/`Dockerfile` resolved `manage.py` to the dead legacy `tradingview2exch/` project (no passphrase gate, hardcoded `SECRET_KEY` public since the first commit), not the hardened `backend/` one. Corrected to `backend/manage.py` + `gunicorn`.
- `HasWebhookPassphrase` raised `KeyError` on every request (`WEBHOOK_PASSPHRASE` was looked up under a nonexistent `[security]` section) — the webhook endpoint's auth gate never actually worked. Also replaced the `==` passphrase comparison with `hmac.compare_digest` (timing attack).
- `Binance_Connector`'s order-execution endpoint was `AllowAny` — now `IsAdminUser`.
- `entrypoint.sh` echoed `API_KEY`/`API_SECRET`/`EMAIL_HOST_PASSWORD` to container logs on every start — removed.
- `exchange` validation was case-sensitive (rejected real-world lowercase TradingView values) — now case-insensitive.
- Test suite was completely uncollectable (`manage.py test` crashed at import due to the legacy app) and several tests exercised dead/mocked-wrong code paths — rewritten, 59 tests passing.

#### Changed
- **Breaking**: renamed `binanceParams`/`webhook`/`webhookReceived`/`orderId`/`marketPosition`/`marketPrevPosition`/etc. to governance-compliant PascalCase/snake_case — see `docs/decisions/ADR-0001-governance-casing-rename.md`. Any TradingView alert already configured needs its field names updated.
- Simplified `DATABASES` to SQLite-only — the Postgres code path was template boilerplate never actually adopted (confirmed against the real `db.sqlite3`). `docker-compose.yml` now has a single `web` service instead of an unused `postgres` one.
- Upgraded Django 5.2.7 → 6.0.7, DRF 3.16.1 → 3.17.1, `binance-connector` 3.12.0 → 3.13.0, `drf-yasg` 1.21.10 → 1.21.15.
- Swagger/Redoc now only served when `DEBUG=True`.
- Added `order_id` uniqueness (idempotency against TradingView webhook retries) and a `GET /binance-connector/status/` health endpoint.

#### Removed
- Legacy dead code: `tradingview2exch/`, root-level `Binance_Connector/`/`Webhook_Receiver/`, root `manage.py`, `src/`.
- Unused dependencies: `httpx`, `httpcore`, `h11`, `anyio`, `sniffio`, `psycopg2-binary`, `dj-database-url`, `requests`.

#### Security
- `config.toml` and `logs/project.json` were tracked in git despite `.gitignore` — untracked (kept locally).
- **Git history rewritten** (`git filter-repo --path tradingview2exch/settings.py --invert-paths`) to purge the historically-public `SECRET_KEY` from every commit — confirmed via `git log --all -- tradingview2exch/settings.py` returning nothing. Every commit SHA on every local branch changed as a result. A full pre-rewrite bundle backup was taken before running it. `origin` was removed by `git filter-repo` as a safety default (standard behavior) — a force-push to re-establish the remote is a separate, explicitly-confirmed step, not run automatically. A fresh `SECRET_KEY`/`WEBHOOK_PASSPHRASE` must be set in `.env` — see the sprint close report.

### Added
- Adopted Token-Optimized Agent Pipeline governance (`.agents` v4.2.1) — onboarding scenario: C (mature project, no prior docs, zero prior agentic traces; Full Reverse Engineering per `standardization_workflow.md` Phase 6). Physical `docs/` topology scaffolded, `docs/active_state.json` seeded as Zero Coordinate, `docs/0_SYSTEM_OVERVIEW.md` materialized. #000

## [v0.0.0-legacy] - 2026-07-27
_Seed entry: audited state of the project at governance adoption (Scenario C — summarized, not itemized line-by-line)._

- Backend-only Django trading webhook relay: TradingView alerts -> `Webhook_Receiver` -> `Binance_Connector` -> Binance API, under `backend/config/` (settings, urls) and `backend/apps/` (`core`, `Binance_Connector`, `Webhook_Receiver`).
- Prior undocumented history migrated the project onto a Django-Pro template, introduced a Service Layer, and hardened security (commit `6cd4c32`), followed by ruff linting fixes and explicit `.env` loading in `manage.py` (commit `f5ea84d`), predating this governance adoption.
- **Known cleanup candidate (flagged, not actioned)**: root-level `Binance_Connector/` and `Webhook_Receiver/` directories are pre-migration duplicates of the now-active `backend/apps/` versions — confirmed dead code, not referenced in `settings.py`/`urls.py`. Left in place pending an explicit human deletion decision; tracked as `legacy_flags` in `docs/active_state.json`.
- Containerization present at `docker/DockerFile` + `docker-compose.yml`; app-level runtime config at root `config.toml` (distinct from Django settings).
