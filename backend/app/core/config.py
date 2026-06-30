from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Project
    PROJECT_NAME: str = "AutoSupport API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/autosupport"

    # CORS — open so Vercel frontend can reach Render backend
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Groq AI
    GROQ_API_KEY: str = ""

    # Application
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
