from django.test import TestCase, override_settings
from rest_framework import serializers
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from ..models import binanceParams
from ..serializers import binanceParamsserializers
from unittest.mock import patch, Mock
from binance.error import ClientError
import logging


class BinanceParamsModelTests(TestCase):

    def setUp(self):
        # Test data to create a binanceParams instance
        self.params_data = {
            'exchange': 'binance',
            'symbol': 'btcusdt',
            'side': 'buy',
            'type': 'market',
            'size': 0.00015
        }
        # Create a binanceParams instance with the test data
        self.params_instance = binanceParams.objects.create(**self.params_data)

    def tearDown(self):
        # Delete the binanceParams instance created during the test
        self.params_instance.delete()

    def testbinanceParamsCreation(self):
        """
        Ensure we can create a binanceParams instance with valid data.
        """
        self.assertIsInstance(self.params_instance, binanceParams)
        for key, value in self.params_data.items():
            self.assertEqual(getattr(self.params_instance,
                             key).upper(), str(value).upper())

    def testbinanceParamsUppercaseConversion(self):
        """
        Ensure all string fields are converted to uppercase before saving.
        """
        self.assertEqual(self.params_instance.exchange,
                         self.params_data['exchange'].upper())
        self.assertEqual(self.params_instance.symbol,
                         self.params_data['symbol'].upper())
        self.assertEqual(self.params_instance.side,
                         self.params_data['side'].upper())
        self.assertEqual(self.params_instance.type,
                         self.params_data['type'].upper())

    def testbinanceParamsStringRepresentation(self):
        """
        Ensure the string representation of the binanceParams instance is correct.
        """
        expected_str = (f"{self.params_data['exchange'].upper()} - {self.params_data['symbol'].upper()} - "
                        f"{self.params_data['side'].upper()} - {self.params_data['type'].upper()} - "
                        f"{self.params_data['size']}")
        self.assertEqual(str(self.params_instance), expected_str)


class BinanceParamsSerializersTests(APITestCase):

    def setUp(self):
        # Test data to create a binanceParams instance
        self.valid_data = {
            'exchange': 'BINANCE',
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'type': 'MARKET',
            'size': 0.00015
        }
        self.invalid_data = {
            'exchange': 'NOTBINANCE',
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'type': 'MARKET',
            'size': 0.00015
        }

    def testValidDataSerialization(self):
        """
        Ensure that valid data is serialized correctly.
        """
        serializer = binanceParamsserializers(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data['exchange'], self.valid_data['exchange'])
        self.assertEqual(
            serializer.validated_data['symbol'], self.valid_data['symbol'])
        self.assertEqual(
            serializer.validated_data['side'], self.valid_data['side'])
        self.assertEqual(
            serializer.validated_data['type'], self.valid_data['type'])
        self.assertEqual(
            serializer.validated_data['size'], self.valid_data['size'])

    def testInvalidDataSerialization(self):
        """
        Ensure that invalid data is not serialized and raises a validation error.
        """
        serializer = binanceParamsserializers(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('exchange', serializer.errors)
        self.assertEqual(
            serializer.errors['exchange'][0], 'Exchange is not allowed')

    def testSerializedDataFields(self):
        """
        Ensure that all fields are included in the serialized data.
        """
        instance = binanceParams.objects.create(**self.valid_data)
        serializer = binanceParamsserializers(instance)
        data = serializer.data
        for field in self.valid_data.keys():
            self.assertIn(field, data)
            self.assertEqual(data[field], str(self.valid_data[field]) if isinstance(
                self.valid_data[field], float) else self.valid_data[field])

    def testExchangeFieldHelpText(self):
        """
        Ensure that the help text for the 'exchange' field is correct.
        """
        serializer = binanceParamsserializers()
        self.assertEqual(serializer.fields['exchange'].help_text,
                         'Field to store the exchange associated with the alert.')


class BinanceParamsViewTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = 'binanceParams'
        self.valid_payload = {
            'exchange': 'BINANCE',
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'type': 'MARKET',
            'size': '0.00015'
        }
        self.invalid_payload = {
            'exchange': 'NOTBINANCE',
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'type': 'MARKET',
            'size': '0.00015'
        }

    @patch('binance.spot.Spot.new_order_test', return_value={'msg': 'Test order created'})
    @override_settings(DEBUG=True)
    def testValidPayloadDebug(self, mock_new_order_test):
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_new_order_test.assert_called_once_with(
            symbol=self.valid_payload['symbol'],
            side=self.valid_payload['side'],
            type=self.valid_payload['type'],
            quantity=self.valid_payload['size']
        )

    @patch('binance.spot.Spot.new_order', return_value={'msg': 'Order created'})
    @override_settings(DEBUG=False)
    def testValidPayloadProduction(self, mock_new_order):
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_new_order.assert_called_once_with(
            symbol=self.valid_payload['symbol'],
            side=self.valid_payload['side'],
            type=self.valid_payload['type'],
            quantity=self.valid_payload['size']
        )

    def testInvalidPayload(self):
        response = self.client.post(
            self.url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('exchange', response.data)

    @patch('binance.spot.Spot.new_order_test', side_effect=ClientError(400, -1013, "Invalid order", None))
    @override_settings(DEBUG=True)
    def testClientErrorHandling(self, mock_new_order_test):
        response = self.client.post(
            self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        mock_new_order_test.assert_called_once()

    def testSerializerValidation(self):
        serializer = binanceParamsserializers(data=self.valid_payload)
        self.assertTrue(serializer.is_valid())
        serializer = binanceParamsserializers(data=self.invalid_payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn('exchange', serializer.errors)
