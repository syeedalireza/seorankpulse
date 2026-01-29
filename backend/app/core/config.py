"""
Application configuration using Pydantic Settings.

This module manages all environment variables and application settings
using Pydantic's BaseSettings for type safety and validation.
"""

from typing import List, Optional
from functools import lru_cache

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "SEO Analysis Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    # Database - PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "seo_db"
    POSTGRES_USER: str = "seo_user"
    POSTGRES_PASSWORD: str
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        """Construct PostgreSQL connection URL."""
        if isinstance(v, str):
            return v
        
        values = info.data
        return (
            f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:"
            f"{values.get('POSTGRES_PASSWORD')}@"
            f"{values.get('POSTGRES_HOST')}:{values.get('POSTGRES_PORT')}/"
            f"{values.get('POSTGRES_DB')}"
        )

    # Neo4j Graph Database
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str

    # Elasticsearch
    ELASTICSEARCH_HOST: str = "localhost:9200"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # AI/ML API Keys
    HUGGINGFACE_API_KEY: Optional[str] = None
    GOOGLE_CLOUD_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    SERP_API_KEY: Optional[str] = None

    # Crawler Settings
    CRAWLER_USER_AGENT: str = "SEO-Analyzer-Bot/1.0"
    CRAWLER_MAX_DEPTH: int = 10
    CRAWLER_DELAY_MS: int = 1000
    CRAWLER_CONCURRENT_REQUESTS: int = 10
    CRAWLER_TIMEOUT_SECONDS: int = 30

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def is_development(self) -> bool:
        """Check if application is running in development mode."""
        return self.ENVIRONMENT.lower() in ("development", "dev")

    @property
    def is_production(self) -> bool:
        """Check if application is running in production mode."""
        return self.ENVIRONMENT.lower() in ("production", "prod")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Using lru_cache ensures settings are loaded only once
    and reused across the application.
    
    Returns:
        Settings: Application settings instance.
    """
    return Settings()


# Global settings instance
settings = get_settings()
