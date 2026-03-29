from rest_framework import permissions
from config.settings import config
import logging

logger = logging.getLogger('project')

class HasWebhookPassphrase(permissions.BasePermission):
    """
    Custom permission to only allow requests that provide the correct passphrase
    in the 'passphrase' field of the JSON body.
    """

    def has_permission(self, request, view):
        # In case of GET or other methods, we might want to deny or allow
        if request.method != 'POST':
            return False

        # Get the required passphrase from configuration
        # If not set in config, we might want to warn and allow/deny. 
        # For security, let's deny if not configured.
        required_passphrase = config['security'].get('WEBHOOK_PASSPHRASE')
        
        if not required_passphrase:
            logger.warning("WEBHOOK_PASSPHRASE is not configured in config.toml/env. Denying all requests.")
            return False

        # Check the request body
        provided_passphrase = request.data.get('passphrase')
        
        if provided_passphrase == required_passphrase:
            return True
        
        logger.warning(f"Unauthorized access attempt with invalid passphrase from {request.META.get('REMOTE_ADDR')}")
        return False
