# Contract Analyzer API

Production-ready AI-powered contract analysis API built with FastAPI, OpenAI, and Supabase.

## Features

- 🤖 **AI-Powered Analysis**: Uses OpenAI GPT models to extract key contract information
- 📄 **Multi-Format Support**: Processes PDF, DOCX, DOC, and TXT files
- 🔒 **Production-Ready**: Includes logging, error handling, rate limiting, and security headers
- 🚀 **Async Architecture**: Fully asynchronous for high performance
- 📊 **Health Monitoring**: Built-in health checks and metrics
- 🔄 **Retry Logic**: Automatic retries for transient failures
- 🗄️ **Database Integration**: Optional Supabase persistence
- 🐳 **Docker Support**: Ready for containerized deployment

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- (Optional) Supabase account for data persistence

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "Legal Tech"
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Configuration

All configuration is managed through environment variables. See `.env.example` for all available options.

### Required Settings

- `OPENAI_API_KEY`: Your OpenAI API key

### Optional Settings

- `SUPABASE_URL`: Supabase project URL (for persistence)
- `SUPABASE_KEY`: Supabase API key
- `ENVIRONMENT`: `development`, `staging`, or `production`
- `LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `RATE_LIMIT_PER_MINUTE`: API rate limit (default: 10)

## API Endpoints

### POST /api/v1/analyze

Analyze a contract document.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (contract document)

**Response:**
```json
{
  "request_id": "uuid",
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
  "record_id": "uuid",
  "processing_time_ms": 1234
}
```

### GET /health

Health check endpoint for monitoring.

### GET /

API information and version.

## Docker Deployment

### Build and run with Docker Compose:

```bash
docker-compose up -d
```

### Build Docker image:

```bash
docker build -t contract-analyzer .
```

### Run Docker container:

```bash
docker run -p 8000:8000 --env-file .env contract-analyzer
```

## Development

### Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Run tests:

```bash
pytest
```

### Code formatting:

```bash
black .
ruff check .
```

### Type checking:

```bash
mypy .
```

## Production Deployment

### Recommended Setup

1. Use environment variables for all secrets
2. Enable HTTPS/TLS
3. Set up proper monitoring and alerting
4. Configure rate limiting based on your needs
5. Use a reverse proxy (nginx, Caddy) in front of the API
6. Set `ENVIRONMENT=production` to disable debug endpoints

### Environment Variables for Production

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_ENABLED=true
```

## Architecture

- **FastAPI**: Modern async web framework
- **OpenAI**: GPT models for contract analysis
- **Docling**: Document processing and text extraction
- **Supabase**: PostgreSQL database for persistence
- **Tenacity**: Retry logic for resilience
- **Pydantic**: Data validation and settings management

## License

[Your License Here]

