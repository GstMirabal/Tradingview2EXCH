# backend/apps/core/tests.py

"""Configuration and Sanity Tests for the Core App.

This file contains tests to verify that the project's foundational
configuration is correct and robust.
"""

from django.test import TestCase, override_settings
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class ConfigurationSmokeTest(TestCase):
    """A simple smoke test to ensure the project can start and tests can run."""

    def test_settings_load_correctly(self) -> None:
        """Verify that settings are loaded without raising errors."""
        self.assertTrue(expr=True)


class DatabaseConnectionTest(TestCase):
    """Verifies the database configuration and custom user model interaction."""

    def test_database_connection_and_user_model(self) -> None:
        """Verify database connectivity and custom user model integration."""
        self.assertEqual(settings.AUTH_USER_MODEL, 'users.User')
        try:
            user = User.objects.create_user(
                username='testuser', password='TestPassword123!'
            )
            self.assertIsNotNone(user)
        except Exception as e:  # noqa: BLE001
            self.fail(
                'User creation failed, indicating a problem with the CC DB '
                f'connection or AUTH_USER_MODEL setup. Original error: {e}'
            )


class ProductionSecurityHeadersTest(TestCase):
    """Verifies key security headers are set in simulated production environment."""
    @override_settings(DEBUG=False, SECURE_SSL_REDIRECT=False)
    def test_security_headers_are_present_in_production(self) -> None:
        """Ensure security headers are active in production environments."""
        response = self.client.get('/admin/login/', follow=True)

        # We verify headers NOT dependent on an HTTPS connection.
        # These are set by the SecurityMiddleware regardless of the protocol.
        self.assertIn('X-Frame-Options', response.headers)
        self.assertEqual(response.headers['X-Frame-Options'], 'DENY')

        self.assertIn('X-Content-Type-Options', response.headers)
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')

        # NOTE: HSTS header is only sent over HTTPS, so we don't test for it here.
        # self.assertIn('Strict-Transport-Security', response.headers)
