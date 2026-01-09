"""
Contract analysis service using OpenAI API with async support and retry logic.
"""
import json
from openai import AsyncOpenAI
from pydantic import ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from typing import Optional

from config import get_settings
from models import ContractAnalysis
from exceptions import ContractAnalysisError, OpenAIError
from logger import get_logger

logger = get_logger(__name__)


class ContractAnalyzer:
    """
    Async contract analyzer using OpenAI API with retry logic.
    """

    def __init__(self, settings: Optional[object] = None):
        """Initialize the analyzer with settings."""
        self.settings = settings or get_settings()
        self.client = AsyncOpenAI(
            api_key=self.settings.openai_api_key,
            timeout=self.settings.openai_timeout,
            max_retries=0  # We handle retries with tenacity
        )
        logger.info("ContractAnalyzer initialized", extra={
            "model": self.settings.openai_model,
            "max_tokens": self.settings.openai_max_tokens
        })

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((OpenAIError, Exception)),
        reraise=True
    )
    async def _call_openai(self, messages: list[dict]) -> str:
        """
        Call OpenAI API with retry logic.

        Args:
            messages: List of message dictionaries

        Returns:
            Assistant's response text

        Raises:
            OpenAIError: If API call fails after retries
        """
        try:
            logger.debug("Calling OpenAI API", extra={
                         "model": self.settings.openai_model})

            response = await self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=messages,
                max_tokens=self.settings.openai_max_tokens,
                temperature=self.settings.openai_temperature
            )

            content = response.choices[0].message.content
            logger.debug("OpenAI API call successful", extra={
                "tokens_used": response.usage.total_tokens if response.usage else None
            })

            return content

        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}", exc_info=True)
            raise OpenAIError(
                message=f"Failed to call OpenAI API: {str(e)}",
                details={"error": str(e)}
            ) from e

    def _parse_json_response(self, text: str) -> dict:
        """
        Parse JSON from OpenAI response, handling various formats.

        Args:
            text: Response text from OpenAI

        Returns:
            Parsed JSON dictionary

        Raises:
            ContractAnalysisError: If JSON parsing fails
        """
        try:
            # Try direct parsing first
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # Fallback: extract JSON block from text
            start = text.find("{")
            end = text.rfind("}")

            if start != -1 and end != -1:
                try:
                    return json.loads(text[start:end+1])
                except json.JSONDecodeError as e:
                    logger.error("Failed to parse JSON from response", extra={
                                 "text": text[:200]})
                    raise ContractAnalysisError(
                        message="Failed to parse JSON from model output",
                        details={"error": str(
                            e), "response_preview": text[:200]}
                    ) from e
            else:
                logger.error("No JSON found in response",
                             extra={"text": text[:200]})
                raise ContractAnalysisError(
                    message="Model did not return JSON output as expected",
                    details={"response_preview": text[:200]}
                )

    async def analyze(self, contract_text: str) -> ContractAnalysis:
        """
        Analyze contract text and return a validated ContractAnalysis object.

        Args:
            contract_text: The contract text to analyze

        Returns:
            ContractAnalysis object with extracted information

        Raises:
            ContractAnalysisError: If analysis fails
        """
        try:
            # Truncate text if too long
            if len(contract_text) > self.settings.max_contract_chars:
                logger.warning(
                    f"Contract text truncated from {len(contract_text)} to {self.settings.max_contract_chars} chars"
                )
                contract_text = contract_text[:self.settings.max_contract_chars] + "..."

            # Build prompt
            prompt = (
                "You are a legal contract analyzer. Extract the following fields and "
                "return a JSON object with keys: contract_type, parties (list), "
                "key_dates (list), key_terms (list), risk_level, summary. Be concise.\n\n"
                f"CONTRACT:\n{contract_text}"
            )

            messages = [
                {"role": "system", "content": "You are a helpful legal contract analyzer."},
                {"role": "user", "content": prompt},
            ]

            # Call OpenAI with retry logic
            assistant_text = await self._call_openai(messages)

            # Parse JSON response
            parsed = self._parse_json_response(assistant_text)

            # Validate with Pydantic
            try:
                analysis = ContractAnalysis.model_validate(parsed)
                logger.info("Contract analysis completed successfully", extra={
                    "contract_type": analysis.contract_type,
                    "risk_level": analysis.risk_level
                })
                return analysis

            except ValidationError as e:
                logger.error("Contract analysis validation failed",
                             extra={"errors": e.errors()})
                raise ContractAnalysisError(
                    message="Contract analysis did not match expected schema",
                    details={"validation_errors": e.errors()}
                ) from e

        except (OpenAIError, ContractAnalysisError):
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error during contract analysis: {str(e)}", exc_info=True)
            raise ContractAnalysisError(
                message=f"Unexpected error during analysis: {str(e)}",
                details={"error": str(e)}
            ) from e
