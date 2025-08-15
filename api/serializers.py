from rest_framework import serializers
from .constants import NATIONAL_ID_LENGTH, ErrorMessages


class NationalIDSerializer(serializers.Serializer):
    """Serializer for National ID validation requests"""

    national_id = serializers.CharField(
        max_length=NATIONAL_ID_LENGTH,
        min_length=NATIONAL_ID_LENGTH,
        help_text=f"Egyptian National ID - exactly {NATIONAL_ID_LENGTH} digits"
    )

    def validate_national_id(self, value):
        """
        Custom validation for national_id field

        Args:
            value: The national ID string

        Returns:
            Validated national ID string

        Raises:
            ValidationError: If national ID format is invalid
        """
        # Remove any whitespace
        value = value.strip()

        # Check if it contains only digits
        if not value.isdigit():
            raise serializers.ValidationError(ErrorMessages.INVALID_FORMAT)

        # Length is already validated by field definition, but double-check
        if len(value) != NATIONAL_ID_LENGTH:
            raise serializers.ValidationError(ErrorMessages.INVALID_LENGTH)

        return value
