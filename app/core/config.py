"""
Application configuration settings.
"""

from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="app/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "AI Banking Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["*"]
    LOG_LEVEL: str = "INFO"

    # LLM (Ollama)
    LLM_MODEL: str = "qwen3-coder:30b"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 1024

    # RAG
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_DB_PATH: str = "./chroma_db"
    RAG_K: int = 4


settings = Settings()
