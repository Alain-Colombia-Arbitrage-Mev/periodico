"""
Image download and processing utilities with Computer Vision quality validation
"""
import asyncio
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse
import aiofiles
import httpx
from PIL import Image
from loguru import logger

from .image_quality_assessor import ImageQualityAssessor


class ImageHandler:
    """Handle image downloading and processing"""

    def __init__(
        self,
        output_dir: str = "data/images",
        max_size: int = 2560,  # Increased for better quality
        quality: int = 90,  # Increased for better quality
        timeout: int = 30,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        storage_bucket: str = "noticias"
    ):
        self.output_dir = Path(output_dir)
        self.max_size = max_size
        self.quality = quality
        self.timeout = timeout
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.storage_bucket = storage_bucket
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_filename(self, url: str, category: str) -> str:
        """Generate unique filename from URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        parsed = urlparse(url)
        extension = Path(parsed.path).suffix or '.jpg'

        if extension.lower() not in ['.jpg', '.jpeg', '.png', '.webp']:
            extension = '.jpg'

        return f"{category}_{url_hash}{extension}"

    def _get_category_path(self, category: str) -> Path:
        """Get or create category directory"""
        category_path = self.output_dir / category.lower()
        category_path.mkdir(parents=True, exist_ok=True)
        return category_path

    async def _upload_to_supabase(self, local_path: Path, remote_path: str) -> Optional[str]:
        """
        Upload image to Supabase Storage

        Args:
            local_path: Local file path
            remote_path: Remote path in storage (e.g., "economia/image.jpg")

        Returns:
            Public URL of uploaded image or None if failed
        """
        if not self.supabase_url or not self.supabase_key:
            logger.debug("Supabase credentials not provided, skipping upload")
            return None

        try:
            async with aiofiles.open(local_path, 'rb') as f:
                image_data = await f.read()

            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true"  # Overwrite if exists
            }

            upload_url = f"{self.supabase_url}/storage/v1/object/{self.storage_bucket}/{remote_path}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    upload_url,
                    headers=headers,
                    content=image_data
                )

                if response.status_code in [200, 201]:
                    # Return public URL
                    public_url = f"{self.supabase_url}/storage/v1/object/public/{self.storage_bucket}/{remote_path}"
                    logger.info(f"Uploaded image to Supabase: {remote_path}")
                    return public_url
                else:
                    logger.error(f"Failed to upload image to Supabase: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error uploading image to Supabase: {e}")
            return None

    async def download_image(
        self,
        url: str,
        category: str,
        force: bool = False
    ) -> Optional[str]:
        """
        Download and process an image

        Args:
            url: Image URL
            category: Category for organization (economia, politica, etc)
            force: Force re-download even if exists

        Returns:
            Path to downloaded image or None if failed
        """
        try:
            # Generate paths
            filename = self._generate_filename(url, category)
            category_path = self._get_category_path(category)
            output_path = category_path / filename

            # Check if already exists
            if output_path.exists() and not force:
                logger.debug(f"Image already exists: {output_path}")
                return str(output_path.relative_to(self.output_dir))

            # Download image with proper headers to avoid 403 errors
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': url.split('/')[0] + '//' + url.split('/')[2],  # e.g., https://www.lanacion.com.ar
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
            }
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"Downloading image: {url}")
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()

                # Save to temporary file
                temp_path = output_path.with_suffix('.tmp')
                async with aiofiles.open(temp_path, 'wb') as f:
                    await f.write(response.content)

                # Process image
                await self._process_image(temp_path, output_path)

                # Remove temp file
                temp_path.unlink(missing_ok=True)

                logger.info(f"Image downloaded: {url} -> {output_path}")

                # ===== NEW: Computer Vision Quality Validation =====
                # Validate image quality before uploading to Supabase
                try:
                    quality_assessment = ImageQualityAssessor.comprehensive_assessment(output_path)

                    if not quality_assessment['is_acceptable']:
                        logger.warning(
                            f"Image REJECTED due to low quality: {url}\n"
                            f"  Score: {quality_assessment['overall_score']}/100\n"
                            f"  Tier: {quality_assessment['quality_tier']}\n"
                            f"  Reasons: {', '.join(quality_assessment['rejection_reasons'])}"
                        )

                        # Delete low-quality image
                        output_path.unlink(missing_ok=True)
                        return None

                    logger.info(
                        f"Image ACCEPTED - Quality score: {quality_assessment['overall_score']}/100 "
                        f"({quality_assessment['quality_tier']}) - {url}"
                    )

                except Exception as e:
                    logger.error(f"Error during quality assessment, accepting image anyway: {e}")
                    # Continue with upload if validation fails (fail-safe)
                # ===== END Quality Validation =====

                # Upload to Supabase Storage
                relative_path = str(output_path.relative_to(self.output_dir))
                supabase_url = await self._upload_to_supabase(output_path, relative_path)

                # Return Supabase URL if uploaded, otherwise local path
                if supabase_url:
                    return supabase_url
                else:
                    return relative_path

        except httpx.HTTPError as e:
            logger.error(f"HTTP error downloading image {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error downloading image {url}: {e}")
            return None

    async def _process_image(self, input_path: Path, output_path: Path) -> None:
        """Process and optimize image"""
        try:
            # Open image
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Resize if too large
                if img.width > self.max_size or img.height > self.max_size:
                    img.thumbnail((self.max_size, self.max_size), Image.Resampling.LANCZOS)

                # Save optimized
                img.save(
                    output_path,
                    format='JPEG',
                    quality=self.quality,
                    optimize=True
                )

                logger.debug(f"Image processed: {output_path}")

        except Exception as e:
            logger.error(f"Error processing image {input_path}: {e}")
            # Copy original if processing fails
            output_path.write_bytes(input_path.read_bytes())

    async def download_multiple(
        self,
        urls: list[str],
        category: str,
        max_concurrent: int = 5
    ) -> list[Optional[str]]:
        """
        Download multiple images concurrently

        Args:
            urls: List of image URLs
            category: Category for organization
            max_concurrent: Maximum concurrent downloads

        Returns:
            List of paths to downloaded images
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_with_semaphore(url: str) -> Optional[str]:
            async with semaphore:
                return await self.download_image(url, category)

        tasks = [download_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        paths = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error in concurrent download: {result}")
                paths.append(None)
            else:
                paths.append(result)

        return paths

    def get_image_info(self, path: str) -> Optional[dict]:
        """Get image information"""
        try:
            full_path = self.output_dir / path
            if not full_path.exists():
                return None

            with Image.open(full_path) as img:
                return {
                    'path': path,
                    'format': img.format,
                    'size': img.size,
                    'mode': img.mode,
                    'file_size': full_path.stat().st_size
                }
        except Exception as e:
            logger.error(f"Error getting image info for {path}: {e}")
            return None

    def cleanup_old_images(self, days: int = 30) -> int:
        """Remove images older than specified days"""
        import time
        count = 0
        current_time = time.time()
        max_age = days * 24 * 60 * 60

        for image_path in self.output_dir.rglob('*'):
            if image_path.is_file():
                age = current_time - image_path.stat().st_mtime
                if age > max_age:
                    image_path.unlink()
                    count += 1
                    logger.debug(f"Deleted old image: {image_path}")

        logger.info(f"Cleaned up {count} old images")
        return count
