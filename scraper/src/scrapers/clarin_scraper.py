"""
Clarín scraper implementation
"""
from typing import List, Optional
from datetime import datetime
from ..models.article import Article
from .base_scraper import BaseScraper
from ..utils.category_detector import CategoryDetector
from ..utils.text_cleaner import TextCleaner
from ..utils.image_validator import ImageValidator


class ClarinScraper(BaseScraper):
    """Scraper for Clarin.com"""

    def __init__(self, image_handler, headless: bool = True):
        super().__init__(
            source_name="Clarín",
            base_url="https://www.clarin.com",
            image_handler=image_handler,
            headless=headless
        )

        # Category mappings
        self.category_urls = {
            "economia": "/economia/",
            "politica": "/politica/",
            "sociedad": "/sociedad/",
            "internacional": "/mundo/",
        }

    async def scrape_listing(self, category: str, max_articles: int = 20) -> List[str]:
        """Scrape article URLs from category page"""
        category_path = self.category_urls.get(category.lower(), f"/{category}/")
        url = f"{self.base_url}{category_path}"

        # Don't wait for specific selector, just load page
        html = await self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_html(html)
        article_urls = []

        # Find all links that look like article URLs
        all_links = soup.find_all('a', href=True)

        for link in all_links:
            if len(article_urls) >= max_articles:
                break

            href = link.get('href', '')

            # Skip if not a valid link
            if not href:
                continue

            # Make absolute URL
            if href.startswith('/'):
                href = self.base_url + href
            elif not href.startswith('http'):
                continue

            # Filter valid articles - Clarín articles follow pattern /category/article-title-123456/
            if (href not in article_urls and
                'clarin.com' in href and
                '/amp/' not in href and
                href.count('/') >= 4 and  # /category/article-slug/
                not any(x in href for x in ['/tags/', '/autor/', '/search/', '/opinion/', '/videos/'])):

                # Check if link has meaningful text (likely an article title)
                link_text = link.get_text().strip()
                if len(link_text) > 20:  # Articles usually have titles > 20 chars
                    article_urls.append(href)

        self.logger.info(f"Found {len(article_urls)} articles in {category}")
        return article_urls

    async def scrape_article(self, url: str, category: str) -> Optional[Article]:
        """Scrape individual article from Clarín"""
        html = await self.fetch_page(url)
        if not html:
            return None

        soup = self.parse_html(html)

        try:
            # Extract title
            title_elem = (
                soup.find('h1', class_='title') or
                soup.find('h1', id='title') or
                soup.find('h1')
            )
            title_raw = title_elem.get_text() if title_elem else None
            title = TextCleaner.clean_title(self.clean_text(title_raw)) if title_raw else None

            if not title:
                self.logger.warning(f"No title found for {url}")
                return None

            # Extract subtitle/volanta
            subtitle_elem = (
                soup.find('h2', class_='subtitle') or
                soup.find('h2', class_='volanta') or
                soup.find('p', class_='bajada')
            )
            subtitle_raw = subtitle_elem.get_text() if subtitle_elem else None
            subtitle = TextCleaner.clean_text(self.clean_text(subtitle_raw)) if subtitle_raw else None

            # Extract content
            content_elem = (
                soup.find('div', class_='body-nota') or
                soup.find('div', id='body-nota') or
                soup.find('section', class_='article-body')
            )

            content = ""
            if content_elem:
                paragraphs = content_elem.find_all('p')
                content_raw = "\n\n".join(
                    p.get_text()
                    for p in paragraphs
                    if p.get_text().strip() and not p.find('strong', text='Mirá también')
                )
                content = TextCleaner.clean_content(self.clean_text(content_raw))

            # Extract excerpt
            excerpt = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                excerpt_raw = meta_desc['content']
                excerpt = TextCleaner.clean_text(self.clean_text(excerpt_raw))
            elif content:
                excerpt = content[:200] + "..." if len(content) > 200 else content

            # Extract image - collect multiple candidates
            image_candidates = []

            # Try og:image first
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                image_candidates.append(og_image.get('content'))

            # Try article image classes
            img_elem = (
                soup.find('figure', class_='image-wrapper') or
                soup.find('div', class_='image-container')
            )

            if img_elem:
                img = img_elem.find('img')
                if img:
                    src = (
                        img.get('data-src') or
                        img.get('src') or
                        img.get('data-lazy-src')
                    )
                    if src:
                        image_candidates.append(src)

            # Try all images in article content
            if content_elem:
                for img in content_elem.find_all('img'):
                    src = img.get('data-src') or img.get('src') or img.get('data-lazy-src')
                    if src and src not in image_candidates:
                        image_candidates.append(src)

            # Validate and select best image
            image_url = ImageValidator.get_best_image(image_candidates, 'clarin.com')

            if not image_url:
                self.logger.warning(f"No valid article image found for {url}")

            # Download image
            local_image_path = None
            if image_url:
                # Clean image URL (remove query params that might be tracking)
                if '?' in image_url:
                    image_url = image_url.split('?')[0]

                local_image_path = await self.image_handler.download_image(
                    image_url,
                    category
                )

            # No extraer autor - siempre usar "Redacción" (sin referencias a fuentes)
            author = "Redacción"

            # Extract publish date
            date_elem = (
                soup.find('time') or
                soup.find('span', class_='date') or
                soup.find('meta', property='article:published_time')
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
            tag_elems = (
                soup.find_all('a', class_='tag') or
                soup.find_all('a', rel='tag') or
                soup.find('div', class_='tags')
            )

            if tag_elems:
                if isinstance(tag_elems[0], str):
                    # If tags container found
                    tag_links = soup.find('div', class_='tags').find_all('a')
                    tags = [TextCleaner.clean_text(self.clean_text(tag.get_text())) for tag in tag_links]
                else:
                    tags = [TextCleaner.clean_text(self.clean_text(tag.get_text())) 
                           for tag in tag_elems if tag.get_text().strip()]

            # Detectar categoría automáticamente
            detected_category = CategoryDetector.detect_category(
                url=url,
                title=title,
                content=content,
                excerpt=excerpt,
                soup=soup
            )
            
            # Usar categoría detectada o la proporcionada como fallback
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
                tags=tags[:10],  # Limit tags
                meta_description=excerpt
            )

            return article

        except Exception as e:
            self.logger.error(f"Error parsing article {url}: {e}")
            return None
