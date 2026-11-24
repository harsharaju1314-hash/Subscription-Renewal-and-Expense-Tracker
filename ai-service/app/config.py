import os

# Disable telemetry and remote tracing lookups for immediate local execution
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["ANONYMIZED_TELEMETRY"] = "false"

from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    SERVICE_NAME: str = "Financial AI Inference Microservice"
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 5001
    DEBUG: bool = True

    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIM: int = 1536

    # FAISS Storage
    FAISS_INDEX_DIR: str = os.getenv("FAISS_INDEX_DIR", "./data/faiss_index")
    TOP_K_RETRIEVAL: int = 4
    SIMILARITY_THRESHOLD: float = 0.65

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = AISettings()
