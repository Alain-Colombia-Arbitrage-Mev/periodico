"""
Scrapers package
"""
from .base_scraper import BaseScraper
from .news_scraper import NewsScraper

__all__ = [
    'BaseScraper',
    'NewsScraper',
]
