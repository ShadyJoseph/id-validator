from django.test import TestCase
from rest_framework.exceptions import ValidationError
from api.serializers import NationalIDSerializer


class NationalIDSerializerTest(TestCase):
    def test_valid_national_id(self):
        """Test serializer with valid national ID"""
        data = {"national_id": "30307020102113"}
        serializer = NationalIDSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data['national_id'], "30307020102113")

    def test_invalid_length_short(self):
        """Test serializer with short national ID"""
        data = {"national_id": "123456789"}
        serializer = NationalIDSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('national_id', serializer.errors)

    def test_invalid_length_long(self):
        """Test serializer with long national ID"""
        data = {"national_id": "123456789012345"}
        serializer = NationalIDSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('national_id', serializer.errors)

    def test_invalid_characters(self):
        """Test serializer with non-digit characters"""
        data = {"national_id": "3030702010211a"}
        serializer = NationalIDSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('national_id', serializer.errors)

    def test_whitespace_trimming(self):
        """Test that whitespace is trimmed"""
        data = {"national_id": " 30307020102113 "}
        serializer = NationalIDSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data['national_id'], "30307020102113")
