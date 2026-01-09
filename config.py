"""
Production-ready configuration management using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Settings
    app_name: str = "Contract Analyzer API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"  # development, staging, production

    # API Settings
    api_v1_prefix: str = "/api/v1"
    max_upload_size_mb: int = 50

    # OpenAI Settings
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 800
    openai_temperature: float = 0.0
    openai_timeout: int = 60
    openai_max_retries: int = 3

    # Supabase Settings
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # Authentication & Security
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours

    # Stripe Payment Settings
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    stripe_publishable_key: Optional[str] = None

    # Document Processing Settings
    max_contract_chars: int = 12000

    # CORS Settings
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 10

    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "json"  # json or text

    # Monitoring
    enable_metrics: bool = True

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures we only create one Settings instance.
    """
    return Settings()
