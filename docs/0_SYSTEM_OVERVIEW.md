# System Overview: Tradingview2EXCH
**Last Audit Sprint**: #000
**Last Audit Date**: 2026-07-27
**Last Audit Commit SHA**: 9fad6e6

This is the **Documentation Entry Point**. `agents.md §0 (Entry Point)` requires every session to read this file before anything else. It is intentionally short — for the full component inventory, see the topology map maintained inside `docs/active_state.json` (`topology_map` key).

---

## 1. What this is
Tradingview2EXCH is a **backend-only Django trading webhook relay**. It receives trading alerts fired from TradingView, validates and translates them, and forwards the resulting order intents to the Binance API. This project adopted the **Token-Optimized Agent Pipeline (`.agents`)** framework as a git submodule (pinned `v4.2.1`) at Sprint #000, onboarded under **Scenario C** (mature project, no prior docs, zero prior agentic traces) per `.agents/workflows/standardization_workflow.md` Phase 6 — Full Reverse Engineering.

## 2. Architecture at a glance (C4 Level 1-2)

> Deviation note: `agents.md §1 (technical_clarity)` restricts Mermaid/ASCII diagrams in favor of Markdown tables. The C4 diagrams below are rendered as tables instead of the Mermaid blocks the template placeholder implies.

**Level 1 — Context**: this system and what it talks to outside its own boundary.

| Actor / External System | Relationship to Tradingview2EXCH |
| :--- | :--- |
| TradingView (external, alert source) | Sends HTTP webhook alerts consumed by `Webhook_Receiver`. |
| Binance API (external exchange) | Receives order/trade requests issued by `Binance_Connector`; returns execution results. |
| Operator / Trader (human) | Authors TradingView alert configurations upstream; consumes relay state via the Django admin (`core` app). |

**Level 2 — Container**: the deployable/functional pieces this system is built from.

| Container | Location | Role |
| :--- | :--- | :--- |
| Django project config | `backend/config/` | `settings.py`, `urls.py` — wires installed apps, database, environment. |
| Core app | `backend/apps/core/` | Shared/cross-cutting domain logic. |
| Webhook Receiver app | `backend/apps/Webhook_Receiver/` | Ingests and validates inbound TradingView alerts; confirmed wired in `settings.py` INSTALLED_APPS and `urls.py`. |
| Binance Connector app | `backend/apps/Binance_Connector/` | Translates validated alerts into Binance API calls; confirmed wired in `settings.py` INSTALLED_APPS and `urls.py`. |
| Containerization | `docker/DockerFile`, `docker-compose.yml` | Runtime packaging for the backend (and its datastore, per compose services). |
| Runtime config | `config.toml` (root) | App-level runtime configuration, distinct from Django settings. |

Component-level (Level 3) detail is advisory only for this stack: `backend/apps/` currently holds 3 containers (`core`, `Binance_Connector`, `Webhook_Receiver`), under the 5-container safety floor in `rules/documentation_standard.md §2.1` point 6. Per-module `[MODULE]_BLUEPRINT.md` content is out of scope for this scaffold pass — owned by `doc-orchestrator`.

## 3. Sprint #001 remediation
The legacy root-level `Binance_Connector/`, `Webhook_Receiver/`, `tradingview2exch/`, and root `manage.py` flagged at onboarding (Sprint #000) were confirmed to be more than dead code — Docker's `entrypoint.sh` actually resolved to the legacy, unauthenticated `tradingview2exch/` project in production. Sprint #001 deleted all of it, fixed the deploy path to `backend/`, purged a publicly-leaked `SECRET_KEY` from git history, and renamed several identifiers to governance casing (`docs/decisions/ADR-0001-governance-casing-rename.md`). See `docs/walkthroughs/BACKEND_MIGRATION_WALKTHROUGH.md` for the full account.

## 4. The governance hierarchy
| Layer | Location | Role |
| :--- | :--- | :--- |
| **Governance Rules** | `.agents/agents.md` | The absolute, transversal rules. Nothing overrides this. |
| **Rules** | `.agents/rules/*.md` | Domain-specific standards (QA, topology, skills, security, documentation). |
| **Workflows** | `.agents/workflows/*.md` | Step-by-step protocols, invoked as `/agents:<name>` slash commands. |
| **Subagents** | `.agents/agents/*.md` | The roles that execute workflow steps (Principal, Orchestrator, QA, Tester, Topology Mapper, etc.). |
| **Skills** | `.agents/skills/*/` | Concrete tools subagents call into (linters, scaffolders, auditors). |

## 5. How a session starts
Run `/agents:start`. It will:
1. Read `.agents/agents.md` and this file (Zero-Memory anchor).
2. Verify the Claude Code bridge (`.agents/scripts/install_claude.sh`) — already installed, `.claude/` populated.
3. Resume from `docs/active_state.json` (Zero Coordinate) — this is the first seed, produced during this onboarding pass.
4. Hand off to the Principal Agent for Planning (Sprint 000 or first real sprint, per the Approval Gate).

## 6. Where state lives
- `docs/active_state.json` — this project's own session anchor. Never committed to `.agents`. Holds `topology_map` (flat string paths, maintained by `topology-mapper`) and the sibling `code_containers` declaration.
- `CHANGELOG.md` (root) — the **Master Ledger**: sprint entries at close, version seals at deployment. Strictly separate jurisdiction from `.agents/CHANGELOG.md` (framework evolution).
- `docs/roadmaps/`, `docs/sprints/`, `docs/walkthroughs/`, `docs/architecture/`, `docs/contracts/`, `docs/decisions/`, `docs/guides/`, `docs/standards/` — this project's own historical record, currently scaffolded empty (physical topology only — content is `doc-orchestrator`'s and `orchestrator`'s jurisdiction in subsequent pipeline phases).
- `.agents/docs/` — the framework's own (separate) self-documentation; not this project's.

## 7. Full inventory
For the flat structural inventory (what physically exists, current legacy/dead flags), read the `topology_map` and `legacy_flags` keys inside `docs/active_state.json`.
