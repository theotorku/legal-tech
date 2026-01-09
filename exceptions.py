"""
Custom exceptions for the Contract Analyzer API.
"""
from typing import Any, Optional


class ContractAnalyzerException(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DocumentProcessingError(ContractAnalyzerException):
    """Raised when document processing fails."""
    
    def __init__(self, message: str = "Failed to process document", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class ContractAnalysisError(ContractAnalyzerException):
    """Raised when contract analysis fails."""
    
    def __init__(self, message: str = "Failed to analyze contract", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class DatabaseError(ContractAnalyzerException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class ValidationError(ContractAnalyzerException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Validation failed", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class RateLimitError(ContractAnalyzerException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=429, details=details)


class OpenAIError(ContractAnalyzerException):
    """Raised when OpenAI API calls fail."""
    
    def __init__(self, message: str = "OpenAI API error", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=502, details=details)

