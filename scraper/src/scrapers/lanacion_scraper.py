"""
La Nación scraper implementation
"""
from typing import List, Optional
from datetime import datetime
from ..models.article import Article
from .base_scraper import BaseScraper
from ..utils.category_detector import CategoryDetector
from ..utils.text_cleaner import TextCleaner
from ..utils.image_validator import ImageValidator


class LaNacionScraper(BaseScraper):
    """Scraper for LaNacion.com.ar"""

    def __init__(self, image_handler, headless: bool = True):
        super().__init__(
            source_name="La Nación",
            base_url="https://www.lanacion.com.ar",
            image_handler=image_handler,
            headless=headless
        )

        # Category mappings
        self.category_urls = {
            "economia": "/economia",
            "politica": "/politica",
            "sociedad": "/sociedad",
            "internacional": "/el-mundo",
        }

    async def scrape_listing(self, category: str, max_articles: int = 20) -> List[str]:
        """Scrape article URLs from category page"""
        category_path = self.category_urls.get(category.lower(), f"/{category}")
        url = f"{self.base_url}{category_path}"

        html = await self.fetch_page(url, wait_for="article")
        if not html:
            return []

        soup = self.parse_html(html)
        article_urls = []

        # Find article links
        articles = soup.find_all('article', limit=max_articles * 2)

        for article in articles:
            if len(article_urls) >= max_articles:
                break

            link = (
                article.find('h2', class_='titulo').find('a') if article.find('h2', class_='titulo') else None or
                article.find('a', class_='title-link') or
                article.find('a', href=True)
            )

            if link and link.get('href'):
                href = link['href']

                # Make absolute URL
                if href.startswith('/'):
                    href = self.base_url + href
                elif not href.startswith('http'):
                    continue

                # Filter valid articles
                if (href not in article_urls and
                    'lanacion.com.ar' in href and
                    '/amp/' not in href):
                    article_urls.append(href)

        self.logger.info(f"Found {len(article_urls)} articles in {category}")
        return article_urls

    async def scrape_article(self, url: str, category: str) -> Optional[Article]:
        """Scrape individual article from La Nación"""
        html = await self.fetch_page(url)
        if not html:
            return None

        soup = self.parse_html(html)

        try:
            # Extract title
            title_elem = (
                soup.find('h1', class_='title') or
                soup.find('h1', id='titulo') or
                soup.find('h1')
            )
            title_raw = title_elem.get_text() if title_elem else None
            title = TextCleaner.clean_title(self.clean_text(title_raw)) if title_raw else None

            if not title:
                self.logger.warning(f"No title found for {url}")
                return None

            # Extract subtitle/bajada
            subtitle_elem = (
                soup.find('h2', class_='subtitle') or
                soup.find('h2', class_='bajada') or
                soup.find('p', class_='bajada')
            )
            subtitle_raw = subtitle_elem.get_text() if subtitle_elem else None
            subtitle = TextCleaner.clean_text(self.clean_text(subtitle_raw)) if subtitle_raw else None

            # Extract content
            content_elem = (
                soup.find('section', class_='article-body') or
                soup.find('div', class_='article-content') or
                soup.find('div', id='cuerpo')
            )

            content = ""
            if content_elem:
                paragraphs = content_elem.find_all('p')
                content_raw = "\n\n".join(
                    p.get_text()
                    for p in paragraphs
                    if (p.get_text().strip() and
                        not p.find_parent('figcaption') and
                        'Relacionadas' not in p.get_text())
                )
                content = TextCleaner.clean_content(self.clean_text(content_raw))

            # Extract excerpt
            excerpt = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                excerpt_raw = meta_desc['content']
                excerpt = TextCleaner.clean_text(self.clean_text(excerpt_raw))
            elif subtitle:
                excerpt = subtitle
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
                soup.find('figure', class_='photo-article') or
                soup.find('div', class_='image-container')
            )

            if img_elem:
                img = img_elem.find('img')
                if img:
                    src = (
                        img.get('data-src') or
                        img.get('src') or
                        img.get('data-original')
                    )
                    if src:
                        image_candidates.append(src)

            # Try all images in article content
            if content_elem:
                for img in content_elem.find_all('img'):
                    src = img.get('data-src') or img.get('src') or img.get('data-original')
                    if src and src not in image_candidates:
                        image_candidates.append(src)

            # Validate and select best image
            image_url = ImageValidator.get_best_image(image_candidates, 'lanacion.com.ar')

            if not image_url:
                self.logger.warning(f"No valid article image found for {url}")

            # Download image
            local_image_path = None
            if image_url:
                # Clean image URL
                if '?' in image_url:
                    base_url = image_url.split('?')[0]
                    # Keep image transformations but remove tracking
                    if any(x in image_url for x in ['width', 'height', 'quality']):
                        image_url = base_url + '?' + '&'.join(
                            p for p in image_url.split('?')[1].split('&')
                            if any(x in p for x in ['width', 'height', 'quality'])
                        )
                    else:
                        image_url = base_url

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

            # Extract tags/keywords
            tags = []

            # Try meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and meta_keywords.get('content'):
                keywords_str = meta_keywords['content']
                tags = [TextCleaner.clean_text(k.strip()) 
                       for k in keywords_str.split(',') if k.strip()][:10]

            # Try tag links
            if not tags:
                tag_elems = (
                    soup.find_all('a', class_='tag') or
                    soup.find_all('a', rel='tag')
                )
                tags = [TextCleaner.clean_text(self.clean_text(tag.get_text())) 
                       for tag in tag_elems if tag.get_text().strip()][:10]

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
                tags=tags,
                keywords=tags,
                meta_description=excerpt
            )

            return article

        except Exception as e:
            self.logger.error(f"Error parsing article {url}: {e}")
            return None
