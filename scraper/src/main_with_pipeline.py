"""
Main scraper with complete pipeline (Scrape -> LLM Rewrite -> Supabase Sync)
"""
import asyncio
import os
from pydantic_settings import BaseSettings
from loguru import logger

from .pipeline import ArticlePipeline
from .storage.supabase_storage import SupabaseStorage
from .utils.logger import setup_logger
from .utils.image_handler import ImageHandler


class Settings(BaseSettings):
    """Application settings"""

    # Supabase (único storage)
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""  # Service role key for Storage uploads

    # Scraper
    scrape_interval: int = 43200  # 12 hours (default)
    max_articles_per_category: int = 20  # More articles for production

    # Cleanup
    delete_old_articles: bool = True  # Delete old scraped articles
    old_articles_days: int = 3  # Days to keep scraped articles
    page_timeout: int = 30000  # Page timeout in milliseconds

    # Images
    download_images: bool = True
    image_quality: int = 85
    max_image_size: int = 2048

    # LLM (OpenRouter) - Opcional
    openrouter_api_key: str = ""
    llm_model: str = "deepseek/deepseek-v3.2-exp"  # Mejor relación calidad/precio
    llm_rewrite_enabled: bool = True  # Habilitado por defecto para reescribir noticias

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignorar campos extra del .env


async def main():
    """Main entry point with pipeline"""

    # Load settings
    settings = Settings()

    # Setup logging
    setup_logger(
        log_level=settings.log_level,
        log_file="logs/pipeline.log"
    )

    logger.info("Starting Article Pipeline System")

    # Validate required settings
    if not settings.supabase_url or not settings.supabase_key:
        logger.error("Supabase URL and Key are REQUIRED!")
        logger.info("Set SUPABASE_URL and SUPABASE_KEY in .env")
        return

    if settings.llm_rewrite_enabled and not settings.openrouter_api_key:
        logger.error("OpenRouter API key is required when LLM rewriting is enabled!")
        logger.info("Set OPENROUTER_API_KEY in .env or disable with LLM_REWRITE_ENABLED=false")
        return

    # Initialize components
    # Use SERVICE_ROLE_KEY for storage uploads if available, otherwise use regular key
    storage_key = settings.supabase_service_key if settings.supabase_service_key else settings.supabase_key

    supabase_storage = SupabaseStorage(
        supabase_url=settings.supabase_url,
        supabase_key=storage_key
    )
    
    image_handler = ImageHandler(
        output_dir="data/images",
        max_size=settings.max_image_size,
        quality=settings.image_quality,
        supabase_url=settings.supabase_url,
        supabase_key=storage_key,
        storage_bucket="noticias"
    )

    # Create pipeline
    pipeline = ArticlePipeline(
        image_handler=image_handler,
        supabase_storage=supabase_storage,
        openrouter_api_key=settings.openrouter_api_key,
        llm_model=settings.llm_model,
        rewrite_enabled=settings.llm_rewrite_enabled,
        max_articles_per_category=settings.max_articles_per_category
    )

    # Check run mode
    run_mode = os.getenv("RUN_MODE", "continuous")

    if run_mode == "once":
        logger.info("Running pipeline once")
        await pipeline.run_full_pipeline()

        # Show Supabase stats
        stats = await pipeline.get_supabase_stats()
        logger.info(f"Supabase stats: {stats}")

    else:
        logger.info(f"Running pipeline continuously (interval: {settings.scrape_interval}s)")

        while True:
            try:
                # Delete old scraped articles if enabled
                if settings.delete_old_articles:
                    logger.info(f"Deleting scraped articles from last {settings.old_articles_days} days...")
                    deleted = await supabase_storage.delete_recent_scraped_articles(days=settings.old_articles_days)
                    if deleted > 0:
                        logger.info(f"Deleted {deleted} old scraped articles")

                # Run pipeline
                await pipeline.run_full_pipeline()

                # Show stats
                stats = await pipeline.get_supabase_stats()
                logger.info(f"Supabase total articles: {stats.get('total_articles', 0)}")

                # Wait for next run
                logger.info(f"Waiting {settings.scrape_interval}s until next run...")
                await asyncio.sleep(settings.scrape_interval)

            except KeyboardInterrupt:
                logger.info("Shutting down pipeline...")
                break
            except Exception as e:
                logger.error(f"Error in pipeline: {e}")
                logger.info("Waiting 60s before retry...")
                await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
