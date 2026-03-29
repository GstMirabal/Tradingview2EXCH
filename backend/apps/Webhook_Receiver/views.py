import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.core.permissions import HasWebhookPassphrase
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from binance.error import ClientError

from .serializers import webhookSerializer
from apps.Binance_Connector.services import binance_service

logger = logging.getLogger('project')

class webhookReceived(APIView):
    """
    API view to handle receiving new webhooks from TradingView.
    """
    # Use custom permission to validate passphrase
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
                'orderId': openapi.Schema(type=openapi.TYPE_STRING, description='Order ID associated with the alert', example='BFP1'),
                'marketPosition': openapi.Schema(type=openapi.TYPE_STRING, description='Market position', example='0.00363'),
                'marketPrevPosition': openapi.Schema(type=openapi.TYPE_STRING, description='Previous market position', example='0.00338'),
                'type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of alert', example='MARKET')
            }
        ),
        responses={
            201: 'Webhook successfully processed and sent to exchange',
            400: 'Bad Request',
            500: 'Internal Server Error'
        },
        operation_id='Receive Webhook'
    )
    def post(self, request):
        """
        Receive a new alert.
        """
        try:
            # Deserialize the incoming JSON to the Alerta model using the serializer
            serializer = webhookSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                # Directly forward to BinanceService instead of an internal HTTP-like call
                exchange = serializer.data.get('exchange', 'BINANCE').upper()
                if exchange == 'BINANCE':
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
                else:
                    return Response(
                        {'error': f"Exchange {exchange} not supported yet."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                logger.error(f"Invalid webhook payload: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except ClientError as e:
            return Response(
                {'error': f"Binance Client Error: {e.error_message}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Internal error processing webhook: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
