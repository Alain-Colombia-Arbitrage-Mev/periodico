"""
RSS-based pipeline: Scrape RSS feeds -> Rewrite with LLM -> Sync to Supabase
No browser required - works on Railway without Playwright
"""
import asyncio
from typing import List, Dict
from datetime import datetime
from loguru import logger

from .models.article import Article
from .scrapers.stealth_rss_scraper import StealthRSScraper
from .services.llm_rewriter import LLMRewriter
from .storage.supabase_storage import SupabaseStorage
from .utils.image_handler import ImageHandler
from .utils.purge_old_news import NewsPurger


class RSSArticlePipeline:
    """RSS-based pipeline for article processing (no browser required)"""

    def __init__(
        self,
        image_handler: ImageHandler,
        supabase_storage: SupabaseStorage,
        openrouter_api_key: str,
        llm_model: str = "openrouter/sherlock-think-alpha",
        rewrite_enabled: bool = True,
        max_articles_per_category: int = 20,
        days_to_keep: int = 3
    ):
        self.image_handler = image_handler
        self.storage = supabase_storage
        self.max_articles_per_category = max_articles_per_category

        # Initialize RSS scraper (no browser needed)
        self.rss_scraper = StealthRSScraper(rate_limit=1.5)

        # Initialize LLM rewriter
        self.llm_rewriter = LLMRewriter(
            api_key=openrouter_api_key,
            model=llm_model
        ) if rewrite_enabled else None

        self.purger = NewsPurger(
            supabase_storage=supabase_storage,
            days_to_keep=days_to_keep
        )

        self.rewrite_enabled = rewrite_enabled

        logger.info("RSS Article Pipeline initialized (no browser required)")
        logger.info(f"  - LLM Rewriting: {'Enabled' if rewrite_enabled else 'Disabled'}")
        logger.info(f"  - Storage: Supabase")

    async def run_full_pipeline(self) -> Dict:
        """Run complete RSS pipeline"""
        start_time = datetime.now()

        logger.info("╔" + "=" * 58 + "╗")
        logger.info("║" + " " * 12 + "STARTING RSS PIPELINE" + " " * 25 + "║")
        logger.info("╚" + "=" * 58 + "╝")

        overall_stats = {
            "sources": [],
            "total_scraped": 0,
            "total_rewritten": 0,
            "total_synced": 0,
            "duration_seconds": 0
        }

        try:
            # Step 1: Scrape RSS feeds
            logger.info("Step 1/3: Scraping RSS feeds...")
            raw_articles = await self.rss_scraper.scrape_all_sources(
                max_articles_per_source=self.max_articles_per_category
            )
            overall_stats["total_scraped"] = len(raw_articles)
            logger.success(f"✅ Scraped {len(raw_articles)} articles from RSS feeds")

            if not raw_articles:
                logger.warning("No articles scraped from RSS feeds")
                return overall_stats

            # Convert to Article objects
            articles = self._convert_to_articles(raw_articles)

            # Step 2: Rewrite with LLM
            rewritten_articles = articles
            if self.rewrite_enabled and self.llm_rewriter:
                logger.info("Step 2/3: Rewriting articles with LLM...")

                # Estimate cost
                cost_estimate = self.llm_rewriter.estimate_cost(articles)
                logger.info(f"Estimated cost: ${cost_estimate['estimated_total_cost_usd']:.4f}")

                rewritten_articles = await self.llm_rewriter.rewrite_multiple(
                    articles,
                    max_concurrent=2
                )
                overall_stats["total_rewritten"] = len(rewritten_articles)

                if rewritten_articles:
                    logger.success(f"✅ Rewrote {len(rewritten_articles)} articles")
                else:
                    logger.warning("No articles rewritten, using originals")
                    rewritten_articles = articles
            else:
                logger.info("Step 2/3: LLM rewriting disabled, skipping...")

            # Step 3: Save to Supabase
            logger.info("Step 3/3: Saving to Supabase...")
            saved = await self._save_to_supabase(rewritten_articles)
            overall_stats["total_synced"] = saved

            # Purge old news
            logger.info("Purging old news...")
            purge_stats = await self.purger.purge_old_news()
            overall_stats["purged"] = purge_stats.get("deleted", 0)

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            import traceback
            traceback.print_exc()

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        overall_stats["duration_seconds"] = duration

        # Log summary
        logger.info("")
        logger.info("╔" + "=" * 58 + "╗")
        logger.info("║" + " " * 15 + "RSS PIPELINE COMPLETE" + " " * 22 + "║")
        logger.info("╠" + "=" * 58 + "╣")
        logger.info(f"║  Total Scraped:    {overall_stats['total_scraped']:>4} articles" + " " * 24 + "║")
        logger.info(f"║  Total Rewritten:  {overall_stats['total_rewritten']:>4} articles" + " " * 24 + "║")
        logger.info(f"║  Total Synced:     {overall_stats['total_synced']:>4} articles" + " " * 24 + "║")
        logger.info(f"║  Duration:         {duration:>6.1f} seconds" + " " * 23 + "║")
        logger.info("╚" + "=" * 58 + "╝")

        return overall_stats

    def _convert_to_articles(self, raw_articles: List[Dict]) -> List[Article]:
        """Convert raw RSS articles to Article objects"""
        articles = []

        for raw in raw_articles:
            try:
                article = Article(
                    title=raw.get('title', ''),
                    content=raw.get('content', raw.get('excerpt', '')),
                    excerpt=raw.get('excerpt', ''),
                    url=raw.get('url', ''),
                    source_url=raw.get('source_url', raw.get('url', '')),
                    image_url=raw.get('image_url', ''),
                    source=raw.get('source', ''),
                    category_slug=raw.get('category', 'general'),
                    published_at=datetime.fromisoformat(raw.get('published_at', datetime.now().isoformat()).replace('Z', '+00:00')) if raw.get('published_at') else datetime.now(),
                    source_type=raw.get('source_type', 0)
                )
                articles.append(article)
            except Exception as e:
                logger.warning(f"Error converting article: {e}")
                continue

        return articles

    async def _save_to_supabase(self, articles: List[Article]) -> int:
        """Save articles to Supabase"""
        saved = 0

        for article in articles:
            try:
                article_dict = article.to_dict()

                # Use external image URL directly (RSS already provides valid URLs)
                if not article_dict.get("image_url"):
                    article_dict["image_url"] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="400"%3E%3Crect width="800" height="400" fill="%23e5e7eb"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" fill="%239ca3af"%3ESin imagen%3C/text%3E%3C/svg%3E'

                # Check for duplicates by source_url
                source_url = article_dict.get("source_url", "")
                if source_url and await self.storage.article_exists_by_source_url(source_url):
                    logger.debug(f"Article exists: {article_dict['title'][:50]}...")
                    continue

                # Save article
                if await self.storage.save_article(article_dict):
                    saved += 1
                    logger.info(f"✅ Saved: {article_dict['title'][:50]}...")

            except Exception as e:
                logger.error(f"Error saving article: {e}")

        logger.info(f"Saved {saved}/{len(articles)} articles to Supabase")
        return saved

    async def get_supabase_stats(self) -> Dict:
        """Get statistics from Supabase"""
        return await self.storage.get_stats()
