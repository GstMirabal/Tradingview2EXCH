from django.apps import AppConfig


class BinanceConnectorConfig(AppConfig):
    """App configuration for the Binance order-execution app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.Binance_Connector'
