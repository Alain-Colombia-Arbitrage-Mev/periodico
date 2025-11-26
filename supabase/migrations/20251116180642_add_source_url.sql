-- Add source_url column to noticias table
ALTER TABLE noticias ADD COLUMN IF NOT EXISTS source_url TEXT;

-- Create index for faster lookups when checking duplicates
CREATE INDEX IF NOT EXISTS idx_noticias_source_url ON noticias(source_url);

-- Add comment
COMMENT ON COLUMN noticias.source_url IS 'Original URL from the news source (used for duplicate detection)';
