from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Subscription and Expense Analytics Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security & JWT
    SECRET_KEY: str = "prod-insecure-secret-key-change-in-production-min-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    INTERNAL_SERVICE_SECRET: str = "internal-analytics-shared-secret-key-prod-2026"

    # Database
    DATABASE_URL: str = "sqlite:///./subscription_tracker.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis Caching
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    CACHE_DEFAULT_TTL: int = 300  # 5 minutes
    CACHE_ENABLED: bool = True

    # Analytics & AI Service Integration
    ANALYTICS_SERVICE_URL: str = "http://localhost:5001"
    AI_SERVICE_URL: str = "http://localhost:5001"
    AI_SERVICE_TIMEOUT: float = 15.0

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:80",
        "http://localhost:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
