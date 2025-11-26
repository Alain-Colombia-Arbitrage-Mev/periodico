#!/usr/bin/env python3
"""
Test script to verify Supabase Storage upload functionality
This validates that the bucket and policies are configured correctly
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.storage.supabase_storage import SupabaseStorage
from src.utils.image_handler import ImageHandler


async def test_storage_configuration():
    """Test storage bucket configuration and policies"""

    logger.info("=" * 60)
    logger.info("STORAGE CONFIGURATION TEST")
    logger.info("=" * 60)

    # Get credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_KEY", supabase_key)

    if not supabase_url or not supabase_key:
        logger.error("❌ Missing Supabase credentials")
        logger.info("Required environment variables:")
        logger.info("  - SUPABASE_URL")
        logger.info("  - SUPABASE_KEY (anon key)")
        logger.info("  - SUPABASE_SERVICE_KEY (optional, for service role)")
        return False

    logger.info(f"✅ Supabase URL: {supabase_url}")
    logger.info(f"✅ Using key: {'service_role' if service_key != supabase_key else 'anon'}")

    try:
        # Initialize storage
        storage = SupabaseStorage(
            supabase_url=supabase_url,
            supabase_key=service_key
        )

        # Test 1: Check bucket existence
        logger.info("\n" + "=" * 60)
        logger.info("TEST 1: Bucket Existence")
        logger.info("=" * 60)

        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{supabase_url}/storage/v1/bucket/noticias",
                headers={
                    "apikey": service_key,
                    "Authorization": f"Bearer {service_key}"
                }
            )

            if response.status_code == 200:
                bucket_info = response.json()
                logger.info(f"✅ Bucket 'noticias' exists")
                logger.info(f"   - Public: {bucket_info.get('public', False)}")
                logger.info(f"   - File size limit: {bucket_info.get('file_size_limit', 0)} bytes")
            else:
                logger.error(f"❌ Bucket 'noticias' not found: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False

        # Test 2: Test image download and upload
        logger.info("\n" + "=" * 60)
        logger.info("TEST 2: Image Download and Upload")
        logger.info("=" * 60)

        # Test image URL (La Nación)
        test_image_url = "https://www.lanacion.com.ar/resizer/v2/la-inflacion-de-diciembre-salio-por-debajo-de-IKDGWQZL5VDKZKDQLB3AIVQ2A4.jpg?auth=f123456&width=800"

        image_handler = ImageHandler(
            output_dir="data/test_images",
            supabase_url=supabase_url,
            supabase_key=service_key,
            storage_bucket="noticias"
        )

        logger.info(f"Downloading test image: {test_image_url[:60]}...")

        image_path = await image_handler.download_image(
            url=test_image_url,
            category="test"
        )

        if image_path:
            if image_path.startswith('https://'):
                logger.info(f"✅ Image uploaded to Supabase Storage!")
                logger.info(f"   URL: {image_path}")

                # Test 3: Verify image is accessible
                logger.info("\n" + "=" * 60)
                logger.info("TEST 3: Public Access Verification")
                logger.info("=" * 60)

                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(image_path)
                    if response.status_code == 200:
                        logger.info(f"✅ Image is publicly accessible")
                        logger.info(f"   Content-Type: {response.headers.get('content-type')}")
                        logger.info(f"   Size: {len(response.content)} bytes")
                    else:
                        logger.error(f"❌ Image not accessible: {response.status_code}")
                        return False
            else:
                logger.warning(f"⚠️  Image downloaded but not uploaded to Supabase")
                logger.warning(f"   Local path: {image_path}")
                return False
        else:
            logger.error(f"❌ Failed to download/upload image")
            return False

        # Test 4: Test storage policies with anon key
        logger.info("\n" + "=" * 60)
        logger.info("TEST 4: Anon Key Upload Test")
        logger.info("=" * 60)

        storage_anon = SupabaseStorage(
            supabase_url=supabase_url,
            supabase_key=supabase_key  # Use anon key
        )

        image_handler_anon = ImageHandler(
            output_dir="data/test_images",
            supabase_url=supabase_url,
            supabase_key=supabase_key,  # Use anon key
            storage_bucket="noticias"
        )

        test_image_url_2 = "https://www.clarin.com/resizer/v2/clarin-HPVUJX3QHRGOTAM5BCFNPHKXHY.jpg?auth=abc123&width=800"

        logger.info(f"Testing upload with ANON key...")
        image_path_anon = await image_handler_anon.download_image(
            url=test_image_url_2,
            category="test"
        )

        if image_path_anon and image_path_anon.startswith('https://'):
            logger.info(f"✅ Anon key can upload images!")
            logger.info(f"   This means the scraper will work correctly")
        else:
            logger.error(f"❌ Anon key CANNOT upload images")
            logger.error(f"   Check RLS policies in Supabase Dashboard")
            logger.error(f"   Run the migration: 20250120000000_setup_storage_complete.sql")
            return False

        # Success!
        logger.info("\n" + "=" * 60)
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("=" * 60)
        logger.info("✅ Bucket exists and is public")
        logger.info("✅ Images can be uploaded with service key")
        logger.info("✅ Images are publicly accessible")
        logger.info("✅ Images can be uploaded with anon key (scraper)")
        logger.info("")
        logger.info("The scraper is ready to upload images to Supabase Storage!")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Main entry point"""
    success = await test_storage_configuration()

    if success:
        logger.info("\n✅ Storage configuration is READY")
        sys.exit(0)
    else:
        logger.error("\n❌ Storage configuration has ISSUES")
        logger.info("\nTo fix:")
        logger.info("1. Run the migration: supabase/migrations/20250120000000_setup_storage_complete.sql")
        logger.info("2. Or manually configure in Supabase Dashboard:")
        logger.info("   - Create bucket 'noticias' (public)")
        logger.info("   - Add RLS policies for INSERT, SELECT, UPDATE")
        logger.info("3. Re-run this test")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
