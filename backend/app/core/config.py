from pydantic_settings import BaseSettings
from typing import List
import os


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
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # ML Models
    MODEL_PATH: str = "./models"
    CLASSIFICATION_MODEL: str = "distilbert-base-uncased"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    SENTIMENT_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
    
    # ChromaDB
    CHROMA_DB_PATH: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "support_tickets"
    
    # MLflow
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_EXPERIMENT_NAME: str = "autosupport"
    
    # Celery
    CELERY_BROKER_URL: str = "amqp://guest:guest@localhost:5672//"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # Application
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    MAX_WORKERS: int = 4
    
    # Email (for notifications)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@autosupport.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
