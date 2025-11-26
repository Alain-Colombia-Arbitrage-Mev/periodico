-- Migration V3: Remove authors and sources with proper FK handling
-- Date: 2025-11-15
-- Purpose: Eliminar author_id, source_url y mejorar schema

-- ============================================================
-- PARTE 1: PREPARACIÓN - Crear usuario genérico temporal
-- ============================================================

-- Crear usuario genérico si no existe (para migrar datos existentes)
DO $$
DECLARE
  generic_user_id uuid;
BEGIN
  -- Verificar si existe un usuario genérico
  SELECT id INTO generic_user_id FROM usuarios WHERE email = 'sistema@automatico.com' LIMIT 1;

  -- Si no existe, crearlo
  IF generic_user_id IS NULL THEN
    INSERT INTO usuarios (email, name, role)
    VALUES ('sistema@automatico.com', 'Sistema Automático', 'author')
    RETURNING id INTO generic_user_id;

    RAISE NOTICE 'Created generic user with id: %', generic_user_id;
  ELSE
    RAISE NOTICE 'Generic user already exists with id: %', generic_user_id;
  END IF;

  -- Actualizar todas las noticias sin autor al usuario genérico
  UPDATE noticias
  SET author_id = generic_user_id
  WHERE author_id IS NULL;

END $$;

-- ============================================================
-- PARTE 2: ELIMINAR FOREIGN KEYS y COLUMNAS
-- ============================================================

-- Eliminar constraint de author_id
ALTER TABLE noticias DROP CONSTRAINT IF EXISTS noticias_author_id_fkey;

-- Eliminar columnas
ALTER TABLE noticias DROP COLUMN IF EXISTS author_id CASCADE;
ALTER TABLE noticias DROP COLUMN IF EXISTS source_url CASCADE;

-- ============================================================
-- PARTE 3: MEJORAR COLUMNAS EXISTENTES
-- ============================================================

-- Subtitle: ya es TEXT, solo hacerla nullable
ALTER TABLE noticias ALTER COLUMN subtitle DROP NOT NULL;

-- Crear índice único en slug si no existe
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes WHERE indexname = 'noticias_slug_unique_idx'
  ) THEN
    CREATE UNIQUE INDEX noticias_slug_unique_idx ON noticias(slug);
  END IF;
END $$;

-- Agregar columnas nuevas
ALTER TABLE noticias ADD COLUMN IF NOT EXISTS keywords TEXT[];
ALTER TABLE noticias ADD COLUMN IF NOT EXISTS meta_description TEXT;

-- ============================================================
-- PARTE 4: MODIFICAR TABLA tags EXISTENTE
-- ============================================================

-- Agregar usage_count a la tabla tags si no existe
ALTER TABLE tags ADD COLUMN IF NOT EXISTS usage_count INTEGER DEFAULT 0;

-- Crear índices en tags
CREATE INDEX IF NOT EXISTS tags_name_idx ON tags(name);
CREATE INDEX IF NOT EXISTS tags_usage_count_idx ON tags(usage_count DESC);

-- ============================================================
-- PARTE 5: ÍNDICES PARA PERFORMANCE
-- ============================================================

CREATE INDEX IF NOT EXISTS noticias_published_at_idx ON noticias(published_at DESC);
CREATE INDEX IF NOT EXISTS noticias_category_id_idx ON noticias(category_id);
CREATE INDEX IF NOT EXISTS noticias_is_breaking_idx ON noticias(is_breaking) WHERE is_breaking = true;
CREATE INDEX IF NOT EXISTS noticias_source_type_idx ON noticias(source_type);
CREATE INDEX IF NOT EXISTS noticias_status_idx ON noticias(status);

-- ============================================================
-- PARTE 6: ROW LEVEL SECURITY - NOTICIAS
-- ============================================================

ALTER TABLE noticias ENABLE ROW LEVEL SECURITY;

-- Lectura pública (solo noticias publicadas)
DROP POLICY IF EXISTS "Public read access" ON noticias;
CREATE POLICY "Public read access"
  ON noticias FOR SELECT
  TO public
  USING (status = 'published');

-- Inserción pública (para scraper con anon key)
DROP POLICY IF EXISTS "Public insert access" ON noticias;
CREATE POLICY "Public insert access"
  ON noticias FOR INSERT
  TO anon
  WITH CHECK (true);

-- Inserción autenticada (para CMS)
DROP POLICY IF EXISTS "Authenticated insert access" ON noticias;
CREATE POLICY "Authenticated insert access"
  ON noticias FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Actualización autenticada
