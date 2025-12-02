"""
Supabase synchronization service
"""
import asyncio
from typing import List, Optional, Dict
from datetime import datetime
import httpx
from loguru import logger
from ..models.article import Article


class SupabaseSync:
    """Sync articles with Supabase"""

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        storage_bucket: str = "noticias"
    ):
        self.supabase_url = supabase_url.rstrip('/')
        self.supabase_key = supabase_key
        self.storage_bucket = storage_bucket
        self.timeout = 30

        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }

    async def sync_article(self, article: Article) -> bool:
        """
        Sync single article to Supabase

        Args:
            article: Article to sync

        Returns:
            True if successful
        """
        try:
            # Upload image first if exists
            image_url = None
            if article.local_image_path:
                image_url = await self.upload_image(
                    article.local_image_path,
                    f"{article.category_slug}/{article.slug}.jpg"
                )

            # Prepare article data for Supabase
            article_data = {
                "id": article.id,
                "slug": article.slug,
                "title": article.title,
                "subtitle": article.subtitle,
                "excerpt": article.excerpt,
                "content": article.content,
                "category": article.category,
                "category_slug": article.category_slug,
                "author": article.author,
                "published_at": article.published_at.isoformat(),
                "image_url": image_url or article.image_url,
                "tags": article.tags,
                "is_breaking": article.is_breaking,
                "source": article.source,
                "source_url": str(article.source_url),
                "source_type": 0,  # 0 = scraper automático
                "views": article.views,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # Upsert to Supabase
            success = await self._upsert_article(article_data)

            if success:
                logger.success(f"Synced to Supabase: {article.title[:50]}...")
                return True
            else:
                logger.error(f"Failed to sync: {article.title[:50]}...")
                return False

        except Exception as e:
            logger.error(f"Error syncing article to Supabase: {e}")
            return False

    async def upload_image(
        self,
        local_path: str,
        remote_path: str
    ) -> Optional[str]:
        """
        Upload image to Supabase Storage

        Args:
            local_path: Local image path (relative to data/images/)
            remote_path: Remote path in bucket

        Returns:
            Public URL of uploaded image or None
        """
        try:
            import aiofiles
            from pathlib import Path

            # Read image file
            full_path = Path(f"data/images/{local_path}")
            if not full_path.exists():
                logger.warning(f"Image file not found: {full_path}")
                return None

            async with aiofiles.open(full_path, 'rb') as f:
                image_data = await f.read()

            # Upload to Supabase Storage
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                upload_url = f"{self.supabase_url}/storage/v1/object/{self.storage_bucket}/{remote_path}"

                response = await client.post(
                    upload_url,
                    headers={
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                        "Content-Type": "image/jpeg"
                    },
                    content=image_data
                )

                if response.status_code in [200, 201]:
                    # Return public URL
                    public_url = f"{self.supabase_url}/storage/v1/object/public/{self.storage_bucket}/{remote_path}"
                    logger.debug(f"Uploaded image: {remote_path}")
                    return public_url
                else:
                    logger.error(f"Failed to upload image: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error uploading image to Supabase: {e}")
            return None

    async def _upsert_article(self, article_data: Dict) -> bool:
        """Upsert article to Supabase database"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use upsert (insert or update if exists)
                response = await client.post(
                    f"{self.supabase_url}/rest/v1/articles",
                    headers={
                        **self.headers,
                        "Prefer": "resolution=merge-duplicates"
                    },
                    json=article_data
                )

                if response.status_code in [200, 201]:
                    return True
                else:
                    logger.error(f"Supabase upsert failed: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Error upserting to Supabase: {e}")
            return False

    async def sync_multiple(
        self,
        articles: List[Article],
        max_concurrent: int = 5
    ) -> Dict[str, int]:
        """
        Sync multiple articles to Supabase

        Args:
            articles: List of articles
            max_concurrent: Max concurrent uploads

        Returns:
            Dictionary with sync statistics
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        results = {"success": 0, "failed": 0, "total": len(articles)}

        async def sync_with_semaphore(article: Article) -> bool:
            async with semaphore:
                return await self.sync_article(article)

        tasks = [sync_with_semaphore(article) for article in articles]
        sync_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in sync_results:
            if isinstance(result, bool) and result:
                results["success"] += 1
            else:
                results["failed"] += 1

        logger.info(
            f"Supabase sync complete: {results['success']} success, "
            f"{results['failed']} failed out of {results['total']}"
        )

        return results

    async def delete_article(self, article_id: str) -> bool:
        """Delete article from Supabase"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.supabase_url}/rest/v1/articles?id=eq.{article_id}",
                    headers=self.headers
                )

                if response.status_code == 204:
                    logger.info(f"Deleted article from Supabase: {article_id}")
                    return True
                else:
                    logger.error(f"Failed to delete: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Error deleting from Supabase: {e}")
            return False

    async def get_existing_articles(self, limit: int = 1000) -> List[Dict]:
        """Get existing articles from Supabase"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/articles?select=id,slug,source_url&limit={limit}",
                    headers=self.headers
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to fetch articles: {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"Error fetching from Supabase: {e}")
            return []

    async def article_exists(self, source_url: str) -> bool:
        """Check if article exists in Supabase"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/articles?source_url=eq.{source_url}&select=id",
                    headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    return len(data) > 0
                else:
                    return False

        except Exception as e:
            logger.error(f"Error checking article existence: {e}")
            return False

    async def get_stats(self) -> Dict:
        """Get statistics from Supabase"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Total articles
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/articles?select=count",
                    headers={**self.headers, "Prefer": "count=exact"}
                )

                total = 0
                if response.status_code == 200:
                    # Count is in the Content-Range header
                    content_range = response.headers.get("Content-Range", "")
                    if "/" in content_range:
                        total = int(content_range.split("/")[1])

                # By category
                by_category = {}
                categories = ["economia", "politica", "sociedad", "internacional", "judicial"]

                for category in categories:
                    response = await client.get(
                        f"{self.supabase_url}/rest/v1/articles?category_slug=eq.{category}&select=count",
                        headers={**self.headers, "Prefer": "count=exact"}
                    )

                    if response.status_code == 200:
                        content_range = response.headers.get("Content-Range", "")
                        if "/" in content_range:
                            count = int(content_range.split("/")[1])
                            by_category[category] = count

                return {
                    "total_articles": total,
                    "by_category": by_category
                }

        except Exception as e:
            logger.error(f"Error getting Supabase stats: {e}")
            return {"total_articles": 0, "by_category": {}}

    async def cleanup_old_articles(self, days: int = 90) -> int:
        """Delete articles older than specified days"""
        try:
            from datetime import timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.supabase_url}/rest/v1/articles?published_at=lt.{cutoff_date}",
                    headers=self.headers
                )

                if response.status_code == 204:
                    logger.info(f"Cleaned up old articles (older than {days} days)")
                    return 0  # Supabase doesn't return count on delete
                else:
                    logger.error(f"Failed to cleanup: {response.status_code}")
                    return 0

        except Exception as e:
            logger.error(f"Error cleaning up Supabase: {e}")
            return 0
