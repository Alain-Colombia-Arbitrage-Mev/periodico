"""
Base scraper class with common functionality
"""
import asyncio
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup
from loguru import logger

from ..models.article import Article
from ..utils.image_handler import ImageHandler
from ..utils.category_detector import CategoryDetector
from ..utils.text_cleaner import TextCleaner
from ..utils.stealth_config import StealthConfig, RateLimiter, StealthBrowser
from ..utils.advanced_stealth import get_advanced_stealth_script
from ..utils.image_validator import ImageValidator


class BaseScraper(ABC):
    """Base class for all news scrapers"""

    def __init__(
        self,
        source_name: str,
        base_url: str,
        image_handler: ImageHandler,
        headless: bool = False,  # Cambiar a False para debugging en macOS
        timeout: int = None,  # Will be set from env or default
        enable_stealth: bool = True,  # Enable stealth mode by default
        requests_per_minute: int = None  # Rate limiting
    ):
        self.source_name = source_name
        self.base_url = base_url
        self.image_handler = image_handler
        self.headless = headless
        # Get timeout from environment or use default (30 seconds)
        if timeout is None:
            timeout = int(os.getenv("PAGE_TIMEOUT", "30000"))
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.logger = logger.bind(scraper=source_name)

        # Stealth configuration
        self.enable_stealth = enable_stealth
        self.user_agent = StealthConfig.get_random_user_agent()
        self.viewport_size = StealthConfig.get_viewport_size()

        # Rate limiting (configurable via env or default)
        if requests_per_minute is None:
            requests_per_minute = int(os.getenv("STEALTH_REQUESTS_PER_MINUTE", "10"))
        self.rate_limiter = RateLimiter(requests_per_minute=requests_per_minute)

        self.logger.info(f"Stealth mode: {'ENABLED' if enable_stealth else 'DISABLED'}")
        if enable_stealth:
            self.logger.debug(f"User-Agent: {self.user_agent[:50]}...")
            self.logger.debug(f"Viewport: {self.viewport_size}")
            self.logger.debug(f"Rate limit: {requests_per_minute} req/min")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()

    async def start(self):
        """Initialize browser with stealth configuration"""
        self.logger.info(f"Starting {self.source_name} scraper")
        self.playwright = await async_playwright().start()

        # Advanced browser launch arguments for maximum stealth
        launch_args = [
            '--disable-blink-features=AutomationControlled',  # Hide automation
            '--disable-dev-shm-usage',  # Overcome limited resource problems
            '--no-sandbox',  # Required for Docker
            '--disable-setuid-sandbox',
            '--disable-infobars',  # Hide "Chrome is being controlled" message
            '--disable-extensions',  # Disable extensions for consistency
            '--disable-plugins-discovery',  # Hide plugin discovery
            '--disable-default-apps',  # Disable default apps
        ]

        if self.enable_stealth:
            # Additional advanced stealth args
            launch_args.extend([
                '--disable-web-security',  # Bypass some CORS checks
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-blink-features=AutomationControlled',
                '--exclude-switches=enable-automation',  # Remove automation flag
                '--disable-background-timer-throttling',  # Prevent throttling
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--enable-features=NetworkService,NetworkServiceInProcess',
                '--force-color-profile=srgb',  # Consistent color profile
                '--metrics-recording-only',  # Disable metrics
                '--mute-audio',  # Mute audio
            ])

        # Usar Chromium (instalado en Docker)
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            timeout=60000,
            args=launch_args
        )
        self.logger.debug("Chromium browser launched successfully with stealth configuration")

    async def stop(self):
        """Close browser and playwright"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            await self.playwright.stop()
        self.logger.info(f"Stopped {self.source_name} scraper")

    async def create_page(self) -> Page:
        """Create new browser page with stealth settings"""
        if not self.browser:
            raise RuntimeError("Browser not initialized. Call start() first.")

        page = await self.browser.new_page()

        # Set viewport size (realistic and variable)
        await page.set_viewport_size({
            "width": self.viewport_size[0],
            "height": self.viewport_size[1]
        })

        # Set realistic headers
        if self.enable_stealth:
            headers = StealthConfig.get_headers(self.user_agent)
            await page.set_extra_http_headers(headers)

            # Inject advanced anti-detection script
            advanced_script = get_advanced_stealth_script()
            await page.add_init_script(advanced_script)
            
            # Additional page-level overrides
            await page.add_init_script("""
                // Override window.chrome for consistency
                if (!window.chrome) {
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                }
                
                // Ensure webdriver is always undefined
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                    configurable: false
                });
            """)
        else:
            # Basic user agent
            await page.set_extra_http_headers({
                "User-Agent": self.user_agent
            })

        return page

    async def fetch_page(self, url: str, wait_for: Optional[str] = None, max_retries: int = 3) -> Optional[str]:
        """
        Fetch a page using Playwright with stealth behaviors and retry logic

        Args:
            url: URL to fetch
            wait_for: CSS selector to wait for (optional)
            max_retries: Maximum number of retry attempts

        Returns:
            Page HTML or None if failed
        """
        page = None
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Apply rate limiting if stealth enabled
                if self.enable_stealth and hasattr(self, 'rate_limiter'):
                    try:
                        # Verify rate_limiter is actually a RateLimiter instance, not a dict
                        if isinstance(self.rate_limiter, RateLimiter):
                            await self.rate_limiter.wait_if_needed(url)
                            # Only try to get stats if it's a proper RateLimiter instance
                            if hasattr(self.rate_limiter, 'get_stats') and callable(getattr(self.rate_limiter, 'get_stats', None)):
                                try:
                                    stats = self.rate_limiter.get_stats(url)
                                    self.logger.debug(f"Rate limit stats: {stats}")
                                except Exception as stats_error:
                                    # Silently handle stats errors to avoid breaking scraping
                                    self.logger.debug(f"Could not get rate limit stats: {stats_error}")
                    except Exception as rate_error:
                        # If rate limiter fails, log but continue
                        self.logger.debug(f"Rate limiter error (continuing anyway): {rate_error}")

                page = await self.create_page()
                self.logger.debug(f"Navigating to: {url} (attempt {attempt + 1}/{max_retries})")

                # Use domcontentloaded instead of networkidle for faster loading
                # Modern news sites have too many ads/trackers that never stop loading
                await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)

                # Wait for specific element if specified
                if wait_for:
                    try:
                        await page.wait_for_selector(wait_for, timeout=self.timeout)
                    except Exception as selector_error:
                        self.logger.warning(f"Selector {wait_for} not found, continuing anyway: {selector_error}")

                if self.enable_stealth:
                    # Advanced human-like behavior simulation
                    # Initial reading delay (humans take time to process)
                    reading_delay = StealthConfig.get_reading_delay()
                    self.logger.debug(f"Human reading delay: {reading_delay:.2f}s")
                    await asyncio.sleep(reading_delay)

                    # Scroll behavior (most humans scroll)
                    if StealthConfig.should_add_scroll():
                        try:
                            await StealthBrowser.human_scroll(page)
                        except Exception as scroll_error:
                            self.logger.debug(f"Scroll failed (non-critical): {scroll_error}")

                    # Mouse movement (humans move mouse frequently)
                    if StealthConfig.should_add_mouse_movement():
                        try:
                            move_count = StealthConfig.get_mouse_movement_count()
                            for _ in range(move_count):
                                await StealthBrowser.random_mouse_movement(page)
                                await asyncio.sleep(StealthConfig.get_delay(0.3, 0.8))
                        except Exception as mouse_error:
                            self.logger.debug(f"Mouse movement failed (non-critical): {mouse_error}")

                    # Final delay before extracting content (simulate reading)
                    final_delay = StealthConfig.get_delay(1.5, 3.0)
                    await asyncio.sleep(final_delay)
                else:
                    # Standard delay
                    await asyncio.sleep(5)

                html = await page.content()
                self.logger.debug(f"Successfully fetched page: {url}")
                return html

            except Exception as e:
                last_error = e
                self.logger.warning(f"Error fetching page {url} (attempt {attempt + 1}/{max_retries}): {e}")
                
                # Close page if it exists before retrying
                if page:
                    try:
                        await page.close()
                    except:
                        pass
                    page = None
                
                # Wait before retry (exponential backoff)
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
                    self.logger.debug(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
            finally:
                # Ensure page is closed
                if page:
                    try:
                        await page.close()
                    except:
                        pass
                    page = None
        
        # All retries failed
        self.logger.error(f"Failed to fetch page {url} after {max_retries} attempts. Last error: {last_error}")
        return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML with BeautifulSoup"""
        return BeautifulSoup(html, 'lxml')

    @abstractmethod
    async def scrape_listing(self, category: str, max_articles: int = 20) -> List[str]:
        """
        Scrape article URLs from listing page

        Args:
            category: News category
            max_articles: Maximum articles to scrape

        Returns:
            List of article URLs
        """
        pass

    @abstractmethod
    async def scrape_article(self, url: str, category: str) -> Optional[Article]:
        """
        Scrape individual article

        Args:
            url: Article URL
            category: Article category

        Returns:
            Article object or None if failed
        """
        pass

    async def scrape_category(
        self,
        category: str,
        max_articles: int = 20
    ) -> List[Article]:
        """
        Scrape all articles from a category

        Args:
            category: Category to scrape (used as hint, will be auto-detected)
            max_articles: Maximum articles to scrape

        Returns:
            List of Article objects
        """
        self.logger.info(f"Scraping category: {category}")

        # Get article URLs
        urls = await self.scrape_listing(category, max_articles)
        self.logger.info(f"Found {len(urls)} article URLs in {category}")

        if not urls:
            return []

        # Scrape each article
        articles = []
        for i, url in enumerate(urls):
            try:
                # Pasar category como hint, pero se detectará automáticamente
                article = await self.scrape_article(url, category)
                if article:
                    articles.append(article)
                    self.logger.debug(f"Scraped article: {article.title[:50]}... (category: {article.category_slug})")

                # Be polite - add delay between requests
                if self.enable_stealth:
                    # Variable delay with jitter
                    delay = StealthConfig.get_delay(2, 5)
                    self.logger.debug(f"Article {i+1}/{len(urls)}: waiting {delay:.2f}s before next...")
                    await asyncio.sleep(delay)
                else:
                    await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"Error scraping article {url}: {e}")
                continue

        self.logger.info(f"Successfully scraped {len(articles)} articles from {category}")
        return articles

    async def scrape_all_categories(
        self,
        categories: List[str],
        max_articles_per_category: int = 20
    ) -> dict[str, List[Article]]:
        """
        Scrape articles from multiple categories

        Args:
            categories: List of categories to scrape
            max_articles_per_category: Max articles per category

        Returns:
            Dictionary mapping category to list of articles
        """
        results = {}

        for category in categories:
            try:
                articles = await self.scrape_category(category, max_articles_per_category)
                results[category] = articles
            except Exception as e:
                self.logger.error(f"Error scraping category {category}: {e}")
                results[category] = []

        total = sum(len(articles) for articles in results.values())
        self.logger.info(f"Scraping complete. Total articles: {total}")

        return results

    def clean_text(self, text: str) -> str:
        """Clean and normalize text, removing source references"""
        if not text:
            return ""

        # Remove extra whitespace
        text = " ".join(text.split())

        # Remove special characters
        text = text.replace('\xa0', ' ')
        text = text.replace('\u200b', '')

        # Remove source references (Clarín, Infobae, etc.)
        text = TextCleaner.clean_text(text)

        return text.strip()

    def extract_date(self, date_str: str) -> datetime:
        """Extract datetime from string with advanced Spanish date parsing"""
        from dateutil import parser
        import re
        from datetime import datetime as dt
        
        if not date_str:
            return datetime.now()
        
        # Clean the date string
        date_str = date_str.strip()
        
        # Spanish months mapping (full names and abbreviations)
        spanish_months = {
            'enero': 1, 'ene': 1,
            'febrero': 2, 'feb': 2,
            'marzo': 3, 'mar': 3,
            'abril': 4, 'abr': 4,
            'mayo': 5, 'may': 5,
            'junio': 6, 'jun': 6,
            'julio': 7, 'jul': 7,
            'agosto': 8, 'ago': 8,
            'septiembre': 9, 'sep': 9, 'setiembre': 9,
            'octubre': 10, 'oct': 10,
            'noviembre': 11, 'nov': 11,
            'diciembre': 12, 'dic': 12
        }
        
        # Pattern 1: "DD de MMMM de YYYY" (e.g., "16 de noviembre de 2025")
        spanish_pattern_full = r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})'
        match = re.search(spanish_pattern_full, date_str, re.IGNORECASE)
        
        if match:
            try:
                day = int(match.group(1))
                month_name = match.group(2).lower().strip()
                year = int(match.group(3))
                
                if month_name in spanish_months:
                    month = spanish_months[month_name]
                    if 1 <= day <= 31 and 1 <= month <= 12:
                        return datetime(year, month, day)
            except (ValueError, KeyError) as e:
                self.logger.debug(f"Error parsing Spanish date pattern 1: {e}")
        
        # Pattern 2: "DD/MM/YYYY" or "DD-MM-YYYY"
        numeric_pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
        match = re.search(numeric_pattern, date_str)
        if match:
            try:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))
                if 1 <= day <= 31 and 1 <= month <= 12:
                    return datetime(year, month, day)
            except ValueError:
                pass
        
        # Pattern 3: ISO format or standard formats
        try:
            parsed = parser.parse(date_str, dayfirst=True, fuzzy=True)
            return parsed
        except Exception:
            pass
        
        # Pattern 4: Try with locale Spanish
        try:
            # Try parsing with Spanish locale hints
            for month_name, month_num in spanish_months.items():
                if month_name in date_str.lower() and len(month_name) > 3:  # Only full names
                    # Try to extract day and year
                    parts = re.findall(r'\d+', date_str)
                    if len(parts) >= 2:
                        day = int(parts[0])
                        year = int(parts[-1])
                        if 1 <= day <= 31 and 2000 <= year <= 2100:
                            return datetime(year, month_num, day)
        except Exception:
            pass
        
        # If all parsing fails, log and return current time
        self.logger.warning(f"Could not parse date: {date_str}, using current time")
        return datetime.now()
