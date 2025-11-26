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
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_role ON usuarios(role);

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
CREATE INDEX IF NOT EXISTS idx_categorias_slug ON categorias(slug);

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
CREATE INDEX IF NOT EXISTS idx_tags_slug ON tags(slug);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);

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
CREATE INDEX IF NOT EXISTS idx_noticias_slug ON noticias(slug);
CREATE INDEX IF NOT EXISTS idx_noticias_category ON noticias(category_id);
CREATE INDEX IF NOT EXISTS idx_noticias_author ON noticias(author_id);
CREATE INDEX IF NOT EXISTS idx_noticias_status ON noticias(status);
CREATE INDEX IF NOT EXISTS idx_noticias_published_at ON noticias(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_noticias_views ON noticias(views DESC);
CREATE INDEX IF NOT EXISTS idx_noticias_is_breaking ON noticias(is_breaking) WHERE is_breaking = TRUE;
CREATE INDEX IF NOT EXISTS idx_noticias_source_type ON noticias(source_type);
CREATE INDEX IF NOT EXISTS idx_noticias_source_url ON noticias(source_url);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_noticias_search ON noticias USING gin(to_tsvector('spanish', title || ' ' || excerpt || ' ' || content));

-- ============================================
-- TABLA: noticias_tags (relación muchos a muchos)
-- ============================================
CREATE TABLE IF NOT EXISTS noticias_tags (
  noticia_id UUID NOT NULL REFERENCES noticias(id) ON DELETE CASCADE,
  tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (noticia_id, tag_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_noticias_tags_noticia ON noticias_tags(noticia_id);
CREATE INDEX IF NOT EXISTS idx_noticias_tags_tag ON noticias_tags(tag_id);

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
DROP TRIGGER IF EXISTS update_noticias_updated_at ON noticias;
CREATE TRIGGER update_noticias_updated_at
  BEFORE UPDATE ON noticias
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Trigger para usuarios
DROP TRIGGER IF EXISTS update_usuarios_updated_at ON usuarios;
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
