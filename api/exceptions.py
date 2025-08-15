from rest_framework.exceptions import ValidationError


class NationalIDValidationError(ValidationError):
    """Raised for National ID validation errors."""
