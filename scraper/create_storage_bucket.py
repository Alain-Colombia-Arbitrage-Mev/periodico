"""
Script para crear el bucket de Storage en Supabase
"""
import os
import httpx
import asyncio
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

async def create_storage_bucket():
    """Crear bucket article-images en Supabase Storage"""
    supabase_url = os.getenv("SUPABASE_URL")
    # Intentar usar service_role key primero (tiene permisos de admin)
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL y SUPABASE_KEY (o SUPABASE_SERVICE_ROLE_KEY) deben estar configurados en .env")
        return False
    
    bucket_name = "article-images"
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    bucket_config = {
        "name": bucket_name,
        "public": True,  # Bucket público para acceso a imágenes
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
                logger.info(f"✅ Bucket '{bucket_name}' ya existe")
                return True
            
            # Crear el bucket
            logger.info(f"Creando bucket '{bucket_name}'...")
            create_response = await client.post(
                f"{supabase_url}/storage/v1/bucket",
                headers=headers,
                json=bucket_config
            )
            
            if create_response.status_code in [200, 201]:
                logger.success(f"✅ Bucket '{bucket_name}' creado exitosamente")
                
                # Configurar políticas de acceso público
                policy_config = {
                    "name": f"Public Access for {bucket_name}",
                    "bucket_id": bucket_name,
                    "definition": {
                        "SELECT": {
                            "policy_name": "Public Access",
                            "roles": ["anon", "authenticated"],
                            "using_expression": "true",
                            "check_expression": "true"
                        }
                    }
                }
                
                # Crear política de acceso público
                policy_response = await client.post(
                    f"{supabase_url}/storage/v1/bucket/{bucket_name}/policies",
                    headers=headers,
                    json=policy_config
                )
                
                if policy_response.status_code in [200, 201]:
                    logger.success(f"✅ Política de acceso público configurada")
                else:
                    logger.warning(f"⚠️  No se pudo configurar política automáticamente: {policy_response.status_code}")
                    logger.info("Puedes configurarla manualmente en el dashboard de Supabase")
                
                return True
            else:
                logger.error(f"❌ Error al crear bucket: {create_response.status_code}")
                logger.error(f"Response: {create_response.text}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error al crear bucket: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(create_storage_bucket())

