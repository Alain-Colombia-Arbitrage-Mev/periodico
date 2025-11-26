"""
Main scraper orchestrator
"""
import asyncio
import os
import time
from datetime import datetime
from typing import List
from pydantic_settings import BaseSettings
from loguru import logger

from models.article import Article, ScrapingResult
from scrapers.news_scraper import NewsScraper
from storage.database import Database
from storage.cache import Cache
from utils.logger import setup_logger
from utils.image_handler import ImageHandler


class Settings(BaseSettings):
    """Application settings"""

    # Database
    database_url: str = "postgresql://scraper:scraper_password_2024@localhost:5432/scraper_db"

    # Redis
    redis_url: str = "redis://:redis_password_2024@localhost:6379/0"

    # Scraper
    scrape_interval: int = 3600  # 1 hour
    max_articles_per_category: int = 20
    max_concurrent_requests: int = 5

    # Images
    download_images: bool = True
    image_quality: int = 85
    max_image_size: int = 2048

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


class ScraperOrchestrator:
    """Main scraper orchestrator"""

    def __init__(self, settings: Settings):
        self.settings = settings

        # Setup logging
        setup_logger(
            log_level=settings.log_level,
            log_file="logs/scraper.log"
        )

        # Initialize components
        self.db = Database(settings.database_url)
        self.cache = Cache(settings.redis_url)
        self.image_handler = ImageHandler(
            output_dir="data/images",
            max_size=settings.max_image_size,
            quality=settings.image_quality
        )

        # Categories to scrape
        self.categories = ["economia", "politica", "sociedad", "internacional"]

        logger.info("Scraper orchestrator initialized")

    async def scrape_source(
        self,
        scraper_class,
        source_name: str
    ) -> ScrapingResult:
        """
        Scrape a single news source

        Args:
            scraper_class: Scraper class to use
            source_name: Name of the source

        Returns:
            ScrapingResult
        """
        start_time = time.time()
        errors = []
        articles_found = 0
        articles_saved = 0

        try:
            logger.info(f"Starting scrape of {source_name}")

            async with scraper_class(self.image_handler) as scraper:
                all_articles: List[Article] = []

                # Scrape each category
                for category in self.categories:
                    try:
                        logger.info(f"Scraping {source_name} - {category}")

                        articles = await scraper.scrape_category(
                            category,
                            max_articles=self.settings.max_articles_per_category
                        )

                        all_articles.extend(articles)
                        articles_found += len(articles)

                        logger.info(
                            f"Found {len(articles)} articles in {source_name}/{category}"
                        )

                    except Exception as e:
                        error_msg = f"Error scraping {source_name}/{category}: {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)

                # Save to database
                if all_articles:
                    logger.info(f"Saving {len(all_articles)} articles from {source_name}")

                    for article in all_articles:
                        try:
                            # Check if already exists
                            if not self.db.article_exists(str(article.source_url)):
                                if self.db.save_article(article.to_dict()):
                                    articles_saved += 1

                                    # Cache article
                                    cache_key = f"article:{article.id}"
                                    self.cache.set(cache_key, article.to_dict(), ttl=7200)

                        except Exception as e:
                            error_msg = f"Error saving article: {e}"
                            logger.error(error_msg)
                            errors.append(error_msg)

            duration = time.time() - start_time

            result = ScrapingResult(
                source=source_name,
                success=len(errors) == 0,
                articles_found=articles_found,
                articles_saved=articles_saved,
                errors=errors,
                duration_seconds=duration
            )

            logger.info(
                f"Completed {source_name}: "
                f"Found={articles_found}, Saved={articles_saved}, "
                f"Duration={duration:.2f}s"
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Critical error scraping {source_name}: {e}"
            logger.error(error_msg)

            return ScrapingResult(
                source=source_name,
                success=False,
                articles_found=articles_found,
                articles_saved=articles_saved,
                errors=[error_msg],
                duration_seconds=duration
            )

    async def scrape_all_sources(self) -> List[ScrapingResult]:
        """Scrape all news sources"""
        logger.info("=" * 60)
        logger.info("Starting scraping run")
        logger.info("=" * 60)

        sources = [
            (NewsScraper, "Scraper Automático"),
        ]

        results = []

        for scraper_class, source_name in sources:
            result = await self.scrape_source(scraper_class, source_name)
            results.append(result)

            # Update stats in cache
            stats_key = f"stats:{source_name}:{datetime.now().strftime('%Y-%m-%d')}"
            self.cache.set(stats_key, result.model_dump(), ttl=86400)  # 24 hours

        # Log summary
        total_found = sum(r.articles_found for r in results)
        total_saved = sum(r.articles_saved for r in results)
        total_duration = sum(r.duration_seconds for r in results)

        logger.info("=" * 60)
        logger.info("Scraping run completed")
        logger.info(f"Total articles found: {total_found}")
        logger.info(f"Total articles saved: {total_saved}")
        logger.info(f"Total duration: {total_duration:.2f}s")
        logger.info("=" * 60)

        # Get database stats
        db_stats = self.db.get_stats()
        logger.info(f"Database stats: {db_stats}")

        return results

    async def run_continuous(self):
        """Run scraper continuously"""
        logger.info(
            f"Starting continuous scraping with interval: "
            f"{self.settings.scrape_interval}s"
        )

        while True:
            try:
                await self.scrape_all_sources()

                # Wait for next run
                logger.info(
                    f"Waiting {self.settings.scrape_interval}s until next run..."
                )
                await asyncio.sleep(self.settings.scrape_interval)

            except KeyboardInterrupt:
                logger.info("Shutting down scraper...")
                break
            except Exception as e:
                logger.error(f"Error in continuous run: {e}")
                logger.info("Waiting 60s before retry...")
                await asyncio.sleep(60)

    async def run_once(self):
        """Run scraper once and exit"""
        await self.scrape_all_sources()


async def main():
    """Main entry point"""
    # Load settings
    settings = Settings()

    # Create orchestrator
    orchestrator = ScraperOrchestrator(settings)

    # Check if running once or continuously
    run_mode = os.getenv("RUN_MODE", "continuous")

    if run_mode == "once":
        logger.info("Running scraper once")
        await orchestrator.run_once()
    else:
        logger.info("Running scraper continuously")
        await orchestrator.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())
