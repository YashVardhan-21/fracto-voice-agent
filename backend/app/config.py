from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "FRACTO Voice Agent Platform"
    environment: str = "development"
    secret_key: str  # No default — app fails to start if not set in .env
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8
    database_url: str = "postgresql://fracto:fracto@localhost:5432/fracto"
    redis_url: str = "redis://localhost:6379/0"
    gemini_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    vapi_api_key: Optional[str] = None
    vapi_voice_id: Optional[str] = None
    vapi_phone_number_id: Optional[str] = None
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    scraping_delay_seconds: float = 2.0
    max_scraping_results: int = 50
    allow_mock_scraping_fallback: bool = False
    google_places_api_key: Optional[str] = None
    adzuna_app_id: Optional[str] = None
    adzuna_app_key: Optional[str] = None
    adzuna_country: str = "gb"
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    stripe_starter_price_id: Optional[str] = None
    stripe_pro_price_id: Optional[str] = None
    frontend_url: str = "http://localhost:5173"

settings = Settings()
