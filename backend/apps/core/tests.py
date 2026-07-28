# backend/apps/core/tests.py

"""Tests for the project's foundational configuration and shared components."""

from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.test import RequestFactory, TestCase, override_settings

from apps.core.permissions import HasWebhookPassphrase
from apps.core.validators import PasswordComplexityValidator

User = get_user_model()


class ConfigurationSmokeTest(TestCase):
    """A simple smoke test to ensure the project can start and tests can run."""

    def test_settings_load_correctly(self) -> None:
        """Verify that settings are loaded without raising errors."""
        self.assertTrue(expr=True)


class DatabaseConnectionTest(TestCase):
    """Verifies the database configuration and the default user model."""

    def test_database_connection_and_user_model(self) -> None:
        """Verify DB connectivity and that the default auth.User model is in use.

        This project deliberately uses Django's built-in user model — no
        custom `users` app exists or is planned (see settings.py Section 8.1).
        """
        self.assertEqual(settings.AUTH_USER_MODEL, 'auth.User')
        try:
            user = User.objects.create_user(
                username='testuser', password='TestPassword123!'
            )
            self.assertIsNotNone(user)
        except Exception as e:  # noqa: BLE001
            self.fail(
                'User creation failed, indicating a problem with the DB '
                f'connection or the default user model setup. Original error: {e}'
            )


class ProductionSecurityHeadersTest(TestCase):
    """Verifies key security headers are set in simulated production environment."""

    @override_settings(DEBUG=False, SECURE_SSL_REDIRECT=False)
    def test_security_headers_are_present_in_production(self) -> None:
        """Ensure security headers are active in production environments."""
        response = self.client.get('/admin/login/', follow=True)

        self.assertIn('X-Frame-Options', response.headers)
        self.assertEqual(response.headers['X-Frame-Options'], 'DENY')

        self.assertIn('X-Content-Type-Options', response.headers)
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')

        # HSTS header is only sent over HTTPS, so it's not checked here.


class HasWebhookPassphraseTests(TestCase):
    """Tests for the shared webhook passphrase permission."""

    def setUp(self) -> None:
        """Build a bare request factory and the permission instance under test."""
        self.factory = RequestFactory()
        self.permission = HasWebhookPassphrase()

    def _make_post_request(self, passphrase: str | None) -> HttpRequest:
        """Build a DRF-style request carrying the given passphrase.

        Args:
            passphrase: The passphrase to include in the body, or None to omit it.

        Returns:
            A request object with a DRF-compatible `.data` accessor.
        """
        request = self.factory.post('/webhook-receiver/webhook/')
        data = {} if passphrase is None else {'passphrase': passphrase}
        request.data = data
        return request

    @patch(
        'apps.core.permissions.config',
        {'django_settings': {'WEBHOOK_PASSPHRASE': 'correct-horse'}},
    )
    def test_valid_passphrase_grants_permission(self) -> None:
        """A matching passphrase is accepted."""
        request = self._make_post_request('correct-horse')
        self.assertTrue(self.permission.has_permission(request, None))

    @patch(
        'apps.core.permissions.config',
        {'django_settings': {'WEBHOOK_PASSPHRASE': 'correct-horse'}},
    )
    def test_invalid_passphrase_denies_permission(self) -> None:
        """A mismatched passphrase is rejected."""
        request = self._make_post_request('wrong-passphrase')
        self.assertFalse(self.permission.has_permission(request, None))

    @patch(
        'apps.core.permissions.config',
        {'django_settings': {'WEBHOOK_PASSPHRASE': 'correct-horse'}},
    )
    def test_missing_passphrase_denies_permission(self) -> None:
        """A request with no passphrase field at all is rejected."""
        request = self._make_post_request(None)
        self.assertFalse(self.permission.has_permission(request, None))

    @patch('apps.core.permissions.config', {'django_settings': {}})
    def test_unconfigured_passphrase_denies_all_requests(self) -> None:
        """If WEBHOOK_PASSPHRASE is not configured, every request is denied."""
        request = self._make_post_request('anything')
        self.assertFalse(self.permission.has_permission(request, None))

    @patch(
        'apps.core.permissions.config',
        {'django_settings': {'WEBHOOK_PASSPHRASE': 'correct-horse'}},
    )
    def test_non_post_method_denies_permission(self) -> None:
        """Only POST requests are ever considered."""
        request = self.factory.get('/webhook-receiver/webhook/')
        request.data = {'passphrase': 'correct-horse'}
        self.assertFalse(self.permission.has_permission(request, None))

    @patch(
        'apps.core.permissions.config',
        {'django_settings': {'WEBHOOK_PASSPHRASE': 'correct-horse'}},
    )
    def test_non_string_passphrase_denies_permission(self) -> None:
        """A non-string passphrase value (e.g. a list) cannot crash the comparison."""
        request = self.factory.post('/webhook-receiver/webhook/')
        request.data = {'passphrase': ['not', 'a', 'string']}
        self.assertFalse(self.permission.has_permission(request, None))


class PasswordComplexityValidatorTests(TestCase):
    """Tests for each individual rule of the custom password validator."""

    def setUp(self) -> None:
        """Instantiate the validator under test."""
        self.validator = PasswordComplexityValidator()

    def test_valid_password_passes(self) -> None:
        """A password satisfying every rule raises nothing."""
        self.validator.validate('Str0ng!Passw0rd')

    def test_missing_uppercase_fails(self) -> None:
        """A password with no uppercase letter is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate('str0ng!passw0rd')
        self.assertEqual(ctx.exception.code, 'password_no_upper')

    def test_missing_lowercase_fails(self) -> None:
        """A password with no lowercase letter is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate('STR0NG!PASSW0RD')
        self.assertEqual(ctx.exception.code, 'password_no_lower')

    def test_missing_digit_fails(self) -> None:
        """A password with no digit is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate('Strong!Password')
        self.assertEqual(ctx.exception.code, 'password_no_digit')

    def test_missing_symbol_fails(self) -> None:
        """A password with no special character is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate('Str0ngPassw0rd')
        self.assertEqual(ctx.exception.code, 'password_no_symbol')

    def test_get_help_text_is_non_empty(self) -> None:
        """The help text shown to users is a non-empty string."""
        self.assertTrue(self.validator.get_help_text())
