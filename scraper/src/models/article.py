"""
Data models for news articles
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field, validator
from slugify import slugify


class Article(BaseModel):
    """News article model"""

    # Identifiers
    id: Optional[str] = None
    slug: Optional[str] = None
    source: str
    source_url: HttpUrl

    # Content
    title: str
    subtitle: Optional[str] = None
    excerpt: str
    content: Optional[str] = None

    # Metadata
    category: str
    category_slug: str
    author: Optional[str] = "Redacción"
    published_at: datetime
    scraped_at: datetime = Field(default_factory=datetime.now)

    # Media
    image_url: Optional[str] = None
    local_image_path: Optional[str] = None
    images: List[str] = Field(default_factory=list)

    # Tags & Classification
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

    # Stats
    views: int = 0
    is_breaking: bool = False

    # SEO
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }

    @validator('slug', pre=True, always=True)
    def generate_slug(cls, v, values):
        """Generate slug from title if not provided"""
        if v:
            return v
        if 'title' in values:
            return slugify(values['title'])
        return None

    @validator('category_slug', pre=True, always=True)
    def generate_category_slug(cls, v, values):
        """Generate category slug if not provided"""
        if v:
            return v
        if 'category' in values:
            return slugify(values['category'])
        return None

    @validator('excerpt', pre=True, always=True)
    def generate_excerpt(cls, v, values):
        """Generate excerpt from content if not provided"""
        if v:
            return v
        if 'content' in values and values['content']:
            content = values['content']
            # Take first 200 characters
            excerpt = content[:200]
            if len(content) > 200:
                excerpt += "..."
            return excerpt
        return ""

    def to_dict(self) -> dict:
        """Convert to dictionary with URL fields as strings"""
        data = self.model_dump()

        # Convert Pydantic URL objects to strings for database compatibility
        if 'source_url' in data and data['source_url']:
            data['source_url'] = str(data['source_url'])
        if 'image_url' in data and data['image_url']:
            data['image_url'] = str(data['image_url'])

        # Ensure id and slug are generated if not present
        if not data.get('id'):
            from slugify import slugify
            import hashlib
            url_hash = hashlib.md5(str(data['source_url']).encode()).hexdigest()[:12]
            data['id'] = f"{data['source']}_{url_hash}"

        if not data.get('slug'):
            from slugify import slugify
            if data.get('title'):
                data['slug'] = slugify(data['title'])

        return data

    def to_json(self) -> str:
        """Convert to JSON string"""
        return self.model_dump_json()


class ScrapingResult(BaseModel):
    """Result of a scraping operation"""

    source: str
    success: bool
    articles_found: int
    articles_saved: int
    errors: List[str] = Field(default_factory=list)
    duration_seconds: float
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScrapingStats(BaseModel):
    """Scraping statistics"""

    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    total_articles: int = 0
    total_images: int = 0
    last_run: Optional[datetime] = None
    average_duration: float = 0.0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
