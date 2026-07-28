from django.apps import AppConfig


class WebhookReceiverConfig(AppConfig):
    """App configuration for the TradingView webhook intake app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.Webhook_Receiver'
