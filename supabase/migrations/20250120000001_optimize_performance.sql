-- ============================================================
-- PERFORMANCE OPTIMIZATION MIGRATION
-- Date: 2025-01-20
-- Purpose: Add indexes and optimize queries for better performance
-- ============================================================

-- ============================================================
-- STEP 1: OPTIMIZE NOTICIAS TABLE INDEXES
-- ============================================================

-- Drop existing indexes if they exist (to recreate with better configuration)
DROP INDEX IF EXISTS idx_noticias_slug;
DROP INDEX IF EXISTS idx_noticias_category;
DROP INDEX IF EXISTS idx_noticias_author;
DROP INDEX IF EXISTS idx_noticias_status;
DROP INDEX IF EXISTS idx_noticias_published_at;
DROP INDEX IF EXISTS idx_noticias_views;
DROP INDEX IF EXISTS idx_noticias_is_breaking;
DROP INDEX IF EXISTS idx_noticias_source_type;
DROP INDEX IF EXISTS idx_noticias_source_url;
DROP INDEX IF EXISTS idx_noticias_search;

-- Create optimized indexes with better names and configurations
CREATE INDEX IF NOT EXISTS noticias_slug_idx ON noticias(slug) WHERE status = 'published';
CREATE INDEX IF NOT EXISTS noticias_category_published_idx ON noticias(category_id, published_at DESC) WHERE status = 'published';
CREATE INDEX IF NOT EXISTS noticias_status_published_at_idx ON noticias(status, published_at DESC);
CREATE INDEX IF NOT EXISTS noticias_breaking_published_idx ON noticias(is_breaking, published_at DESC) WHERE is_breaking = TRUE AND status = 'published';
CREATE INDEX IF NOT EXISTS noticias_views_idx ON noticias(views DESC) WHERE status = 'published';
CREATE INDEX IF NOT EXISTS noticias_source_url_idx ON noticias(source_url) WHERE source_url IS NOT NULL;
CREATE INDEX IF NOT EXISTS noticias_source_type_idx ON noticias(source_type, published_at DESC);

-- Full-text search index for Spanish content
CREATE INDEX IF NOT EXISTS noticias_fts_idx ON noticias
  USING gin(to_tsvector('spanish', coalesce(title, '') || ' ' || coalesce(excerpt, '') || ' ' || coalesce(content, '')));

-- ============================================================
-- STEP 2: ADD MATERIALIZED VIEW FOR ANALYTICS
-- ============================================================

-- Drop existing view if exists
DROP MATERIALIZED VIEW IF EXISTS noticias_stats_mv;

-- Create materialized view for fast analytics
CREATE MATERIALIZED VIEW noticias_stats_mv AS
SELECT
  c.slug as category_slug,
  c.name as category_name,
  COUNT(*) as total_articles,
  COUNT(*) FILTER (WHERE n.status = 'published') as published_articles,
  COUNT(*) FILTER (WHERE n.is_breaking = TRUE) as breaking_news,
  SUM(n.views) as total_views,
  AVG(n.views) as avg_views,
  MAX(n.published_at) as latest_article_date,
  COUNT(*) FILTER (WHERE n.source_type = 0) as scraped_articles,
  COUNT(*) FILTER (WHERE n.source_type = 1) as manual_articles
FROM noticias n
JOIN categorias c ON n.category_id = c.id
GROUP BY c.slug, c.name;

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS noticias_stats_mv_category_idx ON noticias_stats_mv(category_slug);

-- ============================================================
-- STEP 3: CREATE FUNCTION TO REFRESH STATS
-- ============================================================

CREATE OR REPLACE FUNCTION refresh_noticias_stats()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY noticias_stats_mv;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- STEP 4: OPTIMIZE CATEGORIAS TABLE
-- ============================================================

CREATE INDEX IF NOT EXISTS categorias_slug_idx ON categorias(slug);
CREATE INDEX IF NOT EXISTS categorias_order_idx ON categorias("order");

-- ============================================================
-- STEP 5: OPTIMIZE TAGS TABLE
-- ============================================================

CREATE INDEX IF NOT EXISTS tags_slug_idx ON tags(slug);
CREATE INDEX IF NOT EXISTS tags_name_idx ON tags(name);

-- Create index on junction table
CREATE INDEX IF NOT EXISTS noticias_tags_noticia_idx ON noticias_tags(noticia_id);
CREATE INDEX IF NOT EXISTS noticias_tags_tag_idx ON noticias_tags(tag_id);
CREATE INDEX IF NOT EXISTS noticias_tags_combined_idx ON noticias_tags(noticia_id, tag_id);

-- ============================================================
-- STEP 6: CREATE OPTIMIZED VIEWS
-- ============================================================

-- Drop existing view
DROP VIEW IF EXISTS noticias_completas;

