"""
RSS Image Scraper - Extract real images from news RSS feeds
Bypasses anti-scraping protection by using official RSS feeds
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
from loguru import logger
from urllib.parse import urljoin, urlparse

class RSSImageScraper:
    """Scraper that extracts articles with real images from RSS feeds"""

    RSS_FEEDS = {
        'cronista': {
            'url': 'https://www.cronista.com/rss/politica/',
            'name': 'El Cronista',
            'category': 'política'
        },
        'lanacion': {
            'url': 'https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/politica/',
            'name': 'La Nación',
            'category': 'política'
        },
        'clarin': {
            'url': 'https://www.clarin.com/rss/politica/',
            'name': 'Clarín',
            'category': 'política'
        },
    }

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0; +http://politicaargentina.com)',
                'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            }
        )

    async def scrape_all_sources(self, max_articles_per_source: int = 20) -> List[Dict]:
        """Scrape all RSS sources concurrently"""
        logger.info("🚀 Starting RSS scraping from all sources")

        tasks = [
            self.scrape_source(source_key, max_articles_per_source)
            for source_key in self.RSS_FEEDS.keys()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles = []
        for source_key, result in zip(self.RSS_FEEDS.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"❌ Error scraping {source_key}: {result}")
            else:
                all_articles.extend(result)
                logger.info(f"✅ {source_key}: {len(result)} articles")

        logger.success(f"📊 Total articles scraped: {len(all_articles)}")
        return all_articles

    async def scrape_source(self, source_key: str, max_articles: int = 20) -> List[Dict]:
        """Scrape a single RSS source"""
        feed_config = self.RSS_FEEDS.get(source_key)
        if not feed_config:
            logger.error(f"Unknown source: {source_key}")
            return []

        logger.info(f"📡 Scraping {feed_config['name']} RSS feed...")

        try:
            response = await self.client.get(feed_config['url'])
            response.raise_for_status()

            # Parse RSS XML
            root = ET.fromstring(response.content)

            articles = []
            for item in root.findall('.//item')[:max_articles]:
                article = self._parse_rss_item(item, source_key, feed_config)
                if article:
                    articles.append(article)

            logger.info(f"✅ Extracted {len(articles)} articles from {feed_config['name']}")
            return articles

        except Exception as e:
            logger.error(f"❌ Error scraping {feed_config['name']}: {e}")
            return []

    def _parse_rss_item(self, item: ET.Element, source_key: str, feed_config: Dict) -> Optional[Dict]:
        """Parse a single RSS item and extract image"""
        try:
            # Extract basic fields
            title = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            description = item.findtext('description', '')
            pub_date = item.findtext('pubDate', '')

            if not title or not link:
                return None

            # Extract image URL (multiple strategies)
            image_url = self._extract_image_from_item(item, description, link)

            # Parse publication date
            published_at = self._parse_pub_date(pub_date)

            # Clean description
            excerpt = self._clean_description(description)

            article = {
                'title': title,
                'url': link,
                'source_url': link,
                'image_url': image_url,
                'excerpt': excerpt,
                'content': excerpt,  # Full content would require visiting the page
                'published_at': published_at,
                'source': feed_config['name'],
                'source_key': source_key,
                'category': feed_config['category'],
                'source_type': 0,  # Scraped with LLM rewriting
            }

            return article

        except Exception as e:
            logger.warning(f"Error parsing RSS item: {e}")
            return None

    def _extract_image_from_item(self, item: ET.Element, description: str, article_url: str) -> Optional[str]:
        """Extract image URL from RSS item using multiple strategies"""

        # Strategy 1: media:content (most reliable for news sites)
        media_ns = {'media': 'http://search.yahoo.com/mrss/'}
        media_content = item.find('.//media:content', media_ns)
        if media_content is not None and media_content.get('url'):
            url = media_content.get('url')
            logger.debug(f"📷 Image from media:content: {url}")
            return url

        # Strategy 2: media:thumbnail
        media_thumbnail = item.find('.//media:thumbnail', media_ns)
        if media_thumbnail is not None and media_thumbnail.get('url'):
            url = media_thumbnail.get('url')
            logger.debug(f"📷 Image from media:thumbnail: {url}")
            return url

        # Strategy 3: enclosure tag
        enclosure = item.find('enclosure')
        if enclosure is not None:
            enc_type = enclosure.get('type', '')
            enc_url = enclosure.get('url', '')
            if enc_type.startswith('image/') and enc_url:
                logger.debug(f"📷 Image from enclosure: {enc_url}")
                return enc_url

        # Strategy 4: Parse description HTML
        if description:
            soup = BeautifulSoup(description, 'html.parser')
            img_tag = soup.find('img')
            if img_tag and img_tag.get('src'):
                url = img_tag['src']
                # Make absolute URL if relative
                if url.startswith('/'):
                    parsed_url = urlparse(article_url)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    url = urljoin(base_url, url)
                logger.debug(f"📷 Image from description HTML: {url}")
                return url

        # Strategy 5: og:image from description (some feeds include it)
        if 'og:image' in description:
            soup = BeautifulSoup(description, 'html.parser')
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                url = og_image['content']
                logger.debug(f"📷 Image from og:image: {url}")
                return url

        logger.warning(f"⚠️ No image found for article: {article_url}")
        return None

    def _parse_pub_date(self, pub_date_str: str) -> Optional[str]:
        """Parse RSS publication date to ISO format"""
        if not pub_date_str:
            return None

        try:
            # Try common RSS date formats
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(pub_date_str)
            return dt.isoformat()
        except Exception:
            # Fallback to current time
            return datetime.now().isoformat()

    def _clean_description(self, description: str) -> str:
        """Clean HTML from description and truncate"""
        if not description:
            return ""

        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Truncate to 200 characters
        if len(text) > 200:
            text = text[:197] + '...'

        return text

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Quick test function
async def test_rss_scraper():
    """Test the RSS scraper"""
    scraper = RSSImageScraper()

    try:
        articles = await scraper.scrape_all_sources(max_articles_per_source=5)

        print(f"\n📊 Scraped {len(articles)} articles\n")

        for i, article in enumerate(articles[:5], 1):
            print(f"{i}. {article['title'][:60]}...")
            print(f"   Source: {article['source']}")
            print(f"   Image: {article['image_url'] or '❌ No image'}")
            print(f"   URL: {article['url']}\n")

    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(test_rss_scraper())
