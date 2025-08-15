import logging
from django.db import DatabaseError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import ApiKey
from .constants import API_KEY_HEADER, ErrorMessages

logger = logging.getLogger(__name__)


class ApiKeyAuthentication(BaseAuthentication):
    """API key-based authentication."""

    def authenticate(self, request):
        """Authenticate request using API key."""
        try:
            api_key = request.headers.get(API_KEY_HEADER)
            if not api_key:
                raise AuthenticationFailed(ErrorMessages.API_KEY_REQUIRED)

            try:
                key_obj = ApiKey.authenticate(api_key)
                if not key_obj:
                    logger.warning(
                        f"Invalid API key attempt: {api_key[:8]}...")
                    raise AuthenticationFailed(ErrorMessages.INVALID_API_KEY)

                return (key_obj, None)

            except DatabaseError as e:
                logger.error(f"Database error in authentication: {str(e)}")
                raise AuthenticationFailed(
                    "Authentication service unavailable")

        except AuthenticationFailed:
            raise
        except Exception as e:
            logger.error(f"Unexpected authentication error: {str(e)}")
            raise AuthenticationFailed(
                "Authentication failed due to server error")
