"""
Production-ready Contract Analyzer API with FastAPI.
"""
import time
import tempfile
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import get_settings, Settings
from models import AnalyzeResponse, ErrorResponse, HealthResponse, DocumentMetadata
from exceptions import (
    ContractAnalyzerException,
    DocumentProcessingError,
    ContractAnalysisError,
    DatabaseError,
    ValidationError as AppValidationError
)
from logger import setup_logging, get_logger
from middleware import RequestIDMiddleware, LoggingMiddleware, SecurityHeadersMiddleware
from dependencies import (
    initialize_services,
    shutdown_services,
    get_processor,
    get_analyzer,
    get_db,
    get_request_id
)
from routers import auth, subscriptions

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Get settings
settings = get_settings()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    try:
        initialize_services(settings)
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    shutdown_services()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered contract analysis API for legal document processing",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add middleware (order matters - first added is outermost)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(subscriptions.router, prefix=settings.api_v1_prefix)


# Exception Handlers
@app.exception_handler(ContractAnalyzerException)
async def contract_analyzer_exception_handler(request: Request, exc: ContractAnalyzerException):
    """Handle custom application exceptions."""
    request_id = get_request_id(request)

    logger.error(
        f"Application error: {exc.message}",
        extra={
            "error_type": type(exc).__name__,
            "status_code": exc.status_code,
            "details": exc.details
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            request_id=request_id,
            error=type(exc).__name__,
            message=exc.message,
            details=[{"message": str(v), "field": k}
                     for k, v in exc.details.items()] if exc.details else None,
            timestamp=datetime.utcnow()
        ).model_dump(mode='json')
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    request_id = get_request_id(request)

    logger.warning(
        "Validation error",
        extra={"errors": exc.errors()}
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            request_id=request_id,
            error="ValidationError",
            message="Request validation failed",
            details=[
                {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"]
                }
                for err in exc.errors()
            ],
            timestamp=datetime.utcnow()
        ).model_dump(mode='json')
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    request_id = get_request_id(request)

    logger.error(
        f"Unexpected error: {str(exc)}",
        exc_info=True
    )

    # Don't expose internal errors in production
    message = str(
        exc) if settings.is_development else "An internal error occurred"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            request_id=request_id,
            error="InternalServerError",
            message=message,
            timestamp=datetime.utcnow()
        ).model_dump(mode='json')
    )


# API Routes
@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs_url": "/docs" if not settings.is_production else None,
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db=Depends(get_db)):
    """
    Health check endpoint for monitoring.
    Returns service status and component health.
    """
    checks = {
        "api": "healthy",
        "database": "not_configured"
    }

    # Check database if configured
    if db:
        try:
            db_healthy = await db.health_check()
            checks["database"] = "healthy" if db_healthy else "unhealthy"
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            checks["database"] = "unhealthy"

    # Determine overall status
    if any(v == "unhealthy" for v in checks.values()):
        overall_status = "unhealthy"
    elif any(v == "degraded" for v in checks.values()):
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return HealthResponse(
        status=overall_status,
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        checks=checks
    )


@app.post(
    f"{settings.api_v1_prefix}/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    tags=["Analysis"]
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute" if settings.rate_limit_enabled else "1000/minute")
async def analyze_contract(
    request: Request,
    file: UploadFile = File(...,
                            description="Contract file to analyze (PDF, DOCX, etc.)"),
    processor=Depends(get_processor),
    analyzer=Depends(get_analyzer),
    db=Depends(get_db),
    request_id: str = Depends(get_request_id)
):
    """
    Analyze a contract document and extract key information.

    This endpoint:
    1. Accepts a contract file upload
    2. Extracts text from the document
    3. Analyzes the contract using AI
    4. Optionally persists results to database
    5. Returns structured analysis results

    **Supported file formats:** PDF, DOCX, DOC, TXT

    **Rate limit:** {settings.rate_limit_per_minute} requests per minute
    """
    start_time = time.time()
    tmp_path = None

    try:
        # Validate file
        if not file.filename:
            raise AppValidationError(
                message="Filename is required",
                details={"field": "file"}
            )

        # Check file size
        content = await file.read()
        file_size = len(content)

        if file_size > settings.max_upload_size_bytes:
            raise AppValidationError(
                message=f"File size exceeds maximum allowed size of {settings.max_upload_size_mb}MB",
                details={
                    "file_size": file_size,
                    "max_size": settings.max_upload_size_bytes
                }
            )

        logger.info(f"Processing file: {file.filename}", extra={
            "filename": file.filename,
            "size_bytes": file_size,
            "content_type": file.content_type
        })

        # Save uploaded file temporarily
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # Process document
        processed = await processor.process(tmp_path)

        # Analyze contract
        analysis_obj = await analyzer.analyze(processed["text"])
        analysis = analysis_obj.model_dump()

        # Persist to database if available
        record_id = None
        if db:
            try:
                record = await db.insert_contract(processed["metadata"], analysis)
                record_id = record.get("id") if record else None
            except DatabaseError as e:
                # Log but don't fail the request if database is unavailable
                logger.warning(f"Failed to persist to database: {str(e)}")

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(f"Analysis completed successfully: {file.filename}", extra={
            "filename": file.filename,
            "contract_type": analysis["contract_type"],
            "processing_time_ms": processing_time_ms
        })

        return AnalyzeResponse(
            request_id=request_id,
            filename=processed["metadata"]["filename"],
            analysis=analysis_obj,
            metadata=DocumentMetadata(**processed["metadata"]),
            record_id=record_id,
            processing_time_ms=processing_time_ms
        )

    finally:
        # Cleanup temporary file
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")
