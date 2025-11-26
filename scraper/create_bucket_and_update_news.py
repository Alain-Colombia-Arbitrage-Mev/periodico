"""
Script para crear el bucket de Storage y actualizar noticias con imágenes optimizadas
"""
import os
import asyncio
import httpx
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from src.storage.supabase_storage import SupabaseStorage

load_dotenv()

async def create_bucket_with_service_role():
    """Crear bucket usando service_role key si está disponible"""
    supabase_url = os.getenv("SUPABASE_URL")
    # Intentar service_role key primero
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL y SUPABASE_KEY requeridos")
        return False
    
    bucket_name = "article-images"
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    bucket_config = {
        "name": bucket_name,
        "public": True,
        "file_size_limit": 5242880,  # 5MB
        "allowed_mime_types": ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Verificar si existe
            check_response = await client.get(
                f"{supabase_url}/storage/v1/bucket/{bucket_name}",
                headers=headers
            )
            
            if check_response.status_code == 200:
                logger.success(f"✅ Bucket '{bucket_name}' ya existe")
                return True
            
            # Crear bucket
            logger.info(f"🪣 Creando bucket '{bucket_name}'...")
            create_response = await client.post(
                f"{supabase_url}/storage/v1/bucket",
                headers=headers,
                json=bucket_config
            )
            
            if create_response.status_code in [200, 201]:
                logger.success(f"✅ Bucket '{bucket_name}' creado exitosamente")
                return True
            else:
                logger.warning(f"⚠️  No se pudo crear bucket: {create_response.status_code}")
                logger.info(f"   Response: {create_response.text}")
                logger.info("")
                logger.info("📝 Necesitas crear el bucket manualmente:")
                logger.info(f"   1. Ve a Supabase Dashboard → Storage")
                logger.info(f"   2. Crea bucket: {bucket_name}")
                logger.info(f"   3. Público: Sí")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

async def update_news_with_images():
    """Actualizar noticias existentes subiendo imágenes al bucket"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL y SUPABASE_KEY requeridos")
        return
    
    storage = SupabaseStorage(supabase_url, supabase_key)
    
    # Obtener noticias sin imágenes en Supabase Storage
    logger.info("📰 Obteniendo noticias para actualizar...")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            }
            
            # Obtener noticias con source_type = 0 que no tengan imágenes en Supabase Storage
            response = await client.get(
                f"{supabase_url}/rest/v1/noticias?source_type=eq.0&select=id,title,image_url,source_url",
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
            
            updated = 0
            for noticia in noticias:
                try:
                    image_url = noticia.get("image_url", "")
                    source_url = noticia.get("source_url", "")
                    noticia_id = noticia["id"]
                    
                    # Verificar si la imagen ya está en Supabase Storage
                    if image_url and "storage/v1/object/public/article-images" in image_url:
                        logger.debug(f"✅ Imagen ya en Supabase: {noticia['title'][:50]}...")
                        continue
                    
                    # Buscar imagen local basándose en el slug o título
                    image_path = None
                    images_dir = Path("data/images")
                    
                    # Obtener categoría para buscar en la carpeta correcta
                    cat_response = await client.get(
                        f"{supabase_url}/rest/v1/categorias?id=eq.{noticia['category_id']}&select=slug",
                        headers=headers
                    )
                    category_slug = "politica"  # default
                    if cat_response.status_code == 200:
                        cat_data = cat_response.json()
                        if cat_data:
                            category_slug = cat_data[0].get("slug", "politica")
                    
                    # Buscar imagen en la carpeta de la categoría
                    category_dir = images_dir / category_slug
                    if category_dir.exists():
                        # Buscar por nombre de archivo que contenga parte del slug
                        noticia_slug = noticia.get("slug", "")
                        if noticia_slug:
                            # Buscar archivos que coincidan con el slug
                            for ext in ["*.png", "*.jpg", "*.jpeg"]:
                                for img_file in category_dir.glob(ext):
                                    if img_file.exists():
                                        # Usar la primera imagen encontrada en la categoría
                                        image_path = img_file
                                        break
                                if image_path:
                                    break
                    
                    # Si no se encuentra, buscar cualquier imagen en la categoría
                    if not image_path and category_dir.exists():
                        for ext in ["*.png", "*.jpg", "*.jpeg"]:
                            images = list(category_dir.glob(ext))
                            if images:
                                image_path = images[0]  # Tomar la primera
                                break
                    
                    if not image_path or not image_path.exists():
                        logger.warning(f"⚠️  Imagen local no encontrada para: {noticia['title'][:50]}...")
                        continue
                    
                    # Subir imagen a Supabase Storage
                    logger.info(f"📤 Subiendo imagen para: {noticia['title'][:50]}...")
                    remote_path = f"{image_path.parent.name}/{image_path.name}"
                    new_image_url = await storage.upload_image(str(image_path), remote_path)
                    
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
                    else:
                        logger.warning(f"⚠️  No se pudo subir imagen para: {noticia['title'][:50]}...")
                        
                except Exception as e:
                    logger.error(f"❌ Error procesando noticia: {e}")
                    continue
            
            logger.success(f"✅ Actualizadas {updated}/{len(noticias)} noticias con imágenes")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")

async def main():
    """Ejecutar todo el proceso"""
    logger.info("🚀 Iniciando creación de bucket y actualización de noticias...")
    
    # 1. Crear bucket
    bucket_created = await create_bucket_with_service_role()
    
    if not bucket_created:
        logger.warning("⚠️  El bucket no se pudo crear automáticamente")
        logger.info("   Por favor créalo manualmente antes de continuar")
        logger.info("   Ver: CREAR_BUCKET_MANUAL.md")
        return
    
    # 2. Actualizar noticias
    await update_news_with_images()
    
    logger.success("✅ Proceso completado")

if __name__ == "__main__":
    asyncio.run(main())

