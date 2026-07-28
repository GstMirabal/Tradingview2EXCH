from decimal import Decimal
from unittest.mock import Mock, patch

from binance.error import ClientError
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..models import BinanceParams
from ..serializers import BinanceParamsSerializer
from ..services import BinanceService, binance_service

User = get_user_model()


class BinanceParamsModelTests(TestCase):
    """Tests for the BinanceParams model."""

    def setUp(self) -> None:
        """Create a test instance with lowercase input data."""
        self.params_data = {
            'exchange': 'binance',
            'symbol': 'btcusdt',
            'side': 'buy',
            'type': 'market',
            'size': Decimal('0.00015'),
        }
        self.params_instance = BinanceParams.objects.create(**self.params_data)

    def test_creation(self) -> None:
        """The instance is created and is of the right type."""
        self.assertIsInstance(self.params_instance, BinanceParams)

    def test_uppercase_conversion(self) -> None:
        """Every char field is uppercased by save(); size is untouched."""
        self.assertEqual(self.params_instance.exchange, 'BINANCE')
        self.assertEqual(self.params_instance.symbol, 'BTCUSDT')
        self.assertEqual(self.params_instance.side, 'BUY')
        self.assertEqual(self.params_instance.type, 'MARKET')
        self.assertEqual(self.params_instance.size, Decimal('0.000150'))

    def test_string_representation(self) -> None:
        """__str__ reflects the (uppercased) stored values."""
        expected_str = f'BINANCE - BTCUSDT - BUY - MARKET - {self.params_instance.size}'
        self.assertEqual(str(self.params_instance), expected_str)


class BinanceParamsSerializerTests(APITestCase):
    """Tests for the BinanceParamsSerializer."""

    def setUp(self) -> None:
        """Prepare valid and invalid payloads."""
        self.valid_data = {
            'exchange': 'BINANCE',
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'type': 'MARKET',
            'size': '0.00015',
        }
        self.invalid_data = {**self.valid_data, 'exchange': 'NOTBINANCE'}

    def test_valid_data_is_accepted(self) -> None:
        """A fully valid payload passes validation."""
        serializer = BinanceParamsSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_lowercase_exchange_is_accepted_and_normalized(self) -> None:
        """`validate_exchange` is case-insensitive and uppercases the result."""
        serializer = BinanceParamsSerializer(
            data={**self.valid_data, 'exchange': 'binance'}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['exchange'], 'BINANCE')

    def test_invalid_exchange_is_rejected(self) -> None:
        """Any exchange other than BINANCE is rejected."""
        serializer = BinanceParamsSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('exchange', serializer.errors)

    def test_serialized_size_uses_fixed_decimal_places(self) -> None:
        """DRF serializes `size` (decimal_places=6) with a fixed 6-decimal string."""
        instance = BinanceParams.objects.create(
            **{**self.valid_data, 'size': Decimal('0.00015')}
        )
        data = BinanceParamsSerializer(instance).data
        self.assertEqual(data['size'], '0.000150')

    def test_exchange_help_text(self) -> None:
        """The 'exchange' field carries its documented help text."""
        serializer = BinanceParamsSerializer()
        self.assertEqual(
            serializer.fields['exchange'].help_text,
            'Field to store the exchange associated with the alert.',
        )


