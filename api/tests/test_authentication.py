from django.test import TestCase, RequestFactory
from rest_framework.exceptions import AuthenticationFailed
from unittest.mock import patch, Mock
from api.authentication import ApiKeyAuthentication
from api.models import ApiKey


class ApiKeyAuthenticationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.auth = ApiKeyAuthentication()
        self.test_key = "test_key_12345678901234567890"

    def test_authenticate_no_key(self):
        """Test authentication without API key"""
        request = self.factory.get('/')
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_authenticate_valid_key(self):
        """Test authentication with valid key"""
        api_key = ApiKey.objects.create(user="testuser", is_active=True)
        api_key.set_key(self.test_key)
        api_key.save()

        request = self.factory.get('/', HTTP_X_API_KEY=self.test_key)
        result = self.auth.authenticate(request)

        self.assertIsNotNone(result)
        self.assertEqual(result[0].user, "testuser")

    def test_authenticate_invalid_key(self):
        """Test authentication with invalid key"""
        request = self.factory.get('/', HTTP_X_API_KEY="invalid_key")

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    @patch('api.models.ApiKey.authenticate')
    def test_authenticate_database_error(self, mock_auth):
        """Test authentication with database error"""
        from django.db import DatabaseError
        mock_auth.side_effect = DatabaseError("Connection failed")

        request = self.factory.get('/', HTTP_X_API_KEY=self.test_key)

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)
