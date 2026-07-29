# Changelog

All notable changes to Tradingview2EXCH. This file is the **Master Ledger** (agents.md §0): every Sprint Closeout appends its sprint entry under `[Unreleased]`; every deployment seals that section as `[vX.Y.Z] - date` immediately before tagging.

Format: [Keep a Changelog](https://keepachangelog.com/) · Versioning: [SemVer](https://semver.org/).

> Jurisdiction note: framework changes live in `.agents/CHANGELOG.md`, never here. When the `.agents` pin is updated, this ledger records only the bump (e.g. `chore(deps): pin .agents to v4.2.1 #000`).

## [Unreleased]

### Sprint #002 — Independent re-audit before publishing

An independent second-pass audit (fresh code re-read + a background subagent that actually built and ran the Docker image, not just validated it statically) found real gaps Sprint #001 left behind.

#### Fixed
- **Critical — `DEBUG`/`EMAIL_USE_TLS` were never real booleans in any real deployment.** `envtoml` substitutes an unset/text `$DEBUG` into a quoted TOML string, so `config['django_settings']['DEBUG']` always resolved to the Python string `'True'`/`'False'`, never a boolean — and any non-empty string is truthy, so `DEBUG="False"` in `.env` silently behaved as `DEBUG=True`. The entire production-only security block (HSTS, CSP, `SECURE_SSL_REDIRECT`, secure cookies, `X_FRAME_OPTIONS`) never activated in any real deployment, `ALLOWED_HOSTS` stayed pinned to `localhost`/`127.0.0.1` (production would be unreachable from its real domain), and Django would show full debug error pages on a 500 to any public visitor. Existing tests never caught it because they set `DEBUG` via `override_settings` (a native Python bool), bypassing the exact code path that broke. Found and confirmed via real end-to-end HTTP testing against a running server driven through the actual `config.toml` + `envtoml` pipeline, not mocks. Added `_config_bool()` plus regression tests that mock the config layer to return strings, matching real behavior.
- `SECURE_SSL_REDIRECT=True` with no `SECURE_PROXY_SSL_HEADER` meant any deployment behind a reverse proxy (gunicorn itself never terminates TLS) would infinite-redirect-loop.
- **Docker never actually worked**: `config.toml` wasn't `COPY`'d into the image and was excluded via `.dockerignore` — the container crashed on `manage.py migrate` with `ImproperlyConfigured`. Verified by building and running the container end-to-end, before and after the fix.
- `config.toml` was still git-tracked despite Sprint #001's CHANGELOG entry claiming otherwise — untracked for real this time, verified with `git ls-files config.toml` immediately before the commit.
- Bare `except Exception` handlers in both views leaked `str(e)` to API clients — now a generic message; detail stays server-side in the log.
- `SQLITE_NAME` empty-string bug (envtoml substitutes an unset `$VAR` with `''`, not a missing key, so `dict.get(key, default)` never fell back) — fixed with an `or` fallback; the same pattern was applied proactively to the new `TIME_ZONE` setting.
- `CORE_BLUEPRINT.md` was never updated in Sprint #001 — still described the `config['security']` `KeyError` bug and the old `webhookReceived` name as current fact.

#### Changed
- Last camelCase route: `binanceParams/` → `binance-params/` (internal, `IsAdminUser`-gated endpoint).
- Removed the dead `USE_SQLITE` toggle (documented, never read by `settings.py`).
- `TIME_ZONE` moved from hardcoded to config-driven (defaults to `UTC`).
- Added DRF `ScopedRateThrottle` (20/min) on `WebhookReceivedView` — internet-facing, previously gated only by a static passphrase with no rate limit.
- Fixed ~20 stale `docs.djangoproject.com/en/5.2` links left over from the Django 6.0 upgrade.
- `identity.config.json` (blank since the `.agents` bridge install) completed with real project identity.

#### Removed
- `memory/telemetry/raw_errors.json` (ephemeral hook-violation log) purged per `agents.md`'s zero-tolerance memory rule.

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
