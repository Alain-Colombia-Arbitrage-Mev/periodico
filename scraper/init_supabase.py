"""
Script para inicializar categorías en Supabase
"""
import asyncio
import os
import httpx
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

async def init_categories():
    """Inicializar categorías en Supabase"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    categories = [
        {"name": "Economía", "slug": "economia", "color": "#16A34A", "order": 1},
        {"name": "Política", "slug": "politica", "color": "#2563EB", "order": 2},
        {"name": "Judicial", "slug": "judicial", "color": "#DC2626", "order": 3},
        {"name": "Internacional", "slug": "internacional", "color": "#9333EA", "order": 4},
        {"name": "Sociedad", "slug": "sociedad", "color": "#EA580C", "order": 5},
    ]
    
    async with httpx.AsyncClient(timeout=30) as client:
        for category in categories:
            try:
                # Verificar si existe
                check_response = await client.get(
                    f"{supabase_url}/rest/v1/categorias?slug=eq.{category['slug']}&select=id",
                    headers=headers
                )
                
                if check_response.status_code == 200:
                    existing = check_response.json()
                    if existing:
                        logger.info(f"Category {category['slug']} already exists")
                        continue
                
                # Crear categoría
                response = await client.post(
                    f"{supabase_url}/rest/v1/categorias",
                    headers=headers,
                    json=category
                )
                
                if response.status_code in [200, 201]:
                    logger.success(f"Created category: {category['slug']}")
                else:
                    logger.error(f"Failed to create category {category['slug']}: {response.status_code} - {response.text}")
                    
            except Exception as e:
                logger.error(f"Error creating category {category['slug']}: {e}")

if __name__ == "__main__":
    asyncio.run(init_categories())