-- Create optimized view with better performance
CREATE OR REPLACE VIEW noticias_completas AS
SELECT
  n.id,
  n.title,
  n.subtitle,
  n.slug,
  n.excerpt,
  n.content,
  n.image_url,
  n.views,
  n.status,
  n.is_breaking,
  n.source_type,
  n.source_url,
  n.published_at,
  n.created_at,
  n.updated_at,
  c.id as category_id,
  c.name as category_name,
  c.slug as category_slug,
  c.color as category_color,
  u.id as author_id,
  u.name as author_name,
  u.email as author_email,
  u.avatar_url as author_avatar,
  COALESCE(
    (
      SELECT json_agg(json_build_object('id', t.id, 'name', t.name, 'slug', t.slug))
      FROM tags t
      INNER JOIN noticias_tags nt ON t.id = nt.tag_id
      WHERE nt.noticia_id = n.id
    ),
    '[]'::json
  ) as tags
FROM noticias n
LEFT JOIN categorias c ON n.category_id = c.id
LEFT JOIN usuarios u ON n.author_id = u.id;

-- ============================================================
-- STEP 7: CREATE UTILITY FUNCTIONS
-- ============================================================

-- Function to get related articles
CREATE OR REPLACE FUNCTION get_related_articles(
  p_noticia_id UUID,
  p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
  id UUID,
  title VARCHAR(255),
  slug VARCHAR(255),
  excerpt TEXT,
  image_url TEXT,
  category_name VARCHAR(100),
  published_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT DISTINCT
    n.id,
    n.title,
    n.slug,
    n.excerpt,
    n.image_url,
    c.name as category_name,
    n.published_at
  FROM noticias n
  JOIN categorias c ON n.category_id = c.id
  WHERE n.status = 'published'
    AND n.id != p_noticia_id
    AND n.category_id = (
      SELECT category_id FROM noticias WHERE id = p_noticia_id
    )
  ORDER BY n.published_at DESC
  LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to get trending articles
CREATE OR REPLACE FUNCTION get_trending_articles(
  p_hours INTEGER DEFAULT 24,
  p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
  id UUID,
  title VARCHAR(255),
  slug VARCHAR(255),
  excerpt TEXT,
  image_url TEXT,
  views INTEGER,
  category_name VARCHAR(100),
  published_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    n.id,
    n.title,
    n.slug,
    n.excerpt,
    n.image_url,
    n.views,
    c.name as category_name,
    n.published_at
  FROM noticias n
  JOIN categorias c ON n.category_id = c.id
  WHERE n.status = 'published'
    AND n.published_at > NOW() - (p_hours || ' hours')::INTERVAL
  ORDER BY n.views DESC, n.published_at DESC
  LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================
-- STEP 8: ADD PARTITIONING PREPARATION (FUTURE-PROOF)
-- ============================================================

-- Add comments for future partitioning strategy
COMMENT ON TABLE noticias IS 'Main news table. Consider partitioning by published_at (monthly) when data exceeds 1M rows';

-- ============================================================
-- STEP 9: OPTIMIZE VACUUM AND ANALYZE SETTINGS
-- ============================================================

-- Set autovacuum settings for noticias table (high-traffic table)
ALTER TABLE noticias SET (
  autovacuum_vacuum_scale_factor = 0.01,
  autovacuum_analyze_scale_factor = 0.005
);

-- ============================================================
-- STEP 10: VERIFICATION AND REPORTING
-- ============================================================

DO $$
DECLARE
  index_count INTEGER;
  view_count INTEGER;
  function_count INTEGER;
BEGIN
  -- Count indexes
  SELECT COUNT(*) INTO index_count
  FROM pg_indexes
  WHERE schemaname = 'public'
    AND tablename IN ('noticias', 'categorias', 'tags', 'noticias_tags');

  -- Count views
  SELECT COUNT(*) INTO view_count
  FROM pg_views
  WHERE schemaname = 'public'
    AND viewname LIKE 'noticias_%';

  -- Count functions
  SELECT COUNT(*) INTO function_count
  FROM pg_proc
  WHERE proname IN ('get_related_articles', 'get_trending_articles', 'refresh_noticias_stats');

  RAISE NOTICE '==========================================';
  RAISE NOTICE 'PERFORMANCE OPTIMIZATION REPORT';
  RAISE NOTICE '==========================================';
  RAISE NOTICE 'Indexes created: %', index_count;
  RAISE NOTICE 'Views created: %', view_count;
  RAISE NOTICE 'Functions created: %', function_count;
  RAISE NOTICE '==========================================';

  IF index_count >= 10 AND view_count >= 1 AND function_count = 3 THEN
    RAISE NOTICE '✅ Performance optimization COMPLETE';
  ELSE
    RAISE WARNING '⚠️  Some optimizations may be missing';
  END IF;
END $$;

-- ============================================================
-- END OF MIGRATION
-- ============================================================
