import os
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from unittest.mock import patch
from api.models import ApiKey, Log


class ApiKeyModelTest(TestCase):
    def setUp(self):
        self.test_key = "test_key_12345678901234567890"
        self.user = "testuser"

    def test_set_key_creates_hash_and_preview(self):
        """Test that set_key properly creates hash and preview"""
        api_key = ApiKey()
        api_key.set_key(self.test_key)

        self.assertEqual(len(api_key.key_hash), 64)  # SHA-256 hex length
        self.assertEqual(api_key.key_preview, "7890")  # Last 4 chars
        self.assertTrue(api_key.encrypted_key)

    def test_verify_key_works_correctly(self):
        """Test key verification"""
        api_key = ApiKey(user=self.user)
        api_key.set_key(self.test_key)

        self.assertTrue(api_key.verify_key(self.test_key))
        self.assertFalse(api_key.verify_key("wrong_key"))

    def test_authenticate_returns_valid_key(self):
        """Test authentication with valid key"""
        api_key = ApiKey.objects.create(user=self.user, is_active=True)
        api_key.set_key(self.test_key)
        api_key.save()

        authenticated = ApiKey.authenticate(self.test_key)
        self.assertEqual(authenticated.user, self.user)

    def test_authenticate_returns_none_for_invalid_key(self):
        """Test authentication with invalid key"""
        result = ApiKey.authenticate("invalid_key")
        self.assertIsNone(result)

    def test_authenticate_returns_none_for_inactive_key(self):
        """Test authentication with inactive key"""
        api_key = ApiKey.objects.create(user=self.user, is_active=False)
        api_key.set_key(self.test_key)
        api_key.save()

        result = ApiKey.authenticate(self.test_key)
        self.assertIsNone(result)

    def test_unique_hash_constraint(self):
        """Test that duplicate hash raises IntegrityError"""
        api_key1 = ApiKey.objects.create(user="user1")
        api_key1.set_key(self.test_key)
        api_key1.save()

        api_key2 = ApiKey(user="user2")
        api_key2.set_key(self.test_key)

        with self.assertRaises(IntegrityError):
            api_key2.save()

    @patch('os.environ.get')
    def test_encryption_fallback(self, mock_env):
        """Test encryption fallback when key is missing"""
        mock_env.return_value = None

        api_key = ApiKey()
        api_key.set_key(self.test_key)

        # Should not raise an error and should set encrypted_key
        self.assertTrue(api_key.encrypted_key)


class LogModelTest(TestCase):
    def test_log_creation(self):
        """Test log entry creation"""
        log = Log.objects.create(
            national_id="12345678901234",
            valid=True,
            extracted_data={"gender": "Male"},
            api_key_used="test"
        )

        self.assertTrue(log.timestamp)
        self.assertEqual(log.national_id, "12345678901234")
        self.assertTrue(log.valid)
        self.assertTrue(log.is_successful)

    def test_unsuccessful_log(self):
        """Test unsuccessful validation log"""
        log = Log.objects.create(
            national_id="12345678901234",
            valid=False,
            error="Invalid format"
        )

        self.assertFalse(log.is_successful)
        self.assertEqual(log.error, "Invalid format")
