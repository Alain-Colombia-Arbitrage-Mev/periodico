-- Migration: Fix Storage RLS Policies for bucket 'noticias'
-- Date: 2025-11-15
-- Purpose: Corregir políticas RLS para permitir subida de imágenes desde el scraper

-- ============================================================
-- PARTE 1: HABILITAR RLS EN STORAGE.OBJECTS
-- ============================================================

ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- PARTE 2: ELIMINAR POLÍTICAS EXISTENTES (para recrearlas correctamente)
-- ============================================================

-- Eliminar políticas públicas existentes
DROP POLICY IF EXISTS "Allow public uploads" ON storage.objects;
DROP POLICY IF EXISTS "Allow public downloads" ON storage.objects;
DROP POLICY IF EXISTS "Allow public updates" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated deletes" ON storage.objects;

-- ============================================================
-- PARTE 3: CREAR POLÍTICAS CORRECTAS PARA BUCKET 'noticias'
-- ============================================================

-- Policy 1: INSERT - Permitir subida pública (anon y authenticated)
-- Esto permite que el scraper suba imágenes usando la anon key
CREATE POLICY "Allow public uploads"
  ON storage.objects FOR INSERT
  TO public
  WITH CHECK (bucket_id = 'noticias');

-- Policy 2: SELECT - Permitir lectura pública
-- Esto permite que las imágenes sean accesibles públicamente
CREATE POLICY "Allow public downloads"
  ON storage.objects FOR SELECT
  TO public
  USING (bucket_id = 'noticias');

-- Policy 3: UPDATE - Permitir actualización pública (para sobrescribir imágenes)
CREATE POLICY "Allow public updates"
  ON storage.objects FOR UPDATE
  TO public
  USING (bucket_id = 'noticias')
  WITH CHECK (bucket_id = 'noticias');

-- Policy 4: DELETE - Permitir borrado solo para usuarios autenticados
CREATE POLICY "Allow authenticated deletes"
  ON storage.objects FOR DELETE
  TO authenticated
  USING (bucket_id = 'noticias');

-- ============================================================
-- PARTE 4: VERIFICACIÓN
-- ============================================================

-- Verificar que las políticas están activas
DO $$
DECLARE
  policy_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO policy_count
  FROM pg_policies
  WHERE schemaname = 'storage'
    AND tablename = 'objects'
    AND policyname IN (
      'Allow public uploads',
      'Allow public downloads',
      'Allow public updates',
      'Allow authenticated deletes'
    );

  IF policy_count = 4 THEN
    RAISE NOTICE '✅ Todas las políticas de Storage están configuradas correctamente';
  ELSE
    RAISE WARNING '⚠️  Solo se encontraron % políticas de las 4 esperadas', policy_count;
  END IF;
END $$;

-- ============================================================
-- PARTE 5: VERIFICAR QUE EL BUCKET ES PÚBLICO
-- ============================================================

DO $$
DECLARE
  bucket_public BOOLEAN;
BEGIN
  SELECT public INTO bucket_public
  FROM storage.buckets
  WHERE name = 'noticias';

  IF bucket_public THEN
    RAISE NOTICE '✅ El bucket "noticias" es público';
  ELSE
    RAISE WARNING '⚠️  El bucket "noticias" NO es público. Debes marcarlo como público en el Dashboard';
  END IF;
END $$;

-- ============================================================
-- FIN DE MIGRACIÓN
-- ============================================================







