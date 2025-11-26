-- Database initialization script
-- This script is automatically run when the PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create articles table (will be created by SQLAlchemy, this is backup)
CREATE TABLE IF NOT EXISTS articles (
    id VARCHAR(100) PRIMARY KEY,
    slug VARCHAR(255) UNIQUE NOT NULL,
    source VARCHAR(50) NOT NULL,
    source_url VARCHAR(500) UNIQUE NOT NULL,

    -- Content
    title VARCHAR(500) NOT NULL,
    subtitle TEXT,
    excerpt TEXT NOT NULL,
    content TEXT,

    -- Metadata
    category VARCHAR(50) NOT NULL,
    category_slug VARCHAR(50) NOT NULL,
    author VARCHAR(200),
    published_at TIMESTAMP NOT NULL,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Media
    image_url VARCHAR(500),
    local_image_path VARCHAR(255),
    images JSONB,

    -- Tags
    tags JSONB,
    keywords JSONB,

    -- Stats
    views INTEGER DEFAULT 0,
    is_breaking BOOLEAN DEFAULT FALSE,

    -- SEO
    meta_description TEXT,
    meta_keywords TEXT,

    -- Timestamps
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_category_slug ON articles(category_slug);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_scraped_at ON articles(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_is_breaking ON articles(is_breaking) WHERE is_breaking = TRUE;

-- Create full-text search index
CREATE INDEX IF NOT EXISTS idx_articles_title_search ON articles USING gin(to_tsvector('spanish', title));
CREATE INDEX IF NOT EXISTS idx_articles_content_search ON articles USING gin(to_tsvector('spanish', content));

-- Create trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create scraping_stats table for monitoring
CREATE TABLE IF NOT EXISTS scraping_stats (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    category VARCHAR(50),
    articles_found INTEGER DEFAULT 0,
    articles_saved INTEGER DEFAULT 0,
    errors TEXT[],
    duration_seconds FLOAT,
    success BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_scraping_stats_source ON scraping_stats(source);
CREATE INDEX IF NOT EXISTS idx_scraping_stats_created_at ON scraping_stats(created_at DESC);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO scraper;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO scraper;

-- Insert sample data (optional)
-- You can remove this section if you don't want sample data

COMMENT ON TABLE articles IS 'Stores scraped news articles from various sources';
COMMENT ON TABLE scraping_stats IS 'Tracks scraping operations performance and results';
