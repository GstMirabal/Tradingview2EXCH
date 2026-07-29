import logging

from binance.error import ClientError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BinanceParamsSerializer
from .services import binance_service

logger = logging.getLogger('project')


class BinanceParamsView(APIView):
    """API view to handle direct Binance order submissions.

    This is an internal/admin tool for submitting orders outside the
    TradingView webhook flow, so it requires an authenticated staff session
    rather than the webhook passphrase.
    """

    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description='Receive data and execute order on Binance',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'exchange': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Exchange associated with the alert',
                    example='BINANCE',
                ),
                'symbol': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Symbol associated with the alert',
                    example='BTCUSDT',
                ),
                'side': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Side associated with the alert (e.g., BUY or SELL)',
                    example='BUY',
                ),
                'type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Type of alert',
                    example='MARKET',
                ),
                'size': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Size associated with the alert',
                    example='0.00015',
                ),
            },
        ),
        responses={
            200: 'Operation completed successfully',
            400: 'Bad Request',
            500: 'Internal Server Error',
        },
        operation_id='Binance Params',
    )
    def post(self, request: Request) -> Response:
        """Validate the submitted order parameters and execute them on Binance.

        Args:
            request: The incoming DRF request carrying the order payload.

        Returns:
            200 with the Binance response on success, 400 on invalid payload
            or a Binance client error, 500 on an unexpected failure.
        """
        serializer = BinanceParamsSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f'Invalid Binance params: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save()
            response = binance_service.execute_order(
                symbol=serializer.data.get('symbol'),
                side=serializer.data.get('side'),
                order_type=serializer.data.get('type'),
                quantity=serializer.data.get('size'),
            )
            return Response(
                {'message': 'Order processed successfully', 'response': response},
                status=status.HTTP_200_OK,
            )
        except ClientError as e:
            return Response(
                {'error': f'Binance Client Error: {e.error_message}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # API boundary: never leak a 500 traceback, always log + respond JSON.
        except Exception as e:  # noqa: BLE001
            logger.error(f'Internal server error: {str(e)}')
            return Response(
                {'error': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BinanceStatusView(APIView):
    """API view exposing Binance system/account status for operational checks."""

    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description='Check Binance system status and account assets',
        responses={200: 'Status retrieved successfully'},
        operation_id='Binance Status',
    )
    def get(self, request: Request) -> Response:
        """Return Binance system status and account asset information.

        Args:
            request: The incoming DRF request.

        Returns:
            200 with the combined system status and user assets payload.
        """
        return Response(
            {
                'system_status': binance_service.get_system_status(),
                'user_assets': binance_service.get_user_assets(),
            },
            status=status.HTTP_200_OK,
        )
