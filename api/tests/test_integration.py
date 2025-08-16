from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import ApiKey, Log


class IntegrationTest(TransactionTestCase):
    """End-to-end integration tests"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('national_id')
        self.test_key = "integration_test_key_123456"

        # Create test API key
        self.api_key = ApiKey.objects.create(
            user="integration_user", is_active=True)
        self.api_key.set_key(self.test_key)
        self.api_key.save()

    def test_complete_validation_workflow(self):
        """Test complete validation workflow from request to logging"""
        # Set API key
        self.client.credentials(HTTP_X_API_KEY=self.test_key)

        # Make request
        response = self.client.post(self.url, {
            "national_id": "30307020102113"
        }, format='json')

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])
        self.assertEqual(response.data['birth_year'], 2003)
        self.assertEqual(response.data['gender'], 'Male')
        self.assertEqual(response.data['governorate'], 'Cairo')

        # Check log was created
        log = Log.objects.filter(national_id="30307020102113").first()
        self.assertIsNotNone(log)
        self.assertTrue(log.valid)
        self.assertIsNotNone(log.extracted_data)

    def test_invalid_id_workflow(self):
        """Test workflow with invalid national ID"""
        self.client.credentials(HTTP_X_API_KEY=self.test_key)

        response = self.client.post(self.url, {
            "national_id": "40307020102113"  # Invalid century
        }, format='json')

        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['valid'])

        # Check log was created for failed attempt
        log = Log.objects.filter(national_id="40307020102113").first()
        self.assertIsNotNone(log)
        self.assertFalse(log.valid)
        self.assertIsNotNone(log.error)

    def test_multiple_requests_different_keys(self):
        """Test multiple requests with different API keys"""
        # Create second API key
        api_key2 = ApiKey.objects.create(user="user2", is_active=True)
        test_key2 = "second_test_key_123456789"
        api_key2.set_key(test_key2)
        api_key2.save()

        # First request with first key
        self.client.credentials(HTTP_X_API_KEY=self.test_key)
        response1 = self.client.post(self.url, {
            "national_id": "30307020102113"
        }, format='json')

        # Second request with second key
        self.client.credentials(HTTP_X_API_KEY=test_key2)
        response2 = self.client.post(self.url, {
            "national_id": "30307020102114"  # Different ID
        }, format='json')

        # Both should succeed
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Check logs were created with correct API key previews
        log1 = Log.objects.filter(national_id="30307020102113").first()
        log2 = Log.objects.filter(national_id="30307020102114").first()

        self.assertNotEqual(log1.api_key_used, log2.api_key_used)

    def test_authentication_and_validation_flow(self):
        """Test complete authentication and validation flow"""
        # Test without API key - should fail
        response = self.client.post(self.url, {
            "national_id": "30307020102113"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test with invalid API key - should fail
        self.client.credentials(HTTP_X_API_KEY="invalid_key_123")
        response = self.client.post(self.url, {
            "national_id": "30307020102113"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test with valid API key - should succeed
        self.client.credentials(HTTP_X_API_KEY=self.test_key)
        response = self.client.post(self.url, {
            "national_id": "30307020102113"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify log was created only for successful authentication
        logs = Log.objects.filter(national_id="30307020102113")
        self.assertEqual(logs.count(), 1)  # Only one log should exist

    def test_edge_case_national_ids(self):
        """Test various edge cases for national ID validation"""
        self.client.credentials(HTTP_X_API_KEY=self.test_key)

        test_cases = [
            # (national_id, should_be_valid, expected_status)
            ("30307020102113", True, status.HTTP_200_OK),   # Valid ID
            ("40307020102113", False, status.HTTP_400_BAD_REQUEST),  # Invalid century
            ("30313020102113", False, status.HTTP_400_BAD_REQUEST),  # Invalid month
            ("30307320102113", False, status.HTTP_400_BAD_REQUEST),  # Invalid day
            # Invalid governorate
            ("30307020999913", False, status.HTTP_400_BAD_REQUEST),
            ("123", False, status.HTTP_400_BAD_REQUEST),             # Too short
            ("123456789012345", False, status.HTTP_400_BAD_REQUEST),  # Too long
            # Invalid characters
            ("3030702010211a", False, status.HTTP_400_BAD_REQUEST),
        ]

        for national_id, should_be_valid, expected_status in test_cases:
            with self.subTest(national_id=national_id):
                response = self.client.post(self.url, {
                    "national_id": national_id
                }, format='json')

                self.assertEqual(response.status_code, expected_status)
                self.assertEqual(response.data.get(
                    'valid', False), should_be_valid)
