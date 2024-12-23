from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import os


load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Orbidi Challenge"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str =  os.getenv("ENVIRONMENT", "development")
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@db:5432/fastapi_db')
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    API_KEY_HEADER: str =  "X-API-KEY"
    REVIEW_EXPIRATION_DAYS: int = 30

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()