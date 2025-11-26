#!/usr/bin/env python3
"""
Script para limpiar la base de datos de Supabase
Elimina todas las noticias y limpia el storage
"""
import asyncio
import os
import httpx
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

async def clean_database():
    """Eliminar todas las noticias de la base de datos"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        # 1. Contar noticias actuales
        logger.info("📊 Contando noticias actuales...")
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/noticias?select=id",
            headers=headers
        )

        if response.status_code == 200:
            count = len(response.json())
            logger.info(f"✅ Encontradas {count} noticias en la base de datos")
        else:
            logger.error(f"❌ Error contando noticias: {response.status_code}")
            return

        # 2. Eliminar todas las noticias
        if count > 0:
            logger.info("🗑️  Eliminando todas las noticias...")
            response = await client.delete(
                f"{SUPABASE_URL}/rest/v1/noticias?id=neq.00000000-0000-0000-0000-000000000000",
                headers=headers
            )

            if response.status_code in [200, 204]:
                logger.info(f"✅ Eliminadas {count} noticias exitosamente")
            else:
                logger.error(f"❌ Error eliminando noticias: {response.status_code} - {response.text}")
                return

        # 3. Limpiar Storage bucket (opcional - comentado por seguridad)
        logger.info("📦 Bucket de storage 'noticias' debe limpiarse manualmente desde el dashboard")
        logger.info("   URL: https://supabase.com/dashboard/project/dnacsmoubqrzpbvjhary/storage/buckets/noticias")

        logger.info("\n✅ Base de datos limpiada exitosamente")
        logger.info("🚀 Listo para ejecutar el scraper con nuevas noticias")

if __name__ == "__main__":
    asyncio.run(clean_database())
