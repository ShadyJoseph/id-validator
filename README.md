# Egyptian National ID Validator API

A Django REST API for validating Egyptian national IDs and extracting personal information such as birth date, gender, and governorate.

## Features

- **National ID Validation**: Validates 14-digit Egyptian national IDs
- **Data Extraction**: Extracts birth year, birth date, gender, and governorate
- **API Key Authentication**: Secure service-to-service authentication
- **Rate Limiting**: 100 requests per minute per API key (configurable)
- **Encrypted Storage**: API keys are encrypted at rest in the database
- **Request Logging**: All validation attempts are logged for audit purposes
- **Django Admin**: Web interface for managing API keys and viewing logs

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Generate required keys and create a `.env` file in the root directory:

```bash
# Generate Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate encryption key for API keys
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Create `.env` file with the generated values:

```env
SECRET_KEY=django-insecure-generated-key-from-first-command-above
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
ENCRYPTION_KEY=generated-encryption-key-from-second-command-above
DEFAULT_RATE_LIMIT=100/minute
LOG_LEVEL=INFO
```

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optional: for Django admin access
```

### 4. Create API Key

```bash
python manage.py create_api_key "client_name"
```

Save the generated API key - it cannot be retrieved again!

### 5. Run the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/v1/`

## API Usage

### Endpoint

```
POST /api/v1/national-id/
```

### Headers

```
X-API-KEY: your-api-key-here
Content-Type: application/json
```

### Request Body

```json
{
  "national_id": "29001011234567"
}
```

### Response (Valid ID)

```json
{
  "valid": true,
  "birth_year": 1990,
  "birth_date": "01/01/1990",
  "gender": "Male",
  "governorate": "Cairo"
}
```

### Response (Invalid ID)

```json
{
  "valid": false,
  "error": "Invalid governorate code"
}
```

## Egyptian National ID Format

Egyptian national IDs follow this 14-digit format: `CYYMMDDGGXXXS`

- **C** (1st digit): Century (2=1900s, 3=2000s)
- **YY** (2nd-3rd): Year of birth
- **MM** (4th-5th): Month of birth
- **DD** (6th-7th): Day of birth
- **GG** (8th-9th): Governorate code
- **XXX** (10th-12th): Serial number
- **S** (13th): Gender (odd=male, even=female)

### Supported Governorates

The API recognizes all 27 Egyptian governorates plus foreign-born individuals (code 88).

## Architecture Decisions

### Security

- **Encrypted API Keys**: Keys are encrypted using Fernet (AES 128) before database storage
- **Hashed Lookups**: API key authentication uses SHA-256 hashes for fast, secure lookups
- **No Plain Text Storage**: Original API keys are never stored in plain text

### Performance

- **Database Indexing**: Strategic indexes on frequently queried fields
- **Rate Limiting**: Prevents API abuse while allowing legitimate usage
- **Minimal Dependencies**: Only essential packages to reduce attack surface

## Error Handling

The API provides detailed error messages for various validation failures:

- Invalid length (not 14 digits)
- Non-numeric characters
- Invalid century digit
- Invalid governorate code
- Invalid birth date
- Future birth dates

## Rate Limiting

- **Default**: 100 requests per minute per API key
- **Configurable**: Adjust via `DEFAULT_RATE_LIMIT` environment variable
- **Per-Key**: Each API key has independent rate limiting

## Logging

All validation requests are logged with:

- Timestamp
- National ID (for audit purposes)
- Validation result
- Extracted data (if successful)
- Error message (if failed)
- API key used (preview only for privacy)

## Admin Interface

Access Django admin at `/admin/` to:

- View and manage API keys
- Monitor validation logs
- Analyze usage patterns

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

The project follows Django best practices and PEP 8 standards.

## Production Deployment

1. Set `DEBUG=False` in environment variables
2. Configure `ALLOWED_HOSTS` for your domain
3. Use a production database (PostgreSQL recommended)
4. Set up proper logging (file-based)
5. Configure HTTPS
6. Set secure Django settings (CSRF, CORS, etc.)
