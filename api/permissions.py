from rest_framework.permissions import BasePermission
from .models import ApiKey


class HasApiKey(BasePermission):
    def has_permission(self, request, view):
        # Check if the request has an authenticated ApiKey
        return request.user and isinstance(request.user, ApiKey)
