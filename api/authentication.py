from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import ApiKey


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            raise AuthenticationFailed('API Key required')
        try:
            key_obj = ApiKey.objects.get(key=api_key)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API Key')
        return (key_obj, None)  # request.user will be ApiKey instance
