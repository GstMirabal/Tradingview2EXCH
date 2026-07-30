# Walkthrough: BACKEND_MIGRATION
**File**: `docs/walkthroughs/BACKEND_MIGRATION_WALKTHROUGH.md` (RA-06 Option B naming)
**Last updated**: Sprint #001

---

## 1. What was achieved
| Sprint | Milestone | Outcome |
| :--- | :--- | :--- |
| #000 (commit `48bad3b`, "feat: migrate to professional Django-Pro template and refactor apps with Service Layer and security hardening") | Django project restructured to a `backend/config/` + `backend/apps/` layout; `core`, `Binance_Connector`, and `Webhook_Receiver` re-created under `backend/apps/`, wired into `INSTALLED_APPS` and `backend/config/urls.py` | Active code now lives exclusively under `backend/apps/`; the pre-migration root-level `Binance_Connector/` and `Webhook_Receiver/` directories were left in place, unwired, becoming dead code from this commit onward (see §3) |
| #000 (commit `48bad3b`) | Service Layer introduced for Binance interaction (`apps/Binance_Connector/services.py`, `BinanceService`) | `Binance_Connector`'s view and `Webhook_Receiver`'s view both call `binance_service.execute_order(...)` instead of talking to the `binance` SDK inline |
| #000 (commit `48bad3b`) | Security hardening in `backend/config/settings.py`: `SecurityMiddleware`, `csp.middleware.CSPMiddleware`, `corsheaders.middleware.CorsMiddleware`, conditional `SECURE_SSL_REDIRECT` / `SECURE_HSTS_*` / `CSP_DEFAULT_SRC` / `X_FRAME_OPTIONS` / `SECURE_REFERRER_POLICY` when `DEBUG` is `False`; shared-secret passphrase gate (`apps.core.permissions.HasWebhookPassphrase`) added in front of the webhook intake endpoint | `backend/apps/core/tests.py::ProductionSecurityHeadersTest` verifies `X-Frame-Options: DENY` and `X-Content-Type-Options: nosniff` are present under simulated production settings |
| #000 (commit `ddd7b14`, "chore: fixed ruff linting in tests and added explicit .env loading in manage.py") | Ruff lint fixes applied to the test suite; `manage.py` updated to load `.env` explicitly | Follow-up hardening pass after the architectural rewrite, no structural change |
| #000 (commit `c2c714a`, "chore: resolve merge conflicts by adopting the new template structure") | Merge conflicts from the template migration resolved in favor of the new `backend/` structure | Confirms `backend/apps/` as the sole active code path at this audit's baseline commit |
| #001 (full security/quality remediation sprint) | Fixed the Docker/production deploy path (it was booting the dead legacy `tradingview2exch/` project, unauthenticated); fixed the passphrase-gate `KeyError`; fixed a `django-csp` incompatibility that made Django refuse to start with `DEBUG=False`; deleted all legacy code (`tradingview2exch/`, root `Binance_Connector/`/`Webhook_Receiver/`, `src/`); renamed `binanceParams`/`webhook`/etc. to governance casing (`ADR-0001`); simplified DB config to SQLite-only (Postgres was never-adopted template boilerplate); upgraded Django to 6.0; added idempotency (`order_id` unique) and case-insensitive exchange validation; rewrote the entire test suite (59 tests, previously broken/uncollectable) | `python backend/manage.py check` passes with `DEBUG=False`; `python manage.py test` (bare, from `backend/`) passes 59/59; `ruff check backend/` reports zero issues |

## 2. Current state
Three Django apps are active under `backend/apps/`: `core` (shared password-validator and webhook-passphrase permission, no model), `Binance_Connector` (`BinanceParamsView` + `BinanceStatusView`, `BinanceParams` model, `BinanceService` Service Layer wrapping the `binance-connector` SDK), and `Webhook_Receiver` (`WebhookReceivedView` intake endpoint + `Webhook` model, calling `Binance_Connector`'s Service Layer directly for `exchange == 'BINANCE'` alerts). Verified by reading `backend/config/settings.py` `INSTALLED_APPS` and `backend/config/urls.py`, direct inspection of each app's `models.py`/`serializers.py`/`views.py`/`services.py`/`urls.py`, and by running the full test suite (59/59 passing) and `manage.py check` under both `DEBUG` values. Blueprints: `docs/architecture/CORE_BLUEPRINT.md`, `docs/architecture/BINANCE_CONNECTOR_BLUEPRINT.md`, `docs/architecture/WEBHOOK_RECEIVER_BLUEPRINT.md`. Decision record: `docs/decisions/ADR-0001-governance-casing-rename.md`.

## 3. Known limitations / tech debt
| Item | Marked as | Tracked where |
| :--- | :--- | :--- |
| Django app package names (`Binance_Connector/`, `Webhook_Receiver/`) are not PascalCase-normalized — deliberately out of scope for the Sprint #001 rename, since an app-label rename rewrites `django_content_type`/`auth_permission` rows and migration history, a data-migration-class risk rather than a code refactor | `:tech-debt:` | `docs/decisions/ADR-0001-governance-casing-rename.md` §2 |
| A same-`order_id` race between two concurrent requests both passing the serializer's uniqueness check before either commits is caught at the DB level (`IntegrityError` → `HTTP 409`) — this path exists in `WebhookReceivedView.post()` but isn't exercised by an automated test (hard to reproduce deterministically without a real concurrency harness) | `:tech-debt:` | `backend/apps/Webhook_Receiver/views.py` |

## 4. How to operate it
Minimum commands to run/verify the module (deterministic, prefixed paths per agents.md §3):

```bash
python backend/manage.py runserver
cd backend && python manage.py test   # bare `test` discovers relative to cwd — run from backend/
```

---
*Updated at every Sprint Closeout touching this module (RA-05).*
