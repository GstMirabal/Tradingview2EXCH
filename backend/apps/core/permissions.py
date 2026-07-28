import hmac
import logging

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from config.settings import config

logger = logging.getLogger('project')


class HasWebhookPassphrase(permissions.BasePermission):
    """Custom permission to only allow requests carrying the correct passphrase.

    The passphrase is expected in the 'passphrase' field of the JSON body and is
    compared against the value configured under `[django_settings].WEBHOOK_PASSPHRASE`.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check whether the request carries a valid webhook passphrase.

        Args:
            request: The incoming DRF request.
            view: The view this permission is attached to.

        Returns:
            True if the request is a POST with a matching passphrase.
        """
        if request.method != 'POST':
            return False

        # WEBHOOK_PASSPHRASE lives under [django_settings], not [security] —
        # that section does not exist in config.toml.
        required_passphrase = config['django_settings'].get('WEBHOOK_PASSPHRASE')

        if not required_passphrase:
            logger.warning(
                'WEBHOOK_PASSPHRASE is not configured. Denying all requests.'
            )
            return False

        provided_passphrase = request.data.get('passphrase')

        if not isinstance(provided_passphrase, str):
            return False

        # Constant-time comparison avoids leaking the passphrase via timing.
        if hmac.compare_digest(provided_passphrase, required_passphrase):
            return True

        remote_addr = request.META.get('REMOTE_ADDR')
        logger.warning(
            f'Unauthorized access attempt with invalid passphrase from {remote_addr}'
        )
        return False
