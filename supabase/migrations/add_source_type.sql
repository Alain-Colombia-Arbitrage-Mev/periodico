-- Migration: Add source_type field to noticias table
-- Date: 2025-01-11
-- Description: Adds source_type field to differentiate between scraped (0) and manual (1) news

-- Add source_type column if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'noticias' AND column_name = 'source_type'
  ) THEN
    ALTER TABLE noticias
    ADD COLUMN source_type INTEGER NOT NULL DEFAULT 1
    CHECK (source_type IN (0, 1));

    COMMENT ON COLUMN noticias.source_type IS 'Origen de la noticia: 0=scraper automático, 1=publicación manual';
  END IF;
END $$;

-- Add source_url column if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'noticias' AND column_name = 'source_url'
  ) THEN
    ALTER TABLE noticias
    ADD COLUMN source_url TEXT;

    COMMENT ON COLUMN noticias.source_url IS 'URL de origen si la noticia proviene del scraper';
  END IF;
END $$;

-- Create indexes if they don't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE tablename = 'noticias' AND indexname = 'idx_noticias_source_type'
  ) THEN
    CREATE INDEX idx_noticias_source_type ON noticias(source_type);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE tablename = 'noticias' AND indexname = 'idx_noticias_source_url'
  ) THEN
    CREATE INDEX idx_noticias_source_url ON noticias(source_url);
  END IF;
END $$;

-- Update existing rows to have source_type = 1 (manual) by default
-- You can later update specific rows to 0 if they came from the scraper
UPDATE noticias SET source_type = 1 WHERE source_type IS NULL;

-- Success message
DO $$
BEGIN
  RAISE NOTICE 'Migration completed successfully: source_type and source_url fields added';
END $$;
