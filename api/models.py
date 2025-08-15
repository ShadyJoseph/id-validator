from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from .constants import API_KEY_MAX_LENGTH, NATIONAL_ID_LENGTH


class ApiKey(models.Model):
    """Model for API key management"""

    key = models.CharField(
        max_length=API_KEY_MAX_LENGTH,
        unique=True,
        db_index=True,
        validators=[MinLengthValidator(20)],  # Minimum security requirement
        help_text="Unique API key for authentication"
    )
    user = models.CharField(
        max_length=100,
        help_text="User identifier associated with this API key"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this API key was created"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this API key is active"
    )

    def __str__(self):
        return f"{self.user} - {self.key[:8]}..."

    def is_valid(self):
        """Check if the API key is valid and active"""
        return self.is_active

    class Meta:
        app_label = 'api'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']


class Log(models.Model):
    """Model for logging validation attempts"""

    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the validation was performed"
    )
    national_id = models.CharField(
        max_length=NATIONAL_ID_LENGTH,
        validators=[
            MinLengthValidator(NATIONAL_ID_LENGTH),
            MaxLengthValidator(NATIONAL_ID_LENGTH)
        ],
        help_text="The national ID that was validated"
    )
    valid = models.BooleanField(
        help_text="Whether the national ID was valid"
    )
    extracted_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Extracted data if validation was successful"
    )
    error = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if validation failed"
    )
    api_key_used = models.CharField(
        max_length=API_KEY_MAX_LENGTH,
        null=True,
        blank=True,
        db_index=True,
        help_text="API key used for this validation"
    )

    def __str__(self):
        status = "Valid" if self.valid else "Invalid"
        return f"{status} - {self.national_id} at {self.timestamp}"

    @property
    def is_successful(self):
        """Check if the validation was successful"""
        return self.valid and self.extracted_data is not None

    class Meta:
        app_label = 'api'
        verbose_name = 'Validation Log'
        verbose_name_plural = 'Validation Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'valid']),
            models.Index(fields=['api_key_used', 'timestamp']),
        ]
