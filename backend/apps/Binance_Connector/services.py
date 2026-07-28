import logging
from typing import Any

from binance.error import ClientError
from binance.spot import Spot as BinanceClient
from django.conf import settings

from config.settings import config

logger = logging.getLogger('project')


class BinanceService:
    """Encapsulates all logic for interacting with the Binance API.

    Provides lazy client initialization and handling for both test and real orders.
    """

    def __init__(self) -> None:
        """Read Binance credentials from configuration without connecting yet."""
        self._client: BinanceClient | None = None
        self.api_key: str | None = config['binance'].get('API_KEY')
        self.api_secret: str | None = config['binance'].get('API_SECRET')
        self.base_url = 'https://api1.binance.com'

    @property
    def client(self) -> BinanceClient:
        """Lazily initialize and return the Binance SDK client.

        Returns:
            The connected Binance SDK client instance.

        Raises:
            ValueError: If the API key/secret are not configured.
        """
        if self._client is None:
            if not self.api_key or not self.api_secret:
                logger.error('Binance API credentials missing.')
                raise ValueError('Binance API credentials missing.')
            self._client = BinanceClient(
                self.api_key, self.api_secret, base_url=self.base_url
            )
        return self._client

    def execute_order(
        self, symbol: str, side: str, order_type: str, quantity: str
    ) -> dict[str, Any]:
        """Execute a buy or sell order on Binance.

        Uses `new_order_test` in DEBUG mode, and a real order in production.

        Args:
            symbol: The trading pair symbol (e.g. 'BTCUSDT').
            side: 'BUY' or 'SELL'.
            order_type: The Binance order type (e.g. 'MARKET').
            quantity: The order quantity.

        Returns:
            The raw response from the Binance API.

        Raises:
            ClientError: If Binance rejects the order.
            Exception: For any other unexpected failure.
        """
        try:
            params = {
                'symbol': symbol.upper(),
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': quantity,
            }

            logger.info(f'Executing order with params: {params}')

            if settings.DEBUG:
                logger.info('Running in DEBUG mode, using test_order.')
                response = self.client.new_order_test(**params)
            else:
                logger.info('Running in Production mode, executing REAL order.')
                response = self.client.new_order(**params)

            logger.info(f'Order completed: {response}')
            return response
        except ClientError as e:
            logger.error(
                f'Binance Client Error: {e.error_message} (Code: {e.error_code})'
            )
            raise
        except Exception as e:
            logger.error(f'Unexpected error in BinanceService: {str(e)}')
            raise

    def get_system_status(self) -> dict[str, Any] | None:
        """Check the Binance system status.

        Returns:
            The system status payload, or None if the check failed.
        """
        try:
            return self.client.system_status()
        except ClientError as e:
            logger.error(f'Error checking system status: {e}')
            return None

    def get_user_assets(self) -> dict[str, Any] | None:
        """Retrieve the authenticated account's asset balances.

        Returns:
            The user asset payload, or None if the request failed.
        """
        try:
            return self.client.user_asset()
        except ClientError as e:
            logger.error(f'Error getting user assets: {e}')
            return None


# Module-level singleton: credentials are read once at import time, so a
# credential rotation requires restarting the process to take effect.
binance_service = BinanceService()
