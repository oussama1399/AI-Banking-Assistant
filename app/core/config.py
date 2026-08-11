"""
Application configuration settings
"""

from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "AI Banking Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Database settings
    DATABASE_URL: str = "sqlite:///./banking_assistant.db"

    # RAG settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_DB_PATH: str = "./chroma_db"

    class Config:
        case_sensitive = True

settings = Settings()