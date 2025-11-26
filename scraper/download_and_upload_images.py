"""
Script para descargar imágenes externas y subirlas a Supabase Storage
Actualiza todas las noticias existentes
"""
import os
import asyncio
import httpx
import aiofiles
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from loguru import logger
from src.storage.supabase_storage import SupabaseStorage
from src.utils.image_handler import ImageHandler

load_dotenv()

async def download_and_upload_image(image_url: str, category_slug: str, storage: SupabaseStorage, image_handler: ImageHandler) -> str:
    """Descargar imagen externa y subirla a Supabase Storage"""
    try:
        # Verificar si ya está en Supabase Storage
        if "supabase.co/storage/v1/object/public/article-images" in image_url:
            logger.debug(f"✅ Imagen ya en Supabase Storage: {image_url}")
            return image_url
        
        # Descargar imagen
        logger.info(f"📥 Descargando imagen: {image_url[:80]}...")
        local_path = await image_handler.download_image(image_url, category_slug)
        
        if not local_path:
            logger.warning(f"⚠️  No se pudo descargar imagen: {image_url}")
            return image_url  # Retornar URL original si falla
        
        # Resolver ruta completa
        if not Path(local_path).is_absolute():
            full_path = Path("data/images") / local_path
        else:
            full_path = Path(local_path)
        
        if not full_path.exists():
            logger.warning(f"⚠️  Archivo descargado no encontrado: {full_path}")
            return image_url
        
        # Subir a Supabase Storage
        logger.info(f"📤 Subiendo a Supabase Storage: {full_path.name}")
        remote_path = f"{category_slug}/{full_path.name}"
        supabase_url = await storage.upload_image(str(full_path.resolve()), remote_path)
        
        if supabase_url:
            logger.success(f"✅ Imagen subida: {supabase_url}")
            return supabase_url
        else:
            logger.warning(f"⚠️  No se pudo subir a Supabase, usando URL original")
            return image_url
            
    except Exception as e:
        logger.error(f"❌ Error procesando imagen: {e}")
        return image_url

async def update_all_news_images():
    """Actualizar todas las noticias descargando y subiendo imágenes a Supabase"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL y SUPABASE_KEY requeridos")
        return
    
    storage = SupabaseStorage(supabase_url, supabase_key)
    image_handler = ImageHandler(
        output_dir="data/images",
        max_size=2048,
        quality=85
    )
    
    logger.info("📰 Obteniendo todas las noticias...")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            }
            
            # Obtener todas las noticias
            response = await client.get(
                f"{supabase_url}/rest/v1/noticias?select=id,title,image_url,category_id",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error obteniendo noticias: {response.status_code}")
                return
            
            noticias = response.json()
            logger.info(f"📰 Encontradas {len(noticias)} noticias para actualizar")
            
            if not noticias:
                logger.info("✅ No hay noticias para actualizar")
                return
            
            # Obtener mapeo de categorías
            cat_response = await client.get(
                f"{supabase_url}/rest/v1/categorias?select=id,slug",
                headers=headers
            )
            category_map = {}
            if cat_response.status_code == 200:
                for cat in cat_response.json():
                    category_map[cat["id"]] = cat["slug"]
            
            updated = 0
            skipped = 0
            errors = 0
            
            for noticia in noticias:
                try:
                    noticia_id = noticia["id"]
                    current_image_url = noticia.get("image_url", "")
                    category_id = noticia.get("category_id")
                    
                    if not current_image_url:
                        logger.warning(f"⚠️  Sin imagen: {noticia['title'][:50]}...")
                        skipped += 1
                        continue
                    
                    # Verificar si ya está en Supabase Storage
                    if "supabase.co/storage/v1/object/public/article-images" in current_image_url:
                        logger.debug(f"✅ Ya en Supabase: {noticia['title'][:50]}...")
                        skipped += 1
                        continue
                    
                    # Obtener slug de categoría
                    category_slug = category_map.get(category_id, "politica")
                    
                    # Descargar y subir imagen
                    logger.info(f"🔄 Procesando: {noticia['title'][:50]}...")
                    new_image_url = await download_and_upload_image(
                        current_image_url,
                        category_slug,
                        storage,
                        image_handler
                    )
                    
                    # Actualizar noticia si la URL cambió
                    if new_image_url != current_image_url:
                        update_response = await client.patch(
                            f"{supabase_url}/rest/v1/noticias?id=eq.{noticia_id}",
                            headers=headers,
                            json={"image_url": new_image_url}
                        )
                        
                        if update_response.status_code in [200, 204]:
                            logger.success(f"✅ Actualizada: {noticia['title'][:50]}...")
                            updated += 1
                        else:
                            logger.error(f"❌ Error actualizando: {update_response.status_code}")
                            errors += 1
                    else:
                        skipped += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error procesando noticia '{noticia.get('title', 'Unknown')}': {e}")
                    errors += 1
                    continue
            
            logger.success(f"✅ Proceso completado:")
            logger.info(f"   - Actualizadas: {updated}")
            logger.info(f"   - Omitidas: {skipped}")
            logger.info(f"   - Errores: {errors}")
            
    except Exception as e:
        logger.error(f"❌ Error general: {e}")

async def main():
    """Ejecutar actualización"""
    logger.info("🚀 Iniciando descarga y subida de imágenes a Supabase Storage...")
    logger.warning("⚠️  Asegúrate de que el bucket 'article-images' esté creado en Supabase")
    
    await update_all_news_images()
    
    logger.success("✅ Proceso completado")

if __name__ == "__main__":
    asyncio.run(main())









