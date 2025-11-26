"""
Supabase storage - Reemplaza PostgreSQL y Redis
Almacena noticias directamente en Supabase
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import httpx
from loguru import logger


class SupabaseStorage:
    """Storage manager usando solo Supabase (reemplaza Database + Cache)"""

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        storage_bucket: str = "noticias"  # Bucket de Supabase Storage
    ):
        self.supabase_url = supabase_url.rstrip('/')
        self.supabase_key = supabase_key
        self.storage_bucket = storage_bucket
        self.timeout = 30

        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

        logger.info(f"SupabaseStorage initialized: {self.supabase_url}")

    async def _get_category_id(self, category_slug: str) -> Optional[str]:
        """Obtener ID de categoría por slug"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/categorias?slug=eq.{category_slug}&select=id",
                    headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    if data:
                        return data[0]["id"]
                return None

        except Exception as e:
            logger.error(f"Error getting category ID: {e}")
            return None

    async def _get_or_create_author(self, author_name: str = "Redacción") -> Optional[str]:
        """Obtener o crear autor para noticias del scraper"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Buscar autor existente
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/usuarios?email=eq.scraper@politicaargentina.com&select=id",
                    headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    if data:
                        return data[0]["id"]

                # Crear autor si no existe (siempre "Redacción")
                author_data = {
                    "email": "scraper@politicaargentina.com",
                    "name": "Redacción",  # Siempre "Redacción", sin referencias a fuentes
                    "role": "author"
                }

                response = await client.post(
                    f"{self.supabase_url}/rest/v1/usuarios",
                    headers=self.headers,
                    json=author_data
                )

                if response.status_code in [200, 201]:
                    data = response.json()
                    if isinstance(data, list) and data:
                        return data[0]["id"]
                    elif isinstance(data, dict):
                        return data["id"]
                return None

        except Exception as e:
            logger.error(f"Error getting/creating author: {e}")
            return None

    async def save_article(self, article_data: dict) -> bool:
        """
        Guardar o actualizar artículo en Supabase

        Args:
            article_data: Diccionario con datos del artículo

        Returns:
            True si fue exitoso
        """
        try:
            # Obtener IDs necesarios
            category_id = await self._get_category_id(article_data.get("category_slug", ""))
            if not category_id:
                logger.error(f"Category not found: {article_data.get('category_slug')}")
                return False

            # Obtener o crear autor (requerido por el schema)
            author_id = await self._get_or_create_author("Redacción")
            if not author_id:
                logger.error(f"Failed to get or create author")
                return False

            # Convertir published_at a ISO string si es datetime
            published_at = article_data.get("published_at")
            if published_at and isinstance(published_at, datetime):
                published_at = published_at.isoformat()
            elif published_at is None:
                published_at = datetime.now().isoformat()

            # Preparar datos para Supabase (formato noticias)
            # source_type: 0x00 (0) = scraper + LLM, 0x01 (1) = manual
            supabase_data = {
                "title": article_data["title"],
                "subtitle": article_data.get("subtitle"),
                "slug": article_data["slug"],
                "category_id": category_id,
                "author_id": author_id,  # REQUERIDO por el schema
                "excerpt": article_data["excerpt"],
                "content": article_data.get("content", ""),
                "image_url": article_data.get("image_url", ""),
                "views": article_data.get("views", 0),
                "status": "published",  # Noticias del scraper se publican automáticamente
                "is_breaking": article_data.get("is_breaking", False),
                "source_type": 0,  # 0x00 = scraper automático con LLM rewriting
                "source_url": article_data.get("source_url", ""),  # URL original del artículo
                "published_at": published_at
            }

            # Insertar nuevo artículo (ya verificamos duplicados antes de llamar a save_article)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Crear nuevo artículo
                insert_response = await client.post(
                    f"{self.supabase_url}/rest/v1/noticias",
                    headers=self.headers,
                    json=supabase_data
                )
                
                if insert_response.status_code in [200, 201]:
                    logger.info(f"✅ Created article: {article_data['title'][:50]}... (source_type: 0x00)")
                    return True
                else:
                    # Si falla por duplicado, intentar actualizar
                    if insert_response.status_code == 409 or 'duplicate' in str(insert_response.text).lower():
                        logger.debug(f"Article exists, updating: {article_data['title'][:50]}...")
                        update_response = await client.patch(
                            f"{self.supabase_url}/rest/v1/noticias?slug=eq.{article_data['slug']}",
                            headers=self.headers,
                            json=supabase_data
                        )
                        if update_response.status_code in [200, 204]:
                            logger.debug(f"Updated article: {article_data['title'][:50]}...")
                            return True

                logger.error(f"Failed to save article: {article_data['title'][:50]}... Status: {insert_response.status_code}, Response: {insert_response.text}")
                return False

        except Exception as e:
            logger.error(f"Error saving article to Supabase: {e}")
            return False

    async def save_articles(self, articles_data: List[dict]) -> int:
        """
        Guardar múltiples artículos

        Args:
            articles_data: Lista de diccionarios de artículos

        Returns:
            Número de artículos guardados
        """
        saved = 0

        for article_data in articles_data:
            if await self.save_article(article_data):
                saved += 1

        logger.info(f"Saved {saved}/{len(articles_data)} articles to Supabase")
        return saved

    async def article_exists(self, slug: str) -> bool:
        """Verificar si artículo existe por slug (DEPRECATED - usar article_exists_by_source_url)"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/noticias?slug=eq.{slug}&select=id",
                    headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    return len(data) > 0
                return False

        except Exception as e:
            logger.error(f"Error checking article existence: {e}")
            return False

    async def article_exists_by_source_url(self, source_url: str) -> bool:
        """
        Verificar si artículo existe por source_url (URL original).
        Este es el método CORRECTO para evitar duplicados cuando el LLM genera títulos diferentes.
        """
        try:
            if not source_url:
                return False

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/noticias?source_url=eq.{source_url}&select=id",
                    headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    exists = len(data) > 0
                    if exists:
                        logger.debug(f"Article already exists with source_url: {source_url[:60]}...")
                    return exists
                return False

        except Exception as e:
            logger.error(f"Error checking article existence by source_url: {e}")
            return False

    async def article_exists_by_slug(self, slug: str) -> bool:
        """Verificar si artículo existe por slug"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/noticias?slug=eq.{slug}&select=id",
                    headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    return len(data) > 0
                return False

        except Exception as e:
            logger.error(f"Error checking article existence by slug: {e}")
            return False

    async def get_articles_by_category(
        self,
        category_slug: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """Obtener artículos por categoría"""
        try:
            # Primero obtener category_id
            category_id = await self._get_category_id(category_slug)
            if not category_id:
                return []

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/noticias?category_id=eq.{category_id}&status=eq.published&order=published_at.desc&limit={limit}&offset={offset}",
                    headers=self.headers
                )

                if response.status_code == 200:
                    return response.json()
                return []

        except Exception as e:
            logger.error(f"Error getting articles by category: {e}")
            return []

    async def get_recent_articles(self, limit: int = 50) -> List[dict]:
        """Obtener artículos más recientes"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/noticias?status=eq.published&order=published_at.desc&limit={limit}",
                    headers=self.headers
                )

                if response.status_code == 200:
                    return response.json()
                return []

        except Exception as e:
            logger.error(f"Error getting recent articles: {e}")
            return []

    async def get_breaking_news(self, limit: int = 10) -> List[dict]:
        """Obtener noticias de última hora"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/noticias?is_breaking=eq.true&status=eq.published&order=published_at.desc&limit={limit}",
                    headers=self.headers
                )

                if response.status_code == 200:
                    return response.json()
                return []

        except Exception as e:
            logger.error(f"Error getting breaking news: {e}")
            return []

    async def get_stats(self) -> dict:
        """Obtener estadísticas de Supabase"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Total de artículos
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/noticias?select=count",
                    headers={**self.headers, "Prefer": "count=exact"}
                )

                total = 0
                if response.status_code == 200:
                    content_range = response.headers.get("Content-Range", "")
                    if "/" in content_range:
                        total = int(content_range.split("/")[1])

                # Por categoría
                by_category = {}
                categories = ["economia", "politica", "sociedad", "internacional", "judicial"]

                for category_slug in categories:
                    category_id = await self._get_category_id(category_slug)
                    if category_id:
                        response = await client.get(
                            f"{self.supabase_url}/rest/v1/noticias?category_id=eq.{category_id}&select=count",
                            headers={**self.headers, "Prefer": "count=exact"}
                        )

                        if response.status_code == 200:
                            content_range = response.headers.get("Content-Range", "")
                            if "/" in content_range:
                                count = int(content_range.split("/")[1])
                                by_category[category_slug] = count

                return {
                    "total_articles": total,
                    "by_category": by_category
                }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_articles": 0, "by_category": {}}

    async def cleanup_old_articles(self, days: int = 90) -> int:
        """Eliminar artículos más antiguos que X días"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.supabase_url}/rest/v1/noticias?published_at=lt.{cutoff_date}",
                    headers=self.headers
                )

                if response.status_code == 204:
                    logger.info(f"Cleaned up articles older than {days} days")
                    return 0  # Supabase no devuelve count en delete
                return 0

        except Exception as e:
            logger.error(f"Error cleaning up: {e}")
            return 0

    async def delete_recent_scraped_articles(self, days: int = 3) -> int:
        """
        Eliminar artículos scraped (source_type=0) de los últimos X días
        Esto limpia las noticias antiguas antes de scrapear nuevas
        """
        try:
            # Calcular fecha límite (ahora - X días)
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Primero obtener los IDs de artículos a eliminar
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/noticias?source_type=eq.0&published_at=gte.{cutoff_date}&select=id",
                    headers=self.headers
                )

                if response.status_code == 200:
                    articles = response.json()
                    if not articles:
                        logger.info(f"No scraped articles from last {days} days to delete")
                        return 0

                    # Eliminar por source_type=0 y fecha >= cutoff
                    delete_response = await client.delete(
                        f"{self.supabase_url}/rest/v1/noticias?source_type=eq.0&published_at=gte.{cutoff_date}",
                        headers=self.headers
                    )

                    if delete_response.status_code == 204:
                        count = len(articles)
                        logger.info(f"Deleted {count} scraped articles from last {days} days")
                        return count

                return 0

        except Exception as e:
            logger.error(f"Error deleting recent scraped articles: {e}")
            return 0

    # Métodos de cache usando Supabase (opcional, para compatibilidad)
    async def cache_get(self, key: str) -> Optional[Any]:
        """Obtener del cache (usando tabla temporal en Supabase o simplemente retornar None)"""
        # Para simplificar, no implementamos cache en Supabase
        # El cache se puede manejar en memoria si es necesario
        return None

    async def cache_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Guardar en cache"""
        # No implementado - usar cache en memoria si es necesario
        return True

    async def cache_delete(self, key: str) -> bool:
        """Eliminar del cache"""
        return True

    async def upload_image(
        self,
        local_path: str,
        remote_path: str = None
    ) -> Optional[str]:
        """
        Upload image to Supabase Storage

        Args:
            local_path: Local image path (absolute or relative to data/images/)
            remote_path: Remote path in bucket (optional, auto-generated if not provided)

        Returns:
            Public URL of uploaded image or None
        """
        try:
            import aiofiles
            from pathlib import Path

            # Resolve full path
            if not Path(local_path).is_absolute():
                full_path = Path("data/images") / local_path
            else:
                full_path = Path(local_path)

            if not full_path.exists():
                logger.warning(f"Image file not found: {full_path}")
                return None

            # Generate remote path if not provided
            if not remote_path:
                remote_path = f"{full_path.parent.name}/{full_path.name}"

            # Read image file
            async with aiofiles.open(full_path, 'rb') as f:
                image_data = await f.read()

            # Upload to Supabase Storage
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                upload_url = f"{self.supabase_url}/storage/v1/object/{self.storage_bucket}/{remote_path}"

                response = await client.post(
                    upload_url,
                    headers={
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                        "Content-Type": "image/jpeg",
                        "x-upsert": "true"  # Overwrite if exists
                    },
                    content=image_data
                )

                if response.status_code in [200, 201]:
                    # Return public URL
                    public_url = f"{self.supabase_url}/storage/v1/object/public/{self.storage_bucket}/{remote_path}"
                    logger.info(f"Uploaded image to Supabase: {remote_path}")
                    return public_url
                else:
                    logger.error(f"Failed to upload image: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error uploading image to Supabase: {e}")
            return None

    async def delete_all_articles(self) -> int:
        """Delete all articles from Supabase"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # First get all article IDs
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/noticias?select=id",
                    headers={**self.headers, "Prefer": "count=exact"}
                )

                if response.status_code == 200:
                    articles = response.json()
                    if not articles:
                        logger.info("No articles to delete")
                        return 0

                    # Delete in batches
                    deleted = 0
                    for article in articles:
                        delete_response = await client.delete(
                            f"{self.supabase_url}/rest/v1/noticias?id=eq.{article['id']}",
                            headers=self.headers
                        )
                        if delete_response.status_code == 204:
                            deleted += 1

                    logger.info(f"Deleted {deleted} articles from Supabase")
                    return deleted
                else:
                    logger.error(f"Failed to get articles: {response.status_code} - {response.text}")
                    return 0

        except Exception as e:
            logger.error(f"Error deleting all articles: {e}")
            return 0

