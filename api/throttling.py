from rest_framework.throttling import SimpleRateThrottle
from .models import ApiKey


class ApiKeyRateThrottle(SimpleRateThrottle):
    scope = 'api_key'

    def get_cache_key(self, request, view):
        if request.user and isinstance(request.user, ApiKey):
            return f"throttle_{request.user.key_hash}"
        return None
