import logging

from binance.error import ClientError
from django.db import IntegrityError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.Binance_Connector.services import binance_service
from apps.core.permissions import HasWebhookPassphrase

from .serializers import WebhookSerializer

logger = logging.getLogger('project')


class WebhookReceivedView(APIView):
    """API view to handle receiving new webhooks from TradingView."""

    permission_classes = [HasWebhookPassphrase]

    @swagger_auto_schema(
        operation_description="Receive a new webhook and forward it to Binance",
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
                'order_id': openapi.Schema(type=openapi.TYPE_STRING, description='Order ID associated with the alert', example='BFP1'),
                'market_position': openapi.Schema(type=openapi.TYPE_STRING, description='Market position', example='0.00363'),
                'market_prev_position': openapi.Schema(type=openapi.TYPE_STRING, description='Previous market position', example='0.00338'),
                'type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of alert', example='MARKET')
            }
        ),
        responses={
            201: 'Webhook successfully processed and sent to exchange',
            400: 'Bad Request',
            409: 'Duplicate order_id — alert already processed',
            500: 'Internal Server Error'
        },
        operation_id='Receive Webhook'
    )
    def post(self, request: Request) -> Response:
        """Validate an incoming TradingView alert and execute it on Binance.

        Only 'BINANCE' is currently a supported exchange (enforced by the
        serializer); routing to additional exchanges is not implemented yet.

        Args:
            request: The incoming DRF request carrying the alert payload.

        Returns:
            201 with the Binance response on success, 400 on invalid payload
            or a Binance client error, 409 if `order_id` was already processed
            (protects against TradingView's webhook retries placing a
            duplicate real order), 500 on an unexpected failure.
        """
        serializer = WebhookSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Invalid webhook payload: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save()
        except IntegrityError:
            logger.warning(f"Duplicate order_id rejected: {request.data.get('order_id')}")
            return Response(
                {'error': 'This order_id has already been processed.'},
                status=status.HTTP_409_CONFLICT
            )

        try:
            response = binance_service.execute_order(
                symbol=serializer.data.get('symbol'),
                side=serializer.data.get('side'),
                order_type=serializer.data.get('type'),
                quantity=serializer.data.get('size'),
            )
            return Response(
                {'message': 'Webhook received and processed by exchange', 'exchange_response': response},
                status=status.HTTP_201_CREATED
            )
        except ClientError as e:
            return Response(
                {'error': f"Binance Client Error: {e.error_message}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Internal error processing webhook: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
