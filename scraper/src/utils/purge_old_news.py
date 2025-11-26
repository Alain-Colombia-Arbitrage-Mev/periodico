"""
Purge old news - Keep only last 3 days
"""
from datetime import datetime, timedelta
from loguru import logger
from ..storage.supabase_storage import SupabaseStorage


class NewsPurger:
    """Purge old news from database"""
    
    def __init__(self, supabase_storage: SupabaseStorage, days_to_keep: int = 3):
        self.storage = supabase_storage
        self.days_to_keep = days_to_keep
        
    async def purge_old_news(self) -> dict:
        """
        Delete news older than X days

        Returns:
            dict with purge statistics
        """
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=self.days_to_keep)
            cutoff_str = cutoff_date.isoformat()

            logger.info(f"Purging news older than {self.days_to_keep} days (before {cutoff_str})")

            # Use direct HTTP API instead of client
            import httpx

            # First, get count of old articles
            async with httpx.AsyncClient(timeout=30) as client:
                # Query old news
                response = await client.get(
                    f"{self.storage.supabase_url}/rest/v1/articles?published_at=lt.{cutoff_str}&select=id",
                    headers=self.storage.headers
                )

                if response.status_code != 200:
                    logger.error(f"Failed to query old news: {response.status_code}")
                    return {"deleted": 0, "kept_days": self.days_to_keep}

                old_news = response.json()

                if not old_news:
                    logger.info("No old news to purge")
                    return {"deleted": 0, "kept_days": self.days_to_keep}

                old_news_count = len(old_news)
                logger.info(f"Found {old_news_count} old news to delete")

                # Delete old news
                delete_response = await client.delete(
                    f"{self.storage.supabase_url}/rest/v1/articles?published_at=lt.{cutoff_str}",
                    headers=self.storage.headers
                )

                if delete_response.status_code in [200, 204]:
                    logger.success(f"Successfully purged {old_news_count} old news articles")

                    return {
                        "deleted": old_news_count,
                        "kept_days": self.days_to_keep,
                        "cutoff_date": cutoff_str
                    }
                else:
                    logger.error(f"Failed to delete old news: {delete_response.status_code}")
                    return {"deleted": 0, "error": f"HTTP {delete_response.status_code}"}

        except Exception as e:
            logger.error(f"Error purging old news: {e}")
            return {"deleted": 0, "error": str(e)}
    
    async def get_news_count_by_date(self) -> dict:
        """Get count of news by date for last 7 days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            cutoff_str = cutoff_date.isoformat()

            import httpx

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{self.storage.supabase_url}/rest/v1/articles?published_at=gte.{cutoff_str}&select=published_at",
                    headers=self.storage.headers
                )

                if response.status_code != 200:
                    logger.error(f"Failed to get news count: {response.status_code}")
                    return {}

                data = response.json()

                if not data:
                    return {}

                # Count by date
                date_counts = {}
                for item in data:
                    pub_date = datetime.fromisoformat(item['published_at'].replace('Z', '+00:00'))
                    date_key = pub_date.strftime('%Y-%m-%d')
                    date_counts[date_key] = date_counts.get(date_key, 0) + 1

                return date_counts

        except Exception as e:
            logger.error(f"Error getting news count: {e}")
            return {}
