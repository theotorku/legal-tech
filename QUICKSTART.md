# Quick Start Guide

Get the Contract Analyzer API running in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Installation

### 1. Set up environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API key

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 3. Run the application

```bash
# Development mode with auto-reload
uvicorn main:app --reload

# Or use the Makefile
make run
```

The API will be available at: **http://localhost:8000**

## Test the API

### Using the Interactive Docs

1. Open http://localhost:8000/docs in your browser
2. Click on "POST /api/v1/analyze"
3. Click "Try it out"
4. Upload a contract file
5. Click "Execute"

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@contract.pdf"
```

### Using Python

```python
import requests

url = "http://localhost:8000/api/v1/analyze"
files = {"file": open("contract.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## Check Health

```bash
curl http://localhost:8000/health
```

## Optional: Set up Database

If you want to persist analysis results:

1. Create a [Supabase](https://supabase.com) account (free tier available)
2. Create a new project
3. Run the SQL in `supabase_sql.sql` in the SQL Editor
4. Add to your `.env`:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   ```
5. Restart the application

## Docker Quick Start

If you prefer Docker:

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## Common Commands

```bash
# Run tests
make test

# Format code
make format

# Check code quality
make lint

# Clean temporary files
make clean
```

## Configuration

Key environment variables (see `.env.example` for all options):

- `OPENAI_API_KEY` - **Required** - Your OpenAI API key
- `ENVIRONMENT` - `development` or `production` (default: production)
- `LOG_LEVEL` - `DEBUG`, `INFO`, `WARNING`, `ERROR` (default: INFO)
- `RATE_LIMIT_PER_MINUTE` - API rate limit (default: 10)
- `MAX_UPLOAD_SIZE_MB` - Max file size (default: 50)

## Supported File Formats

- PDF (`.pdf`)
- Microsoft Word (`.docx`, `.doc`)
- Plain text (`.txt`)

## API Response Example

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "contract.pdf",
  "analysis": {
    "contract_type": "NDA",
    "parties": ["Company A", "Company B"],
    "key_dates": ["2024-01-01"],
    "key_terms": ["Confidentiality", "Non-disclosure"],
    "risk_level": "Low",
    "summary": "Standard NDA between two parties"
  },
  "metadata": {
    "filename": "contract.pdf",
    "pages": 5,
    "file_size": 102400,
    "content_type": "application/pdf"
  },
  "record_id": "123e4567-e89b-12d3-a456-426614174000",
  "processing_time_ms": 1234
}
```

## Troubleshooting

**Issue: ModuleNotFoundError**
- Solution: Make sure you activated the virtual environment and installed dependencies

**Issue: OpenAI API error**
- Solution: Check that your API key is correct and has credits

**Issue: File upload fails**
- Solution: Check file size is under 50MB and format is supported

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Review [CHANGELOG.md](CHANGELOG.md) for all features

## Support

For issues or questions:
1. Check the documentation
2. Review error logs
3. Open an issue on GitHub

## License

[Your License Here]

