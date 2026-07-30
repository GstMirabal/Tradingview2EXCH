# 📜 ADR-0001: Rename models/fields/serializers/views to governance-compliant casing
**Status**: `Accepted`
**Date**: 2026-07-28
**Triggers**: 2 (`rules/documentation_standard.md §3.1`)

---

## 1. Context

`agents.md §1` mandates `snake_case` for variables/functions and `PascalCase` for classes. The Django-Pro migration (commit `48bad3b`) introduced a Service Layer and security hardening but left the original model/field/class names untouched: `binanceParams`, `webhook`, `webhookReceived`, `binanceParamsserializers`, and model fields `orderId`, `marketPosition`, `marketPrevPosition`. Because `Webhook`'s serializer uses `fields = '__all__'`, these Python identifiers are also the exact JSON keys in the wire contract that TradingView alerts (configured by the project owner outside this repo) already send to `POST /webhook-receiver/webhook/` — e.g. `orderId` in the alert payload.

## 2. Decision

Rename all affected classes and fields to governance-compliant casing in a single pass, applied via Django migrations (`Binance_Connector/migrations/0002_...py`, `Webhook_Receiver/migrations/0003_...py`):

| Before | After |
| :--- | :--- |
| `binanceParams` (model) | `BinanceParams` |
| `webhook` (model) | `Webhook` |
| `orderId` (field) | `order_id` |
| `marketPosition` (field) | `market_position` |
| `marketPrevPosition` (field) | `market_prev_position` |
| `binanceParamsserializers` | `BinanceParamsSerializer` |
| `webhookSerializer` | `WebhookSerializer` |
| `binanceParams` / `webhookReceived` (view classes) | `BinanceParamsView` / `WebhookReceivedView` |
| `binanceAdmin` / `webhookAdmin` | `BinanceParamsAdmin` / `WebhookAdmin` |
| URL names `binanceParams` / `webhook_Received` | `binance_params` / `webhook_received` |

The Django **app package names** (`Binance_Connector/`, `Webhook_Receiver/`) are explicitly **not** renamed in this pass — an app-label rename is a data-migration-class risk (rewrites `django_content_type`/`auth_permission` rows and the app label recorded in every historical migration), categorically different from a code-identifier rename, and out of scope here.

## 3. Consequences

- The Python codebase is now consistent with `agents.md §1`'s naming rule.
- **Breaking**: the JSON contract the `Webhook` serializer exposes changes key names (`orderId` → `order_id`, `marketPosition` → `market_position`, `marketPrevPosition` → `market_prev_position`). Any TradingView alert already configured against the old field names will submit a payload that fails serializer validation (`400 Bad Request`) until its "Message" template is updated to the new field names.
- The rename was applied via `RenameModel`/`RenameField` migrations, which preserve any existing row data (no data loss) — verified against the local `db.sqlite3`, which held zero rows in both affected tables at the time of this change.
- A same-lowercase model rename (`binanceParams`→`BinanceParams`, `webhook`→`Webhook`) hits a Django migration-state bug (`ProjectState.rename_model` inserts the renamed model under a key identical to the one it then deletes), reproduced directly against this project's installed Django version. Both migrations route through a throwaway intermediate name (e.g. `TempBinanceParamsCasingFix`) to avoid it — a two-step rename, not a single clean one.
- `docs/architecture/BINANCE_CONNECTOR_BLUEPRINT.md` and `WEBHOOK_RECEIVER_BLUEPRINT.md` are updated to reference the new names and link this ADR.

---
*Immutable once Accepted — a changed decision gets a new ADR that supersedes this one, never an in-place edit.*
