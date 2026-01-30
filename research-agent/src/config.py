"""Configuration for Research Agent."""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings for Research Agent."""
    
    # Firecrawl API
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY", "")
    FIRECRAWL_API_URL: str = "https://api.firecrawl.dev/v1"
    
    # Anthropic API for LLM extraction
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    
    # Bright Data LinkedIn API (optional)
    BRIGHTDATA_API_KEY: str = os.getenv("BRIGHTDATA_API_KEY", "")
    BRIGHTDATA_API_URL: str = "https://api.brightdata.com/datasets/v3"
    
    # Google Sheets (optional)
    GOOGLE_CREDENTIALS_PATH: Path = Path(os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"))
    
    # Directory settings
    PROMPTS_DIR: Path = Path("prompts")
    SCHEMAS_DIR: Path = Path("schemas")
    OUTPUT_DIR: Path = Path("output")
    
    # Request settings
    REQUEST_TIMEOUT: int = 60
    MAX_RETRIES: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
