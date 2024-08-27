from django.apps import AppConfig


class WebhookReceiverConfig(AppConfig):
    # Specifies the default field type for auto-created primary keys
    default_auto_field = 'django.db.models.BigAutoField'
    # The name of the application
    name = 'Webhook_Receiver'