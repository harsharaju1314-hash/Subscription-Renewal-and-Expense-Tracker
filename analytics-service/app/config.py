import os

class AnalyticsConfig:
    SERVICE_NAME: str = "Flask Analytics Service"
    PORT: int = int(os.getenv("PORT", "5001"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    INTERNAL_SERVICE_SECRET: str = os.getenv(
        "INTERNAL_SERVICE_SECRET", "internal-analytics-shared-secret-key-prod-2026"
    )
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

settings = AnalyticsConfig()
