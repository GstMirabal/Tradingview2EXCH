# 🔍 Audit 003: TradingView-to-Binance relay

**Module**: WEBHOOK_RECEIVER, BINANCE_CONNECTOR, CORE, CONFIG
**Audit Sprint**: #003
**Audit Date**: 2026-08-01
**Scope**: the whole backend in its post-reconciliation form — 42 files, Django
6.0.7, DRF 3.17.1, binance-connector 3.13.0.

---

## 1. What makes this repository different

The other two repositories in this programme hold a template and a reusable
app. This one places orders. A defect here does not degrade a control or leak a
field; it moves money, or fails to move it when it should have.

That changes what counts as severe. A misconfiguration that silently stops
trading is as serious as one that trades when it should not, and both appear
below.

Every finding was reproduced by execution.

## 2. Findings

| # | Finding | Severity | Status |
| :--- | :--- | :--- | :--- |
| **T-001** | A rejected order permanently blocks its own retry | **High** | **Fixed** |
| **T-002** | `DEBUG` decides whether an order is real | **High** | **Fixed** |
| T-003 | Throttle counters live in a per-process cache | Medium | Fixed |
| T-004 | Only one of four entrypoints loaded `.env`, and it overwrote the environment | Medium | Fixed |
| T-005 | Order parameters and full exchange responses logged at `INFO` | Medium | Partly fixed |
| T-006 | `.env` and `config.toml` are world-readable | Low | Open |
| T-007 | `ruff` selected neither security nor logging rules | Low | Fixed |
| T-008 | Status endpoint cannot distinguish an outage from an empty account | Low | Open |
| T-009 | Credentials are read once at import | Low | Documented |
| T-010 | `new_order_test` runs against the production endpoint | Low | Documented |
| **T-011** | The container ran a different Python from everything tested | Medium | **Fixed** |

---

### T-001 · A rejected order permanently blocks its own retry — **High**

`WebhookReceivedView.post()` persists the alert with `serializer.save()` and
*then* calls Binance. The row is not rolled back when that call fails, and
`order_id` is unique, so the retry TradingView sends is rejected as a
duplicate.

Reproduced end to end:

```
1) Binance rejects the order   -> HTTP 400
   row left in the database?   -> True
2) TradingView retries         -> HTTP 400
   was Binance called?         -> False
```

The second request never reaches the exchange. The trade is lost, and the
system reports it as already processed.

Any transient exchange condition triggers this: a `LOT_SIZE` filter rejection,
a rate limit, a momentary outage. The uniqueness constraint was added to stop a
duplicate delivery placing a second order — a real risk, correctly identified —
but it also defeats the retry of an order that never executed. The blueprint
describes the protective half and not this one.

**Fixed.** `Webhook.execution_status` records the outcome, and only `REJECTED`
reopens the alert for retry.

The distinction that makes this safe is `REJECTED` against `UNKNOWN`. A timeout
means the request may have reached Binance and filled, with only the response
lost — so resending could place a second real order. Those stay blocked and
need reconciliation against the exchange. Reopening every failure would have
converted lost trades into duplicated ones, which is worse; a regression test
holds that line.

### T-002 · `DEBUG` decides whether an order is real — **High**

```python
if settings.DEBUG:
    response = self.client.new_order_test(**params)
else:
    response = self.client.new_order(**params)
```

Confirmed by execution with a mocked SDK: `DEBUG=True` calls `new_order_test`,
`DEBUG=False` calls `new_order`.

`DEBUG` is a Django presentation-and-security flag. Binding capital movement to
it means two unrelated concerns share one switch, in both directions:

- Any environment running with `DEBUG=false` places live orders — staging, a
  smoke test, a container started with the wrong profile.
- A production host left with `DEBUG=true` silently stops trading while still
  answering `201`. Nothing distinguishes a dry run from a fill in the response.

This is documented in `BINANCE_CONNECTOR_BLUEPRINT.md` §6 as a constraint,
which is accurate but frames a hazard as a safeguard. The behaviour is not
hidden; the coupling is the defect.

**Fixed.** `BINANCE_LIVE_TRADING` is read from `[binance].LIVE_TRADING` and
defaults to false, so `DEBUG=false` no longer means "trade" and trading for
real requires writing it down. `binance.W001` reports the state at startup,
because a project that meant to trade and never set the flag would otherwise
validate every order, execute none, and answer `201` throughout.

The default is deliberately fail-safe, and it is a breaking change: a
deployment that relied on `DEBUG=false` to trade must set `LIVE_TRADING = true`
before upgrading, or it stops trading. Recorded in the ledger as such.

### T-003 · Throttle counters in a per-process cache — Medium · **Fixed**

DRF stores throttle state in the default cache. The `webhook` scope is capped
at 20/min, and that cap is the only limit between a caller holding the
passphrase and an unbounded number of orders. No `CACHES` was declared, so
Django applied a per-process `LocMemCache` and the cap was per worker.

**Calibrated**: `entrypoint.sh` runs gunicorn with no `--workers` flag, so one
worker, so 20/min was 20/min. Nothing was breached. The defect is that adding a
worker for throughput would have made it 40 with nothing reporting the change.

`CACHES` is now declared explicitly: Redis when `REDIS_URL` is set, per-process
otherwise, with the consequence stated at the declaration.

### T-004 · One of four entrypoints loaded `.env` — Medium · **Fixed**

`.env` was read by `manage.py`, which only `manage.py` imports. `wsgi`, `asgi`
and every test runner started without it — and the first two are how this
project is served.

