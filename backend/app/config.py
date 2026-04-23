from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "FRACTO Voice Agent Platform"
    environment: str = "development"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8
    database_url: str = "postgresql://fracto:fracto@localhost:5432/fracto"
    redis_url: str = "redis://localhost:6379/0"
    gemini_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    vapi_api_key: Optional[str] = None
    vapi_phone_number_id: Optional[str] = None
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    scraping_delay_seconds: float = 2.0
    max_scraping_results: int = 50

    class Config:
        env_file = ".env"

settings = Settings()
