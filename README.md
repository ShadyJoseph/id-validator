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

Generate a Django SECRET_KEY and create a `.env` file in the root directory:

```bash
# Generate Django SECRET_KEY (required for Django to function)
python -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(50)))"
```

Create `.env` file:

```env
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
DEFAULT_RATE_LIMIT=100/minute
```

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Create API Key via Admin

1. Run the server: `python manage.py runserver`
2. Go to Django admin: `http://localhost:8000/admin/`
3. Log in with your superuser credentials
4. Navigate to **Api Keys** → **Add Api key**
5. Select a user and click **Save**
6. **Important**: Copy the generated API key immediately - it cannot be retrieved again!

### 5. API Ready!

The API will be available at `http://localhost:8000/api/v1/`

## API Usage

### Endpoint

```
POST /api/v1/national-id/
```

### Example Requests

#### PowerShell (Windows)

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/national-id/" `
    -Method POST `
    -Headers @{ "X-API-KEY" = "5qxlToTFWUrOvvQAUdbsUoh9Ss6VkfhM" } `
    -ContentType "application/json" `
    -Body '{"national_id": "30307020102112"}'
```

#### Bash/Terminal (Linux/Mac)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/national-id/ \
    -H "X-API-KEY: 5qxlToTFWUrOvvQAUdbsUoh9Ss6VkfhM" \
    -H "Content-Type: application/json" \
    -d '{"national_id": "30307020102112"}'
```

### Request Body

```json
{
  "national_id": "30307020102112"
}
```

### Response (Valid ID)

```json
{
  "valid": true,
  "message": "Validation successful",
  "birth_year": 2003,
  "birth_date": "02/07/2003",
  "gender": "Male",
  "governorate": "Cairo"
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

## Managing API Keys

### Django Admin Interface

Access the admin at `/admin/` to:

- **Create API Keys**: Generate new keys for clients
- **View API Keys**: See all keys with masked previews
- **Activate/Deactivate**: Control key access
- **Monitor Logs**: View all validation requests and results

### Key Features

- **Auto-generation**: Keys are automatically generated securely
- **One-time Display**: Generated keys are shown only once for security
- **Encrypted Storage**: Keys are encrypted before database storage
- **Usage Tracking**: Monitor which keys are being used

## Architecture Decisions

### Security

- **Encrypted API Keys**: Keys are encrypted using Fernet (AES 128) before database storage
- **Hashed Lookups**: API key authentication uses SHA-256 hashes for fast, secure lookups
- **No Plain Text Storage**: Original API keys are never stored in plain text

### Performance

- **Database Indexing**: Strategic indexes on frequently queried fields
- **Rate Limiting**: Prevents API abuse while allowing legitimate usage
- **Minimal Dependencies**: Only essential packages to reduce attack surface

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

## Development

### Running Tests

```bash
python manage.py test
```
