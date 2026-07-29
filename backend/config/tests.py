"""Tests for the module-level ImproperlyConfigured guards in settings.py.

These guards run once, at import time, so exercising them means reloading
the settings module with a patched `envtoml.load` return value and asserting
the reload itself raises — not calling a function at request time.
"""

import copy
import importlib
from typing import Any
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

import config.settings as settings_module

BASE_CONFIG: dict[str, Any] = {
    'django_settings': {
        'DJANGO_SECRET_KEY': 'test-secret-key',
        'DEBUG': False,
        'ALLOWED_HOSTS': 'example.com',
        'CORS_ALLOWED_ORIGINS': 'https://example.com',
        'WEBHOOK_PASSPHRASE': 'test-passphrase',
    },
    'DB': {'SQLITE_NAME': 'db.sqlite3'},
    'project_logging': {'PROJECT_LOGS_DIR': 'backend/logs'},
    'email_settings': {
        'EMAIL_HOST': 'smtp.example.com',
        'EMAIL_PORT': 587,
        'EMAIL_USE_TLS': True,
        'EMAIL_HOST_USER': 'user',
        'EMAIL_HOST_PASSWORD': 'pass',
    },
    'binance': {'API_KEY': 'k', 'API_SECRET': 's'},
}


def _reload_settings_with(overrides: dict[str, dict[str, Any]]) -> None:
    """Reload config.settings with BASE_CONFIG merged with the given overrides.

    Args:
        overrides: A mapping of TOML section name to keys to override.
    """
    merged = copy.deepcopy(BASE_CONFIG)
    for section, values in overrides.items():
        merged.setdefault(section, {}).update(values)
    with patch('envtoml.load', return_value=merged):
        importlib.reload(settings_module)


class SettingsGuardsTests(SimpleTestCase):
    """Each production-only ImproperlyConfigured guard in settings.py."""

    def tearDown(self) -> None:
        """Reload with the real repo config so the rest of the suite is unaffected."""
        importlib.reload(settings_module)

    def test_missing_secret_key_raises(self) -> None:
        """An empty DJANGO_SECRET_KEY is always fatal, DEBUG or not."""
        with self.assertRaises(ImproperlyConfigured):
            _reload_settings_with({'django_settings': {'DJANGO_SECRET_KEY': ''}})

    def test_missing_allowed_hosts_in_production_raises(self) -> None:
        """DEBUG=False with an empty ALLOWED_HOSTS is fatal."""
        with self.assertRaises(ImproperlyConfigured):
            _reload_settings_with(
                {'django_settings': {'DEBUG': False, 'ALLOWED_HOSTS': ''}}
            )

    def test_missing_cors_origins_in_production_raises(self) -> None:
        """DEBUG=False with an empty CORS_ALLOWED_ORIGINS is fatal."""
        with self.assertRaises(ImproperlyConfigured):
            _reload_settings_with(
                {'django_settings': {'DEBUG': False, 'CORS_ALLOWED_ORIGINS': ''}}
            )

    def test_missing_email_config_in_production_raises(self) -> None:
        """DEBUG=False with an incomplete [email_settings] section is fatal."""
        with self.assertRaises(ImproperlyConfigured):
            _reload_settings_with(
                {
                    'django_settings': {'DEBUG': False},
                    'email_settings': {'EMAIL_HOST': ''},
                }
            )

    def test_valid_production_config_does_not_raise(self) -> None:
        """A fully-populated production config reloads cleanly (control case)."""
        _reload_settings_with({})

    def test_string_debug_false_resolves_to_real_boolean(self) -> None:
        """A string `DEBUG="False"` (as envtoml produces it) resolves to `False`.

        `envtoml` substitutes an unset/text `$DEBUG` into a quoted TOML
        string, so the real pipeline never hands settings.py an actual
        Python bool — BASE_CONFIG's `'DEBUG': False` above uses a native
        bool, which would have hidden this exact bug. This test mimics
        the real return shape (strings) to catch it.
        """
        _reload_settings_with({'django_settings': {'DEBUG': 'False'}})
        self.assertIs(settings_module.DEBUG, False)  # noqa: FBT003
        # Production hardening (Section 3) must actually engage.
        self.assertTrue(settings_module.SECURE_SSL_REDIRECT)
        self.assertIn('DIRECTIVES', settings_module.CONTENT_SECURITY_POLICY)

    def test_string_debug_true_resolves_to_real_boolean(self) -> None:
        """`DEBUG="True"` (a string) must resolve to the boolean `True`."""
        _reload_settings_with({'django_settings': {'DEBUG': 'True'}})
        self.assertIs(settings_module.DEBUG, True)  # noqa: FBT003

    def test_string_email_use_tls_false_resolves_to_real_boolean(self) -> None:
        """`EMAIL_USE_TLS="False"` (a string) must resolve to boolean `False`."""
        _reload_settings_with(
            {
                'django_settings': {'DEBUG': 'False'},
                'email_settings': {'EMAIL_USE_TLS': 'False'},
            }
        )
        self.assertIs(settings_module.EMAIL_USE_TLS, False)  # noqa: FBT003
