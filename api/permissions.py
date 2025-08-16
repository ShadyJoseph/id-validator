from rest_framework.permissions import BasePermission
from .models import ApiKey


class HasApiKey(BasePermission):
    """Check if request has valid API key authentication"""

    def has_permission(self, request, view):
        return (hasattr(request, 'user') and
                request.user and
                isinstance(request.user, ApiKey) and
                request.user.is_valid())
