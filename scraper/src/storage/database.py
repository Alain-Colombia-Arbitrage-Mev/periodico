"""
Database storage for scraped articles
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Text, Integer, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

Base = declarative_base()


class ArticleDB(Base):
    """Article database model"""
    __tablename__ = 'articles'

    id = Column(String(100), primary_key=True)
    slug = Column(String(255), unique=True, index=True)
    source = Column(String(50), index=True)
    source_url = Column(String(500), unique=True)

    # Content
    title = Column(String(500))
    subtitle = Column(Text, nullable=True)
    excerpt = Column(Text)
    content = Column(Text, nullable=True)

    # Metadata
    category = Column(String(50), index=True)
    category_slug = Column(String(50), index=True)
    author = Column(String(200))
    published_at = Column(DateTime, index=True)
    scraped_at = Column(DateTime, default=datetime.now)

    # Media
    image_url = Column(String(500), nullable=True)
    local_image_path = Column(String(255), nullable=True)
    images = Column(JSON, nullable=True)

    # Tags
    tags = Column(JSON, nullable=True)
    keywords = Column(JSON, nullable=True)

    # Stats
    views = Column(Integer, default=0)
    is_breaking = Column(Boolean, default=False)

    # Source type: 0=scraper, 1=manual
    source_type = Column(Integer, default=0, index=True)

    # SEO
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(Text, nullable=True)

    # Timestamps
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Database:
    """Database manager for articles"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info(f"Database initialized: {database_url.split('@')[-1]}")

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    def save_article(self, article_data: dict, session: Optional[Session] = None) -> bool:
        """
        Save or update article in database

        Args:
            article_data: Article dictionary
            session: Optional existing session

        Returns:
            True if successful
        """
        close_session = False
        if session is None:
            session = self.get_session()
            close_session = True

        try:
            # Check if article exists
            existing = session.query(ArticleDB).filter_by(
                source_url=article_data['source_url']
            ).first()

            if existing:
                # Update existing article
                for key, value in article_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                logger.debug(f"Updated article: {article_data['title'][:50]}...")
            else:
                # Create new article
                article = ArticleDB(**article_data)
                session.add(article)
                logger.debug(f"Created article: {article_data['title'][:50]}...")

            session.commit()
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving article: {e}")
            return False

        finally:
            if close_session:
                session.close()

    def save_articles(self, articles_data: List[dict]) -> int:
        """
        Save multiple articles

        Args:
            articles_data: List of article dictionaries

        Returns:
            Number of articles saved
        """
        session = self.get_session()
        saved = 0

        try:
            for article_data in articles_data:
                if self.save_article(article_data, session):
                    saved += 1

            logger.info(f"Saved {saved}/{len(articles_data)} articles to database")
            return saved

        finally:
            session.close()

    def get_article(self, article_id: str) -> Optional[dict]:
        """Get article by ID"""
        session = self.get_session()

        try:
            article = session.query(ArticleDB).filter_by(id=article_id).first()
            if article:
                return self._article_to_dict(article)
            return None

        finally:
            session.close()

    def get_articles_by_category(
        self,
        category: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """Get articles by category"""
        session = self.get_session()

        try:
            articles = (
                session.query(ArticleDB)
                .filter_by(category_slug=category)
                .order_by(ArticleDB.published_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

            return [self._article_to_dict(a) for a in articles]

        finally:
            session.close()

    def get_recent_articles(self, limit: int = 50) -> List[dict]:
        """Get most recent articles"""
        session = self.get_session()

        try:
            articles = (
                session.query(ArticleDB)
                .order_by(ArticleDB.published_at.desc())
                .limit(limit)
                .all()
            )

            return [self._article_to_dict(a) for a in articles]

        finally:
            session.close()

    def get_breaking_news(self, limit: int = 10) -> List[dict]:
        """Get breaking news articles"""
        session = self.get_session()

        try:
            articles = (
                session.query(ArticleDB)
                .filter_by(is_breaking=True)
                .order_by(ArticleDB.published_at.desc())
                .limit(limit)
                .all()
            )

            return [self._article_to_dict(a) for a in articles]

        finally:
            session.close()

    def article_exists(self, source_url: str) -> bool:
        """Check if article exists by URL"""
        session = self.get_session()

        try:
            exists = (
                session.query(ArticleDB)
                .filter_by(source_url=source_url)
                .first()
            ) is not None

            return exists

        finally:
            session.close()

    def get_stats(self) -> dict:
        """Get database statistics"""
        session = self.get_session()

        try:
            total = session.query(ArticleDB).count()

            by_category = {}
            categories = session.query(ArticleDB.category_slug).distinct().all()

            for (category,) in categories:
                count = session.query(ArticleDB).filter_by(category_slug=category).count()
                by_category[category] = count

            by_source = {}
            sources = session.query(ArticleDB.source).distinct().all()

            for (source,) in sources:
                count = session.query(ArticleDB).filter_by(source=source).count()
                by_source[source] = count

            return {
                'total_articles': total,
                'by_category': by_category,
                'by_source': by_source
            }

        finally:
            session.close()

    def cleanup_old_articles(self, days: int = 90) -> int:
        """Delete articles older than specified days"""
        session = self.get_session()

        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)

            deleted = (
                session.query(ArticleDB)
                .filter(ArticleDB.published_at < cutoff_date)
                .delete()
            )

            session.commit()
            logger.info(f"Deleted {deleted} old articles")
            return deleted

        except Exception as e:
            session.rollback()
            logger.error(f"Error cleaning up old articles: {e}")
            return 0

        finally:
            session.close()

    def _article_to_dict(self, article: ArticleDB) -> dict:
        """Convert article model to dictionary"""
        return {
            'id': article.id,
            'slug': article.slug,
            'source': article.source,
            'source_url': article.source_url,
            'title': article.title,
            'subtitle': article.subtitle,
            'excerpt': article.excerpt,
            'content': article.content,
            'category': article.category,
            'category_slug': article.category_slug,
            'author': article.author,
            'published_at': article.published_at.isoformat() if article.published_at else None,
            'scraped_at': article.scraped_at.isoformat() if article.scraped_at else None,
            'image_url': article.image_url,
            'local_image_path': article.local_image_path,
            'images': article.images or [],
            'tags': article.tags or [],
            'keywords': article.keywords or [],
            'views': article.views,
            'is_breaking': article.is_breaking,
            'source_type': article.source_type,
            'meta_description': article.meta_description,
            'meta_keywords': article.meta_keywords
        }
