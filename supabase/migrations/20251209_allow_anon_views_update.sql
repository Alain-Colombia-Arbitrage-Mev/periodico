-- Migration: Allow anonymous users to update views count
-- Date: 2025-12-09
-- Purpose: Permitir que usuarios anónimos incrementen el contador de vistas

-- Crear política para permitir UPDATE de vistas por usuarios anónimos
DROP POLICY IF EXISTS "Allow anon views update" ON noticias;

CREATE POLICY "Allow anon views update"
  ON noticias FOR UPDATE
  TO anon
  USING (true)
  WITH CHECK (true);

-- Alternativa más segura: función RPC con permisos SECURITY DEFINER
-- Esto ejecuta con permisos del owner de la función, no del usuario

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

-- Dar permiso a anon para ejecutar la función
GRANT EXECUTE ON FUNCTION public.increment_views(UUID) TO anon;
GRANT EXECUTE ON FUNCTION public.increment_views(UUID) TO authenticated;

-- Verificar
DO $$
BEGIN
  RAISE NOTICE '✅ Política de vistas para usuarios anónimos creada';
  RAISE NOTICE '✅ Función increment_views actualizada con SECURITY DEFINER';
END $$;
