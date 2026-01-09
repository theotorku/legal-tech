# Legal Tech AI Platform - Quick Start Guide

## 🚀 Getting Started in 30 Minutes

This guide helps you build a minimal viable contract analyzer using the AI Cookbook patterns.

---

## Prerequisites

```bash
# Required
- Python 3.11+
- OpenAI API key
- Git

# Recommended
- Docker (for local development)
- PostgreSQL (or use SQLite for MVP)
```

---

## Step 1: Environment Setup (5 minutes)

```bash
# Clone the AI Cookbook
git clone https://github.com/yourusername/ai-cookbook.git
cd ai-cookbook

# Create new project directory
mkdir "legal tech"
cd "legal tech"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install docling lancedb openai python-dotenv fastapi uvicorn pydantic
```

Create `.env` file:

```bash
OPENAI_API_KEY=your_api_key_here
```

---

## Step 2: Document Processor (10 minutes)

Create `services/document_processor.py`:

```python
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from pathlib import Path

class ContractProcessor:
    def __init__(self):
        self.converter = DocumentConverter()

    def process(self, file_path: str):
        """Process a contract document."""
        # Convert document
        result = self.converter.convert(file_path)

        # Extract text and metadata
        document = result.document
        text = document.export_to_markdown()

        return {
            "text": text,
            "metadata": {
                "filename": Path(file_path).name,
                "pages": len(document.pages) if hasattr(document, 'pages') else 1
            }
        }

# Test it
if __name__ == "__main__":
    processor = ContractProcessor()
    result = processor.process("sample_contract.pdf")
    print(result["text"][:500])  # Print first 500 chars
```

---

## Step 3: Contract Analyzer (10 minutes)

Create `services/contract_analyzer.py`:

```python
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ContractAnalysis(BaseModel):
    """Structured contract analysis result."""
    contract_type: str = Field(description="Type of contract (NDA, MSA, etc.)")
    parties: List[str] = Field(description="Parties involved")
    key_dates: List[str] = Field(description="Important dates")
    key_terms: List[str] = Field(description="Key terms and conditions")
    risk_level: str = Field(description="Overall risk: Low, Medium, High")
    summary: str = Field(description="Brief summary of the contract")

class ContractAnalyzer:
    def __init__(self):
        self.client = client

    def analyze(self, contract_text: str) -> ContractAnalysis:
        """Analyze contract using GPT-4."""

        # Truncate if too long (GPT-4 context limit)
        max_chars = 12000
        if len(contract_text) > max_chars:
            contract_text = contract_text[:max_chars] + "..."

        completion = self.client.beta.chat.completions.parse(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": """You are a legal contract analyzer.
                    Analyze the contract and extract key information.
                    Be thorough but concise."""
                },
                {
                    "role": "user",
                    "content": f"Analyze this contract:\n\n{contract_text}"
                }
            ],
            response_format=ContractAnalysis
        )

        return completion.choices[0].message.parsed

# Test it
if __name__ == "__main__":
    analyzer = ContractAnalyzer()
    sample_text = "This NDA is between Company A and Company B..."
    result = analyzer.analyze(sample_text)
    print(result.model_dump_json(indent=2))
```

---

## Step 4: Simple API (5 minutes)

Create `main.py`:

```python
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from services.document_processor import ContractProcessor
from services.contract_analyzer import ContractAnalyzer
import tempfile
import os

app = FastAPI(title="Contract Analyzer API")

processor = ContractProcessor()
analyzer = ContractAnalyzer()

@app.post("/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    """Upload and analyze a contract."""

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Process document
        processed = processor.process(tmp_path)

        # Analyze contract
        analysis = analyzer.analyze(processed["text"])

        return {
            "filename": processed["metadata"]["filename"],
            "analysis": analysis.model_dump()
        }

    finally:
        # Clean up temp file
        os.unlink(tmp_path)

@app.get("/")
async def root():
    return {"message": "Contract Analyzer API", "version": "0.1.0"}

# Run with: uvicorn main:app --reload
```

---

## Step 5: Run It! (2 minutes)

```bash
# Start the API
uvicorn main:app --reload

# Test with curl (in another terminal)
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@sample_contract.pdf"
```

---

## Next Steps: Add More Features

### Add Clause Extraction

```python
class ClauseExtractor:
    def extract_clauses(self, contract_text: str) -> List[dict]:
        """Extract specific clauses from contract."""

        prompt = """Extract the following clauses from this contract:
        - Indemnification
        - Termination
        - Liability limitations
        - Payment terms
        - Confidentiality

        For each clause found, provide:
        1. Clause type
        2. Full text
        3. Risk level (Low/Medium/High)
        """

        # Implementation here...
```

### Add Vector Search for Similar Clauses

```python
import lancedb
from lancedb.embeddings import get_registry

class ClauseLibrary:
    def __init__(self):
        self.db = lancedb.connect("data/clauses")
        self.func = get_registry().get("openai").create(
            name="text-embedding-3-large"
        )

    def find_similar(self, clause_text: str, limit: int = 5):
        """Find similar clauses in the library."""
        table = self.db.open_table("clauses")
        results = table.search(clause_text).limit(limit).to_pandas()
        return results
```

---

## Production Checklist

Before deploying to production:

- [ ] Add authentication (Auth0, Supabase)
- [ ] Implement rate limiting
- [ ] Add error handling and logging
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Add document encryption
- [ ] Implement job queue for long-running tasks
- [ ] Add comprehensive tests
- [ ] Set up CI/CD pipeline
- [ ] Configure CORS properly
- [ ] Add API documentation (Swagger)
- [ ] Implement usage tracking
- [ ] Add backup and disaster recovery

---

## Cost Estimation

For 100 contracts/month:

```
OpenAI API costs:
- Document analysis: ~$1-2 per contract
- Embeddings: ~$0.10 per contract
- Total: ~$110-210/month

Infrastructure (AWS):
- EC2/ECS: ~$50/month
- S3 storage: ~$5/month
- Database: ~$25/month
- Total: ~$80/month

Grand Total: ~$190-290/month for 100 contracts
```

At $500/month pricing = 63-72% gross margin

---

## Resources

- [AI Cookbook Documentation](../README.md)
- [Docling Documentation](https://ds4sd.github.io/docling/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LanceDB Documentation](https://lancedb.github.io/lancedb/)

---
