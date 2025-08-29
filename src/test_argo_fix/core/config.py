"""Application configuration."""

import secrets
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    project_name: str = "test_argo_fix"
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Security
    # Generate a secure default to avoid hardcoded secrets in code scanners
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key used for signing tokens",
    )
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration in minutes"
    )

    # Server
    # Default to localhost to avoid Bandit B104 (hardcoded bind-all-interfaces)
    # In containers/k8s, override HOST env to 0.0.0.0 at deploy time.
    host: str = Field(default="127.0.0.1", description="Host to bind to")
    port: int = Field(default=8080, description="Port to bind to")

    # API
    api_v1_str: str = Field(default="/api/v1", description="API v1 prefix")
    allowed_hosts: List[str] = Field(
        default_factory=lambda: ["*"], description="Allowed CORS origins"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
