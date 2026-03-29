from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.response import Response
from django.urls import reverse
from unittest.mock import patch
from ..models import webhook
from ..serializers import webhookSerializer
import requests
import logging

# Configure logger for outputting information
logger = logging.getLogger(__name__)


class WebhookModelTests(TestCase):
    """
    Tests for the webhook model
    """

    def setUp(self):
        # Test data to create a webhook instance
        self.webhook_data = {
            'symbol': 'BTCUSDT',
            'exchange': 'BINANCE',
            'time': timezone.now(),
            'interval': 30.00,
            'size': 0.00015,
            'side': 'BUY',
            'price': 58226.21,
            'orderId': 'BFP1',
            'marketPosition': 0.00363,
            'marketPrevPosition': 0.00338,
            'type': 'MARKET'
        }
        # Create a webhook instance with the test data
        self.webhook_instance = webhook.objects.create(**self.webhook_data)

    def tearDown(self):
        # Delete the webhook instance created during the test
        self.webhook_instance.delete()

    def testWebhookCreation(self):
        """
        Ensure we can create a webhook instance with valid data
        """
        # Verify that the instance is of the webhook class
        self.assertIsInstance(self.webhook_instance, webhook)
        # Verify that the instance values match the test data
        for key, value in self.webhook_data.items():
            self.assertEqual(getattr(self.webhook_instance, key), value)

    def testWebhookStringRepresentation(self):
        """
        Ensure the string representation of the webhook instance is correct
        """
        expected_str = (f"{self.webhook_data['symbol']} - {self.webhook_data['exchange']} - "
                        f"{self.webhook_data['time']} - {self.webhook_data['interval']} - "
                        f"{self.webhook_data['size']} - {self.webhook_data['side']} - "
                        f"{self.webhook_data['price']} - {self.webhook_data['orderId']} - "
                        f"{self.webhook_data['marketPosition']} - {self.webhook_data['marketPrevPosition']} - "
                        f"{self.webhook_data['type']}")
        self.assertEqual(str(self.webhook_instance), expected_str)


class WebhookReceivedTests(APITestCase):
    """
    Tests for the webhookReceived view
    """

    def setUp(self):
        logger.info("Setting up the test case")
        self.client = APIClient()
        self.url = reverse('webhook_Received')
        # Valid payload for creating a webhook
        self.valid_payload = {
            'symbol': 'BTCUSDT',
            'exchange': 'BINANCE',
            'time': '2024-05-30T11:25:53Z',
            'interval': '30',
            'size': '0.00015',
            'side': 'BUY',
            'price': '58226.21',
            'orderId': 'BFP1',
            'marketPosition': '0.00363',
            'marketPrevPosition': '0.00338',
            'type': 'MARKET'
        }
        # Invalid payload for creating a webhook
        self.invalid_payload = {
            'symbol': '',
            'exchange': 'BINANCE',
            'time': '2024-05-30T11:25:53Z',
            'interval': '30',
            'size': '0.00015',
            'side': 'BUY',
            'price': '58226.21',
            'orderId': 'BFP1',
            'marketPosition': '0.00363',
            'marketPrevPosition': '0.00338',
            'type': 'MARKET'
        }

    def tearDown(self):
        logger.info("Tearing down the test case")
        # Delete all Alerta instances created during the test
        webhook.objects.all().delete()

    @patch('Binance_Connector.views.binanceParams')
    def testValidWebhook(self, mock_binanceParams):
        """
        Ensure we can create a new webhook with valid payload
        """
        mock_binanceParams.as_view.return_value = Response(
            {'message': 'BinanceParams called successfully'}, status=status.HTTP_201_CREATED)
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(webhook.objects.count(), 1)
        self.assertEqual(webhook.objects.get().symbol, 'BTCUSDT')

    def testInvalidWebhook(self):
        """
        Ensure we cannot create a new webhook with invalid payload
        """
        response = self.client.post(
            self.url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('requests.post')
    def testInternalServerError(self, mock_post):
        """
        Ensure we handle request exceptions and return a 500 internal server error
        """
        mock_post.side_effect = requests.exceptions.RequestException(
            'Error connecting to Binance_Connector')
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)

    def testGenericExceptionHandling(self):
        """
        Ensure we handle generic exceptions and return a 500 internal server error
        """
        with patch.object(webhookSerializer, 'save', side_effect=Exception('Test exception')):
            response = self.client.post(
                self.url, self.valid_payload, format='json')
            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.data)
