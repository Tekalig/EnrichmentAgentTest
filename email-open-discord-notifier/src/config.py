"""Configuration for Email Open Discord Notifier."""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings for Email Open Discord Notifier."""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Close.io API
    CLOSEIO_API_KEY: str = os.getenv("CLOSEIO_API_KEY", "")
    CLOSEIO_API_URL: str = "https://api.close.com/api/v1"
    
    # Discord webhook
    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")
    
    # Polling settings (fallback if webhooks not available)
    POLLING_ENABLED: bool = os.getenv("POLLING_ENABLED", "true").lower() == "true"
    POLLING_INTERVAL_SECONDS: int = int(os.getenv("POLLING_INTERVAL_SECONDS", "300"))  # 5 minutes
    
    # Cache settings
    CACHE_RETENTION_HOURS: int = int(os.getenv("CACHE_RETENTION_HOURS", "24"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/email_opens.db")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
