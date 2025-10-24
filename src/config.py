"""Configuration module for the banking service."""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Banking Service"
    app_env: str = "development"
    debug: bool = True

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    reload: bool = True

    # Database
    database_url: str
    database_echo: bool = False
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()  # type: ignore
