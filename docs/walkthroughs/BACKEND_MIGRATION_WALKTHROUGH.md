# Walkthrough: BACKEND_MIGRATION
**File**: `docs/walkthroughs/BACKEND_MIGRATION_WALKTHROUGH.md` (RA-06 Option B naming)
**Last updated**: Sprint #000

---

## 1. What was achieved
| Sprint | Milestone | Outcome |
| :--- | :--- | :--- |
| #000 (commit `6cd4c32`, "feat: migrate to professional Django-Pro template and refactor apps with Service Layer and security hardening") | Django project restructured to a `backend/config/` + `backend/apps/` layout; `core`, `Binance_Connector`, and `Webhook_Receiver` re-created under `backend/apps/`, wired into `INSTALLED_APPS` and `backend/config/urls.py` | Active code now lives exclusively under `backend/apps/`; the pre-migration root-level `Binance_Connector/` and `Webhook_Receiver/` directories were left in place, unwired, becoming dead code from this commit onward (see §3) |
| #000 (commit `6cd4c32`) | Service Layer introduced for Binance interaction (`apps/Binance_Connector/services.py`, `BinanceService`) | `Binance_Connector`'s view and `Webhook_Receiver`'s view both call `binance_service.execute_order(...)` instead of talking to the `binance` SDK inline |
| #000 (commit `6cd4c32`) | Security hardening in `backend/config/settings.py`: `SecurityMiddleware`, `csp.middleware.CSPMiddleware`, `corsheaders.middleware.CorsMiddleware`, conditional `SECURE_SSL_REDIRECT` / `SECURE_HSTS_*` / `CSP_DEFAULT_SRC` / `X_FRAME_OPTIONS` / `SECURE_REFERRER_POLICY` when `DEBUG` is `False`; shared-secret passphrase gate (`apps.core.permissions.HasWebhookPassphrase`) added in front of the webhook intake endpoint | `backend/apps/core/tests.py::ProductionSecurityHeadersTest` verifies `X-Frame-Options: DENY` and `X-Content-Type-Options: nosniff` are present under simulated production settings |
| #000 (commit `f5ea84d`, "chore: fixed ruff linting in tests and added explicit .env loading in manage.py") | Ruff lint fixes applied to the test suite; `manage.py` updated to load `.env` explicitly | Follow-up hardening pass after the architectural rewrite, no structural change |
| #000 (commit `9fad6e6`, "chore: resolve merge conflicts by adopting the new template structure", current `HEAD`) | Merge conflicts from the template migration resolved in favor of the new `backend/` structure | Confirms `backend/apps/` as the sole active code path at this audit's baseline commit |

## 2. Current state
Three Django apps are active under `backend/apps/`: `core` (shared password-validator and webhook-passphrase permission, no model), `Binance_Connector` (REST endpoint + `binanceParams` model + `BinanceService` Service Layer wrapping the `binance-connector` SDK), and `Webhook_Receiver` (REST intake endpoint + `webhook` model, calling `Binance_Connector`'s Service Layer directly for `exchange == 'BINANCE'` alerts). Verified by reading `backend/config/settings.py` `INSTALLED_APPS` and `backend/config/urls.py`, and by direct inspection of each app's `models.py`, `serializers.py`, `views.py`, `services.py` (where present), and `urls.py`. Blueprints: `docs/architecture/CORE_BLUEPRINT.md`, `docs/architecture/BINANCE_CONNECTOR_BLUEPRINT.md`, `docs/architecture/WEBHOOK_RECEIVER_BLUEPRINT.md`.

## 3. Known limitations / tech debt
| Item | Marked as | Tracked where |
| :--- | :--- | :--- |
| Root-level `Binance_Connector/` and `Webhook_Receiver/` directories (outside `backend/`) are unwired pre-migration duplicates, dead since `6cd4c32` — no ADR authorized keeping them; this is neglect, not a decision. Scheduled for removal only pending a future sprint with explicit human approval (`agents.md §2 destructive_flags`) | `:tech-debt:` | `docs/active_state.json` (`legacy_flags`); no sprint/hotfix doc opened yet |
| `apps.Binance_Connector.views.binanceParams` (the endpoint that triggers real order execution when `DEBUG=False`) declares `permission_classes = [AllowAny]`, with an in-code `# TODO: In production, change to IsAuthenticated or custom permission` comment (`backend/apps/Binance_Connector/views.py` lines 19-20) | `:tech-debt:` | Not yet tracked in a sprint or hotfix doc |
| `backend/apps/core/tests.py::DatabaseConnectionTest` asserts `settings.AUTH_USER_MODEL == 'users.User'`, but `backend/config/settings.py` line 328 has that assignment commented out (`#AUTH_USER_MODEL = 'users.User'`), and no `users` app exists in `INSTALLED_APPS`. Django's default (`auth.User`) would apply instead, meaning this assertion does not match the code as it stands. Unconfirmed whether this test currently passes — flagged as a stale/inconsistent test, not verified by running the suite in this audit | `:tech-debt:` | Not yet tracked in a sprint or hotfix doc |
| `backend/apps/Webhook_Receiver/test/tests.py::WebhookReceivedTests` patches `Binance_Connector.views.binanceParams` (the legacy, unwired root-level module path) and `requests.post`; the current implementation calls `apps.Binance_Connector.services.binance_service.execute_order` directly, in-process, with no `requests` HTTP call involved. These two mocks patch a code path the current view no longer exercises — the tests may pass without covering the actual execution path | `:tech-debt:` | Not yet tracked in a sprint or hotfix doc |
| `Webhook_Receiver`'s view imports and calls `Binance_Connector`'s Service Layer directly, bypassing `Binance_Connector`'s own model/serializer/view — a TradingView-originated order is persisted only to the `webhook` table, never to `binanceParams`. Recorded as an architectural fact in `docs/architecture/WEBHOOK_RECEIVER_BLUEPRINT.md` §6; no ADR exists authorizing this coupling as opposed to routing through `Binance_Connector`'s own endpoint | `:tech-debt:` | `docs/architecture/WEBHOOK_RECEIVER_BLUEPRINT.md` |

No ADR exists for any item above — each is recorded here as unresolved debt, not as the consequence of a documented decision.

## 4. How to operate it
Minimum commands to run/verify the module (deterministic, prefixed paths per agents.md §3). Unconfirmed — exact local dev invocation (venv activation, dependency install) not verified against `docker-compose.yml`/`Makefile` in this audit pass; verify in a future audit before treating these as authoritative:

```bash
python backend/manage.py test apps.core apps.Binance_Connector apps.Webhook_Receiver
python backend/manage.py runserver
```

---
*Updated at every Sprint Closeout touching this module (RA-05).*
