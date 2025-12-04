#!/usr/bin/env python3
"""
Reset database and storage, then run the scraper
"""
import os
import sys
from pathlib import Path

# Load environment variables
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    print(f"Loading environment from {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value.strip()

from supabase import create_client

def main():
    # Initialize Supabase
    supabase_url = os.getenv('SUPABASE_URL') or os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        sys.exit(1)

    supabase = create_client(supabase_url, supabase_key)
    bucket_name = 'noticias'

    print("=" * 60)
    print("RESET: Deleting all news and images")
    print("=" * 60)

    # 1. Delete all articles from database
    print("\n1. Deleting all articles from database...")
    try:
        # First get all article IDs
        articles = supabase.table('noticias').select('id').execute()
        if articles.data:
            for article in articles.data:
                supabase.table('noticias').delete().eq('id', article['id']).execute()
            print(f"   Deleted {len(articles.data)} articles from database")
        else:
            print("   No articles to delete")
    except Exception as e:
        print(f"   Error deleting articles: {e}")

    # 2. Delete all images from storage
    print("\n2. Deleting all images from storage...")
    try:
        # List all files in the bucket
        files = supabase.storage.from_(bucket_name).list('articles')
        if files:
            file_paths = [f"articles/{f['name']}" for f in files]
            if file_paths:
                supabase.storage.from_(bucket_name).remove(file_paths)
                print(f"   Deleted {len(file_paths)} images from storage")
            else:
                print("   No images found in storage")
        else:
            print("   No files in storage bucket")
    except Exception as e:
        print(f"   Error deleting images: {e}")

    print("\n" + "=" * 60)
    print("RESET COMPLETE - Starting scraper...")
    print("=" * 60 + "\n")

    # 3. Run the pipeline
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    from pipeline_complete import main as run_pipeline
    import asyncio

    return asyncio.run(run_pipeline())

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
