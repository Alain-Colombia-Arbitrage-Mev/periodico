-- ============================================================
-- COMPLETE STORAGE SETUP FOR NOTICIAS BUCKET
-- Date: 2025-01-20
-- Purpose: Create bucket and configure RLS policies for image uploads
-- ============================================================

-- ============================================================
-- STEP 1: CREATE BUCKET IF NOT EXISTS
-- ============================================================

DO $$
BEGIN
  -- Insert bucket if it doesn't exist
  INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
  VALUES (
    'noticias',
    'noticias',
    true,  -- Public bucket
    5242880,  -- 5MB limit
    ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/jpg']
  )
  ON CONFLICT (id) DO UPDATE SET
    public = true,
    file_size_limit = 5242880,
    allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];

  RAISE NOTICE '✅ Bucket "noticias" created/updated successfully';
END $$;

-- ============================================================
-- STEP 2: ENABLE RLS ON STORAGE.OBJECTS
-- ============================================================

ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 3: DROP EXISTING POLICIES (CLEAN SLATE)
-- ============================================================

DROP POLICY IF EXISTS "Allow public uploads" ON storage.objects;
DROP POLICY IF EXISTS "Allow public downloads" ON storage.objects;
DROP POLICY IF EXISTS "Allow public updates" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated deletes" ON storage.objects;
DROP POLICY IF EXISTS "Public Access" ON storage.objects;
DROP POLICY IF EXISTS "anon insert noticias" ON storage.objects;
DROP POLICY IF EXISTS "noticias_bucket_public_insert" ON storage.objects;
DROP POLICY IF EXISTS "noticias_bucket_public_select" ON storage.objects;
DROP POLICY IF EXISTS "noticias_bucket_public_update" ON storage.objects;
DROP POLICY IF EXISTS "noticias_bucket_authenticated_delete" ON storage.objects;

-- ============================================================
-- STEP 4: CREATE OPTIMIZED RLS POLICIES
-- ============================================================

-- Policy 1: INSERT - Allow public uploads to noticias bucket
-- This allows the scraper to upload images using the anon key
CREATE POLICY "noticias_public_insert"
  ON storage.objects FOR INSERT
  TO public
  WITH CHECK (bucket_id = 'noticias');

-- Policy 2: SELECT - Allow public reads from noticias bucket
-- This allows images to be publicly accessible
CREATE POLICY "noticias_public_select"
  ON storage.objects FOR SELECT
  TO public
  USING (bucket_id = 'noticias');

-- Policy 3: UPDATE - Allow public updates (for upsert operations)
CREATE POLICY "noticias_public_update"
  ON storage.objects FOR UPDATE
  TO public
  USING (bucket_id = 'noticias')
  WITH CHECK (bucket_id = 'noticias');

-- Policy 4: DELETE - Allow authenticated users to delete
CREATE POLICY "noticias_authenticated_delete"
  ON storage.objects FOR DELETE
  TO authenticated
  USING (bucket_id = 'noticias');

-- ============================================================
-- STEP 5: VERIFICATION
-- ============================================================

DO $$
DECLARE
  policy_count INTEGER;
  bucket_exists BOOLEAN;
  bucket_is_public BOOLEAN;
BEGIN
  -- Check policies
  SELECT COUNT(*) INTO policy_count
  FROM pg_policies
  WHERE schemaname = 'storage'
    AND tablename = 'objects'
    AND policyname LIKE 'noticias_%';

  -- Check bucket
  SELECT EXISTS(
    SELECT 1 FROM storage.buckets WHERE name = 'noticias'
  ) INTO bucket_exists;

  SELECT public INTO bucket_is_public
  FROM storage.buckets
  WHERE name = 'noticias';

  -- Report results
  RAISE NOTICE '==========================================';
  RAISE NOTICE 'STORAGE SETUP VERIFICATION';
  RAISE NOTICE '==========================================';

  IF bucket_exists THEN
    RAISE NOTICE '✅ Bucket "noticias" exists';
  ELSE
    RAISE WARNING '❌ Bucket "noticias" does NOT exist';
  END IF;

  IF bucket_is_public THEN
    RAISE NOTICE '✅ Bucket is PUBLIC';
  ELSE
    RAISE WARNING '❌ Bucket is PRIVATE (should be public)';
  END IF;

  IF policy_count >= 4 THEN
    RAISE NOTICE '✅ All % RLS policies configured', policy_count;
  ELSE
    RAISE WARNING '❌ Only % policies found (expected 4)', policy_count;
  END IF;

  RAISE NOTICE '==========================================';

  -- Overall status
  IF bucket_exists AND bucket_is_public AND policy_count >= 4 THEN
    RAISE NOTICE '🎉 Storage setup COMPLETE and READY';
  ELSE
    RAISE WARNING '⚠️  Storage setup INCOMPLETE - manual intervention needed';
  END IF;
END $$;

-- ============================================================
-- STEP 6: GRANT PERMISSIONS
-- ============================================================

-- Grant storage permissions to anon role
GRANT SELECT, INSERT, UPDATE ON storage.objects TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON storage.objects TO authenticated;
GRANT SELECT ON storage.buckets TO anon;
GRANT SELECT ON storage.buckets TO authenticated;

-- ============================================================
-- END OF MIGRATION
-- ============================================================
