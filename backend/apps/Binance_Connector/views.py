import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from binance.error import ClientError

from .serializers import binanceParamsserializers
from .services import binance_service

logger = logging.getLogger('project')

class binanceParams(APIView):
    """
    API view to handle Binance parameter submissions.
    """
    # TODO: In production, change to IsAuthenticated or custom permission
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Receive data and execute order on Binance",
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
            200: 'Operation completed successfully',
            400: 'Bad Request',
            500: 'Internal Server Error'
        },
        operation_id='Binance Params'
    )
    def post(self, request):
        """
        Receive request to execute a Binance order.
        """
        serializer = binanceParamsserializers(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Invalid Binance params: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save()
            # Use Service Layer to execute order
            response = binance_service.execute_order(
                symbol=serializer.data.get('symbol'),
                side=serializer.data.get('side'),
                order_type=serializer.data.get('type'),
                quantity=serializer.data.get('size'),
            )
            return Response({'message': 'Order processed successfully', 'response': response}, status=status.HTTP_200_OK)
        except ClientError as e:
            return Response(
                {'error': f"Binance Client Error: {e.error_message}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Internal server error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
