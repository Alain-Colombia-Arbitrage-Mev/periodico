#!/usr/bin/env python3
"""
Complete News Scraping Pipeline with Auto-Cleanup
- Deletes news older than 3 days (including images)
- Scrapes fresh news with anti-detection
- Downloads and uploads images to Supabase Storage
- Inserts new articles to database
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import httpx
from io import BytesIO
from PIL import Image
import hashlib
from pathlib import Path

# Configure logging
try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s'
    )
    logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from scrapers.stealth_rss_scraper import StealthRSScraper
except ImportError:
    # Try absolute import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "stealth_rss_scraper",
        Path(__file__).parent / "scrapers" / "stealth_rss_scraper.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    StealthRSScraper = module.StealthRSScraper

# Supabase imports
try:
    from supabase import create_client, Client
except ImportError:
    logger.error("supabase-py not installed. Install with: pip install supabase")
    sys.exit(1)


class NewsScrapingPipeline:
    """Complete pipeline for news scraping with cleanup"""

    def __init__(self):
        # Initialize Supabase
        supabase_url = os.getenv('SUPABASE_URL') or os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.bucket_name = 'noticias'

        # Category mapping
        self.category_ids = {
            'economia': 1,
            'politica': 2,
            'judicial': 3,
            'internacional': 4,
            'sociedad': 5,
        }

        logger.info("✅ Pipeline initialized")

    async def cleanup_old_news(self, days: int = 3):
        """Delete news older than N days including their images"""
        logger.info(f"🗑️  Starting cleanup: Deleting news older than {days} days...")

        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff_date.isoformat()

        try:
            # Get old articles
            response = self.supabase.table('noticias')\
                .select('id, title, image_url')\
                .lt('published_at', cutoff_iso)\
                .execute()

            old_articles = response.data if response.data else []

            if not old_articles:
                logger.info(f"✅ No articles older than {days} days found")
                return 0

            logger.info(f"📋 Found {len(old_articles)} old articles to delete")

            deleted_count = 0
            images_deleted = 0

            for article in old_articles:
                try:
                    # Delete image from storage if it exists
                    if article.get('image_url') and 'supabase.co/storage' in article['image_url']:
                        # Extract file path from URL
                        # Format: https://xxx.supabase.co/storage/v1/object/public/noticias/articles/filename.jpg
                        parts = article['image_url'].split('/storage/v1/object/public/noticias/')
                        if len(parts) > 1:
                            file_path = parts[1]
                            try:
                                self.supabase.storage.from_(self.bucket_name).remove([file_path])
                                images_deleted += 1
                                logger.debug(f"🗑️  Deleted image: {file_path}")
                            except Exception as e:
                                logger.warning(f"⚠️  Could not delete image {file_path}: {e}")

                    # Delete article from database
                    self.supabase.table('noticias').delete().eq('id', article['id']).execute()
                    deleted_count += 1
                    logger.debug(f"✅ Deleted article: {article['title'][:60]}...")

                except Exception as e:
                    logger.error(f"❌ Error deleting article {article['id']}: {e}")

            logger.success(f"✅ Cleanup complete: {deleted_count} articles and {images_deleted} images deleted")
            return deleted_count

        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return 0

    async def scrape_fresh_news(self, max_per_category: int = 10) -> List[Dict]:
        """Scrape fresh news using stealth scraper"""
        logger.info(f"📡 Starting news scraping (max {max_per_category} per category)...")

        scraper = StealthRSScraper(rate_limit=1.5)
        articles = await scraper.scrape_all_sources(max_articles_per_source=max_per_category)

        logger.success(f"✅ Scraped {len(articles)} fresh articles")
        return articles

    def create_slug(self, title: str) -> str:
        """Create URL-friendly slug from title"""
        # Remove accents and special characters
        import unicodedata
        title = unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore').decode('utf-8')

        # Convert to lowercase and replace spaces with hyphens
        slug = title.lower()
        slug = ''.join(c if c.isalnum() or c in ' -' else '' for c in slug)
        slug = '-'.join(slug.split())

        # Limit length
        slug = slug[:100]

        return slug

    async def download_and_upload_image(self, image_url: str, slug: str) -> Optional[str]:
        """Download image from URL and upload to Supabase Storage"""
        try:
            # Download image
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()

                # Validate it's an image
                content_type = response.headers.get('content-type', '').lower()
                if 'image' not in content_type:
                    logger.warning(f"⚠️  Not an image: {content_type}")
                    return None

                # Open and validate with PIL
                img = Image.open(BytesIO(response.content))
                width, height = img.size

                # Validate dimensions
                if width < 300 or height < 150:
                    logger.warning(f"⚠️  Image too small: {width}x{height}")
                    return None

                # Determine format
                format_ext = img.format.lower() if img.format else 'jpg'
                if format_ext == 'jpeg':
                    format_ext = 'jpg'

                # Optimize image if needed
                if width > 1920 or height > 1080:
                    # Resize maintaining aspect ratio
                    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                    logger.debug(f"📐 Resized image to {img.size}")

                # Convert to bytes
                output = BytesIO()
                if format_ext in ['jpg', 'jpeg']:
                    img.save(output, format='JPEG', quality=85, optimize=True)
                elif format_ext == 'png':
                    img.save(output, format='PNG', optimize=True)
                else:
                    img.save(output, format=img.format)

                image_bytes = output.getvalue()

                # Generate unique filename
                file_hash = hashlib.md5(image_bytes).hexdigest()[:8]
                filename = f"articles/{slug}-{file_hash}.{format_ext}"

                # Upload to Supabase Storage
                self.supabase.storage.from_(self.bucket_name).upload(
                    filename,
                    image_bytes,
                    file_options={
                        "content-type": f"image/{format_ext}",
                        "upsert": "true"
                    }
                )

                # Get public URL
                public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(filename)

                logger.debug(f"✅ Uploaded image: {filename}")
                return public_url

        except Exception as e:
            logger.warning(f"⚠️  Error uploading image for {slug}: {e}")
            return None

    async def insert_articles(self, articles: List[Dict]) -> int:
        """Insert articles to database with images"""
        logger.info(f"💾 Inserting {len(articles)} articles to database...")

        inserted = 0
        skipped = 0

        for article in articles:
            try:
                # Get category ID
                category_id = self.category_ids.get(article['category'])
                if not category_id:
                    logger.warning(f"⚠️  Unknown category: {article['category']}")
                    skipped += 1
                    continue

                # Create slug
                slug = self.create_slug(article['title'])

                # Check if article already exists
                existing = self.supabase.table('noticias')\
                    .select('id')\
                    .eq('slug', slug)\
                    .execute()

                if existing.data:
                    logger.debug(f"⏭️  Article already exists: {article['title'][:50]}...")
                    skipped += 1
                    continue

                # Download and upload image
                supabase_image_url = None
                if article.get('image_url'):
                    supabase_image_url = await self.download_and_upload_image(
                        article['image_url'],
                        slug
                    )

                # Prepare article data
                article_data = {
                    'title': article['title'][:255],
                    'slug': slug,
                    'excerpt': article.get('excerpt', '')[:500],
                    'content': article.get('content', article.get('excerpt', ''))[:5000],
                    'image_url': supabase_image_url or article.get('image_url', ''),
                    'source_url': article.get('url', ''),
                    'source': article.get('source', 'Web'),
                    'source_type': article.get('source_type', 0),
                    'category_id': category_id,
                    'status': 'published',
                    'published_at': article.get('published_at', datetime.now().isoformat()),
                    'is_breaking': False,
                    'views': 0,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                }

                # Insert to database
                self.supabase.table('noticias').insert(article_data).execute()
                inserted += 1
                logger.debug(f"✅ Inserted: {article['title'][:60]}...")

            except Exception as e:
                logger.error(f"❌ Error inserting article: {e}")
                skipped += 1

        logger.success(f"✅ Insert complete: {inserted} inserted, {skipped} skipped")
        return inserted

    async def run(self, cleanup_days: int = 3, max_articles_per_category: int = 10):
        """Run complete pipeline"""
        logger.info("=" * 80)
        logger.info("🚀 STARTING COMPLETE NEWS SCRAPING PIPELINE")
        logger.info("=" * 80)

        start_time = datetime.now()

        # Step 1: Cleanup old news
        logger.info("\n📋 STEP 1: Cleanup old news")
        deleted = await self.cleanup_old_news(days=cleanup_days)

        # Step 2: Scrape fresh news
        logger.info("\n📋 STEP 2: Scrape fresh news")
        articles = await self.scrape_fresh_news(max_per_category=max_articles_per_category)

        # Step 3: Insert new articles
        logger.info("\n📋 STEP 3: Insert new articles")
        inserted = await self.insert_articles(articles)

        # Summary
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("\n" + "=" * 80)
        logger.success("✅ PIPELINE COMPLETE")
        logger.info("=" * 80)
        logger.info(f"📊 Statistics:")
        logger.info(f"   - Deleted: {deleted} old articles")
        logger.info(f"   - Scraped: {len(articles)} fresh articles")
        logger.info(f"   - Inserted: {inserted} new articles")
        logger.info(f"   - Time: {elapsed:.1f} seconds")
        logger.info("=" * 80)

        return {
            'deleted': deleted,
            'scraped': len(articles),
            'inserted': inserted,
            'elapsed': elapsed
        }


async def main():
    """Main entry point"""
    # Configure logger
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

    # Create pipeline
    pipeline = NewsScrapingPipeline()

    # Run pipeline
    try:
        results = await pipeline.run(
            cleanup_days=3,
            max_articles_per_category=10
        )

        logger.success(f"✅ Pipeline executed successfully")
        return 0

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
