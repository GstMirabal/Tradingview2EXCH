# 📄 Contract: BINANCE_CONNECTOR
**File**: `docs/contracts/BINANCE_CONNECTOR_CONTRACT.md` (RA-06 Option B naming)
**Module**: BINANCE_CONNECTOR
**Last Audit Sprint**: #003
**Last Audit Date**: 2026-08-01

---

Two staff-only endpoints plus the service layer both they and
`Webhook_Receiver` call. Reference material: shapes and status codes, no
rationale. The reasoning lives in
`docs/architecture/BINANCE_CONNECTOR_BLUEPRINT.md`.

> [!WARNING]
> `POST binance-params/` executes a live order on Binance when
> `[binance].LIVE_TRADING` is true, exactly as the webhook endpoint does. It is
> a manual order-entry surface, not a dry run.

## `POST /binance-connector/binance-params/`

Persists an order-parameter record and executes the corresponding order.

**Auth**: `IsAdminUser` — an authenticated Django staff session. Unlike the
webhook endpoint, this one has a real per-caller identity.

### Request

| Field | Type | Notes |
| :--- | :--- | :--- |
| `exchange` | string <= 30 | Only `BINANCE`, case-insensitively. Uppercased on save. |
| `symbol` | string <= 30 | Trading pair. Uppercased on save. |
| `side` | string <= 30 | `BUY` or `SELL`. Uppercased on save. |
| `type` | string <= 30 | Binance order type, e.g. `MARKET`. Uppercased on save. |
| `size` | decimal(12,6) | Order quantity. |

`BinanceParams.save()` uppercases `exchange`, `symbol`, `side` and `type`, so
the stored record is normalised regardless of what was submitted.

### Responses

| Status | Meaning |
| :--- | :--- |
| `200` | Persisted and accepted by Binance. The raw exchange payload is returned. |
| `400` | Invalid payload, or Binance rejected the order. |
| `403` | Not an authenticated staff user. |
| `500` | Anything else; the message carries no internal detail. |

A successful creation answers `200`, not `201`, even though a row is created.

### Ordering

The record is persisted before the exchange call and is not rolled back when
that call fails, so a `BinanceParams` row records intent rather than execution.
Unlike `Webhook.order_id`, no field here is unique, so nothing prevents the
same parameters being submitted — and executed — twice.

## `GET /binance-connector/status/`

Operational check against the configured Binance account.

**Auth**: `IsAdminUser`.

| Status | Body |
| :--- | :--- |
| `200` | `{"system_status": ..., "user_assets": ...}` |
| `403` | Not an authenticated staff user. |

Both fields come from `BinanceService`, and each is `null` when its call
failed: `get_system_status()` and `get_user_assets()` catch `ClientError` and
return `None`. The endpoint answers `200` either way, so a `null` field means
"the call failed", not "no data" — a caller cannot distinguish an outage from
an empty account.

`user_assets` carries live account balances. The endpoint is staff-only, and
the Swagger UI that documents it is served only when `DEBUG` is true.

## Service layer

`BinanceService.execute_order(symbol, side, order_type, quantity)` is imported
directly by `apps.Webhook_Receiver.views` as the module-level singleton
`binance_service`. It is an in-process call, not HTTP.

| `LIVE_TRADING` | Binance call | Effect |
| :--- | :--- | :--- |
| absent or `false` | `new_order_test` | Validated by Binance, never executed. |
| `true` | `new_order` | **A live order.** |

`BinanceService.client` is built lazily on first use and raises `ValueError`
when `API_KEY` or `API_SECRET` is missing. Because `binance_service` is
instantiated at import, credentials are read once per process and a rotation
takes effect only after a restart.

`base_url` is fixed at `https://api1.binance.com`. There is no testnet setting,
so `new_order_test` validates against production with production credentials.

## Host requirements

| Requirement | Why |
| :--- | :--- |
| `[binance].API_KEY`, `[binance].API_SECRET` | Without them, the first order raises `ValueError`. Read once at import. |
| A staff user | Both endpoints are `IsAdminUser`; no anonymous access exists. |
| `[binance].LIVE_TRADING` | False by default, so nothing trades until it is set. `binance.W001` reports the state at startup. |

---
*Extracted against `views.py`, `serializers.py`, `models.py` and `services.py`,
and checked against the knowledge graph.*
