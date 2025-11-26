"""
Script completo para configurar Supabase automáticamente
- Crea el bucket de Storage (requiere service_role key)
- Verifica que todo esté configurado
"""
import os
import httpx
import asyncio
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

async def setup_supabase_complete():
    """Configurar Supabase completamente"""
    supabase_url = os.getenv("SUPABASE_URL")
    # Usar service_role key para operaciones de admin
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL y SUPABASE_KEY deben estar configurados")
        logger.info("💡 Para crear buckets, necesitas SUPABASE_SERVICE_ROLE_KEY en .env")
        return False
    
    bucket_name = "article-images"
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    # Verificar categorías
    logger.info("📋 Verificando categorías...")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            cats_response = await client.get(
                f"{supabase_url}/rest/v1/categorias?select=name,slug",
                headers=headers
            )
            if cats_response.status_code == 200:
                categories = cats_response.json()
                logger.success(f"✅ {len(categories)} categorías encontradas")
                for cat in categories:
                    logger.info(f"   - {cat['name']} ({cat['slug']})")
    except Exception as e:
        logger.error(f"Error verificando categorías: {e}")
    
    # Verificar usuario scraper
    logger.info("👤 Verificando usuario scraper...")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            user_response = await client.get(
                f"{supabase_url}/rest/v1/usuarios?email=eq.scraper@politicaargentina.com&select=name,email",
                headers=headers
            )
            if user_response.status_code == 200:
                users = user_response.json()
                if users:
                    logger.success(f"✅ Usuario scraper encontrado: {users[0]['name']}")
                else:
                    logger.warning("⚠️  Usuario scraper no encontrado")
    except Exception as e:
        logger.error(f"Error verificando usuario: {e}")
    
    # Intentar crear bucket
    logger.info(f"🪣 Intentando crear bucket '{bucket_name}'...")
    
    bucket_config = {
        "name": bucket_name,
        "public": True,
        "file_size_limit": 5242880,  # 5MB
        "allowed_mime_types": ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Verificar si el bucket ya existe
            check_response = await client.get(
                f"{supabase_url}/storage/v1/bucket/{bucket_name}",
                headers=headers
            )
            
            if check_response.status_code == 200:
                logger.success(f"✅ Bucket '{bucket_name}' ya existe")
                return True
            
            # Crear el bucket
            create_response = await client.post(
                f"{supabase_url}/storage/v1/bucket",
                headers=headers,
                json=bucket_config
            )
            
            if create_response.status_code in [200, 201]:
                logger.success(f"✅ Bucket '{bucket_name}' creado exitosamente")
                return True
            else:
                logger.warning(f"⚠️  No se pudo crear bucket automáticamente: {create_response.status_code}")
                logger.info(f"   Response: {create_response.text}")
                logger.info("")
                logger.info("📝 INSTRUCCIONES MANUALES:")
                logger.info("   1. Ve a Supabase Dashboard → Storage")
                logger.info(f"   2. Crea un bucket llamado: {bucket_name}")
                logger.info("   3. Márcalo como público (Public bucket: Yes)")
                logger.info("   4. File size limit: 5MB")
                logger.info("   5. Allowed MIME types: image/jpeg, image/png, image/webp")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error al crear bucket: {e}")
        logger.info("")
        logger.info("📝 INSTRUCCIONES MANUALES:")
        logger.info("   1. Ve a Supabase Dashboard → Storage")
        logger.info(f"   2. Crea un bucket llamado: {bucket_name}")
        logger.info("   3. Márcalo como público")
        return False

if __name__ == "__main__":
    asyncio.run(setup_supabase_complete())









