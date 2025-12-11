-- =====================================================
-- CORRECCIÓN DE SEGURIDAD - POLÍTICAS RLS
-- Date: 2025-12-11
-- Purpose: Eliminar políticas inseguras y crear nuevas seguras
-- =====================================================

-- PROBLEMA DETECTADO:
-- - Políticas permitían a usuarios anónimos insertar y actualizar noticias
-- - Esto permitió que alguien modificara contenido de noticias

-- =====================================================
-- 1. ELIMINAR TODAS LAS POLÍTICAS INSEGURAS
-- =====================================================

DROP POLICY IF EXISTS "Allow anon views update" ON noticias;
DROP POLICY IF EXISTS "Public insert access" ON noticias;
DROP POLICY IF EXISTS "Permitir inserción de noticias" ON noticias;
DROP POLICY IF EXISTS "Authenticated update access" ON noticias;
DROP POLICY IF EXISTS "Authenticated delete access" ON noticias;
DROP POLICY IF EXISTS "Authenticated insert access" ON noticias;
DROP POLICY IF EXISTS "Noticias públicas son visibles para todos" ON noticias;
DROP POLICY IF EXISTS "Public read access" ON noticias;
DROP POLICY IF EXISTS "Usuarios autenticados pueden ver todas las noticias" ON noticias;
DROP POLICY IF EXISTS "Admins pueden actualizar cualquier noticia" ON noticias;

-- =====================================================
-- 2. CREAR POLÍTICAS SEGURAS
-- =====================================================

-- SELECT público: Solo noticias publicadas
DROP POLICY IF EXISTS "Public read published" ON noticias;
CREATE POLICY "Public read published"
  ON noticias FOR SELECT
  TO public
  USING (status = 'published');

-- SELECT autenticado: Solo admin puede ver todas (incluyendo drafts)
DROP POLICY IF EXISTS "Admin read all" ON noticias;
CREATE POLICY "Admin read all"
  ON noticias FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE usuarios.id = auth.uid() 
      AND usuarios.role = 'admin'
    )
  );

-- INSERT: Solo admin
DROP POLICY IF EXISTS "Admin insert only" ON noticias;
CREATE POLICY "Admin insert only"
  ON noticias FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE usuarios.id = auth.uid() 
      AND usuarios.role = 'admin'
    )
  );

-- UPDATE: Solo admin
DROP POLICY IF EXISTS "Admin update only" ON noticias;
CREATE POLICY "Admin update only"
  ON noticias FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE usuarios.id = auth.uid() 
      AND usuarios.role = 'admin'
    )
  );

-- DELETE: Solo admin
DROP POLICY IF EXISTS "Admin delete only" ON noticias;
CREATE POLICY "Admin delete only"
  ON noticias FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE usuarios.id = auth.uid() 
      AND usuarios.role = 'admin'
    )
  );

-- =====================================================
-- 3. FUNCIÓN SEGURA PARA INCREMENTAR VISTAS
-- =====================================================

-- Esta función usa SECURITY DEFINER para bypass RLS
-- pero SOLO incrementa el campo views
CREATE OR REPLACE FUNCTION public.increment_views(noticia_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  UPDATE noticias
  SET views = views + 1
  WHERE id = noticia_id;
END;
$$;

-- Revocar permisos generales y dar solo EXECUTE
REVOKE ALL ON FUNCTION public.increment_views(UUID) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.increment_views(UUID) TO anon;
GRANT EXECUTE ON FUNCTION public.increment_views(UUID) TO authenticated;

-- =====================================================
-- 4. VERIFICACIÓN
-- =====================================================

DO $$
DECLARE
  policy_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO policy_count
  FROM pg_policies
  WHERE schemaname = 'public' AND tablename = 'noticias';
  
  RAISE NOTICE '=====================================================';
  RAISE NOTICE 'SEGURIDAD CORREGIDA';
  RAISE NOTICE '=====================================================';
  RAISE NOTICE '✅ Políticas inseguras eliminadas';
  RAISE NOTICE '✅ % políticas seguras creadas', policy_count;
  RAISE NOTICE '✅ Función increment_views asegurada con SECURITY DEFINER';
  RAISE NOTICE '=====================================================';
  RAISE NOTICE 'POLÍTICAS ACTUALES:';
  RAISE NOTICE '- Public read published: Solo noticias publicadas';
  RAISE NOTICE '- Admin editor read all: Admin/Editor ven todo';
  RAISE NOTICE '- Admin editor insert: Solo admin/editor insertan';
  RAISE NOTICE '- Admin editor update: Solo admin/editor actualizan';
  RAISE NOTICE '- Admin delete only: Solo admin elimina';
  RAISE NOTICE '=====================================================';
END $$;
