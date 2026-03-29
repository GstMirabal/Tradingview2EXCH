from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.test import APIRequestFactory
from .serializers import webhookSerializer
import requests
import logging
from Binance_Connector.views import binanceParams
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class webhookReceived(APIView):
    """
    API view to handle receiving new webhooks.
    """
    # Specify permissions if needed, such as AllowAny or IsAuthenticated
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Receive a new webhook",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'symbol': openapi.Schema(type=openapi.TYPE_STRING, description='Symbol associated with the alert', example='BTCUSDT'),
                'exchange': openapi.Schema(type=openapi.TYPE_STRING, description='Exchange associated with the alert', example='BINANCE'),
                'time': openapi.Schema(type=openapi.FORMAT_DATETIME, description='Time the alert was generated', example='2024-05-30T11:25:53Z'),
                'interval': openapi.Schema(type=openapi.TYPE_STRING, description='Time interval associated with the alert', example='30'),
                'size': openapi.Schema(type=openapi.TYPE_STRING, description='Size associated with the alert', example='0.00015'),
                'side': openapi.Schema(type=openapi.TYPE_STRING, description='Side associated with the alert (e.g., BUY or SELL)', example='BUY'),
                'price': openapi.Schema(type=openapi.TYPE_STRING, description='Price in USDT of the alert', example='58226.21'),
                'orderId': openapi.Schema(type=openapi.TYPE_STRING, description='Order ID associated with the alert', example='BFP1'),
                'marketPosition': openapi.Schema(type=openapi.TYPE_STRING, description='Market position', example='0.00363'),
                'marketPrevPosition': openapi.Schema(type=openapi.TYPE_STRING, description='Previous market position', example='0.00338'),
                'type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of alert', example='MARKET')
            }
        ),
        responses={
            201: openapi.Response(
                'Webhook successfully received',
                examples={
                    'application/json': {
                        'message': 'Webhook successfully received',
                        'data': {
                            'symbol': 'BTCUSDT',
                            'side': 'BUY',
                            'type': 'MARKET',
                            'size': '0.00015',
                        }
                    }
                }
            ),
            400: 'Bad Request',
            500: 'Internal Server Error'
        },
        operation_id='Receive Webhook'
    )
    def post(self, request):
        """
        Receive a new alert.

        Args:
            request (Request): The incoming request object containing the alert data.

        Returns:
            Response: The response object indicating the result of the operation.
        """
        try:
            # Deserialize the incoming JSON to the Alerta model using the serializer
            serializer = webhookSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                # Extract parameters from the newly created webhook to send to Binance_Connector
                binanceParams_data = {
                    'exchange': serializer.data.get('exchange'),
                    'symbol': serializer.data.get('symbol'),
                    'side': serializer.data.get('side'),
                    'type': serializer.data.get('type'),
                    'size': serializer.data.get('size')
                }
                # Create an internal POST request to /Binance_Conector/Params/ with the validated data
                factory = APIRequestFactory()
                internal_request = factory.post(
                    'Binance_Connector/binanceParams/', binanceParams_data, format='json')
                binanceParams_view = binanceParams.as_view()
                response = binanceParams_view(internal_request)

                # Return the response from the Params class
                return response
            else:
                # Return the errors if the serializer data is not valid
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            # Handle request exceptions and return a 500 internal server error if something goes wrong
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Handle other exceptions and return a 500 internal server error if something goes wrong
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
