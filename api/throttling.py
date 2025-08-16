from rest_framework.throttling import SimpleRateThrottle
from .models import ApiKey
import hashlib


class ApiKeyRateThrottle(SimpleRateThrottle):
    scope = 'api_key'

    def get_cache_key(self, request, view):
        # Get API key from header
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None

        # Create a consistent hash for the API key to use as cache key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return f"throttle_api_key_{key_hash}"

    def allow_request(self, request, view):
        # Only apply throttling if there's a valid API key
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return True  # Let authentication handle missing keys

        # Check if the API key exists and is active
        try:
            key_obj = ApiKey.objects.get_by_key(api_key)
            if not key_obj or not key_obj.is_active:
                return True  # Let authentication handle invalid keys
        except:
            return True  # Let authentication handle invalid keys

        return super().allow_request(request, view)
