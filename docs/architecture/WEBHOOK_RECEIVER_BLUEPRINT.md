# Blueprint: WEBHOOK_RECEIVER
**File**: `docs/architecture/WEBHOOK_RECEIVER_BLUEPRINT.md` (RA-06 Option B naming)
**Status**: `RATIFIED`
**Sprint of origin**: #000
**Last Audit Sprint**: #001
**Last Audit Date**: 2026-07-28
**Last Audit Commit SHA**: 9fad6e6

---

arc42-lite (`rules/documentation_standard.md §5`) — Reference only. This document states current facts, verifiably; it never argues for them. Any decision behind this module's shape lives in a linked ADR, not here.

## 1. Introduction & Goals
`apps.Webhook_Receiver` (`backend/apps/Webhook_Receiver/`) is the external-facing intake boundary for TradingView alerts. It exposes one REST endpoint that authenticates the caller via a shared passphrase, persists the raw alert, and — for `exchange == 'BINANCE'` — forwards it directly to `apps.Binance_Connector`'s Service Layer for execution, in the same request/response cycle.

## 2. Context & Scope
| Aspect | Value |
| :--- | :--- |
| **Upstream dependencies** | `apps.core.permissions.HasWebhookPassphrase` (authentication boundary); `apps.Binance_Connector.services.binance_service` (direct in-process import, not an HTTP call to `Binance_Connector`'s own endpoint) |
| **Downstream consumers** | External: TradingView (or any client sending alert webhooks over HTTP). No internal app imports from `Webhook_Receiver`. |

## 3. Building Block View
| Aspect | Value |
| :--- | :--- |
| **Owns** | `backend/apps/Webhook_Receiver/` (`models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`, `apps.py`, `migrations/`, `test/`) |
| **Must not touch** | `backend/apps/Binance_Connector/` internals beyond importing `services.binance_service`; `backend/apps/core/` internals beyond importing `permissions.HasWebhookPassphrase` |

Contracts (formal interfaces this module exposes):

| Interface | Type | Defined in |
| :--- | :--- | :--- |
| `POST /webhook-receiver/webhook/` (`WebhookReceivedView`) | REST | Not yet published — no `docs/contracts/WEBHOOK_RECEIVER_CONTRACT.md` exists at this audit |

Data model (summary only):
- `Webhook`: one persisted raw TradingView alert — `symbol`, `exchange`, `time` (`DateTimeField`, `db_index=True`), `interval` (`DecimalField`), `size` (`DecimalField`), `side` (`CharField`), `price` (`DecimalField`), `order_id` (`CharField`, `unique=True`), `market_position` (`DecimalField`), `market_prev_position` (`DecimalField`), `type` (`CharField`).

## 4. Runtime View
1. Client sends `POST /webhook-receiver/webhook/` with `symbol`, `exchange`, `time`, `interval`, `size`, `side`, `price`, `order_id`, `market_position`, `market_prev_position`, `type`.
2. `HasWebhookPassphrase.has_permission` (owned by `apps.core`) denies the request if the method is not `POST`, if `WEBHOOK_PASSPHRASE` is not configured (`config.toml`'s `[django_settings]` section), or if the request body's `passphrase` field does not match the configured value (constant-time comparison).
3. `WebhookSerializer` validates the payload; `validate_exchange` accepts `'BINANCE'` case-insensitively.
4. `WebhookReceivedView.post()` persists the validated record via `serializer.save()`. A duplicate `order_id` fails the serializer's automatic uniqueness check (from `unique=True`) and returns `HTTP 400` before Binance is ever called — protects against TradingView's webhook-delivery retries placing a duplicate real order. A same-`order_id` race between two concurrent requests is caught at the DB level (`IntegrityError` → `HTTP 409`) as a secondary guarantee.
5. The view calls `apps.Binance_Connector.services.binance_service.execute_order(...)` directly — this does not create or touch a `Binance_Connector.BinanceParams` row; it calls straight into the Service Layer, bypassing `Binance_Connector`'s own model/serializer/view. Only `'BINANCE'` is currently a supported exchange (enforced by the serializer); multi-exchange routing is not implemented.
6. The Binance response (or a caught `ClientError` / generic `Exception`) is returned to the caller as JSON (`HTTP 201` on success).

## 5. Crosscutting Concepts
- Authentication boundary: the passphrase check (`HasWebhookPassphrase`, owned by `apps.core`) is this app's only access control; there is no per-caller identity, only a shared secret.
- Logging: `logging.getLogger('project')`.

## 6. Non-negotiable Constraints
| Constraint | Verification |
| :--- | :--- |
| Only `exchange == 'BINANCE'` (case-insensitive) is routed to order execution | `backend/apps/Webhook_Receiver/serializers.py::validate_exchange` |
| A `WebhookReceivedView` request never populates `Binance_Connector`'s `BinanceParams` table — the call path goes straight to `BinanceService`, not through `Binance_Connector`'s own view/serializer | `backend/apps/Webhook_Receiver/views.py` (imports `services.binance_service`, never `Binance_Connector.serializers` or `Binance_Connector.models`) |
| Passphrase validation runs before the request body is deserialized (DRF evaluates `permission_classes` ahead of `post()`) | `backend/apps/Webhook_Receiver/views.py`; `backend/apps/core/permissions.py` |
| `order_id` is unique — a repeated value is rejected (`HTTP 400` via the serializer, or `HTTP 409` in a concurrent-request race), never a second order execution | `backend/apps/Webhook_Receiver/models.py::Webhook.order_id` |

## 7. Decisions
- `docs/decisions/ADR-0001-governance-casing-rename.md`: renamed `webhook`→`Webhook`, `webhookSerializer`→`WebhookSerializer`, `webhookReceived`→`WebhookReceivedView`, `orderId`→`order_id`, `marketPosition`→`market_position`, `marketPrevPosition`→`market_prev_position`, and the `webhook_Received`→`webhook_received` URL name.

## 8. Glossary
| Term | Meaning in this module |
| :--- | :--- |
| `Webhook` | Django model persisting one raw TradingView alert. |
| `passphrase` | Shared secret field expected in the POST body; validated by `apps.core`'s `HasWebhookPassphrase` against `config.toml`'s `[django_settings].WEBHOOK_PASSPHRASE`. |
| Alert | A single TradingView-originated payload describing a trade signal (symbol/side/size/price/etc.). |

---
*A module without a ratified Blueprint cannot enter Execution (agents.md §0). C4 Level 3 not required — only 3 containers exist under the declared `backend/apps/` root, under the 5-container safety floor (`rules/documentation_standard.md §2.1` points 6/8); Level 3 stays advisory-only for this project.*
