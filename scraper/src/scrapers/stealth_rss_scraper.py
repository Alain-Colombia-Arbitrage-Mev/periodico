"""
Stealth RSS Image Scraper - Anti-detection optimized
Features:
- User-Agent rotation
- Request rate limiting
- Retry logic with exponential backoff
- Image validation before download
- Advanced logo detection
"""

import asyncio
import httpx
import random
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import re
from io import BytesIO
from PIL import Image
import hashlib
import sys

# Configure basic logging if loguru not available
try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

class StealthRSScraper:
    """Anti-detection RSS scraper with image validation"""

    # User-Agent pool - Real browser user agents
    USER_AGENTS = [
        # Chrome on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        # Chrome on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        # Firefox on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        # Firefox on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
        # Safari on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        # Edge on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    ]

    # RSS feeds por categoría
    RSS_FEEDS = {
        # Economía
        'cronista_economia': {
            'url': 'https://www.cronista.com/rss/economia/',
            'name': 'El Cronista',
            'category': 'economia'
        },
        'lanacion_economia': {
            'url': 'https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/economia/',
            'name': 'La Nación',
            'category': 'economia'
        },
        'clarin_economia': {
            'url': 'https://www.clarin.com/rss/economia/',
            'name': 'Clarín',
            'category': 'economia'
        },
        'ambito_economia': {
            'url': 'https://www.ambito.com/contenidos/economia.rss',
            'name': 'Ámbito',
            'category': 'economia'
        },

        # Política
        'cronista_politica': {
            'url': 'https://www.cronista.com/rss/politica/',
            'name': 'El Cronista',
            'category': 'politica'
        },
        'lanacion_politica': {
            'url': 'https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/politica/',
            'name': 'La Nación',
            'category': 'politica'
        },
        'clarin_politica': {
            'url': 'https://www.clarin.com/rss/politica/',
            'name': 'Clarín',
            'category': 'politica'
        },

        # Internacional
        'lanacion_mundo': {
            'url': 'https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/el-mundo/',
            'name': 'La Nación',
            'category': 'internacional'
        },
        'clarin_mundo': {
            'url': 'https://www.clarin.com/rss/mundo/',
            'name': 'Clarín',
            'category': 'internacional'
        },

        # Sociedad
        'lanacion_sociedad': {
            'url': 'https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/sociedad/',
            'name': 'La Nación',
            'category': 'sociedad'
        },
        'clarin_sociedad': {
            'url': 'https://www.clarin.com/rss/sociedad/',
            'name': 'Clarín',
            'category': 'sociedad'
        },

        # Judicial
        'clarin_policiales': {
            'url': 'https://www.clarin.com/rss/policiales/',
            'name': 'Clarín',
            'category': 'judicial'
        },
        'lanacion_seguridad': {
            'url': 'https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/seguridad/',
            'name': 'La Nación',
            'category': 'judicial'
        },
    }

    # Logo detection patterns
    LOGO_PATTERNS = [
        r'logo', r'brand', r'favicon', r'icon', r'sprite',
        r'lanacion[-_]?logo', r'clarin[-_]?logo', r'cronista[-_]?logo',
        r'thumb', r'small', r'mini', r'avatar',
        r'\d+x\d+\.(?:png|jpg|jpeg|gif)$',  # Small fixed-size images
    ]

    def __init__(self, rate_limit: float = 1.0):
        """
        Initialize scraper

        Args:
            rate_limit: Seconds to wait between requests (default 1.0)
        """
        self.rate_limit = rate_limit
        self.last_request_time = {}
        self.failed_images = set()  # Track failed image URLs

    def _get_random_headers(self) -> Dict[str, str]:
        """Get randomized request headers"""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'application/rss+xml, application/xml, text/xml, application/atom+xml, */*',
            'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

    async def _rate_limited_request(self, client: httpx.AsyncClient, url: str, source_key: str) -> httpx.Response:
        """Make rate-limited HTTP request"""
        # Wait for rate limit
        if source_key in self.last_request_time:
            elapsed = asyncio.get_event_loop().time() - self.last_request_time[source_key]
            if elapsed < self.rate_limit:
                await asyncio.sleep(self.rate_limit - elapsed)

        # Random delay between 0.5-1.5 seconds
        await asyncio.sleep(random.uniform(0.5, 1.5))

        self.last_request_time[source_key] = asyncio.get_event_loop().time()

        response = await client.get(url)
        return response

    async def _retry_request(self, client: httpx.AsyncClient, url: str, source_key: str, max_retries: int = 3) -> Optional[httpx.Response]:
        """Retry request with exponential backoff"""
        for attempt in range(max_retries):
            try:
                response = await self._rate_limited_request(client, url, source_key)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"❌ Failed after {max_retries} attempts: {url} - {e}")
                    return None

                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                logger.warning(f"⚠️ Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

        return None

    def is_logo_image(self, image_url: str) -> bool:
        """
        Detect if image URL is likely a logo using multiple heuristics

        Returns:
            True if image is likely a logo, False otherwise
        """
        if not image_url:
            return True

        url_lower = image_url.lower()

        # Check URL patterns
        for pattern in self.LOGO_PATTERNS:
            if re.search(pattern, url_lower, re.IGNORECASE):
                logger.debug(f"🚫 Logo pattern detected: {pattern} in {image_url[:100]}")
                return True

        # Check dimensions in URL (e.g., 100x100, 200x200)
        dimension_match = re.search(r'(\d+)x(\d+)', url_lower)
        if dimension_match:
            width = int(dimension_match.group(1))
            height = int(dimension_match.group(2))

            # Small squares are usually logos
            if width == height and width < 300:
                logger.debug(f"🚫 Small square image: {width}x{height}")
                return True

            # Very small images are usually logos/icons
            if max(width, height) < 200:
                logger.debug(f"🚫 Very small image: {width}x{height}")
                return True

            # Large images with good aspect ratio are OK
            if width >= 400 and height >= 200:
                return False

        # Check filename length (logos usually have short names)
        parsed = urlparse(image_url)
        filename = parsed.path.split('/')[-1]
        if len(filename) < 10 and 'resizer' not in filename:
            logger.debug(f"🚫 Short filename: {filename}")
            return True

        return False

    async def validate_image(self, client: httpx.AsyncClient, image_url: str, source_key: str) -> bool:
        """
        Validate that image URL returns valid image data

        Returns:
            True if image is valid and downloadable, False otherwise
        """
        # Skip if already failed
        if image_url in self.failed_images:
            return False

        # Check if it's a logo first
        if self.is_logo_image(image_url):
            self.failed_images.add(image_url)
            return False

        try:
            response = await self._retry_request(client, image_url, f"{source_key}_image", max_retries=2)

            if not response or response.status_code != 200:
                logger.warning(f"⚠️ Image request failed: {response.status_code if response else 'No response'}")
                self.failed_images.add(image_url)
                return False

            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'image' not in content_type:
                logger.warning(f"⚠️ Invalid content type: {content_type}")
                self.failed_images.add(image_url)
                return False

            # Validate image can be opened
            try:
                img = Image.open(BytesIO(response.content))
                width, height = img.size

                # Reject small images
                if width < 300 or height < 150:
                    logger.warning(f"⚠️ Image too small: {width}x{height}")
                    self.failed_images.add(image_url)
                    return False

                # Reject square logos
                if width == height and width < 500:
                    logger.warning(f"⚠️ Square image (likely logo): {width}x{height}")
                    self.failed_images.add(image_url)
                    return False

                logger.debug(f"✅ Valid image: {width}x{height} - {image_url[:80]}")
                return True

            except Exception as e:
                logger.warning(f"⚠️ Cannot open image: {e}")
                self.failed_images.add(image_url)
                return False

        except Exception as e:
            logger.warning(f"⚠️ Image validation error: {e}")
            self.failed_images.add(image_url)
            return False

    async def scrape_all_sources(self, max_articles_per_source: int = 10) -> List[Dict]:
        """Scrape all RSS sources with anti-detection measures"""
        logger.info("🚀 Starting stealth RSS scraping from all sources")

        all_articles = []

        # Scrape sources sequentially to avoid detection
        for source_key, feed_config in self.RSS_FEEDS.items():
            try:
                articles = await self.scrape_source(source_key, max_articles_per_source)
                all_articles.extend(articles)
                logger.info(f"✅ {feed_config['name']} ({feed_config['category']}): {len(articles)} articles")

                # Random delay between sources
                await asyncio.sleep(random.uniform(2.0, 4.0))

            except Exception as e:
                logger.error(f"❌ Error scraping {source_key}: {e}")

        logger.success(f"📊 Total articles scraped: {len(all_articles)}")
        return all_articles

    async def scrape_source(self, source_key: str, max_articles: int = 10) -> List[Dict]:
        """Scrape a single RSS source with validation"""
        feed_config = self.RSS_FEEDS.get(source_key)
        if not feed_config:
            logger.error(f"Unknown source: {source_key}")
            return []

        logger.info(f"📡 Scraping {feed_config['name']} RSS feed ({feed_config['category']})...")

        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers=self._get_random_headers()
        ) as client:
            try:
                response = await self._retry_request(client, feed_config['url'], source_key)
                if not response:
                    return []

                # Parse RSS XML
                root = ET.fromstring(response.content)

                articles = []
                for item in root.findall('.//item')[:max_articles * 2]:  # Get 2x to compensate for invalid images
                    article = await self._parse_rss_item(item, source_key, feed_config, client)
                    if article:
                        articles.append(article)

                    # Stop if we have enough valid articles
                    if len(articles) >= max_articles:
                        break

                logger.info(f"✅ Extracted {len(articles)} valid articles from {feed_config['name']}")
                return articles

            except Exception as e:
                logger.error(f"❌ Error scraping {feed_config['name']}: {e}")
                return []

    async def _parse_rss_item(self, item: ET.Element, source_key: str, feed_config: Dict, client: httpx.AsyncClient) -> Optional[Dict]:
        """Parse RSS item and validate image"""
        try:
            # Extract basic fields
            title = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            description = item.findtext('description', '')
            pub_date = item.findtext('pubDate', '')

            if not title or not link:
                return None

            # Extract and validate image URL
            image_url = await self._extract_and_validate_image(item, description, link, source_key, client)

            if not image_url:
                logger.warning(f"⚠️ No valid image for: {title[:60]}...")
                return None

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
                'content': excerpt,
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

    async def _extract_and_validate_image(self, item: ET.Element, description: str, article_url: str, source_key: str, client: httpx.AsyncClient) -> Optional[str]:
        """Extract image URL and validate it's not a logo"""

        # Strategy 1: media:content
        media_ns = {'media': 'http://search.yahoo.com/mrss/'}
        media_content = item.find('.//media:content', media_ns)
        if media_content is not None and media_content.get('url'):
            url = media_content.get('url')
            if await self.validate_image(client, url, source_key):
                return url

        # Strategy 2: media:thumbnail
        media_thumbnail = item.find('.//media:thumbnail', media_ns)
        if media_thumbnail is not None and media_thumbnail.get('url'):
            url = media_thumbnail.get('url')
            if await self.validate_image(client, url, source_key):
                return url

        # Strategy 3: enclosure tag
        enclosure = item.find('enclosure')
        if enclosure is not None and enclosure.get('url'):
            url = enclosure.get('url')
            if await self.validate_image(client, url, source_key):
                return url

        # Strategy 4: Parse HTML in description
        if description:
            soup = BeautifulSoup(description, 'html.parser')
            img_tag = soup.find('img')
            if img_tag and img_tag.get('src'):
                url = img_tag.get('src')
                if await self.validate_image(client, url, source_key):
                    return url

        return None

    def _parse_pub_date(self, pub_date: str) -> str:
        """Parse RSS publication date to ISO format"""
        try:
            from dateutil import parser
            dt = parser.parse(pub_date)
            return dt.isoformat()
        except:
            return datetime.now().isoformat()

    def _clean_description(self, description: str) -> str:
        """Clean HTML from description and extract text"""
        if not description:
            return ""

        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Limit length
        if len(text) > 300:
            text = text[:297] + '...'

        return text


async def main():
    """Test scraper"""
    scraper = StealthRSScraper(rate_limit=1.5)

    logger.info("🔍 Testing stealth RSS scraper...")
    articles = await scraper.scrape_all_sources(max_articles_per_source=5)

    logger.info(f"\n📊 Scraped {len(articles)} articles")

    # Show sample
    for i, article in enumerate(articles[:3], 1):
        logger.info(f"\n{i}. {article['title'][:60]}...")
        logger.info(f"   Category: {article['category']}")
        logger.info(f"   Source: {article['source']}")
        logger.info(f"   Image: {article['image_url'][:80]}...")


if __name__ == '__main__':
    asyncio.run(main())
