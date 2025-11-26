"""
Quick test of the scraper pipeline
"""
import asyncio
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

from src.pipeline import ArticlePipeline
from src.storage.supabase_storage import SupabaseStorage
from src.utils.image_handler import ImageHandler
from loguru import logger

async def main():
    """Quick test"""
    logger.info("Starting quick test...")

    # Initialize components
    supabase_storage = SupabaseStorage(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    )

    image_handler = ImageHandler(
        output_dir="data/images",
        max_size=2048,
        quality=85
    )

    # Create pipeline
    pipeline = ArticlePipeline(
        image_handler=image_handler,
        supabase_storage=supabase_storage,
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet"),
        rewrite_enabled=False,  # Disable LLM for quick test
        max_articles_per_category=3,  # Only 3 articles per category
        days_to_keep=3
    )

    # Run pipeline
    logger.info("Running pipeline (without LLM, 3 articles per category)...")
    results = await pipeline.run_full_pipeline()

    logger.info(f"Test complete!")
    logger.info(f"Results: {results}")

    # Show stats
    stats = await pipeline.get_supabase_stats()
    logger.info(f"Supabase stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
