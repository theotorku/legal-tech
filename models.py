"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime


class ContractAnalysis(BaseModel):
    """Contract analysis result schema."""
    
    contract_type: str = Field(description="Type of contract (NDA, MSA, etc.)")
    parties: list[str] = Field(description="Parties involved")
    key_dates: list[str] = Field(description="Important dates")
    key_terms: list[str] = Field(description="Key terms and conditions")
    risk_level: str = Field(description="Overall risk: Low, Medium, High")
    summary: str = Field(description="Brief summary of the contract")


class DocumentMetadata(BaseModel):
    """Document metadata schema."""
    
    filename: str = Field(description="Original filename")
    pages: int = Field(default=1, description="Number of pages")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    content_type: Optional[str] = Field(default=None, description="MIME type")


class AnalyzeResponse(BaseModel):
    """Response model for contract analysis endpoint."""
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
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
    })
    
    request_id: str = Field(description="Unique request identifier")
    filename: str = Field(description="Processed filename")
    analysis: ContractAnalysis = Field(description="Contract analysis results")
    metadata: DocumentMetadata = Field(description="Document metadata")
    record_id: Optional[str] = Field(default=None, description="Database record ID if persisted")
    processing_time_ms: int = Field(description="Processing time in milliseconds")


class ErrorDetail(BaseModel):
    """Error detail schema."""
    
    field: Optional[str] = Field(default=None, description="Field that caused the error")
    message: str = Field(description="Error message")
    type: Optional[str] = Field(default=None, description="Error type")


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "request_id": "550e8400-e29b-41d4-a716-446655440000",
            "error": "Validation Error",
            "message": "Invalid file format",
            "details": [
                {
                    "field": "file",
                    "message": "Only PDF and DOCX files are supported",
                    "type": "value_error"
                }
            ],
            "timestamp": "2024-01-08T12:00:00Z"
        }
    })
    
    request_id: str = Field(description="Unique request identifier")
    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    details: Optional[list[ErrorDetail]] = Field(default=None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class HealthResponse(BaseModel):
    """Health check response schema."""
    
    status: str = Field(description="Service status: healthy, degraded, unhealthy")
    version: str = Field(description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    checks: dict[str, Any] = Field(description="Individual component health checks")


class MetricsResponse(BaseModel):
    """Metrics response schema."""
    
    total_requests: int = Field(description="Total number of requests processed")
    successful_requests: int = Field(description="Number of successful requests")
    failed_requests: int = Field(description="Number of failed requests")
    average_processing_time_ms: float = Field(description="Average processing time in milliseconds")
    uptime_seconds: float = Field(description="Service uptime in seconds")

