from django.test import TestCase
from unittest.mock import patch, Mock
from api.services import validate_national_id, create_log, process_validation_request
from api.models import ApiKey, Log


class ServicesTest(TestCase):
    def setUp(self):
        self.api_key = ApiKey.objects.create(user="testuser", is_active=True)
        self.api_key.set_key("test_key_12345678901234567890")
        self.api_key.save()

    def test_validate_national_id_success(self):
        """Test successful validation"""
        result = validate_national_id("30307020102113")

        self.assertTrue(result.is_valid)
        self.assertIsNotNone(result.data)
        self.assertEqual(result.data['birth_year'], 2003)

    def test_validate_national_id_failure(self):
        """Test failed validation"""
        result = validate_national_id("40307020102113")  # Invalid century

        self.assertFalse(result.is_valid)
        self.assertIsNotNone(result.error)

    def test_create_log_success(self):
        """Test successful log creation"""
        from api.services import ValidationResult
        result = ValidationResult(True, data={"gender": "Male"})

        log = create_log("30307020102113", result, self.api_key)

        self.assertIsNotNone(log)
        self.assertEqual(log.national_id, "30307020102113")
        self.assertTrue(log.valid)

    @patch('api.models.Log.objects.create')
    def test_create_log_database_error(self, mock_create):
        """Test log creation with database error"""
        from django.db import DatabaseError
        from api.services import ValidationResult
        mock_create.side_effect = DatabaseError("Connection failed")

        result = ValidationResult(True, data={"gender": "Male"})
        log = create_log("30307020102113", result, self.api_key)

        self.assertIsNone(log)  # Should return None on error

    def test_process_validation_request(self):
        """Test complete validation request processing"""
        result, log_entry = process_validation_request(
            "30307020102113", self.api_key
        )

        self.assertTrue(result.is_valid)
        self.assertIsNotNone(log_entry)
        self.assertEqual(log_entry.national_id, "30307020102113")
