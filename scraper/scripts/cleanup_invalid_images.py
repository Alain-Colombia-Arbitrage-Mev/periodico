#!/usr/bin/env python3
"""
Script to identify and remove articles with invalid images (logos, placeholders, etc.)
from the Supabase database.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.image_validator import ImageValidator
from src.storage.supabase_storage import SupabaseStorage
from loguru import logger


async def cleanup_invalid_images():
    """Find and delete articles with invalid images"""

    logger.info("Starting cleanup of articles with invalid images...")

    # Initialize Supabase storage
    storage = SupabaseStorage()

    # Get all scraped articles (source_type=0)
    logger.info("Fetching all scraped articles from database...")

    try:
        import httpx

        supabase_url = os.getenv("SUPABASE_URL")
        service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not service_role_key:
            logger.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
            return

        async with httpx.AsyncClient() as client:
            # Fetch all scraped articles with their images
            response = await client.get(
                f"{supabase_url}/rest/v1/noticias",
                params={
                    "source_type": "eq.0",  # Only scraped articles
                    "select": "id,title,image_url,source"
                },
                headers={
                    "apikey": service_role_key,
                    "Authorization": f"Bearer {service_role_key}"
                }
            )

            if response.status_code != 200:
                logger.error(f"Failed to fetch articles: {response.text}")
                return

            articles = response.json()
            logger.info(f"Found {len(articles)} scraped articles to check")

            # Check each article's image
            invalid_article_ids = []

            for article in articles:
                article_id = article.get('id')
                image_url = article.get('image_url')
                title = article.get('title', '')[:60]
                source = article.get('source', '')

                # Determine source domain
                source_domain = ''
                if 'infobae' in source.lower():
                    source_domain = 'infobae.com'
                elif 'nación' in source.lower() or 'nacion' in source.lower():
                    source_domain = 'lanacion.com.ar'
                elif 'clarín' in source.lower() or 'clarin' in source.lower():
                    source_domain = 'clarin.com'

                # Check if image is valid
                if not image_url:
                    logger.warning(f"Article {article_id} has no image: {title}")
                    invalid_article_ids.append(article_id)
                elif not ImageValidator.is_valid_article_image(image_url, source_domain):
                    logger.warning(f"Article {article_id} has invalid image: {title}")
                    logger.debug(f"  Invalid image URL: {image_url[:100]}")
                    invalid_article_ids.append(article_id)

            logger.info(f"Found {len(invalid_article_ids)} articles with invalid/missing images")

            if not invalid_article_ids:
                logger.info("No articles to delete. All images are valid!")
                return

            # Ask for confirmation
            print(f"\n{'='*60}")
            print(f"ABOUT TO DELETE {len(invalid_article_ids)} ARTICLES WITH INVALID IMAGES")
            print(f"{'='*60}")
            confirmation = input("Type 'DELETE' to confirm deletion: ")

            if confirmation != "DELETE":
                logger.info("Deletion cancelled by user")
                return

            # Delete articles in batches
            batch_size = 100
            deleted_count = 0

            for i in range(0, len(invalid_article_ids), batch_size):
                batch = invalid_article_ids[i:i+batch_size]

                # Delete batch
                delete_response = await client.delete(
                    f"{supabase_url}/rest/v1/noticias",
                    params={"id": f"in.({','.join(map(str, batch))})"},
                    headers={
                        "apikey": service_role_key,
                        "Authorization": f"Bearer {service_role_key}",
                        "Prefer": "return=minimal"
                    }
                )

                if delete_response.status_code in [200, 204]:
                    deleted_count += len(batch)
                    logger.info(f"Deleted batch {i//batch_size + 1}: {len(batch)} articles (total: {deleted_count})")
                else:
                    logger.error(f"Failed to delete batch: {delete_response.text}")

            logger.success(f"✅ Successfully deleted {deleted_count} articles with invalid images!")

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    asyncio.run(cleanup_invalid_images())
