"""Application configuration using Pydantic settings."""
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    environment: str = "development"
    debug: bool = True
    app_name: str = "DocWiz API"
    app_version: str = "0.1.0"

    # Firebase/Firestore Database (Google Cloud)
    firebase_project_id: str = "test-project"
    firebase_credentials_path: str = ""
    # For local development with Firestore emulator
    firestore_emulator_host: str = ""
    use_firestore_emulator: bool = False

    # Redis (for caching and Celery)
    redis_url: str

    # Qdrant Vector Database
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "surgical_embeddings"

    # Google AI Services
    gemini_api_key: str
    nano_banana_api_key: str
    
    # Freepik API
    freepik_api_key: str

    # Google Cloud Storage (for images)
    gcs_bucket_name: str
    gcs_project_id: str
    gcs_credentials_path: str = ""

    # Security
    secret_key: str
    encryption_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Celery (async task processing)
    celery_broker_url: str
    celery_result_backend: str


# Global settings instance
settings = Settings()
