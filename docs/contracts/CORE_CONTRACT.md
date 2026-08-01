# 📄 Contract: CORE
**File**: `docs/contracts/CORE_CONTRACT.md` (RA-06 Option B naming)
**Module**: CORE
**Last Audit Sprint**: #003
**Last Audit Date**: 2026-08-01

---

`apps.core` exposes no HTTP surface. It publishes two interfaces that other
components plug into, both conforming to a framework protocol rather than to
one this project defines. Reference material only; the reasoning lives in
`docs/architecture/CORE_BLUEPRINT.md`.

## `PasswordComplexityValidator.validate(password, user=None)`

Django password-validator protocol. Registered in `AUTH_PASSWORD_VALIDATORS`
(`backend/config/settings.py`), fourth in a chain of five.

**Returns** `None` when the password passes. **Raises** `ValidationError`
otherwise, with the code identifying which rule failed:

| Rule | Pattern | Error code |
| :--- | :--- | :--- |
| At least one uppercase letter | `[A-Z]` | `password_no_upper` |
| At least one lowercase letter | `[a-z]` | `password_no_lower` |
| At least one digit | `[0-9]` | `password_no_digit` |
| At least one special character | `[\W_]` | `password_no_symbol` |

Rules are evaluated in that order and the first failure raises, so a password
breaking several reports only the first.

`user` is accepted because the protocol requires it and is not read. Length is
not checked here — `MinimumLengthValidator` earlier in the chain owns that, and
`PwnedPasswordsValidator` after it owns breach checking.

`get_help_text()` returns the combined requirement as one sentence, which
Django renders in forms.

## `HasWebhookPassphrase.has_permission(request, view)`

DRF permission-class protocol. Attached to `WebhookReceivedView`, and the only
access control on the endpoint that places orders.

**Returns** `True` only when all of the following hold:

| Condition | Otherwise |
| :--- | :--- |
| `request.method` is `POST` | `False`, with no logging |
| `[django_settings].WEBHOOK_PASSPHRASE` is configured and non-empty | `False`, and a `WARNING` is logged. **Fails closed** |
| `request.data['passphrase']` is a `str` | `False`, with no logging |
| That value matches, compared with `hmac.compare_digest` | `False`, and a `WARNING` logs the rejected attempt with `REMOTE_ADDR` |

The comparison is constant-time, so a wrong passphrase leaks no information
about how much of it was right.

`REMOTE_ADDR` is the immediate peer. Behind a proxy or load balancer that is
the proxy's address, so the logged origin is only as accurate as the
deployment's forwarding configuration.

DRF evaluates permissions before `post()`, so an unauthenticated body is never
deserialized and never reaches the database.

## Consumers

| Interface | Consumed by |
| :--- | :--- |
| `PasswordComplexityValidator` | Django's `AUTH_PASSWORD_VALIDATORS` |
| `HasWebhookPassphrase` | `apps.Webhook_Receiver.views.WebhookReceivedView` |

`apps.core` owns no database table and defines no model.

---
*Extracted against `validators.py`, `permissions.py` and `settings.py`, and
checked against the knowledge graph.*