The loader also assigned rather than using `setdefault`, so the file overwrote
the real environment. Proven: exporting `DEBUG=False` and running the loader
left `DEBUG` as `'True'`. Given T-002, that meant the shell could not turn live
trading off.

Moved into `settings.py` with `setdefault`. All four entrypoints now boot, and
`manage.py check --deploy` under a real `DEBUG=False` — unreachable before —
reports nothing.

### T-005 · Order parameters and exchange responses at `INFO` — Medium · **Partly fixed**

Thirteen logging calls built their message with an f-string, evaluated whether
or not the record was emitted. All are converted to lazy `%s` formatting, and
three that discarded the traceback with `str(e)` now use `logger.exception`.

What is **not** changed: `services.py` logs the full order parameters and the
raw Binance response at `INFO`. That is a defensible audit trail for a system
that moves money, and removing it would lose the record of what was actually
sent. It is recorded here so that whoever ships these logs off-host knows the
trading activity travels with them.

`permissions.py` logs `REMOTE_ADDR` on a failed passphrase. Behind a proxy that
is the proxy's address, so the recorded origin is only as accurate as the
forwarding configuration.

### T-006 · Secret files are world-readable — Low

`.env` and `config.toml` are mode `644`. Every account on the host can read the
Binance API key. `600` costs nothing and is the conventional mode for a file
holding credentials.

Not changed here because file modes are a deployment property rather than a
repository one, and altering them on a developer machine proves nothing about
the server.

### T-007 · The linter had no security or logging rules — Low · **Fixed**

`.ruff.toml` selected neither `S` (flake8-bandit) nor `G`
(flake8-logging-format), in a repository that holds exchange credentials.

Both are now enabled. Worth recording: under `S`, the production code came back
**clean** — every finding was a hardcoded password in a test fixture. `G` found
the thirteen calls in T-005.

### T-008 · An outage looks like an empty account — Low

`get_system_status()` and `get_user_assets()` catch `ClientError` and return
`None`, and `GET /binance-connector/status/` answers `200` with those values
either way. A caller reading `"user_assets": null` cannot tell whether the
account is empty or the call failed — on an endpoint whose purpose is knowing
whether things are working.

### T-009 · Credentials are read once at import — Low · **Documented**

`binance_service = BinanceService()` runs at module import, so `API_KEY` and
`API_SECRET` are captured once per process. Rotating a compromised key requires
a restart, not a configuration reload. Stated in
`BINANCE_CONNECTOR_CONTRACT.md`.

### T-010 · `new_order_test` runs against production — Low · **Documented**

`base_url` is fixed at `https://api1.binance.com` with no testnet option, so
the dry-run path validates against the production endpoint using production
credentials. It places no order, but it is not an isolated environment either.

### T-011 · The container ran a Python nothing had tested — Medium · **Fixed**

`docker/DockerFile` pinned `python:3.12-slim` while CI and every local
environment ran 3.13. Each verification in this report — the 71 tests, the
production boot under a real `DEBUG=False`, gunicorn actually serving — was
performed on a runtime the deployment does not use.

**This audit missed it.** Section 4 listed what the protocol could not reach —
live-exchange behaviour, concurrency, the API key's scope — and none of those
is this. The gap was closer to home: the report never compared the runtime it
tested against the runtime it ships.

Surfaced by a Dependabot pull request proposing `3.14-slim`, which would have
widened the divergence rather than closing it. The Dockerfile is now `3.13-slim`
and all three layers agree. Verified by building the image and running Python
inside it (`3.13.14`), not by reading the tag.

The same check found `Django-Pro-Template` already consistent at 3.13, and
`django-users-app` correctly shipping no container at all.

---

## 3. Checked and clean

Recording this matters as much as the findings: it marks where the protocol ran
and produced nothing.

| Technique | Result |
| :--- | :--- |
| Every registered admin form and formset constructed | 4 models, 0 failures |
| Random generators on credential paths | No `random.` anywhere outside tests |
| Logger handler resolution at runtime | `project` resolves to 3 handlers; every module uses that name |
| Clean environment with only `requirements.txt` | Imports and passes `check`; no undeclared dependency |
| Full-history sweep for committed secrets | `config.toml` was tracked in 28 commits, but held 29 `$VAR` references and zero literal secrets |
| Production boot under real `DEBUG=False` | `check --deploy` reports nothing |
| Container runtime matches the tested runtime | Python 3.13 in the image, in CI and in the local environment — checked by running `python -V` inside the built image |
| Bandit rules over production code | Clean |
| Documentation against the knowledge graph | Blueprints accurate; three false claims in the entry point, since corrected |

## 4. Not covered

- **Behaviour against the live exchange.** Every Binance interaction here is
  mocked. Whether the SDK, the account permissions and the symbol filters
  behave as assumed is untested by anything in this repository.
- **Concurrency.** The `409` path is reasoned about and exercised with a
  single-threaded client; no test runs two real requests at once.
- **Whether the strategy is correct.** This audit verifies that the relay does
  what it says. Whether relaying that alert to that order is the right trade is
  not a question it can answer.
- **API key scope.** Whether the configured Binance credentials are restricted
  to trading without withdrawal rights is a property of the exchange account,
  not of this code. It is worth confirming, and cannot be confirmed from here.

---
*Findings feed `docs/roadmaps/GLOBAL_ROADMAP.md`. Both capital-risk findings
are closed, each with a regression test checked to fail without its fix.*
