-- Schema para Política Argentina
-- Base de datos: Supabase PostgreSQL

-- ============================================
-- TABLA: usuarios
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL DEFAULT 'author' CHECK (role IN ('admin', 'editor', 'author')),
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index para búsquedas rápidas
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_role ON usuarios(role);

-- ============================================
-- TABLA: categorias
-- ============================================
CREATE TABLE IF NOT EXISTS categorias (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  color VARCHAR(50) NOT NULL DEFAULT '#3B82F6',
  icon VARCHAR(50),
  "order" INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index para búsquedas
CREATE INDEX idx_categorias_slug ON categorias(slug);

-- Datos iniciales de categorías
INSERT INTO categorias (name, slug, color, "order") VALUES
  ('Economía', 'economia', '#16A34A', 1),
  ('Política', 'politica', '#2563EB', 2),
  ('Judicial', 'judicial', '#DC2626', 3),
  ('Internacional', 'internacional', '#9333EA', 4),
  ('Sociedad', 'sociedad', '#EA580C', 5)
ON CONFLICT (slug) DO NOTHING;

-- ============================================
-- TABLA: tags
-- ============================================
CREATE TABLE IF NOT EXISTS tags (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index para búsquedas
CREATE INDEX idx_tags_slug ON tags(slug);
CREATE INDEX idx_tags_name ON tags(name);

-- ============================================
-- TABLA: noticias
-- ============================================
CREATE TABLE IF NOT EXISTS noticias (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title VARCHAR(255) NOT NULL,
  subtitle TEXT,
  slug VARCHAR(255) UNIQUE NOT NULL,
  category_id UUID NOT NULL REFERENCES categorias(id) ON DELETE RESTRICT,
  excerpt TEXT NOT NULL,
  content TEXT NOT NULL,
  image_url TEXT NOT NULL,
  author_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
  views INTEGER NOT NULL DEFAULT 0,
  status VARCHAR(50) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
  is_breaking BOOLEAN NOT NULL DEFAULT FALSE,
  source_type INTEGER NOT NULL DEFAULT 1 CHECK (source_type IN (0, 1)),
  source_url TEXT,
  published_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes para búsquedas y rendimiento
CREATE INDEX idx_noticias_slug ON noticias(slug);
CREATE INDEX idx_noticias_category ON noticias(category_id);
CREATE INDEX idx_noticias_author ON noticias(author_id);
CREATE INDEX idx_noticias_status ON noticias(status);
CREATE INDEX idx_noticias_published_at ON noticias(published_at DESC);
CREATE INDEX idx_noticias_views ON noticias(views DESC);
CREATE INDEX idx_noticias_is_breaking ON noticias(is_breaking) WHERE is_breaking = TRUE;
CREATE INDEX idx_noticias_source_type ON noticias(source_type);
CREATE INDEX idx_noticias_source_url ON noticias(source_url);

-- Full-text search index
CREATE INDEX idx_noticias_search ON noticias USING gin(to_tsvector('spanish', title || ' ' || excerpt || ' ' || content));

-- ============================================
-- TABLA: noticias_tags (relación muchos a muchos)
-- ============================================
CREATE TABLE IF NOT EXISTS noticias_tags (
  noticia_id UUID NOT NULL REFERENCES noticias(id) ON DELETE CASCADE,
  tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (noticia_id, tag_id)
);

-- Indexes
CREATE INDEX idx_noticias_tags_noticia ON noticias_tags(noticia_id);
CREATE INDEX idx_noticias_tags_tag ON noticias_tags(tag_id);

-- ============================================
-- FUNCIONES
-- ============================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para noticias
CREATE TRIGGER update_noticias_updated_at
  BEFORE UPDATE ON noticias
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Trigger para usuarios
CREATE TRIGGER update_usuarios_updated_at
  BEFORE UPDATE ON usuarios
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Función para incrementar vistas
CREATE OR REPLACE FUNCTION increment_views(noticia_id UUID)
RETURNS VOID AS $$
BEGIN
  UPDATE noticias
  SET views = views + 1
  WHERE id = noticia_id;
END;
$$ LANGUAGE plpgsql;

-- Función para generar slug automáticamente
CREATE OR REPLACE FUNCTION generate_slug(text_input TEXT)
RETURNS TEXT AS $$
DECLARE
  slug TEXT;
BEGIN
  -- Convertir a minúsculas y reemplazar espacios por guiones
  slug := LOWER(text_input);
  slug := REGEXP_REPLACE(slug, '[áàäâ]', 'a', 'g');
  slug := REGEXP_REPLACE(slug, '[éèëê]', 'e', 'g');
  slug := REGEXP_REPLACE(slug, '[íìïî]', 'i', 'g');
  slug := REGEXP_REPLACE(slug, '[óòöô]', 'o', 'g');
  slug := REGEXP_REPLACE(slug, '[úùüû]', 'u', 'g');
  slug := REGEXP_REPLACE(slug, '[ñ]', 'n', 'g');
  slug := REGEXP_REPLACE(slug, '[^a-z0-9]+', '-', 'g');
  slug := REGEXP_REPLACE(slug, '^-+|-+$', '', 'g');
  RETURN slug;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Habilitar RLS
ALTER TABLE noticias ENABLE ROW LEVEL SECURITY;
ALTER TABLE categorias ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- Políticas para noticias (lectura pública, escritura autenticada)
CREATE POLICY "Noticias públicas son visibles para todos"
  ON noticias FOR SELECT
  USING (status = 'published');

CREATE POLICY "Usuarios autenticados pueden ver todas las noticias"
  ON noticias FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "Usuarios autenticados pueden crear noticias"
  ON noticias FOR INSERT
  WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Usuarios pueden actualizar sus propias noticias"
  ON noticias FOR UPDATE
  USING (auth.uid() = author_id);

CREATE POLICY "Admins pueden actualizar cualquier noticia"
  ON noticias FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM usuarios
      WHERE usuarios.id = auth.uid()
      AND usuarios.role = 'admin'
    )
  );

-- Políticas para categorías (lectura pública)
CREATE POLICY "Categorías son visibles para todos"
  ON categorias FOR SELECT
  USING (true);

-- Políticas para tags (lectura pública)
CREATE POLICY "Tags son visibles para todos"
  ON tags FOR SELECT
  USING (true);

-- ============================================
-- VISTAS
-- ============================================

-- Vista para noticias con información completa
CREATE OR REPLACE VIEW noticias_completas AS
SELECT 
  n.*,
  c.name as category_name,
  c.slug as category_slug,
  c.color as category_color,
  u.name as author_name,
  u.email as author_email,
  u.avatar_url as author_avatar,
  ARRAY_AGG(t.name) FILTER (WHERE t.name IS NOT NULL) as tags
FROM noticias n
LEFT JOIN categorias c ON n.category_id = c.id
LEFT JOIN usuarios u ON n.author_id = u.id
LEFT JOIN noticias_tags nt ON n.id = nt.noticia_id
LEFT JOIN tags t ON nt.tag_id = t.id
GROUP BY n.id, c.name, c.slug, c.color, u.name, u.email, u.avatar_url;

-- Vista para estadísticas
CREATE OR REPLACE VIEW estadisticas_dashboard AS
SELECT
  (SELECT COUNT(*) FROM noticias) as total_noticias,
  (SELECT COUNT(*) FROM noticias WHERE status = 'published') as noticias_publicadas,
  (SELECT COUNT(*) FROM noticias WHERE status = 'draft') as noticias_borradores,
  (SELECT SUM(views) FROM noticias) as total_vistas,
  (SELECT COUNT(*) FROM usuarios) as total_usuarios,
  (SELECT COUNT(*) FROM categorias) as total_categorias,
  (SELECT COUNT(*) FROM tags) as total_tags;

-- ============================================
-- DATOS DE EJEMPLO (OPCIONAL)
-- ============================================

-- Usuario admin de ejemplo (cambiar en producción)
INSERT INTO usuarios (email, name, role) VALUES
  ('admin@politicaargentina.com', 'Admin Política Argentina', 'admin'),
  ('editor@politicaargentina.com', 'Editor Principal', 'editor'),
  ('autor@politicaargentina.com', 'Autor Redacción', 'author')
ON CONFLICT (email) DO NOTHING;

-- Tags comunes
INSERT INTO tags (name, slug) VALUES
  ('Dólar Blue', 'dolar-blue'),
  ('Economía', 'economia'),
  ('BCRA', 'bcra'),
  ('Inflación', 'inflacion'),
  ('Milei', 'milei'),
  ('Cristina Kirchner', 'cristina-kirchner'),
  ('Congreso', 'congreso'),
  ('Corte Suprema', 'corte-suprema'),
  ('Exportaciones', 'exportaciones'),
  ('Importaciones', 'importaciones')
ON CONFLICT (slug) DO NOTHING;

-- ============================================
-- COMENTARIOS Y DOCUMENTACIÓN
-- ============================================

COMMENT ON TABLE noticias IS 'Tabla principal de noticias del portal';
COMMENT ON TABLE categorias IS 'Categorías de noticias (Economía, Política, etc.)';
COMMENT ON TABLE tags IS 'Tags/etiquetas para clasificación de noticias';
COMMENT ON TABLE usuarios IS 'Usuarios del sistema (admin, editores, autores)';
COMMENT ON TABLE noticias_tags IS 'Relación muchos a muchos entre noticias y tags';

COMMENT ON COLUMN noticias.slug IS 'URL-friendly identifier generado del título';
COMMENT ON COLUMN noticias.status IS 'Estado: draft, published, archived';
COMMENT ON COLUMN noticias.is_breaking IS 'Marca si es noticia de última hora';
COMMENT ON COLUMN noticias.views IS 'Contador de visualizaciones';
COMMENT ON COLUMN noticias.source_type IS 'Origen de la noticia: 0=scraper automático, 1=publicación manual';
COMMENT ON COLUMN noticias.source_url IS 'URL de origen si la noticia proviene del scraper';

-- ============================================
-- PERMISOS
-- ============================================

-- Permisos para usuarios autenticados
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT INSERT, UPDATE, DELETE ON noticias TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Permisos para usuarios anónimos (solo lectura de noticias publicadas)
GRANT SELECT ON noticias, categorias, tags TO anon;

