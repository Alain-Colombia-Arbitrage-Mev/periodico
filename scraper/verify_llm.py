#!/usr/bin/env python3
"""
Script de verificación: Confirma que el LLM está reescribiendo noticias
"""
import asyncio
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def verify_llm_config():
    """Verifica la configuración del LLM"""
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN LLM")
    print("=" * 60)
    
    # Verificar variables de entorno
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    model = os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet")
    enabled = os.getenv("LLM_REWRITE_ENABLED", "true").lower() == "true"
    
    print(f"\n✓ API Key configurada: {'Sí' if api_key else 'NO'}")
    if api_key:
        print(f"  → {api_key[:20]}...{api_key[-10:]}")
    
    print(f"\n✓ Modelo LLM: {model}")
    print(f"✓ Reescritura habilitada: {'SÍ' if enabled else 'NO'}")
    
    if not api_key:
        print("\n❌ ERROR: No se encontró OPENROUTER_API_KEY en .env")
        return False
    
    if not enabled:
        print("\n⚠️  ADVERTENCIA: LLM_REWRITE_ENABLED está deshabilitado")
        return False
    
    # Test básico de conexión
    print("\n" + "=" * 60)
    print("PROBANDO CONEXIÓN CON OPENROUTER...")
    print("=" * 60)
    
    try:
        import httpx
        
        # Crear un artículo de prueba simple
        test_prompt = """Reescribe este título de noticia de forma breve:
        
        Original: "El gobierno anuncia nuevas medidas económicas"
        
        Responde SOLO con el título reescrito, sin explicaciones."""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": test_prompt}
                    ],
                    "max_tokens": 100
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                rewritten = data["choices"][0]["message"]["content"]
                
                print(f"\n✅ CONEXIÓN EXITOSA!")
                print(f"\nPrueba de reescritura:")
                print(f"  Original: 'El gobierno anuncia nuevas medidas económicas'")
                print(f"  Reescrito: '{rewritten.strip()}'")
                print(f"\n✓ Modelo: {model}")
                print(f"✓ Tokens usados: {data.get('usage', {}).get('total_tokens', 'N/A')}")
                
                return True
            else:
                print(f"\n❌ ERROR: Status {response.status_code}")
                print(f"Respuesta: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR en conexión: {e}")
        return False

async def check_recent_rewrites():
    """Verifica si hay noticias reescritas recientemente en Supabase"""
    print("\n" + "=" * 60)
    print("VERIFICANDO NOTICIAS EN SUPABASE")
    print("=" * 60)
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_KEY", "")
        
        if not supabase_url or not supabase_key:
            print("\n⚠️  No se encontraron credenciales de Supabase")
            return
        
        client = create_client(supabase_url, supabase_key)
        
        # Obtener últimas 5 noticias
        result = client.table('noticias').select('id, title, source_type, created_at').order('created_at', desc=True).limit(5).execute()
        
        if result.data:
            print(f"\n✓ Últimas {len(result.data)} noticias en BD:")
            for i, noticia in enumerate(result.data, 1):
                source_label = "🤖 LLM Reescrita" if noticia.get('source_type') == 0 else "✍️  Manual"
                print(f"\n{i}. {source_label}")
                print(f"   Título: {noticia['title'][:70]}...")
                print(f"   Fecha: {noticia['created_at']}")
        else:
            print("\n⚠️  No hay noticias en la base de datos")
            
    except Exception as e:
        print(f"\n⚠️  Error al consultar Supabase: {e}")

async def main():
    """Main de verificación"""
    print("\n")
    
    # Verificar configuración
    config_ok = await verify_llm_config()
    
    # Verificar noticias
    await check_recent_rewrites()
    
    print("\n" + "=" * 60)
    if config_ok:
        print("✅ TODO CONFIGURADO CORRECTAMENTE")
        print("\nEl scraper está listo para reescribir noticias con:")
        print(f"  → Modelo: {os.getenv('LLM_MODEL')}")
        print(f"  → Provider: OpenRouter")
    else:
        print("❌ HAY PROBLEMAS DE CONFIGURACIÓN")
        print("\nRevisa el archivo .env y asegúrate de tener:")
        print("  - OPENROUTER_API_KEY")
        print("  - LLM_MODEL")
        print("  - LLM_REWRITE_ENABLED=true")
    print("=" * 60)
    print("\n")

if __name__ == "__main__":
    asyncio.run(main())
