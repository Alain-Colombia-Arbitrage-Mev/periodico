#!/usr/bin/env python3
"""
Script Simple para Obtener Noticias Reales
Ejecuta el scraper una vez y guarda en Supabase
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add scraper src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper', 'src'))

# Load env variables
load_dotenv()

async def main():
    print("🚀 Iniciando Scraper de Noticias Reales\n")
    print("=" * 60)

    # Import here after path is set
    from storage.supabase_storage import SupabaseStorage
    from utils.image_handler import ImageHandler
    from pipeline import ArticlePipeline

    # Get environment variables
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    openrouter_key = os.getenv("Openrouter_key")
    llm_model = os.getenv("Openrouter_model", "deepseek/deepseek-v3.2-exp")

    if not supabase_url or not supabase_service_key:
        print("❌ Error: NEXT_PUBLIC_SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY son requeridos")
        print("   Verifica tu archivo .env")
        return

    print(f"✅ Supabase URL: {supabase_url}")
    print(f"✅ LLM Model: {llm_model}")
    print(f"✅ LLM Enabled: {'Yes' if openrouter_key else 'No (usando noticias sin reescribir)'}")
    print()

    # Initialize storage
    supabase_storage = SupabaseStorage(
        supabase_url=supabase_url,
        supabase_key=supabase_service_key
    )

    # Initialize image handler
    image_handler = ImageHandler(
        output_dir="data/images",
        max_size=2048,
        quality=85,
        supabase_url=supabase_url,
        supabase_key=supabase_service_key,
        storage_bucket="noticias"
    )

    # Create pipeline
    pipeline = ArticlePipeline(
        image_handler=image_handler,
        supabase_storage=supabase_storage,
        openrouter_api_key=openrouter_key if openrouter_key else None,
        llm_model=llm_model,
        rewrite_enabled=bool(openrouter_key),  # Solo si hay API key
        max_articles_per_category=10  # Menos para prueba rápida
    )

    print("🔄 Ejecutando pipeline completo...")
    print("   (Esto puede tomar varios minutos)\n")

    # Run pipeline
    await pipeline.run_full_pipeline()

    # Show stats
    stats = await pipeline.get_supabase_stats()

    print("\n" + "=" * 60)
    print("📊 Resultados:")
    print(f"   Total de noticias en Supabase: {stats.get('total_articles', 0)}")
    print(f"   Noticias publicadas: {stats.get('published_articles', 0)}")
    print("=" * 60)
    print("\n✅ ¡Scraper completado!")
    print("\n💡 Próximos pasos:")
    print("   1. Verificar noticias: node check-database.mjs")
    print("   2. Abrir sitio: http://localhost:3001")
    print("   3. Hard refresh: Cmd+Shift+R (Mac) o Ctrl+Shift+R (Windows)")

if __name__ == "__main__":
    asyncio.run(main())
