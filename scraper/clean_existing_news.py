"""
Script para limpiar todas las noticias existentes:
- Eliminar referencias a "clarin", "infobae", "lanacion"
- Eliminar autores y fuentes
"""
import os
import asyncio
import httpx
import re
from dotenv import load_dotenv
from loguru import logger
from src.utils.text_cleaner import TextCleaner

load_dotenv()

# Patrones adicionales para limpiar
SOURCE_PATTERNS = [
    r'\bclarin\b',
    r'\bclarín\b',
    r'\bclarin\.com\b',
    r'\bclarín\.com\b',
    r'\bwww\.clarin\.com\b',
    r'\bwww\.clarín\.com\b',
    r'\binfobae\b',
    r'\binfobae\.com\b',
    r'\bwww\.infobae\.com\b',
    r'\blanacion\b',
    r'\bla\s+naci[oó]n\b',
    r'\blanacion\.com\.ar\b',
    r'\bwww\.lanacion\.com\.ar\b',
    r'fuente:\s*(clarin|clarín|infobae|lanacion|la\s+naci[oó]n)',
    r'según\s+(clarin|clarín|infobae|lanacion|la\s+naci[oó]n)',
    r'sigue\s+todas\s+las\s+noticias\s+de\s+[a-z]+\.com',
    r'sigue\s+todas\s+las\s+noticias\s+de\s+[a-z]+\.com\s+en\s+google\s+news',
    r'sigue\s+todas\s+las\s+noticias\s+de\s+[a-z]+\.com\s+en\s+whatsapp',
]

async def clean_text_field(text: str) -> str:
    """Limpiar un campo de texto"""
    if not text:
        return text
    
    cleaned = TextCleaner.clean_text(text)
    
    # Aplicar patrones adicionales
    for pattern in SOURCE_PATTERNS:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Limpiar espacios múltiples
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned

async def clean_all_news():
    """Limpiar todas las noticias existentes"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL y SUPABASE_KEY requeridos")
        return
    
    logger.info("🧹 Limpiando todas las noticias existentes...")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            }
            
            # Obtener todas las noticias
            response = await client.get(
                f"{supabase_url}/rest/v1/noticias?select=id,title,subtitle,excerpt,content",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error obteniendo noticias: {response.status_code}")
                return
            
            noticias = response.json()
            logger.info(f"📰 Encontradas {len(noticias)} noticias para limpiar")
            
            if not noticias:
                logger.info("✅ No hay noticias para limpiar")
                return
            
            updated = 0
            errors = 0
            
            for noticia in noticias:
                try:
                    noticia_id = noticia["id"]
                    
                    # Limpiar cada campo
                    title_cleaned = await clean_text_field(noticia.get("title", ""))
                    subtitle_cleaned = await clean_text_field(noticia.get("subtitle", ""))
                    excerpt_cleaned = await clean_text_field(noticia.get("excerpt", ""))
                    content_cleaned = await clean_text_field(noticia.get("content", ""))
                    
                    # Verificar si hubo cambios
                    if (title_cleaned != noticia.get("title") or
                        subtitle_cleaned != noticia.get("subtitle") or
                        excerpt_cleaned != noticia.get("excerpt") or
                        content_cleaned != noticia.get("content")):
                        
                        # Actualizar noticia
                        update_data = {}
                        if title_cleaned != noticia.get("title"):
                            update_data["title"] = title_cleaned
                        if subtitle_cleaned != noticia.get("subtitle"):
                            update_data["subtitle"] = subtitle_cleaned
                        if excerpt_cleaned != noticia.get("excerpt"):
                            update_data["excerpt"] = excerpt_cleaned
                        if content_cleaned != noticia.get("content"):
                            update_data["content"] = content_cleaned
                        
                        # Eliminar autor (si existe el campo)
                        update_data["author_id"] = None  # O mantener el scraper user
                        
                        update_response = await client.patch(
                            f"{supabase_url}/rest/v1/noticias?id=eq.{noticia_id}",
                            headers=headers,
                            json=update_data
                        )
                        
                        if update_response.status_code in [200, 204]:
                            logger.success(f"✅ Limpiada: {title_cleaned[:50]}...")
                            updated += 1
                        else:
                            logger.error(f"❌ Error actualizando: {update_response.status_code}")
                            errors += 1
                    else:
                        logger.debug(f"Sin cambios: {noticia.get('title', 'Unknown')[:50]}...")
                        
                except Exception as e:
                    logger.error(f"❌ Error procesando noticia: {e}")
                    errors += 1
                    continue
            
            logger.success(f"✅ Proceso completado:")
            logger.info(f"   - Actualizadas: {updated}")
            logger.info(f"   - Errores: {errors}")
            
    except Exception as e:
        logger.error(f"❌ Error general: {e}")

async def main():
    """Ejecutar limpieza"""
    logger.info("🚀 Iniciando limpieza de noticias existentes...")
    await clean_all_news()
    logger.success("✅ Proceso completado")

if __name__ == "__main__":
    asyncio.run(main())









