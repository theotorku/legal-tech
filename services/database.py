"""
Database service for Supabase with async support and error handling.
"""
from typing import Any, Optional
from supabase import create_client, Client
from tenacity import retry, stop_after_attempt, wait_exponential

from config import get_settings
from exceptions import DatabaseError
from logger import get_logger

logger = get_logger(__name__)


class SupabaseService:
    """
    Async Supabase service for contract data persistence.
    """

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize Supabase client.

        Args:
            url: Supabase URL (optional, reads from settings if not provided)
            key: Supabase key (optional, reads from settings if not provided)

        Raises:
            DatabaseError: If credentials are missing
        """
        settings = get_settings()
        url = url or settings.supabase_url
        key = key or settings.supabase_key

        if not url or not key:
            raise DatabaseError(
                message="SUPABASE_URL and SUPABASE_KEY must be configured",
                details={
                    "solution": "Set SUPABASE_URL and SUPABASE_KEY in environment or .env file"
                }
            )

        try:
            self.client: Client = create_client(url, key)
            self.table = self.client.table("contracts")
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(
                f"Failed to initialize Supabase client: {str(e)}", exc_info=True)
            raise DatabaseError(
                message="Failed to initialize database connection",
                details={"error": str(e)}
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def insert_contract(
        self,
        metadata: dict[str, Any],
        analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Insert contract analysis into database with retry logic.

        Args:
            metadata: Document metadata
            analysis: Contract analysis results

        Returns:
            Inserted record data

        Raises:
            DatabaseError: If insertion fails
        """
        try:
            payload = {
                "filename": metadata.get("filename"),
                "pages": metadata.get("pages", 1),
                "file_size": metadata.get("file_size"),
                "content_type": metadata.get("content_type"),
                "contract_type": analysis.get("contract_type"),
                "parties": analysis.get("parties"),
                "key_dates": analysis.get("key_dates"),
                "key_terms": analysis.get("key_terms"),
                "risk_level": analysis.get("risk_level"),
                "summary": analysis.get("summary"),
                "analysis": analysis,
            }

            logger.debug("Inserting contract into database", extra={
                "filename": payload["filename"],
                "contract_type": payload["contract_type"]
            })

            res = self.table.insert(payload).execute()

            # Check for errors
            if hasattr(res, 'error') and res.error:
                raise DatabaseError(
                    message=f"Failed to insert contract: {res.error}",
                    details={"error": str(res.error)}
                )

            record = res.data[0] if res.data else None

            if record:
                logger.info("Contract inserted successfully", extra={
                    "record_id": record.get("id"),
                    "filename": payload["filename"]
                })

            return record

        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Database insertion failed: {str(e)}", exc_info=True)
            raise DatabaseError(
                message=f"Failed to insert contract: {str(e)}",
                details={"error": str(e), "payload": payload}
            ) from e

    async def health_check(self) -> bool:
        """
        Check database connectivity.

        Returns:
            True if database is accessible, False otherwise
        """
        try:
            # Simple query to check connectivity
            self.table.select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
