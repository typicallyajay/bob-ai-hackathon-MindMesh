from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./threatmesh.db"
    SECRET_KEY: str = "dev-secret-key-change-me"
    CORS_ORIGINS: str = "http://localhost:3000"
    
    WATSONX_URL: Optional[str] = None
    WATSONX_API_KEY: Optional[str] = None
    WATSONX_PROJECT_ID: Optional[str] = None
    WATSONX_MODEL_ID: Optional[str] = None
    
    BOB_API_URL: Optional[str] = None
    BOB_API_KEY: Optional[str] = None
    
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
