from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key-here"  # For development only! Use env var in production
    APP_NAME: str = "Fake Content Detection API"
    DEBUG: bool = False
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_NAME: str = "fake_content_db"
    REDIS_URL: str = "redis://localhost:6379"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    CORS_ORIGINS: List[str] = ["*"]
    HF_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    MEDIA_STORAGE_PATH: str = "./media_storage"
    MODEL_CACHE_PATH: str = "./model_cache"

    class Config:
        env_file = ".env"


settings = Settings()