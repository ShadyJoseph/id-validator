import logging
from typing import Dict, Any, Optional, Tuple, NamedTuple
from django.db import IntegrityError, DatabaseError
from .models import Log, ApiKey
from .validators import validate_and_extract
from .exceptions import NationalIDValidationError
from .constants import ErrorMessages

logger = logging.getLogger(__name__)


class ValidationResult(NamedTuple):
    """Encapsulates validation results."""
    is_valid: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def create_log(national_id: str, result: ValidationResult, api_key_obj: ApiKey) -> Optional[Log]:
    """Create log entry for validation attempt."""
    try:
        # Use the key preview from the API key object
        api_key_preview = api_key_obj.get_key_preview() if api_key_obj else "unknown"

        return Log.objects.create(
            national_id=national_id,
            valid=result.is_valid,
            extracted_data=result.data,
            error=result.error,
            api_key_used=api_key_preview
        )
    except (IntegrityError, DatabaseError) as e:
        logger.error(f"Failed to create log: {str(e)}")
        return None


def validate_national_id(national_id: str) -> ValidationResult:
    """Validate national ID and return result."""
    try:
        extracted_data = validate_and_extract(national_id)
        return ValidationResult(True, data=extracted_data)
    except NationalIDValidationError as e:
        return ValidationResult(False, error=str(e))
    except Exception as e:
        logger.error(f"Unexpected validation error: {str(e)}")
        return ValidationResult(False, error=ErrorMessages.VALIDATION_ERROR)


def process_validation_request(national_id: str, api_key_obj: ApiKey) -> Tuple[ValidationResult, Optional[Log]]:
    """Process validation request including logging."""
    result = validate_national_id(national_id)
    log_entry = create_log(national_id, result, api_key_obj)
    return result, log_entry
