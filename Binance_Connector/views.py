import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.test import APIRequestFactory
from .serializers import binanceParamsserializers
import requests
import logging
from binance.spot import Spot as BinanceClient
from binance.lib.utils import config_logging
from binance.error import ClientError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from tradingview2exch.settings import config

# Configure logging level
config_logging(logging, logging.DEBUG)


# Get API keys
api_key = config['binance'].get('API_KEY')
api_secret = config['binance'].get('API_SECRET')

# Base URL for Binance API
base_url = 'https://api1.binance.com'

# Initialize Binance client
client = BinanceClient(api_key, api_secret, base_url=base_url)

# Function to check system status


def system_status(client):
    """
    Check the system status of Binance API.

    Args:
        client (BinanceClient): The Binance client instance.

    Returns:
        dict or None: The system status if successful, None otherwise.
    """
    try:
        status = client.system_status()
        logging.info(f"System status: {status}")
        return status
    except ClientError as error:
        logging.error(f"Error checking system status: {error}")
        return None

# Function to get user assets


def user_assets(client):
    """
    Retrieve user assets from Binance API.

    Args:
        client (BinanceClient): The Binance client instance.

    Returns:
        dict or None: The user assets if successful, None otherwise.
    """
    try:
        user_asset = client.user_asset()
        logging.info(f"User Asset: {user_asset}")
        return user_asset
    except ClientError as error:
        logging.error(f"Error getting user assets: {error}")
        return None


# Check system status
system_status(client)

# Get user assets
user_assets(client)

# Define Params API view


class binanceParams(APIView):
    """
    API view to handle Binance parameter submissions.
    """
    # Specify permissions if needed, such as AllowAny or IsAuthenticated
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Recive data to send to Binance",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'exchange': openapi.Schema(type=openapi.TYPE_STRING, description='Exchange associated with the alert', example='BINANCE'),
                'symbol': openapi.Schema(type=openapi.TYPE_STRING, description='Symbol associated with the alert', example='BTCUSDT'),
                'side': openapi.Schema(type=openapi.TYPE_STRING, description='Side associated with the alert (e.g., BUY or SELL)', example='BUY'),
                'type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of alert', example='MARKET'),
                'size': openapi.Schema(type=openapi.TYPE_STRING, description='Size associated with the alert', example='0.00015')
            }
        ),
        responses={
            201: openapi.Response(
                'Data successfully send',
                examples={
                    'application/json': {
                        'message': 'Webhook successfully received',
                        'data': {
                            "symbol": "BTCUSDT",
                            "orderId": 28,
                            "orderListId": -1,  # Unless OCO, value will be -1
                            "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
                            "transactTime": 1507725176595,
                            "price": "0.00000000",
                            "origQty": "10.00000000",
                            "executedQty": "10.00000000",
                            "cummulativeQuoteQty": "10.00000000",
                            "status": "FILLED",
                            "timeInForce": "GTC",
                            "type": "MARKET",
                            "side": "SELL",
                            "workingTime": 1507725176595,
                            "selfTradePreventionMode": "NONE"
                        }
                    }
                }
            ),
            400: 'Bad Request',
            500: 'Internal Server Error'
        },
        operation_id='Binance Params'
    )
    def post(self, request):
        """
        Receive the data to send to Binance.

        Args:
            request (Request): The incoming request object containing the data.

        Returns:
            Response: The response object indicating the result of the operation.
        """
        try:
            serializer = binanceParamsserializers(data=request.data)
            if serializer.is_valid():
                serializer.save()

                # Perform a test order if in DEBUG mode, otherwise perform a real order
                if settings.DEBUG:
                    response = client.new_order_test(
                        symbol=serializer.data.get('symbol'),
                        side=serializer.data.get('side'),
                        type=serializer.data.get('type'),
                        quantity=serializer.data.get('size'),
                    )
                else:
                    response = client.new_order(
                        symbol=serializer.data.get('symbol'),
                        side=serializer.data.get('side'),
                        type=serializer.data.get('type'),
                        quantity=serializer.data.get('size'),
                    )
                logging.info(f"Order response: {response}")
                return Response('completed', status=status.HTTP_200_OK)
            else:
                # Return the errors if the serializer data is not valid
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
            return Response(
                {'error': f"Client error: {error.error_message}"},
                status=status.HTTP_400_BAD_REQUEST
            )
