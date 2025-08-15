from rest_framework.throttling import SimpleRateThrottle
from .models import ApiKey
from .constants import DEFAULT_RATE_LIMIT


class ApiKeyRateThrottle(SimpleRateThrottle):
    rate = DEFAULT_RATE_LIMIT

    def get_cache_key(self, request, view):
        if request.user and isinstance(request.user, ApiKey):
            return f"throttle_{request.user.key}"
        return None
