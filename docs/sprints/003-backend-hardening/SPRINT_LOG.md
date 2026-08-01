# 📋 Sprint Log: #003 — Backend / Hardening

**Sprint ID**: 003
**Stack**: backend
**Layer**: hardening
**Opened**: 2026-08-01
**Closed**: 2026-08-01
**Branch**: `ai-sprint/003`

---

## 1. Purpose

Bring this repository onto the shared scaffolding, then audit what it actually
does. It is the third Django host in the programme and the one with real
exposure: it holds exchange credentials and it places orders.

## 2. Order of work, and why it mattered

Documentation first, against a rebuilt graph. That order was not ceremony — it
set up everything that followed:

1. The graph rebuild produced the file inventory the audit worked from.
2. Writing the contracts forced reading each endpoint end to end, which is
   where the two capital-risk findings came from. Neither was visible in a
   blueprint; both needed following a request through to its exchange call.
3. Only then did the scaffolding and dependency work happen, so the audit ran
   against the code in its final shape rather than one about to change.

## 3. Work completed

| Step | Item |
| :--- | :--- |
| 1 | Graph rebuilt; 42 of 42 backend files covered |
| 1 | Three false statements corrected in `0_SYSTEM_OVERVIEW.md` |
| 1 | `active_state.json` schema fixed so the structural check runs |
| 1 | Three contracts written for four endpoints and two internal interfaces |
| 2 | pytest harness: `pytest.ini`, `settings_test.py`, `requirements-dev.txt` |
| 2 | `.env` loading moved into `settings.py` with `setdefault` |
| 3 | CI calls the shared reusable workflow; `.editorconfig` copied |
| 3 | `CACHES` declared explicitly (SECTION 6.5) |
| 4 | Eight scaffolding dependencies raised; `toml` dropped; `dependabot.yml` |
| 5 | Deep audit: ten findings, `AUDIT_003_TRADING_RELAY.md` |
| 6 | Both capital-risk findings closed, with regression tests |
| 7 | Credential review; `SECURITY.md` extended |
| 8 | `flask` topic replaced with `django`; description and homepage set |

## 4. The two that mattered

**A rejected order could never be retried.** The row was written before the
exchange call and never rolled back, and `order_id` is unique, so the retry
TradingView sent was refused as a duplicate. Any transient exchange condition —
a `LOT_SIZE` rejection, a rate limit — lost the trade permanently while
reporting it as already processed.

**`DEBUG` decided whether an order was real.** A Django presentation flag bound
to capital movement, cutting both ways: every `DEBUG=false` environment traded,
and a production host left on `DEBUG=true` stopped trading in silence while
still answering `201`.

Neither was hidden. The second was documented in a blueprint — accurately, but
framed as a safeguard rather than a hazard.

## 5. The distinction that made the first fix safe

Reopening every failed order for retry would have been the obvious fix and the
wrong one. A timeout does not prove non-execution: the request may have reached
Binance and filled with only the response lost, so resending could place a
second real order.

`REJECTED` means the exchange answered and refused, and only that reopens an
alert. `UNKNOWN` stays blocked for a human to reconcile. A regression test
holds that line specifically — reverting `UNKNOWN` to `REJECTED` fails it.

## 6. Metrics

| Measure | Before | After |
| :--- | ---: | ---: |
| Entrypoints that boot unaided | 1 of 4 | 4 of 4 |
| Tests | 63 (`manage.py test` only) | 70, under pytest |
| Contracts | 0 | 3 |
| `ruff` rule sets | 13 | 15 (`S`, `G`) |
| `production check --deploy` | Unreachable | Clean |
| Capital-risk findings open | 2 (unknown) | 0 |

## 7. Operator actions required

**Set `LIVE_TRADING = true` under `[binance]` before deploying if you expect
this to trade.** It is false by default now, and a deployment that relied on
`DEBUG=false` to place orders will stop placing them. `manage.py check` reports
`binance.W001` while it is off.

`chmod 600 .env config.toml` on the host. They are world-readable by default,
and every account on the machine can otherwise read the API key.

## 8. Deferred

| Item | Why |
| :--- | :--- |
| T-006 file permissions | A deployment property; changing a mode on a developer machine proves nothing about the server |
| T-008 `null` in the status endpoint | An outage reads as an empty account. Real, no capital risk |
| T-010 no testnet endpoint | `new_order_test` validates against production with production credentials. Documented rather than changed |
| Live-exchange behaviour | Every Binance interaction here is mocked. Nothing in this repository tests the real SDK against the real API |
| API key scope | Whether the key is restricted to trading without withdrawal is a property of the exchange account, not of this code |
