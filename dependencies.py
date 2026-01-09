"""
FastAPI dependencies for dependency injection.
"""
from typing import Optional
from fastapi import Depends, Request

from config import Settings, get_settings
from services.contract_analyzer import ContractAnalyzer
from services.document_processor import ContractProcessor
from services.database import SupabaseService
from services.auth_service import AuthService
from services.subscription_service import SubscriptionService
from services.payment_service import PaymentService
from logger import get_logger

logger = get_logger(__name__)

# Global instances (initialized on startup)
_processor: Optional[ContractProcessor] = None
_analyzer: Optional[ContractAnalyzer] = None
_db: Optional[SupabaseService] = None
_auth_service: Optional[AuthService] = None
_subscription_service: Optional[SubscriptionService] = None
_payment_service: Optional[PaymentService] = None


def initialize_services(settings: Settings):
    """
    Initialize global service instances.
    Called during application startup.
    """
    global _processor, _analyzer, _db, _auth_service, _subscription_service, _payment_service

    logger.info("Initializing services...")

    # Initialize processor
    _processor = ContractProcessor()
    logger.info("ContractProcessor initialized")

    # Initialize analyzer
    _analyzer = ContractAnalyzer(settings)
    logger.info("ContractAnalyzer initialized")

    # Initialize database (optional)
    if settings.supabase_url and settings.supabase_key:
        try:
            _db = SupabaseService()
            logger.info("SupabaseService initialized")

            # Initialize auth service
            _auth_service = AuthService(_db.client)
            logger.info("AuthService initialized")

            # Initialize subscription service
            _subscription_service = SubscriptionService(_db.client)
            logger.info("SubscriptionService initialized")

            # Initialize payment service (if Stripe configured)
            if settings.stripe_api_key:
                _payment_service = PaymentService(
                    _db.client, settings.stripe_api_key)
                logger.info("PaymentService initialized")
            else:
                logger.info("Stripe not configured, skipping payment service")

        except Exception as e:
            logger.warning(f"Failed to initialize services: {str(e)}")
            _db = None
            _auth_service = None
            _subscription_service = None
            _payment_service = None
    else:
        logger.info(
            "Supabase not configured, skipping database-dependent services")
        _db = None
        _auth_service = None
        _subscription_service = None
        _payment_service = None

    logger.info("All services initialized successfully")


def shutdown_services():
    """
    Cleanup service instances.
    Called during application shutdown.
    """
    global _processor, _analyzer, _db, _auth_service, _subscription_service, _payment_service

    logger.info("Shutting down services...")

    # Cleanup if needed
    _processor = None
    _analyzer = None
    _db = None
    _auth_service = None
    _subscription_service = None
    _payment_service = None

    logger.info("Services shutdown complete")


def get_processor() -> ContractProcessor:
    """Dependency to get ContractProcessor instance."""
    if _processor is None:
        raise RuntimeError("ContractProcessor not initialized")
    return _processor


def get_analyzer() -> ContractAnalyzer:
    """Dependency to get ContractAnalyzer instance."""
    if _analyzer is None:
        raise RuntimeError("ContractAnalyzer not initialized")
    return _analyzer


def get_db() -> Optional[SupabaseService]:
    """Dependency to get SupabaseService instance (may be None)."""
    return _db


def get_auth_service() -> AuthService:
    """Dependency to get AuthService instance."""
    if _auth_service is None:
        raise RuntimeError("AuthService not initialized - Supabase required")
    return _auth_service


def get_subscription_service() -> SubscriptionService:
    """Dependency to get SubscriptionService instance."""
    if _subscription_service is None:
        raise RuntimeError(
            "SubscriptionService not initialized - Supabase required")
    return _subscription_service


def get_payment_service() -> PaymentService:
    """Dependency to get PaymentService instance."""
    if _payment_service is None:
        raise RuntimeError("PaymentService not initialized - Stripe required")
    return _payment_service


def get_request_id(request: Request) -> str:
    """Dependency to get request ID from request state."""
    return getattr(request.state, "request_id", "unknown")