DROP POLICY IF EXISTS "Authenticated update access" ON noticias;
CREATE POLICY "Authenticated update access"
  ON noticias FOR UPDATE
  TO authenticated
  USING (true);

-- Borrado autenticado
DROP POLICY IF EXISTS "Authenticated delete access" ON noticias;
CREATE POLICY "Authenticated delete access"
  ON noticias FOR DELETE
  TO authenticated
  USING (true);

-- ============================================================
-- PARTE 7: STORAGE POLICIES (Bucket: noticias)
-- ============================================================

-- Habilitar RLS en storage.objects
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Permitir uploads públicos al bucket 'noticias'
DROP POLICY IF EXISTS "Allow public uploads" ON storage.objects;
CREATE POLICY "Allow public uploads"
  ON storage.objects FOR INSERT
  TO public
  WITH CHECK (bucket_id = 'noticias');

-- Permitir lectura pública del bucket 'noticias'
DROP POLICY IF EXISTS "Allow public downloads" ON storage.objects;
CREATE POLICY "Allow public downloads"
  ON storage.objects FOR SELECT
  TO public
  USING (bucket_id = 'noticias');

-- Permitir actualización pública (para sobrescribir imágenes)
DROP POLICY IF EXISTS "Allow public updates" ON storage.objects;
CREATE POLICY "Allow public updates"
  ON storage.objects FOR UPDATE
  TO public
  USING (bucket_id = 'noticias')
  WITH CHECK (bucket_id = 'noticias');

-- Permitir borrado autenticado
DROP POLICY IF EXISTS "Allow authenticated deletes" ON storage.objects;
CREATE POLICY "Allow authenticated deletes"
  ON storage.objects FOR DELETE
  TO authenticated
  USING (bucket_id = 'noticias');

-- ============================================================
-- PARTE 8: COMENTARIOS
-- ============================================================

COMMENT ON COLUMN noticias.subtitle IS 'Subtítulo opcional de la noticia';
COMMENT ON COLUMN noticias.slug IS 'URL-friendly identifier (único)';
COMMENT ON COLUMN noticias.source_type IS '0 = scraper automático con LLM, 1 = manual/CMS';
COMMENT ON COLUMN noticias.keywords IS 'Keywords para SEO';
COMMENT ON COLUMN noticias.meta_description IS 'Meta description para SEO';

-- ============================================================
-- PARTE 9: GRANTS
-- ============================================================

GRANT SELECT ON tags TO anon;
GRANT SELECT ON tags TO authenticated;
GRANT INSERT, UPDATE ON tags TO authenticated;

GRANT SELECT ON noticias_tags TO anon;
GRANT SELECT ON noticias_tags TO authenticated;
GRANT INSERT, UPDATE, DELETE ON noticias_tags TO authenticated;

-- ============================================================
-- PARTE 10: VISTA PÚBLICA (sin campos internos)
-- ============================================================

CREATE OR REPLACE VIEW noticias_public AS
SELECT
  n.id,
  n.title,
  n.subtitle,
  n.slug,
  n.category_id,
  c.name as category_name,
  c.slug as category_slug,
  c.color as category_color,
  n.excerpt,
  n.content,
  n.image_url,
  n.views,
  n.is_breaking,
  n.source_type,
  n.published_at,
  n.created_at,
  n.updated_at,
  n.keywords,
  n.meta_description,
  -- Tags agregados
  COALESCE(
    (
      SELECT json_agg(json_build_object('id', t.id, 'name', t.name, 'slug', t.slug))
      FROM noticias_tags nt
      JOIN tags t ON nt.tag_id = t.id
      WHERE nt.noticia_id = n.id
    ),
    '[]'::json
  ) as tags
FROM noticias n
LEFT JOIN categorias c ON n.category_id = c.id
WHERE n.status = 'published'
ORDER BY n.published_at DESC NULLS LAST;

GRANT SELECT ON noticias_public TO anon;
GRANT SELECT ON noticias_public TO authenticated;

-- ============================================================
-- PARTE 11: VERIFICACIÓN FINAL
-- ============================================================

-- Mostrar estructura actualizada
SELECT
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_name = 'noticias'
ORDER BY ordinal_position;

-- ============================================================
-- FIN DE MIGRACIÓN V3
-- ============================================================

-- Resumen de cambios:
-- ✅ Eliminado author_id y su FK
-- ✅ Eliminado source_url
-- ✅ Subtitle mejorado (nullable)
-- ✅ Agregado keywords y meta_description
-- ✅ Políticas RLS configuradas para noticias
-- ✅ Políticas Storage configuradas para bucket 'noticias'
-- ✅ Vista pública con tags agregados
-- ✅ Índices de performance creados
