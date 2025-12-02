"""
Complete pipeline: Scrape -> Rewrite with LLM -> Sync to Supabase
"""
import asyncio
from typing import List, Dict
from datetime import datetime
from pathlib import Path
from loguru import logger

from .models.article import Article, ScrapingResult
from .scrapers import NewsScraper
from .services.llm_rewriter import LLMRewriter
from .storage.supabase_storage import SupabaseStorage
from .utils.image_handler import ImageHandler
from .utils.purge_old_news import NewsPurger


class ArticlePipeline:
    """Complete pipeline for article processing"""

    def __init__(
        self,
        # Scraper settings
        image_handler: ImageHandler,
        supabase_storage: SupabaseStorage,

        # LLM settings
        openrouter_api_key: str,

        # LLM model (with default)
        llm_model: str = "deepseek/deepseek-v3.2-exp",  # Mejor relación calidad/precio

        # Pipeline settings
        rewrite_enabled: bool = True,
        max_articles_per_category: int = 20,
        days_to_keep: int = 3
    ):
        self.image_handler = image_handler
        self.storage = supabase_storage
        self.max_articles_per_category = max_articles_per_category

        # Initialize services
        self.llm_rewriter = LLMRewriter(
            api_key=openrouter_api_key,
            model=llm_model
        ) if rewrite_enabled else None

        self.purger = NewsPurger(
            supabase_storage=supabase_storage,
            days_to_keep=days_to_keep
        )

        self.rewrite_enabled = rewrite_enabled

        # Categories to scrape
        self.categories = ["economia", "politica", "sociedad", "internacional"]

        logger.info("Article Pipeline initialized")
        logger.info(f"  - LLM Rewriting: {'Enabled' if rewrite_enabled else 'Disabled'}")
        logger.info(f"  - Storage: Supabase only")

    async def process_source(
        self,
        scraper_class,
        source_name: str,
        base_url: str = None
    ) -> Dict:
        """
        Process articles from a single source through complete pipeline

        Args:
            scraper_class: Scraper class to use
            source_name: Name of the source
            base_url: Base URL for the scraper (optional)

        Returns:
            Dictionary with processing statistics
        """
        stats = {
            "source": source_name,
            "scraped": 0,
            "rewritten": 0,
            "synced": 0,
            "errors": []
        }

        try:
            logger.info(f"=" * 60)
            logger.info(f"Processing {source_name}")
            logger.info(f"=" * 60)

            # Step 1: Scrape articles
            logger.info(f"Step 1/3: Scraping articles from {source_name}...")
            articles = await self._scrape_articles(scraper_class, source_name, base_url)
            stats["scraped"] = len(articles)

            if not articles:
                logger.warning(f"No articles scraped from {source_name}")
                return stats

            logger.success(f"✅ Scraped {len(articles)} articles from {source_name}")
            logger.info(f"Proceeding to Step 2/3: LLM Rewriting...")

            # Step 2: Rewrite with LLM (if enabled)
            rewritten_articles = articles
            if self.rewrite_enabled and self.llm_rewriter:
                logger.info(f"Step 2/3: Rewriting articles with LLM...")

                # Estimate cost first
                cost_estimate = self.llm_rewriter.estimate_cost(articles)
                logger.info(f"Estimated cost: ${cost_estimate['estimated_total_cost_usd']:.4f}")

                # Rewrite
                rewritten_articles = await self.llm_rewriter.rewrite_multiple(
                    articles,
                    max_concurrent=2  # Be gentle with API
                )
                stats["rewritten"] = len(rewritten_articles)

                if rewritten_articles:
                    logger.success(f"Rewrote {len(rewritten_articles)} articles")
                else:
                    logger.warning("No articles were successfully rewritten")
                    rewritten_articles = articles  # Fallback to original
            else:
                logger.info("Step 2/3: LLM rewriting disabled, skipping...")

            # Step 3: Save to Supabase (rewritten articles only - no duplicates)
            logger.info(f"Step 3/3: Saving rewritten articles to Supabase...")
            await self._save_to_supabase(rewritten_articles, is_rewritten=self.rewrite_enabled)

            # Complete
            logger.info(f"Pipeline complete for {source_name}")
            stats["synced"] = len(rewritten_articles)

            logger.info(f"Completed processing {source_name}")
            return stats

        except Exception as e:
            error_msg = f"Error processing {source_name}: {e}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)
            return stats

    async def _scrape_articles(
        self,
        scraper_class,
        source_name: str,
        base_url: str = None
    ) -> List[Article]:
        """Scrape articles from source"""
        all_articles = []

        # Create scraper with base_url if provided
        scraper_kwargs = {"image_handler": self.image_handler}
        if base_url:
            scraper_kwargs["base_url"] = base_url

        async with scraper_class(**scraper_kwargs) as scraper:
            for category in self.categories:
                try:
                    articles = await scraper.scrape_category(
                        category,
                        max_articles=self.max_articles_per_category
                    )
                    all_articles.extend(articles)

                    logger.info(
                        f"  {source_name}/{category}: {len(articles)} articles"
                    )

                except Exception as e:
                    logger.error(f"Error scraping {source_name}/{category}: {e}")

        return all_articles

    async def _save_to_supabase(
        self,
        articles: List[Article],
        is_rewritten: bool = False
    ):
        """Save articles to Supabase with image upload"""
        saved = 0

        for article in articles:
            try:
                article_dict = article.to_dict()

                # Procesar imagen para Supabase Storage
                image_url_to_use = None

                # Si tiene imagen ya subida a Supabase (URL completa), usarla directamente
                if hasattr(article, 'local_image_path') and article.local_image_path:
                    if article.local_image_path.startswith('https://'):
                        # Ya es una URL de Supabase Storage, usarla directamente
                        image_url_to_use = article.local_image_path
                        article_dict["image_url"] = image_url_to_use
                        logger.debug(f"✅ Using Supabase Storage URL: {article.title[:50]}...")
                    else:
                        # Es una ruta local relativa, intentar subir
                        try:
                            local_path = Path(article.local_image_path)
                            if not local_path.is_absolute():
                                local_path = Path("data/images") / article.local_image_path

                            if local_path.exists():
                                category_slug = article_dict.get("category_slug", "politica")
                                remote_path = f"{category_slug}/{local_path.name}"

                                image_url_to_use = await self.storage.upload_image(str(local_path), remote_path)
                                if image_url_to_use:
                                    article_dict["image_url"] = image_url_to_use
                                    logger.info(f"✅ Image uploaded to Supabase: {article.title[:50]}...")
                                else:
                                    logger.warning(f"⚠️  Failed to upload image, using placeholder")
                                    article_dict["image_url"] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="400"%3E%3Crect width="800" height="400" fill="%23e5e7eb"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" fill="%239ca3af"%3ESin imagen%3C/text%3E%3C/svg%3E'
                            else:
                                logger.warning(f"⚠️  Image file not found: {local_path}, using placeholder")
                                article_dict["image_url"] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="400"%3E%3Crect width="800" height="400" fill="%23e5e7eb"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" fill="%239ca3af"%3ESin imagen%3C/text%3E%3C/svg%3E'
                        except Exception as e:
                            logger.warning(f"Failed to upload image for {article.title[:50]}: {e}")
                            article_dict["image_url"] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="400"%3E%3Crect width="800" height="400" fill="%23e5e7eb"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" fill="%239ca3af"%3ESin imagen%3C/text%3E%3C/svg%3E'
                elif article_dict.get("image_url"):
                    # Si tiene URL externa pero no imagen local, usar URL externa como fallback
                    logger.warning(f"⚠️  Using external image URL (no local image): {article.title[:50]}...")
                    article_dict["image_url"] = article_dict.get("image_url", 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="400"%3E%3Crect width="800" height="400" fill="%23e5e7eb"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" fill="%239ca3af"%3ESin imagen%3C/text%3E%3C/svg%3E')
                else:
                    # Sin imagen - usar placeholder (schema requiere NOT NULL)
                    logger.warning(f"⚠️  Article without image, using placeholder: {article.title[:50]}...")
                    article_dict["image_url"] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="400"%3E%3Crect width="800" height="400" fill="%23e5e7eb"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" fill="%239ca3af"%3ESin imagen%3C/text%3E%3C/svg%3E'

                # Verificar si existe por source_url antes de guardar (NO por slug, porque el LLM genera títulos diferentes)
                source_url = article_dict.get("source_url", "")

                # Verificar por source_url para evitar duplicados (el source_url no cambia aunque el título cambie)
                if source_url and await self.storage.article_exists_by_source_url(source_url):
                    logger.debug(f"Article already exists (by source_url): {article_dict['title'][:50]}...")
                    continue
                
                # Guardar si no existe
                if await self.storage.save_article(article_dict):
                    saved += 1
                    logger.info(f"✅ New article saved: {article_dict['title'][:50]}...")

            except Exception as e:
                logger.error(f"Error saving article to Supabase: {e}")

        logger.info(f"Saved {saved}/{len(articles)} articles to Supabase")

    async def run_full_pipeline(self) -> Dict:
        """
        Run complete pipeline for all sources

        Returns:
            Dictionary with overall statistics
        """
        start_time = datetime.now()

        logger.info("╔" + "=" * 58 + "╗")
        logger.info("║" + " " * 15 + "STARTING FULL PIPELINE" + " " * 21 + "║")
        logger.info("╚" + "=" * 58 + "╝")

        # Multiple sources for comprehensive scraping
        # SOLO Clarín y La Nación - Infobae removido por problemas con logos
        sources = [
            (NewsScraper, "La Nación", "https://www.lanacion.com.ar"),
            (NewsScraper, "Clarín", "https://www.clarin.com"),
        ]

        overall_stats = {
            "sources": [],
            "total_scraped": 0,
            "total_rewritten": 0,
            "total_synced": 0,
            "duration_seconds": 0
        }

        # Process sources in parallel for faster execution
        source_tasks = [
            self.process_source(scraper_class, source_name, base_url)
            for scraper_class, source_name, base_url in sources
        ]

        # Wait for all sources to complete
        source_results = await asyncio.gather(*source_tasks, return_exceptions=True)

        # Process results
        for result in source_results:
            if isinstance(result, Exception):
                logger.error(f"Source processing failed: {result}")
                stats = {"source": "unknown", "scraped": 0, "rewritten": 0, "synced": 0, "errors": [str(result)]}
            else:
                stats = result

            overall_stats["sources"].append(stats)
            overall_stats["total_scraped"] += stats["scraped"]
            overall_stats["total_rewritten"] += stats["rewritten"]
            overall_stats["total_synced"] += stats["synced"]

        # Purge old news (keep only last 3 days)
        logger.info("=" * 60)
        logger.info("Purging old news...")
        purge_stats = await self.purger.purge_old_news()
        overall_stats["purged"] = purge_stats.get("deleted", 0)
        logger.info("=" * 60)

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        overall_stats["duration_seconds"] = duration

        # Log summary
        logger.info("")
        logger.info("╔" + "=" * 58 + "╗")
        logger.info("║" + " " * 18 + "PIPELINE COMPLETE" + " " * 23 + "║")
        logger.info("╠" + "=" * 58 + "╣")
        logger.info(f"║  Total Scraped:    {overall_stats['total_scraped']:>4} articles" + " " * 24 + "║")
        logger.info(f"║  Total Rewritten:  {overall_stats['total_rewritten']:>4} articles" + " " * 24 + "║")
        logger.info(f"║  Total Synced:     {overall_stats['total_synced']:>4} articles" + " " * 24 + "║")
        logger.info(f"║  Duration:         {duration:>6.1f} seconds" + " " * 23 + "║")
        logger.info("╚" + "=" * 58 + "╝")

        # Stats are logged, no need for cache

        return overall_stats

    async def get_supabase_stats(self) -> Dict:
        """Get statistics from Supabase"""
        return await self.storage.get_stats()

    async def cleanup_old_content(self, days: int = 90):
        """Cleanup old content from Supabase"""
        logger.info(f"Cleaning up content older than {days} days...")

        # Cleanup Supabase
        await self.storage.cleanup_old_articles(days)
        logger.info("Cleaned up old articles from Supabase")

        # Cleanup old images
        images_deleted = self.image_handler.cleanup_old_images(days)
        logger.info(f"Deleted {images_deleted} old images")
