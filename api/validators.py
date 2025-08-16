from datetime import datetime
from typing import Dict, Any
from .constants import (
    NATIONAL_ID_LENGTH, GOVERNORATE_CODES,
    ErrorMessages
)
from .exceptions import NationalIDValidationError


def validate_length(nid: str) -> None:
    """Validate national ID length."""
    if len(nid) != NATIONAL_ID_LENGTH:
        raise NationalIDValidationError(ErrorMessages.INVALID_LENGTH)


def validate_digits(nid: str) -> None:
    """Validate national ID contains only digits."""
    if not nid.isdigit():
        raise NationalIDValidationError(ErrorMessages.INVALID_FORMAT)


def validate_and_get_century(century_digit: str) -> int:
    """Validate and get century from digit."""
    if century_digit == '2':
        return 1900
    elif century_digit == '3':
        return 2000
    raise NationalIDValidationError(ErrorMessages.INVALID_CENTURY)


def validate_and_get_governorate(gov_code: str) -> str:
    """Validate and get governorate name."""
    governorate = GOVERNORATE_CODES.get(gov_code)
    if not governorate:
        raise NationalIDValidationError(ErrorMessages.INVALID_GOVERNORATE)
    return governorate


def validate_and_create_date(year: int, month: str, day: str) -> datetime:
    """Validate and create birth date."""
    try:
        birth_date = datetime(year, int(month), int(day))
        if birth_date.date() > datetime.now().date():
            raise NationalIDValidationError(ErrorMessages.FUTURE_DATE)
        return birth_date
    except ValueError:
        raise NationalIDValidationError(ErrorMessages.INVALID_DATE_FORMAT)


def extract_gender(serial_digit: str) -> str:
    """Extract gender from serial digit."""
    return 'Male' if int(serial_digit) % 2 == 1 else 'Female'


def validate_and_extract(nid: str) -> Dict[str, Any]:
    """Validate national ID and extract information."""
    validate_length(nid)
    validate_digits(nid)

    century_digit = nid[0]
    year_part = nid[1:3]
    month_part = nid[3:5]
    day_part = nid[5:7]
    gov_code = nid[7:9]
    gender_digit = nid[12]

    century = validate_and_get_century(century_digit)
    birth_year = century + int(year_part)
    birth_date = validate_and_create_date(birth_year, month_part, day_part)
    governorate = validate_and_get_governorate(gov_code)
    gender = extract_gender(gender_digit)

    return {
        "birth_year": birth_year,
        "birth_date": birth_date.strftime("%d/%m/%Y"),
        "gender": gender,
        "governorate": governorate
    }
