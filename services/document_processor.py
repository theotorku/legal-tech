"""
Document processing service with async support and error handling.
"""
import asyncio
from pathlib import Path
from typing import Optional
import os

from exceptions import DocumentProcessingError
from logger import get_logger

logger = get_logger(__name__)

# Lazily import docling to avoid hard dependency during tests
DocumentConverter = None


class ContractProcessor:
    """
    Async document processor for extracting text from contracts.
    """

    def __init__(self):
        """Initialize the document processor."""
        global DocumentConverter

        # Attempt lazy import
        if DocumentConverter is None:
            try:
                from docling.document_converter import DocumentConverter as _DC
                DocumentConverter = _DC
                logger.info("DocumentConverter loaded successfully")
            except Exception as e:
                logger.warning(f"DocumentConverter not available: {str(e)}")
                DocumentConverter = None

        self.converter = DocumentConverter() if DocumentConverter is not None else None

    def _ensure_converter(self):
        """Ensure converter is available, raise error if not."""
        if self.converter is None:
            global DocumentConverter
            try:
                from docling.document_converter import DocumentConverter as _DC
                DocumentConverter = _DC
                self.converter = DocumentConverter()
                logger.info("DocumentConverter loaded on demand")
            except Exception as e:
                logger.error("Failed to load DocumentConverter", exc_info=True)
                raise DocumentProcessingError(
                    message="docling is required to process documents",
                    details={
                        "error": str(e),
                        "solution": "Install with: pip install docling"
                    }
                ) from e

    async def process(self, file_path: str) -> dict:
        """
        Process a contract document and return text + metadata.

        Args:
            file_path: Path to the document file

        Returns:
            Dictionary with 'text' and 'metadata' keys

        Raises:
            DocumentProcessingError: If processing fails
        """
        try:
            self._ensure_converter()

            # Validate file exists
            path = Path(file_path)
            if not path.exists():
                raise DocumentProcessingError(
                    message=f"File not found: {file_path}",
                    details={"file_path": file_path}
                )

            # Get file size
            file_size = path.stat().st_size

            logger.info(f"Processing document: {path.name}", extra={
                "filename": path.name,
                "size_bytes": file_size
            })

            # Run conversion in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.converter.convert,
                file_path
            )

            document = result.document
            text = document.export_to_markdown()

            metadata = {
                "filename": path.name,
                "pages": len(document.pages) if hasattr(document, "pages") else 1,
                "file_size": file_size,
                "content_type": self._get_content_type(path.suffix)
            }

            logger.info(f"Document processed successfully: {path.name}", extra={
                "pages": metadata["pages"],
                "text_length": len(text)
            })

            return {
                "text": text,
                "metadata": metadata,
            }

        except DocumentProcessingError:
            raise
        except Exception as e:
            logger.error(
                f"Failed to process document: {str(e)}", exc_info=True)
            raise DocumentProcessingError(
                message=f"Failed to process document: {str(e)}",
                details={
                    "file_path": file_path,
                    "error": str(e)
                }
            ) from e

    def _get_content_type(self, suffix: str) -> str:
        """Get MIME type from file suffix."""
        content_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".txt": "text/plain",
        }
        return content_types.get(suffix.lower(), "application/octet-stream")
