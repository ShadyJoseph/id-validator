# Authentication
API_KEY_HEADER = 'X-API-KEY'
API_KEY_MAX_LENGTH = 64

# National ID Configuration
NATIONAL_ID_LENGTH = 14
VALID_CENTURY_DIGITS = ('2', '3')

# Rate Limiting
DEFAULT_RATE_LIMIT = '100/minute'

# Egyptian Governorate Codes
GOVERNORATE_CODES = {
    '01': 'Cairo',
    '02': 'Alexandria',
    '03': 'Port Said',
    '04': 'Suez',
    '11': 'Damietta',
    '12': 'Dakahlia',
    '13': 'Sharkia',
    '14': 'Qalyubia',
    '15': 'Kafr El Sheikh',
    '16': 'Gharbia',
    '17': 'Monufia',
    '18': 'Beheira',
    '19': 'Ismailia',
    '21': 'Giza',
    '22': 'Beni Suef',
    '23': 'Fayoum',
    '24': 'Minya',
    '25': 'Assiut',
    '26': 'Sohag',
    '27': 'Qena',
    '28': 'Aswan',
    '29': 'Luxor',
    '31': 'Red Sea',
    '32': 'New Valley',
    '33': 'Matrouh',
    '34': 'North Sinai',
    '35': 'South Sinai',
    '88': 'Foreign'
}

# Error Messages


class ErrorMessages:
    API_KEY_REQUIRED = 'API Key required'
    INVALID_API_KEY = 'Invalid API Key'
    INACTIVE_API_KEY = 'Inactive API Key'
    INVALID_LENGTH = f'National ID must be exactly {NATIONAL_ID_LENGTH} digits'
    INVALID_FORMAT = 'National ID must contain only digits'
    INVALID_CENTURY = f'Invalid century digit (must be {" or ".join(VALID_CENTURY_DIGITS)})'
    INVALID_GOVERNORATE = 'Invalid governorate code'
    INVALID_DATE_FORMAT = 'Invalid birth date format or values'
    FUTURE_DATE = 'Birth date cannot be in the future'
    DATABASE_ERROR = 'Database operation failed'
    VALIDATION_ERROR = 'Validation failed'

# Response Messages


class ResponseMessages:
    SUCCESS = 'Validation successful'
    VALIDATION_FAILED = 'National ID validation failed'
