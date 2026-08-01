# Blueprint: CORE
**File**: `docs/architecture/CORE_BLUEPRINT.md` (RA-06 Option B naming)
**Status**: `RATIFIED`
**Sprint of origin**: #000
**Last Audit Sprint**: #003
**Last Audit Date**: 2026-08-01
**Last Audit Commit SHA**: 13868e0

---

arc42-lite (`rules/documentation_standard.md §5`) — Reference only. This document states current facts, verifiably; it never argues for them. Any decision behind this module's shape lives in a linked ADR, not here.

## 1. Introduction & Goals
`apps.core` is a shared, cross-cutting Django app under `backend/apps/core/`. It holds two concrete building blocks consumed by other apps — a password complexity validator and a webhook shared-secret permission class — plus placeholder `models.py`, `views.py`, and `admin.py` files with no content beyond the Django scaffolding comment. It owns no database table.

## 2. Context & Scope
| Aspect | Value |
| :--- | :--- |
| **Upstream dependencies** | `django.core.exceptions.ValidationError`, `rest_framework.permissions.BasePermission`, `config.settings.config` (TOML-backed settings dict defined in `backend/config/settings.py`) |
| **Downstream consumers** | Django's `AUTH_PASSWORD_VALIDATORS` (registered in `backend/config/settings.py`, consumes `PasswordComplexityValidator`); `apps.Webhook_Receiver.views` (consumes `HasWebhookPassphrase`) |

## 3. Building Block View
| Aspect | Value |
| :--- | :--- |
| **Owns** | `backend/apps/core/` (`validators.py`, `permissions.py`, `apps.py`, `admin.py`, `views.py`, `models.py`, `tests.py`) |
| **Must not touch** | `backend/apps/Binance_Connector/`, `backend/apps/Webhook_Receiver/`, `backend/config/` (composition root — consumes `core`'s building blocks but is not owned by it) |

Contracts (formal interfaces this module exposes):

| Interface | Type | Defined in |
| :--- | :--- | :--- |
| `PasswordComplexityValidator.validate(password, user=None)` | Function (Django password-validator protocol) | `docs/contracts/CORE_CONTRACT.md` |
| `HasWebhookPassphrase.has_permission(request, view)` | Function (DRF permission-class protocol) | `docs/contracts/CORE_CONTRACT.md` |

Data model (summary only): none. `backend/apps/core/models.py` contains only the default Django scaffolding comment — no model classes are defined.

## 4. Runtime View
1. Password validation: any Django `User` creation/change path (e.g. `createsuperuser`, `set_password`) triggers `AUTH_PASSWORD_VALIDATORS`, which includes `apps.core.validators.PasswordComplexityValidator`; it raises `ValidationError` if the password lacks an uppercase letter, a lowercase letter, a digit, or a non-alphanumeric symbol (`backend/apps/core/validators.py`).
2. Webhook authentication: `apps.Webhook_Receiver.views.WebhookReceivedView` declares `permission_classes = [HasWebhookPassphrase]`; on every incoming request, `has_permission` denies non-`POST` methods outright, denies all requests when `config['django_settings']['WEBHOOK_PASSPHRASE']` is unset (logged as a warning), and otherwise compares the request body's `passphrase` field against that configured value using `hmac.compare_digest` (constant-time, avoids a timing side-channel).

## 5. Crosscutting Concepts
- Settings access pattern: `from config.settings import config`, a TOML-backed dict read as `config['section'].get('KEY')`. Individual Django settings constants are not imported directly.
- Logging: both building blocks that log use `logging.getLogger('project')`.

## 6. Non-negotiable Constraints
| Constraint | Verification |
| :--- | :--- |
| `HasWebhookPassphrase` denies all requests by default when `WEBHOOK_PASSPHRASE` is not configured (fails closed, not open) | `backend/apps/core/permissions.py::HasWebhookPassphrase.has_permission` |
| `HasWebhookPassphrase` only evaluates `POST` requests; any other method is denied | `backend/apps/core/permissions.py::HasWebhookPassphrase.has_permission` |
| Passphrase comparison is constant-time (`hmac.compare_digest`), not `==` | `backend/apps/core/permissions.py::HasWebhookPassphrase.has_permission` |
| `PasswordComplexityValidator` requires uppercase + lowercase + digit + symbol, all four | `backend/apps/core/validators.py::PasswordComplexityValidator.validate` |

## 7. Decisions
No ADR is currently on file for this module.

## 8. Glossary
| Term | Meaning in this module |
| :--- | :--- |
| `WEBHOOK_PASSPHRASE` | Shared secret read from `config.toml`'s `[django_settings]` section, compared against the `passphrase` field of an incoming webhook POST body. |
| `config` | Module-level TOML-backed dict exposed by `backend/config/settings.py`, read via `config['section'].get('KEY')`. |

---
*A module without a ratified Blueprint cannot enter Execution (agents.md §0). C4 Level 3 not required — only 3 containers exist under the declared `backend/apps/` root, under the 5-container safety floor (`rules/documentation_standard.md §2.1` points 6/8); Level 3 stays advisory-only for this project.*
