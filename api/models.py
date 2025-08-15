import os
import hashlib
from cryptography.fernet import Fernet
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.conf import settings
from .constants import API_KEY_MAX_LENGTH, NATIONAL_ID_LENGTH


class ApiKey(models.Model):
    """Model for API key management with encryption at rest"""

    # Store hashed version for lookups
    key_hash = models.CharField(
        max_length=API_KEY_MAX_LENGTH,
        unique=True,
        db_index=True,
        help_text="SHA-256 hash of the API key for lookup"
    )

    # Store encrypted version for display/audit
    encrypted_key = models.TextField(
        help_text="Encrypted API key for audit purposes"
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
        return f"{self.user} - Key ending in {self.get_key_preview()}"

    @staticmethod
    def _get_cipher():
        """Get encryption cipher"""
        key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
        return Fernet(key.encode() if isinstance(key, str) else key)

    @staticmethod
    def hash_key(api_key: str) -> str:
        """Create SHA-256 hash of API key"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def set_key(self, api_key: str):
        """Set API key with encryption and hashing"""
        self.key_hash = self.hash_key(api_key)
        cipher = self._get_cipher()
        self.encrypted_key = cipher.encrypt(api_key.encode()).decode()

    def get_key_preview(self) -> str:
        """Get last 4 characters of decrypted key for display"""
        try:
            cipher = self._get_cipher()
            decrypted = cipher.decrypt(self.encrypted_key.encode()).decode()
            return decrypted[-4:]
        except:
            return "****"

    def verify_key(self, provided_key: str) -> bool:
        """Verify provided key against stored hash"""
        return self.hash_key(provided_key) == self.key_hash

    def is_valid(self):
        """Check if the API key is valid and active"""
        return self.is_active

    @classmethod
    def authenticate(cls, api_key: str):
        """Authenticate API key"""
        key_hash = cls.hash_key(api_key)
        try:
            return cls.objects.get(key_hash=key_hash, is_active=True)
        except cls.DoesNotExist:
            return None

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
        max_length=8,  # Store only preview for privacy
        null=True,
        blank=True,
        db_index=True,
        help_text="API key preview used for this validation"
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
