"""
Script para limpiar todas las noticias de Supabase
"""
import asyncio
import os
from dotenv import load_dotenv
from src.storage.supabase_storage import SupabaseStorage
from loguru import logger

load_dotenv()

async def cleanup_all_articles():
    """Eliminar todas las noticias de Supabase"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return
    
    logger.info("Connecting to Supabase...")
    storage = SupabaseStorage(
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    logger.warning("⚠️  WARNING: This will delete ALL articles from Supabase!")
    logger.warning("Press Ctrl+C within 5 seconds to cancel...")
    
    try:
        await asyncio.sleep(5)
    except asyncio.CancelledError:
        logger.info("Operation cancelled")
        return
    
    logger.info("Deleting all articles...")
    await storage.delete_all_articles()
    logger.success("✅ All articles deleted successfully!")

if __name__ == "__main__":
    asyncio.run(cleanup_all_articles())

