# Implementation Plan - Legal Tech AI Platform (Supabase Edition)

This plan adapts the `quick-start.md` guide to build a Legal Tech MVP using Supabase for data persistence instead of transient storage or LanceDB.

## 1. Project Initialization & Environment Setup
- [ ] Use project directory `Legal Tech` (Current Directory).
- [ ] Initialize Python virtual environment (if not exists).
- [ ] Install dependencies:
    - Core: `docling`, `openai`, `python-dotenv`, `fastapi`, `uvicorn`, `pydantic`
    - Database: `supabase`
- [ ] Create `.env` file structure (User to fill in keys).

## 2. Supabase Schema Design
- [ ] Define SQL schema for `contracts` table to store:
    - Contract metadata (filename, page count).
    - Analysis results (type, parties, risk level, summary, key terms).
    - Timestamp.
- [ ] Provide SQL script for user to run in Supabase SQL Editor.

## 3. Core Services Implementation
- [ ] **Document Processor** (`services/document_processor.py`):
    - Implement `ContractProcessor` using `docling` to extract text and metadata.
- [ ] **Contract Analyzer** (`services/contract_analyzer.py`):
    - Implement `ContractAnalyzer` using `openai` to analyze text and return structured `ContractAnalysis`.
- [ ] **Database Service** (`services/database.py`):
    - **NEW**: Implement `SupabaseService` to handle inserting analysis results into the `contracts` table.

## 4. API Development
- [ ] **Main API** (`main.py`):
    - Setup FastAPI app.
    - Implement `POST /analyze` endpoint:
        1. Receive file.
        2. Process with `ContractProcessor`.
        3. Analyze with `ContractAnalyzer`.
        4. **Store result** using `SupabaseService`.
        5. Return result to client.

## 5. Deployment & Testing
- [ ] Run application with `uvicorn`.
- [ ] Verify content extraction.
- [ ] Verify OpenAI analysis.
- [ ] Verify data persistence in Supabase.

## 6. Next Steps (Optional)
- [ ] Add Vector Search (using Supabase `pgvector` instead of LanceDB).
- [ ] Add Clause Extraction.
