"""Research Agent - Automated prospect research tool."""

from .config import settings
from .models import ExtractionSchema, PromptTemplate, EnrichmentResult, WebsiteContent
from .scraper import FirecrawlScraper
from .extractor import LLMExtractor

__all__ = [
    'settings',
    'ExtractionSchema',
    'PromptTemplate',
    'EnrichmentResult',
    'WebsiteContent',
    'FirecrawlScraper',
    'LLMExtractor',
]
