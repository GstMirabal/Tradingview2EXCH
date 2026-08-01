from django.apps import AppConfig


class BinanceConnectorConfig(AppConfig):
    """App configuration for the Binance order-execution app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.Binance_Connector'

    def ready(self) -> None:
        """Register the startup checks for this app's configuration."""
        from . import checks  # noqa: F401
