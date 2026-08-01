# 📄 Contract: WEBHOOK_RECEIVER
**File**: `docs/contracts/WEBHOOK_RECEIVER_CONTRACT.md` (RA-06 Option B naming)
**Module**: WEBHOOK_RECEIVER
**Last Audit Sprint**: #003
**Last Audit Date**: 2026-08-01

---

The single endpoint through which an external caller causes this system to place
an order. Reference material: shapes and status codes, no rationale. The
reasoning lives in `docs/architecture/WEBHOOK_RECEIVER_BLUEPRINT.md` and the
ADRs it links.

> [!WARNING]
> A successful call to this endpoint executes a live order on Binance when
> `[binance].LIVE_TRADING` is true. It is false by default — see *Execution
> mode* below.

## `POST /webhook-receiver/webhook/`

Persists a TradingView alert and forwards it to Binance in the same
request/response cycle.

**Auth**: shared passphrase in the request body. No per-caller identity exists;
every caller presenting the secret is the same principal.

### Request

`Content-Type: application/json`. Every field is required.

| Field | Type | Notes |
| :--- | :--- | :--- |
| `passphrase` | string | Checked against `[django_settings].WEBHOOK_PASSPHRASE`, constant-time. Consumed by the permission class and **not persisted** — it is not a field on the `Webhook` model. |
| `symbol` | string <= 30 | Trading pair, e.g. `BTCUSDT`. Passed to Binance uppercased. |
| `exchange` | string <= 30 | Only `BINANCE` is accepted, case-insensitively. Stored uppercased. |
| `time` | datetime | ISO 8601, `YYYY-MM-DDTHH:MM:SSZ`. |
| `interval` | decimal(5,2) | Chart interval the alert fired on. |
| `size` | decimal(12,6) | Order quantity. Sent to Binance as-is. |
| `side` | string <= 30 | `BUY` or `SELL`. Passed uppercased. |
| `price` | decimal(12,6) | Price at alert time. Recorded only — **not** sent to Binance. |
| `order_id` | string <= 30 | **Unique.** The idempotency key; see *Retries*. |
| `market_position` | decimal(12,6) | Strategy position after the alert. Recorded only. |
| `market_prev_position` | decimal(12,6) | Strategy position before the alert. Recorded only. |
| `type` | string <= 30 | Binance order type, e.g. `MARKET`. Passed uppercased. |

Only `symbol`, `side`, `type` and `size` reach Binance. The rest are persisted
for the record and never leave this system.

### Responses

| Status | Meaning | Body |
| :--- | :--- | :--- |
| `201` | Alert persisted and accepted by Binance. | `{"message": "...", "exchange_response": <raw Binance payload>}` |
| `400` | Invalid payload, a repeated `order_id`, or Binance rejected the order. | Serializer errors, or `{"error": "Binance Client Error: ..."}` |
| `403` | Missing, malformed or incorrect `passphrase`; or the method is not `POST`. | DRF permission denial. |
| `409` | Two concurrent requests carried the same `order_id`; the database constraint caught the loser. | `{"error": "This order_id has already been processed."}` |
| `500` | Anything else. The message is fixed and carries no internal detail. | `{"error": "Internal error processing webhook."}` |

`400` covers two unrelated situations — a malformed payload and an order Binance
refused. A caller tells them apart by body shape, not by status.

### Execution mode

`execute_order` selects its Binance call from `BINANCE_LIVE_TRADING`, set by
`[binance].LIVE_TRADING` in `config.toml`:

| `LIVE_TRADING` | Binance call | Effect |
| :--- | :--- | :--- |
| absent or `false` | `new_order_test` | Validated by Binance, never executed. No capital moves. |
| `true` | `new_order` | **A live order.** Capital moves. |

The default is not trading. `manage.py check` reports `binance.W001` when the
key is **absent**, because a project that meant to trade and never set it would
otherwise validate every order, execute none, and answer `201` throughout —
with a strategy that simply never seems to fill. Writing `false` is a decision
and draws no warning.

Until Sprint #003 this derived from `DEBUG`, so any environment running
`DEBUG=false` placed real orders, and a production host left with `DEBUG=true`
stopped trading in silence. A deployment upgrading across that change must set
`LIVE_TRADING = true` **before** deploying, or it stops trading.

### Retries

`order_id` is the idempotency key, and what a repeated one means depends on
what happened to the first attempt. Each alert carries an `execution_status`:

| Status | Meaning | A repeated `order_id` is |
| :--- | :--- | :--- |
| `PENDING` | Received; the exchange call has not returned | Refused, `409` |
| `EXECUTED` | The exchange accepted the order | Refused, `409` |
| `REJECTED` | The exchange answered and refused it | **Accepted** — the order provably did not execute, so it is retried on the same row |
| `UNKNOWN` | The call failed without proving non-execution | Refused, `409` |

`UNKNOWN` is the case worth understanding. A timeout means the request may have
reached Binance and filled, with only the response lost. Resending would risk a
second real order, so it stays blocked and needs a human to reconcile against
the exchange.

Until Sprint #003 every repeat was refused alike, so an order Binance rejected
could never be placed at all: the trade was lost and reported as a duplicate.

### Rate limit

Throttle scope `webhook`, 20 requests per minute, declared in
`DEFAULT_THROTTLE_RATES`. It applies per caller as DRF resolves them; with a
single shared passphrase and no identity, that is effectively per IP.

## Host requirements

| Requirement | Why |
| :--- | :--- |
| `[django_settings].WEBHOOK_PASSPHRASE` | Unset, the permission class denies every request and logs a warning. It fails closed. |
| `[binance].API_KEY`, `[binance].API_SECRET` | Read once at import, when the module-level `binance_service` is constructed. Rotating them requires a process restart. |
| `DEBUG` set deliberately | It selects between a dry run and a live order. See *Execution mode*. |

---
*Extracted against `views.py`, `serializers.py`, `models.py` and
`core/permissions.py`, and checked against the knowledge graph.*
