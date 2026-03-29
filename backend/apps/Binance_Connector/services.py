import logging
from binance.spot import Spot as BinanceClient
from binance.error import ClientError
from django.conf import settings
from config.settings import config

logger = logging.getLogger('project')

class BinanceService:
    """
    Encapsulates all logic for interacting with the Binance API.
    Provides lazy initialization and handling for both test and real orders.
    """

    def __init__(self):
        self._client = None
        self.api_key = config['binance'].get('API_KEY')
        self.api_secret = config['binance'].get('API_SECRET')
        self.base_url = 'https://api1.binance.com'

    @property
    def client(self):
        """Lazy initialization of the Binance client."""
        if self._client is None:
            if not self.api_key or not self.api_secret:
                logger.error("Binance API credentials missing.")
                raise ValueError("Binance API credentials missing.")
            self._client = BinanceClient(self.api_key, self.api_secret, base_url=self.base_url)
        return self._client

    def execute_order(self, symbol, side, order_type, quantity):
        """
        Executes a Buy or Sell order on Binance.
        Uses test_order in DEBUG mode, and a real order in production.
        """
        try:
            params = {
                'symbol': symbol.upper(),
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': quantity
            }
            
            logger.info(f"Executing order with params: {params}")

            if settings.DEBUG:
                logger.info("Running in DEBUG mode, using test_order.")
                response = self.client.new_order_test(**params)
            else:
                logger.info("Running in Production mode, executing REAL order.")
                response = self.client.new_order(**params)
                
            logger.info(f"Order completed: {response}")
            return response
        except ClientError as e:
            logger.error(f"Binance Client Error: {e.error_message} (Code: {e.error_code})")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in BinanceService: {str(e)}")
            raise e

    def get_system_status(self):
        """Check system status."""
        try:
            return self.client.system_status()
        except ClientError as e:
            logger.error(f"Error checking system status: {e}")
            return None

    def get_user_assets(self):
        """Retrieve user assets."""
        try:
            return self.client.user_asset()
        except ClientError as e:
            logger.error(f"Error getting user assets: {e}")
            return None

# Singleton-like instance for internal use
binance_service = BinanceService()
