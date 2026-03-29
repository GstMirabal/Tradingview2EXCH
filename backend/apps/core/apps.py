from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration class for the Core application.

    This module handles the initialization, metadata, and default settings
    for the core business logic of the project.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
