"""
Script para actualizar noticias existentes subiendo imágenes al bucket de Supabase Storage
Ejecutar después de crear el bucket manualmente
"""
import os
import asyncio
import httpx
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from src.storage.supabase_storage import SupabaseStorage

load_dotenv()

async def update_news_with_images():
    """Actualizar noticias existentes subiendo imágenes al bucket"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL y SUPABASE_KEY requeridos")
        return
    
    storage = SupabaseStorage(supabase_url, supabase_key)
    
    logger.info("📰 Obteniendo noticias para actualizar...")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            }
            
            # Obtener todas las noticias con source_type = 0
            response = await client.get(
                f"{supabase_url}/rest/v1/noticias?source_type=eq.0&select=id,title,slug,image_url,source_url,category_id",
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
                    
                    # Verificar si la imagen ya está en Supabase Storage
                    if current_image_url and "storage/v1/object/public/article-images" in current_image_url:
                        logger.debug(f"✅ Imagen ya en Supabase: {noticia['title'][:50]}...")
                        skipped += 1
                        continue
                    
                    # Obtener slug de categoría
                    category_slug = category_map.get(category_id, "politica")
                    
                    # Buscar imagen local
                    images_dir = Path("data/images")
                    category_dir = images_dir / category_slug
                    
                    image_path = None
                    
                    if category_dir.exists():
                        # Buscar imágenes en la carpeta de la categoría
                        for ext in ["*.png", "*.jpg", "*.jpeg"]:
                            images = list(category_dir.glob(ext))
                            if images:
                                # Usar la imagen más reciente o la primera
                                image_path = max(images, key=lambda p: p.stat().st_mtime) if images else images[0]
                                break
                    
                    if not image_path or not image_path.exists():
                        logger.warning(f"⚠️  Imagen local no encontrada para: {noticia['title'][:50]}...")
                        errors += 1
                        continue
                    
                    # Subir imagen a Supabase Storage
                    logger.info(f"📤 Subiendo imagen para: {noticia['title'][:50]}...")
                    remote_path = f"{category_slug}/{image_path.name}"
                    
                    # Pasar ruta absoluta para evitar duplicación
                    abs_image_path = str(image_path.resolve())
                    new_image_url = await storage.upload_image(abs_image_path, remote_path)
                    
                    if new_image_url:
                        # Actualizar noticia con nueva URL
                        update_response = await client.patch(
                            f"{supabase_url}/rest/v1/noticias?id=eq.{noticia_id}",
                            headers=headers,
                            json={"image_url": new_image_url}
                        )
                        
                        if update_response.status_code in [200, 204]:
                            logger.success(f"✅ Actualizada: {noticia['title'][:50]}...")
                            updated += 1
                        else:
                            logger.error(f"❌ Error actualizando noticia: {update_response.status_code}")
                            errors += 1
                    else:
                        logger.warning(f"⚠️  No se pudo subir imagen para: {noticia['title'][:50]}...")
                        errors += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error procesando noticia '{noticia.get('title', 'Unknown')}': {e}")
                    errors += 1
                    continue
            
            logger.success(f"✅ Proceso completado:")
            logger.info(f"   - Actualizadas: {updated}")
            logger.info(f"   - Omitidas (ya en Supabase): {skipped}")
            logger.info(f"   - Errores: {errors}")
            
    except Exception as e:
        logger.error(f"❌ Error general: {e}")

async def main():
    """Ejecutar actualización"""
    logger.info("🚀 Iniciando actualización de imágenes de noticias...")
    logger.info("⚠️  Asegúrate de que el bucket 'article-images' esté creado en Supabase")
    
    await update_news_with_images()
    
    logger.success("✅ Proceso completado")

if __name__ == "__main__":
    asyncio.run(main())

