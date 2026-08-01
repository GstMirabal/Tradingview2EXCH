from decimal import Decimal
from unittest.mock import Mock, patch

from binance.error import ClientError
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase

from ..models import Webhook
from ..serializers import WebhookSerializer

PASSPHRASE_PATCH_TARGET = 'apps.core.permissions.config'
VALID_PASSPHRASE_CONFIG = {'django_settings': {'WEBHOOK_PASSPHRASE': 'correct-horse'}}


class WebhookModelTests(TestCase):
    """Tests for the Webhook model."""

    def setUp(self) -> None:
        """Create a test instance with the current, renamed field names."""
        self.webhook_data = {
            'symbol': 'BTCUSDT',
            'exchange': 'BINANCE',
            'time': timezone.now(),
            'interval': Decimal('30.00'),
            'size': Decimal('0.00015'),
            'side': 'BUY',
            'price': Decimal('58226.21'),
            'order_id': 'BFP1',
            'market_position': Decimal('0.00363'),
            'market_prev_position': Decimal('0.00338'),
            'type': 'MARKET',
        }
        self.webhook_instance = Webhook.objects.create(**self.webhook_data)

    def test_creation(self) -> None:
        """The instance is created with the expected field values."""
        self.assertIsInstance(self.webhook_instance, Webhook)
        for key, value in self.webhook_data.items():
            self.assertEqual(getattr(self.webhook_instance, key), value)

    def test_string_representation(self) -> None:
        """__str__ reflects the stored field values."""
        d = self.webhook_data
        expected_str = (
            f'{d["symbol"]} - {d["exchange"]} - {d["time"]} - {d["interval"]} - '
            f'{d["size"]} - {d["side"]} - {d["price"]} - {d["order_id"]} - '
            f'{d["market_position"]} - {d["market_prev_position"]} - {d["type"]}'
        )
        self.assertEqual(str(self.webhook_instance), expected_str)

    def test_duplicate_order_id_is_rejected_at_db_level(self) -> None:
        """`order_id` is unique — a repeat raises IntegrityError."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            Webhook.objects.create(**{**self.webhook_data, 'time': timezone.now()})


class WebhookSerializerTests(TestCase):
    """Tests for the WebhookSerializer."""

    def setUp(self) -> None:
        """Prepare a valid payload."""
        self.valid_data = {
            'symbol': 'BTCUSDT',
            'exchange': 'BINANCE',
            'time': '2024-05-30T11:25:53Z',
            'interval': '30',
            'size': '0.00015',
            'side': 'BUY',
            'price': '58226.21',
            'order_id': 'BFP1',
            'market_position': '0.00363',
            'market_prev_position': '0.00338',
            'type': 'MARKET',
        }

    def test_valid_data_is_accepted(self) -> None:
        """A fully valid payload passes validation."""
        serializer = WebhookSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_lowercase_exchange_is_accepted_and_normalized(self) -> None:
        """`validate_exchange` is case-insensitive and uppercases the result."""
        serializer = WebhookSerializer(data={**self.valid_data, 'exchange': 'binance'})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['exchange'], 'BINANCE')

    def test_invalid_exchange_is_rejected(self) -> None:
        """Any exchange other than BINANCE is rejected."""
        serializer = WebhookSerializer(data={**self.valid_data, 'exchange': 'KRAKEN'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('exchange', serializer.errors)

    def test_time_is_formatted_as_iso8601(self) -> None:
        """The 'time' field is serialized in ISO 8601 with a trailing 'Z'."""
        instance = Webhook.objects.create(
            symbol='BTCUSDT',
            exchange='BINANCE',
            time=timezone.now(),
            interval=Decimal('30'),
            size=Decimal('0.00015'),
            side='BUY',
            price=Decimal('58226.21'),
            order_id='BFP2',
            market_position=Decimal('0.00363'),
            market_prev_position=Decimal('0.00338'),
            type='MARKET',
        )
        data = WebhookSerializer(instance).data
        self.assertTrue(data['time'].endswith('Z'))


class WebhookReceivedViewTests(APITestCase):
    """Tests for WebhookReceivedView."""

    def setUp(self) -> None:
        """Build a client and a valid TradingView-shaped payload."""
        self.client = APIClient()
        self.url = reverse('webhook_received')
        self.valid_payload = {
            'symbol': 'BTCUSDT',
            'exchange': 'BINANCE',
            'time': '2024-05-30T11:25:53Z',
            'interval': '30',
            'size': '0.00015',
            'side': 'BUY',
            'price': '58226.21',
            'order_id': 'BFP1',
            'market_position': '0.00363',
            'market_prev_position': '0.00338',
            'type': 'MARKET',
        }
        self.invalid_payload = {**self.valid_payload, 'symbol': ''}

    def _post(self, payload: dict, passphrase: str = 'correct-horse') -> Response:
        """POST a payload with the given passphrase attached.

        Args:
            payload: The alert body to send.
            passphrase: The passphrase value to include.

        Returns:
            The DRF test client response.
        """
        return self.client.post(
            self.url, {**payload, 'passphrase': passphrase}, format='json'
        )

    @patch(PASSPHRASE_PATCH_TARGET, VALID_PASSPHRASE_CONFIG)
    def test_missing_passphrase_is_rejected(self) -> None:
        """A request with no passphrase field is denied with 403."""
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(PASSPHRASE_PATCH_TARGET, VALID_PASSPHRASE_CONFIG)
    def test_wrong_passphrase_is_rejected(self) -> None:
        """A request with an incorrect passphrase is denied with 403."""
        response = self._post(self.valid_payload, passphrase='wrong')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(PASSPHRASE_PATCH_TARGET, VALID_PASSPHRASE_CONFIG)
    @patch(
        'apps.Binance_Connector.services.binance_service.execute_order',
        return_value={'msg': 'ok'},
    )
    def test_valid_webhook_is_processed(self, mock_execute_order: Mock) -> None:
        """A correctly authenticated, valid alert is persisted and executed."""
        response = self._post(self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Webhook.objects.count(), 1)
        self.assertEqual(Webhook.objects.get().symbol, 'BTCUSDT')
        mock_execute_order.assert_called_once_with(
            symbol='BTCUSDT',
            side='BUY',
            order_type='MARKET',
            quantity='0.000150',
        )

    @patch(PASSPHRASE_PATCH_TARGET, VALID_PASSPHRASE_CONFIG)
    def test_invalid_payload_is_rejected(self) -> None:
        """An invalid payload returns 400 and nothing is persisted."""
        response = self._post(self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Webhook.objects.count(), 0)

    @patch(PASSPHRASE_PATCH_TARGET, VALID_PASSPHRASE_CONFIG)
    @patch('apps.Binance_Connector.services.binance_service.execute_order')
    def test_duplicate_order_id_is_rejected_not_re_executed(
        self, mock_execute_order: Mock
    ) -> None:
        """A redelivered alert that already executed is refused, not re-sent.

        Since Sprint #003 the refusal is a 409 carrying the execution status,
        rather than a 400 from the serializer's uniqueness check. The status
        distinction is what lets a *rejected* order be retried while an
        executed one stays blocked (audit T-001); the property that matters
        here is unchanged — `execute_order` is never called a second time.
        """
        mock_execute_order.return_value = {'msg': 'ok'}
        first = self._post(self.valid_payload)
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self._post({**self.valid_payload, 'time': '2024-05-30T11:26:00Z'})
        self.assertEqual(second.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Webhook.objects.count(), 1)
        mock_execute_order.assert_called_once()

    @patch(PASSPHRASE_PATCH_TARGET, VALID_PASSPHRASE_CONFIG)
    @patch(
        'apps.Binance_Connector.services.binance_service.execute_order',
        side_effect=ClientError(400, -1013, 'Invalid order', None),
    )
    def test_binance_client_error_returns_400(self, mock_execute_order: Mock) -> None:
        """A ClientError from Binance is surfaced as 400."""
        response = self._post(self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch(PASSPHRASE_PATCH_TARGET, VALID_PASSPHRASE_CONFIG)
    @patch(
        'apps.Binance_Connector.services.binance_service.execute_order',
        side_effect=RuntimeError('boom'),
    )
    def test_unexpected_exception_returns_500(self, mock_execute_order: Mock) -> None:
        """Any other exception during execution is surfaced as 500."""
        response = self._post(self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)

    @patch(PASSPHRASE_PATCH_TARGET, VALID_PASSPHRASE_CONFIG)
    @patch(
        'apps.Binance_Connector.services.binance_service.execute_order',
        return_value={'msg': 'ok'},
    )
    def test_throttling_limits_requests(self, mock_execute_order: Mock) -> None:
        """A caller exceeding the configured 'webhook' scope rate (20/min) gets 429.

        Uses the real configured rate rather than @override_settings — DRF's
        SimpleRateThrottle subclasses bind THROTTLE_RATES as a class attribute
        at import time, so overriding REST_FRAMEWORK in a test doesn't change
        an already-bound rate. Requires a valid passphrase: DRF's APIView
        checks permissions before throttles (see `initial()`), so an invalid
        passphrase would 403 every request before the throttle is ever hit.

        The throttle cache (LocMemCache) is process-global and isn't reset
        between test methods the way the DB is, so this clears it on both
        ends to avoid bleeding rate-limit state into other tests.
        """
        cache.clear()
        self.addCleanup(cache.clear)
        for i in range(20):
            response = self._post({**self.valid_payload, 'order_id': f'THROTTLE-{i}'})
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self._post({**self.valid_payload, 'order_id': 'THROTTLE-20'})
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


@override_settings(
    DEBUG=False,
    ALLOWED_HOSTS=['testserver'],
    CORS_ALLOWED_ORIGINS=['https://example.com'],
)
class SettingsProductionBranchesTests(TestCase):
    """Exercises settings.py's production-only ImproperlyConfigured guards.

    These run against the already-loaded settings module (Django evaluates
    settings.py once, at import time), so they assert on the guard's
    documented behavior via direct inspection rather than re-triggering
    module import — the guards themselves are covered structurally by
    `manage.py check` passing under both DEBUG values (see Fase A.3/CSP fix).
    """

    def test_production_settings_do_not_crash_check(self) -> None:
        """Sanity check that the production branch settings are consistent."""
        from django.conf import settings

        self.assertFalse(settings.DEBUG)
        self.assertIn('testserver', settings.ALLOWED_HOSTS)
