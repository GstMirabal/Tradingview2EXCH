# Blueprint: BINANCE_CONNECTOR
**File**: `docs/architecture/BINANCE_CONNECTOR_BLUEPRINT.md` (RA-06 Option B naming)
**Status**: `RATIFIED`
**Sprint of origin**: #000
**Last Audit Sprint**: #001
**Last Audit Date**: 2026-07-28
**Last Audit Commit SHA**: n/a (git filter-repo rewrote all commit SHAs in this same sprint; audit spans the whole ai-sprint/001-full-remediation branch, see CHANGELOG)

---

arc42-lite (`rules/documentation_standard.md §5`) — Reference only. This document states current facts, verifiably; it never argues for them. Any decision behind this module's shape lives in a linked ADR, not here.

## 1. Introduction & Goals
`apps.Binance_Connector` (`backend/apps/Binance_Connector/`) exposes a REST endpoint that accepts order parameters, persists them, and executes the corresponding order against the Binance API through a `services.py` Service Layer (`BinanceService`) wrapping the `binance-connector` Python SDK (`binance.spot.Spot`).

## 2. Context & Scope
| Aspect | Value |
| :--- | :--- |
| **Upstream dependencies** | `binance.spot.Spot` / `binance.error.ClientError` (external SDK), `config.settings.config` (`[binance]` section: `API_KEY`, `API_SECRET`), `django.conf.settings.DEBUG` |
| **Downstream consumers** | `apps.Webhook_Receiver.views` imports `apps.Binance_Connector.services.binance_service` directly (in-process function call, not an HTTP call to this app's own endpoint) |

## 3. Building Block View
| Aspect | Value |
| :--- | :--- |
| **Owns** | `backend/apps/Binance_Connector/` (`models.py`, `serializers.py`, `services.py`, `views.py`, `urls.py`, `admin.py`, `apps.py`, `migrations/`, `test/`) |
| **Must not touch** | `backend/apps/Webhook_Receiver/`, `backend/apps/core/` |

Contracts (formal interfaces this module exposes):

| Interface | Type | Defined in |
| :--- | :--- | :--- |
| `POST /binance-connector/binanceParams/` (`BinanceParamsView`) | REST | Not yet published — no `docs/contracts/BINANCE_CONNECTOR_CONTRACT.md` exists at this audit |
| `GET /binance-connector/status/` (`BinanceStatusView`) | REST | Not yet published |
| `BinanceService.execute_order(symbol, side, order_type, quantity)` | Function (Service Layer) | Not yet published |

Data model (summary only):
- `BinanceParams`: one submitted order-parameter record — `exchange`, `symbol`, `side`, `type` (all `CharField`, uppercased on `save()`), `size` (`DecimalField`, max_digits=12, decimal_places=6).

## 4. Runtime View
1. Client sends `POST /binance-connector/binanceParams/` with `exchange`, `symbol`, `side`, `type`, `size`, authenticated as a Django staff user (`IsAdminUser`).
2. `BinanceParamsSerializer` validates the payload; `validate_exchange` accepts `'BINANCE'` case-insensitively.
3. `BinanceParamsView.post()` persists the validated record via `serializer.save()`.
4. The view calls `binance_service.execute_order(...)`. `BinanceService.client` lazily instantiates a `binance.spot.Spot` client from `config['binance']['API_KEY']` / `API_SECRET`, raising `ValueError` if either is missing.
5. If `settings.DEBUG` is `True`, `execute_order` calls `client.new_order_test(**params)` (dry-run validation, no real order). If `False`, it calls `client.new_order(**params)` (a live order against `https://api1.binance.com`).
6. The Binance response (or a caught `ClientError` / generic `Exception`) is returned to the caller as JSON.
7. `GET /binance-connector/status/` (`BinanceStatusView`, also `IsAdminUser`) returns `BinanceService.get_system_status()` and `get_user_assets()` for operational checks.

## 5. Crosscutting Concepts
- Service Layer: a single module-level instance `binance_service = BinanceService()` (bottom of `services.py`) is imported and reused by both this app's view and `apps.Webhook_Receiver.views` — a de facto singleton, not a Django-managed one.
- Logging: `logging.getLogger('project')`, used for both request tracing and error capture.

## 6. Non-negotiable Constraints
| Constraint | Verification |
| :--- | :--- |
| Only `exchange == 'BINANCE'` (case-insensitive) is accepted by the serializer | `backend/apps/Binance_Connector/serializers.py::validate_exchange` |
| `execute_order` only places a real, capital-risking order when `settings.DEBUG` is `False`; otherwise it uses the SDK's `new_order_test` dry-run call | `backend/apps/Binance_Connector/services.py` |
| `BinanceParamsView`/`BinanceStatusView` require `IsAdminUser` (authenticated Django staff session) | `backend/apps/Binance_Connector/views.py` |

## 7. Decisions
- `docs/decisions/ADR-0001-governance-casing-rename.md`: renamed `binanceParams`→`BinanceParams`, `binanceParamsserializers`→`BinanceParamsSerializer`, view/admin classes, and the `binanceParams`→`binance_params` URL name to governance-compliant casing.

## 8. Glossary
| Term | Meaning in this module |
| :--- | :--- |
| `BinanceParams` | Django model persisting one submitted order-parameter record (exchange/symbol/side/type/size). |
| `BinanceService` | Service-layer class encapsulating all `binance-connector` SDK interaction; lazily initializes its client, exposes `execute_order`, `get_system_status`, `get_user_assets`. |
| `new_order_test` vs `new_order` | Binance SDK's dry-run order-validation call vs. its live order-placement call; selected by `settings.DEBUG`. |

---
*A module without a ratified Blueprint cannot enter Execution (agents.md §0). C4 Level 3 not required — only 3 containers exist under the declared `backend/apps/` root, under the 5-container safety floor (`rules/documentation_standard.md §2.1` points 6/8); Level 3 stays advisory-only for this project.*
