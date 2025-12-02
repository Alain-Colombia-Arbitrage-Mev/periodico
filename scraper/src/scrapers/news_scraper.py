"""
Generic news scraper implementation
"""
from typing import List, Optional
from datetime import datetime
from ..models.article import Article
from .base_scraper import BaseScraper
from ..utils.category_detector import CategoryDetector
from ..utils.text_cleaner import TextCleaner


class NewsScraper(BaseScraper):
    """Generic scraper for news websites"""

    def __init__(self, image_handler, headless: bool = None, base_url: str = None):
        import os
        import platform

        # Use env variable or default
        if base_url is None:
            base_url = os.getenv("SCRAPER_BASE_URL", "https://www.infobae.com")

        # Auto-detect headless mode: False on macOS, True on Linux/Docker
        if headless is None:
            headless = platform.system() != "Darwin"  # False if macOS, True otherwise

        super().__init__(
            source_name="Scraper Automático",
            base_url=base_url,
            image_handler=image_handler,
            headless=headless
        )

        # Category mappings - configure based on base_url
        if "infobae" in base_url:
            self.category_urls = {
                "economia": "/economia/",
                "politica": "/politica/",
                "sociedad": "/sociedad/",
                "internacional": "/america/",
                "judicial": "/politica/",
            }
        elif "clarin" in base_url:
            self.category_urls = {
                "economia": "/economia/",
                "politica": "/politica/",
                "sociedad": "/sociedad/",
                "internacional": "/mundo/",
                "judicial": "/policiales/",
            }
        elif "lanacion" in base_url:
            self.category_urls = {
                "economia": "/economia/",
                "politica": "/politica/",
                "sociedad": "/sociedad/",
                "internacional": "/el-mundo/",
                "judicial": "/seguridad/",
            }
        else:
            # Generic fallback
            self.category_urls = {
                "economia": "/economia/",
                "politica": "/politica/",
                "sociedad": "/sociedad/",
                "internacional": "/internacional/",
                "judicial": "/judicial/",
            }

    async def scrape_listing(self, category: str, max_articles: int = 20) -> List[str]:
        """Scrape article URLs from category page"""
        category_path = self.category_urls.get(category.lower(), f"/{category}/")
        url = f"{self.base_url}{category_path}"

        html = await self.fetch_page(url, wait_for="article")
        if not html:
            return []

        soup = self.parse_html(html)
        article_urls = []

        # Find article links using generic selectors
        articles = soup.find_all('article', limit=max_articles * 2)

        for article in articles:
            if len(article_urls) >= max_articles:
                break

            # Try to find article link
            link = article.find('a', href=True)
            if link:
                href = link['href']

                # Make absolute URL
                if href.startswith('/'):
                    href = self.base_url + href
                elif not href.startswith('http'):
                    continue

                # Avoid duplicates and AMP pages
                if href not in article_urls and '/amp/' not in href:
                    article_urls.append(href)

        self.logger.info(f"Found {len(article_urls)} articles in {category}")
        return article_urls

    async def scrape_article(self, url: str, category: str) -> Optional[Article]:
        """Scrape individual article using generic selectors"""
        html = await self.fetch_page(url)
        if not html:
            return None

        soup = self.parse_html(html)

        try:
            # Extract title using generic selectors
            title_elem = (
                soup.find('h1', class_='article-title') or
                soup.find('h1', class_='title') or
                soup.find('h1') or
                soup.find('meta', property='og:title') or
                soup.find('title')
            )

            title_raw = None
            if title_elem:
                if title_elem.name == 'meta':
                    title_raw = title_elem.get('content')
                else:
                    title_raw = title_elem.get_text()

            title = TextCleaner.clean_title(self.clean_text(title_raw)) if title_raw else None

            if not title:
                self.logger.warning(f"No title found for {url}")
                return None

            # Extract subtitle
            subtitle_elem = (
                soup.find('h2', class_='article-subtitle') or
                soup.find('h2', class_='subtitle') or
                soup.find('h2', class_='deck') or
                soup.find('p', class_='lead')
            )
            subtitle_raw = subtitle_elem.get_text() if subtitle_elem else None
            subtitle = TextCleaner.clean_text(self.clean_text(subtitle_raw)) if subtitle_raw else None

            # Extract content
            content_elem = (
                soup.find('div', class_='article-content') or
                soup.find('div', class_='article-body') or
                soup.find('div', class_='content') or
                soup.find('article')
            )

            content = ""
            if content_elem:
                # Get all paragraphs
                paragraphs = content_elem.find_all('p')
                content_raw = "\n\n".join(
                    p.get_text()
                    for p in paragraphs
                    if p.get_text().strip()
                )
                content = TextCleaner.clean_content(self.clean_text(content_raw))

            # Extract excerpt (from meta or first paragraph)
            excerpt = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                excerpt_raw = meta_desc['content']
                excerpt = TextCleaner.clean_text(self.clean_text(excerpt_raw))
            elif content:
                excerpt = content[:200] + "..." if len(content) > 200 else content

            # Extract image
            image_url = None
            img_elem = (
                soup.find('meta', property='og:image') or
                soup.find('img', class_='article-image') or
                soup.find('img', class_='featured-image') or
                soup.find('figure', class_='article-figure')
            )

            if img_elem:
                if img_elem.name == 'meta':
                    image_url = img_elem.get('content')
                elif img_elem.name == 'img':
                    image_url = img_elem.get('src') or img_elem.get('data-src')
                else:
                    img = img_elem.find('img')
                    if img:
                        image_url = img.get('src') or img.get('data-src')

            # Download image
            local_image_path = None
            if image_url:
                local_image_path = await self.image_handler.download_image(
                    image_url,
                    category
                )

            # Always use generic author
            author = "Redacción"

            # Extract publish date
            date_elem = (
                soup.find('time') or
                soup.find('meta', property='article:published_time') or
                soup.find('meta', attrs={'name': 'publishdate'})
            )

            published_at = datetime.now()
            if date_elem:
                if date_elem.name == 'meta':
                    date_str = date_elem.get('content')
                else:
                    date_str = date_elem.get('datetime') or date_elem.get_text()

                if date_str:
                    published_at = self.extract_date(date_str)

            # Extract tags
            tags = []
            tag_elems = soup.find_all('a', class_='tag') or soup.find_all('a', rel='tag')
            tags = [TextCleaner.clean_text(self.clean_text(tag.get_text()))
                   for tag in tag_elems if tag.get_text().strip()]

            # Auto-detect category
            detected_category = CategoryDetector.detect_category(
                url=url,
                title=title,
                content=content,
                excerpt=excerpt,
                soup=soup
            )

            # Use detected category or fallback to provided one
            final_category = detected_category if detected_category else category.lower()
            if detected_category != category.lower():
                self.logger.info(f"Category auto-detected: {detected_category} (was: {category})")

            # Create article
            article = Article(
                source=self.source_name,
                source_url=url,
                title=title,
                subtitle=subtitle,
                excerpt=excerpt,
                content=content,
                category=final_category.capitalize(),
                category_slug=final_category.lower(),
                author=author,
                published_at=published_at,
                image_url=image_url,
                local_image_path=local_image_path,
                tags=tags,
                meta_description=excerpt
            )

            return article

        except Exception as e:
            self.logger.error(f"Error parsing article {url}: {e}")
            return None
