"""Configuration for Enrichment Agent."""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # Enrichment Agent settings
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    FIRECRAWL_API_URL: str = "https://api.firecrawl.dev/v1"
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    
    PROMPTS_DIR: Path = Path("prompts")
    SCHEMAS_DIR: Path = Path("schemas")
    OUTPUT_DIR: Path = Path("output")
    
    REQUEST_TIMEOUT: int = 60
    MAX_RETRIES: int = 3
    
    # Email Notifier settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    CLOSEIO_API_KEY: str = os.getenv("CLOSEIO_API_KEY", "")
    CLOSEIO_API_URL: str = "https://api.close.com/api/v1"
    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")
    POLLING_ENABLED: bool = os.getenv("POLLING_ENABLED", "true").lower() == "true"
    POLLING_INTERVAL_SECONDS: int = int(os.getenv("POLLING_INTERVAL_SECONDS", "300"))
    CACHE_RETENTION_HOURS: int = int(os.getenv("CACHE_RETENTION_HOURS", "24"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/email_opens.db")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields from environment


settings = Settings()