class BinanceParamsViewTests(APITestCase):
    """Tests for BinanceParamsView (IsAdminUser-gated order execution)."""

    def setUp(self) -> None:
        """Build an authenticated staff client plus a valid/invalid payload."""
        self.client = APIClient()
        self.url = reverse('binance_params')
        self.staff_user = User.objects.create_user(
            username='staffuser', password='TestPassword123!', is_staff=True
        )
        self.valid_payload = {
            'exchange': 'BINANCE',
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'type': 'MARKET',
            'size': '0.00015',
        }
        self.invalid_payload = {**self.valid_payload, 'exchange': 'NOTBINANCE'}
        # The view calls the module-level `binance_service` singleton, not a
        # fresh instance — give it fake credentials so `.client` doesn't
        # short-circuit with "credentials missing" before the mocked SDK
        # method is ever reached.
        self._original_api_key = binance_service.api_key
        self._original_api_secret = binance_service.api_secret
        binance_service.api_key = 'fake-key'
        binance_service.api_secret = 'fake-secret'
        binance_service._client = None

    def tearDown(self) -> None:
        """Restore the singleton's original credentials."""
        binance_service.api_key = self._original_api_key
        binance_service.api_secret = self._original_api_secret
        binance_service._client = None

    def test_anonymous_request_is_rejected(self) -> None:
        """An unauthenticated request is denied before reaching the view logic."""
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_non_staff_request_is_rejected(self) -> None:
        """A regular (non-staff) authenticated user is denied."""
        User.objects.create_user(username='regular', password='TestPassword123!')
        self.client.login(username='regular', password='TestPassword123!')
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        'binance.spot.Spot.new_order_test', return_value={'msg': 'Test order created'}
    )
    @override_settings(DEBUG=True)
    def test_valid_payload_debug_mode(self, mock_new_order_test: Mock) -> None:
        """In DEBUG mode, a valid payload triggers the dry-run test order."""
        self.client.login(username='staffuser', password='TestPassword123!')
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_new_order_test.assert_called_once_with(
            symbol=self.valid_payload['symbol'],
            side=self.valid_payload['side'],
            type=self.valid_payload['type'],
            quantity='0.000150',
        )

    @patch('binance.spot.Spot.new_order', return_value={'msg': 'Order created'})
    @override_settings(DEBUG=False)
    def test_valid_payload_production_mode(self, mock_new_order: Mock) -> None:
        """Outside DEBUG mode, a valid payload places a real order."""
        self.client.login(username='staffuser', password='TestPassword123!')
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_new_order.assert_called_once_with(
            symbol=self.valid_payload['symbol'],
            side=self.valid_payload['side'],
            type=self.valid_payload['type'],
            quantity='0.000150',
        )

    def test_invalid_payload_is_rejected(self) -> None:
        """An invalid exchange returns 400 without calling Binance at all."""
        self.client.login(username='staffuser', password='TestPassword123!')
        response = self.client.post(self.url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('exchange', response.data)

    @patch(
        'binance.spot.Spot.new_order_test',
        side_effect=ClientError(400, -1013, 'Invalid order', None),
    )
    @override_settings(DEBUG=True)
    def test_binance_client_error_returns_400(self, mock_new_order_test: Mock) -> None:
        """A ClientError from Binance is surfaced as 400, not 500."""
        self.client.login(username='staffuser', password='TestPassword123!')
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        mock_new_order_test.assert_called_once()

    @patch('binance.spot.Spot.new_order_test', side_effect=RuntimeError('boom'))
    @override_settings(DEBUG=True)
    def test_unexpected_exception_returns_500(self, mock_new_order_test: Mock) -> None:
        """Any other exception is surfaced as 500."""
        self.client.login(username='staffuser', password='TestPassword123!')
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class BinanceStatusViewTests(APITestCase):
    """Tests for BinanceStatusView."""

    def setUp(self) -> None:
        """Build an authenticated staff client."""
        self.client = APIClient()
        self.url = reverse('binance_status')
        User.objects.create_user(
            username='staffuser', password='TestPassword123!', is_staff=True
        )

    def test_anonymous_request_is_rejected(self) -> None:
        """An unauthenticated request is denied."""
        response = self.client.get(self.url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    @patch(
        'apps.Binance_Connector.services.BinanceService.get_user_assets',
        return_value={'assets': []},
    )
    @patch(
        'apps.Binance_Connector.services.BinanceService.get_system_status',
        return_value={'status': 0},
    )
    def test_staff_request_returns_status(
        self, mock_status: Mock, mock_assets: Mock
    ) -> None:
        """A staff request returns both system status and user assets."""
        self.client.login(username='staffuser', password='TestPassword123!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['system_status'], {'status': 0})
        self.assertEqual(response.data['user_assets'], {'assets': []})


class BinanceServiceTests(TestCase):
    """Tests for the BinanceService Service Layer, independent of the view."""

    def setUp(self) -> None:
        """Build a service instance with fake credentials."""
        self.service = BinanceService()
        self.service.api_key = 'fake-key'
        self.service.api_secret = 'fake-secret'

    @patch('binance.spot.Spot.new_order_test', return_value={'msg': 'ok'})
    @override_settings(DEBUG=True)
    def test_execute_order_debug_mode_uses_test_order(
        self, mock_new_order_test: Mock
    ) -> None:
        """DEBUG mode routes through the dry-run SDK call."""
        response = self.service.execute_order('btcusdt', 'buy', 'market', '0.001')
        self.assertEqual(response, {'msg': 'ok'})
        mock_new_order_test.assert_called_once_with(
            symbol='BTCUSDT', side='BUY', type='MARKET', quantity='0.001'
        )

    @patch('binance.spot.Spot.new_order', return_value={'msg': 'ok'})
    @override_settings(DEBUG=False)
    def test_execute_order_production_mode_uses_real_order(
        self, mock_new_order: Mock
    ) -> None:
        """Outside DEBUG mode, the real order-placement SDK call is used."""
        response = self.service.execute_order('btcusdt', 'buy', 'market', '0.001')
        self.assertEqual(response, {'msg': 'ok'})
        mock_new_order.assert_called_once()

    def test_missing_credentials_raises_value_error(self) -> None:
        """Accessing the client without credentials fails fast."""
        self.service.api_key = None
        self.service.api_secret = None
        with self.assertRaises(ValueError):
            _ = self.service.client

    @patch('binance.spot.Spot.system_status', return_value={'status': 0})
    def test_get_system_status_success(self, mock_status: Mock) -> None:
        """A successful system status call returns the raw payload."""
        self.assertEqual(self.service.get_system_status(), {'status': 0})

    @patch(
        'binance.spot.Spot.system_status',
        side_effect=ClientError(400, -1000, 'error', None),
    )
    def test_get_system_status_failure_returns_none(self, mock_status: Mock) -> None:
        """A failed system status call returns None instead of raising."""
        self.assertIsNone(self.service.get_system_status())

    @patch('binance.spot.Spot.user_asset', return_value={'assets': []})
    def test_get_user_assets_success(self, mock_assets: Mock) -> None:
        """A successful asset lookup returns the raw payload."""
        self.assertEqual(self.service.get_user_assets(), {'assets': []})

    @patch(
        'binance.spot.Spot.user_asset',
        side_effect=ClientError(400, -1000, 'error', None),
    )
    def test_get_user_assets_failure_returns_none(self, mock_assets: Mock) -> None:
        """A failed asset lookup returns None instead of raising."""
        self.assertIsNone(self.service.get_user_assets())
