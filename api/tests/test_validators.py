from django.test import TestCase
from datetime import datetime
from api.validators import (
    validate_length, validate_digits, validate_and_get_century,
    validate_and_get_governorate, validate_and_create_date,
    extract_gender, validate_and_extract
)
from api.exceptions import NationalIDValidationError


class ValidatorTest(TestCase):
    def assertValid(self, func, *args):
        """Helper: call func, expect no exception"""
        func(*args)

    def assertInvalid(self, func, *args):
        """Helper: call func, expect NationalIDValidationError"""
        with self.assertRaises(NationalIDValidationError):
            func(*args)

    def test_validate_length(self):
        self.assertValid(validate_length, "12345678901234")
        self.assertInvalid(validate_length, "123456789")

    def test_validate_digits(self):
        self.assertValid(validate_digits, "12345678901234")
        self.assertInvalid(validate_digits, "1234567890123a")

    def test_century_validation(self):
        self.assertEqual(validate_and_get_century("2"), 1900)
        self.assertEqual(validate_and_get_century("3"), 2000)
        self.assertInvalid(validate_and_get_century, "4")

    def test_governorate_validation(self):
        self.assertEqual(validate_and_get_governorate("01"), "Cairo")
        self.assertEqual(validate_and_get_governorate("88"), "Foreign")
        self.assertInvalid(validate_and_get_governorate, "99")

    def test_date_validation(self):
        # Valid
        date = validate_and_create_date(2000, "01", "15")
        self.assertEqual((date.year, date.month, date.day), (2000, 1, 15))

        # Invalids
        future_year = datetime.now().year + 1
        self.assertInvalid(validate_and_create_date, future_year, "01", "01")
        self.assertInvalid(validate_and_create_date, 2000,
                           "13", "01")  # invalid month

    def test_gender_extraction(self):
        self.assertEqual(extract_gender("1"), "Male")
        self.assertEqual(extract_gender("2"), "Female")
        self.assertEqual(extract_gender("9"), "Male")
        self.assertEqual(extract_gender("8"), "Female")

    def test_complete_validation(self):
        result = validate_and_extract("30307020102113")  # valid
        self.assertEqual(result["birth_year"], 2003)
        self.assertEqual(result["birth_date"], "02/07/2003")
        self.assertEqual(result["gender"], "Male")
        self.assertEqual(result["governorate"], "Cairo")

        self.assertInvalid(validate_and_extract, "40307020102113")  # invalid
