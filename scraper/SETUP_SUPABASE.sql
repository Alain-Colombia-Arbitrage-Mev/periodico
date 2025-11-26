-- ============================================
-- SETUP SUPABASE PARA SCRAPER DE NOTICIAS
-- ============================================
-- Ejecuta este script en: Supabase Dashboard > SQL Editor
-- ============================================

-- 1. Crear tabla de artículos
CREATE TABLE IF NOT EXISTS articles (
  id TEXT PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,

  -- Contenido
  title TEXT NOT NULL,
  subtitle TEXT,
  excerpt TEXT NOT NULL,
  content TEXT,

  -- Clasificación
  category TEXT NOT NULL,
  category_slug TEXT NOT NULL,

  -- Autoría
  author TEXT,
  source TEXT NOT NULL,
  source_url TEXT UNIQUE NOT NULL,

  -- Fechas
  published_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Media
  image_url TEXT,
  tags JSONB DEFAULT '[]'::jsonb,

  -- Métricas
  is_breaking BOOLEAN DEFAULT false,
  views INTEGER DEFAULT 0
);

-- 2. Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category_slug);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_breaking ON articles(is_breaking) WHERE is_breaking = true;
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);

-- 3. Full-text search en español (opcional pero recomendado)
CREATE INDEX IF NOT EXISTS idx_articles_search
ON articles USING gin(to_tsvector('spanish', title || ' ' || COALESCE(content, '')));

-- 4. Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5. Trigger para updated_at
DROP TRIGGER IF EXISTS articles_updated_at ON articles;
CREATE TRIGGER articles_updated_at
BEFORE UPDATE ON articles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

-- 6. Política RLS (Row Level Security) - Permitir lectura pública
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- Permitir a todos leer
CREATE POLICY "Allow public read access"
ON articles FOR SELECT
TO anon, authenticated
USING (true);

-- Permitir a autenticados insertar/actualizar
CREATE POLICY "Allow authenticated insert/update"
ON articles FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Allow authenticated update"
ON articles FOR UPDATE
TO authenticated
USING (true);

-- 7. Comentarios para documentación
COMMENT ON TABLE articles IS 'Artículos de noticias scrapeados y reescritos con IA';
COMMENT ON COLUMN articles.slug IS 'URL-friendly identifier';
COMMENT ON COLUMN articles.category_slug IS 'categoria en minúsculas: economia, politica, sociedad, internacional';
COMMENT ON COLUMN articles.source IS 'Fuente original: Infobae, Clarín, La Nación';
COMMENT ON COLUMN articles.is_breaking IS 'Si es noticia de última hora';

-- ============================================
-- QUERIES ÚTILES (copiar para usar)
-- ============================================

-- Ver total de artículos
-- SELECT COUNT(*) FROM articles;

-- Por categoría
-- SELECT category, COUNT(*) as total FROM articles GROUP BY category ORDER BY total DESC;

-- Últimos 10 artículos
-- SELECT title, source, published_at FROM articles ORDER BY published_at DESC LIMIT 10;

-- Breaking news
-- SELECT title, published_at FROM articles WHERE is_breaking = true ORDER BY published_at DESC;

-- Buscar por texto
-- SELECT title, excerpt FROM articles
-- WHERE to_tsvector('spanish', title || ' ' || COALESCE(content, '')) @@ to_tsquery('spanish', 'economía');

-- ============================================
-- DONE! ✅
-- ============================================
-- Ahora crea el bucket en Storage:
-- 1. Ve a Storage en el menú lateral
-- 2. Create bucket: "article-images"
-- 3. Marca como "Public bucket"
-- 4. Create bucket
-- ============================================
