"""
Crear bucket de Storage usando la API REST de Supabase
Requiere SUPABASE_SERVICE_ROLE_KEY en .env
"""
import os
import httpx
import asyncio
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

async def create_bucket():
    """Crear bucket article-images en Supabase Storage"""
    supabase_url = os.getenv("SUPABASE_URL")
    # Usar service_role key (tiene permisos de admin)
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url:
        logger.error("❌ SUPABASE_URL requerido")
        return False
    
    if not service_role_key:
        logger.error("❌ SUPABASE_SERVICE_ROLE_KEY requerido para crear buckets")
        logger.info("   Obtén la service_role key desde: Supabase Dashboard → Settings → API")
        return False
    
    bucket_name = "article-images"
    
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
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
                
                # Crear política de acceso público
                policy_sql = f"""
                CREATE POLICY "Public Access" ON storage.objects
                FOR SELECT USING (bucket_id = '{bucket_name}');
                """
                
                logger.info("✅ Bucket creado. Las políticas de acceso se configuran automáticamente para buckets públicos.")
                return True
            else:
                logger.error(f"❌ Error creando bucket: {create_response.status_code}")
                logger.error(f"   Response: {create_response.text}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(create_bucket())









