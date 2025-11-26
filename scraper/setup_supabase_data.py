"""
Setup inicial de datos en Supabase para el scraper
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

async def setup():
    print("🔧 Configurando datos iniciales en Supabase...\n")

    async with httpx.AsyncClient(timeout=30) as client:
        # 1. Verificar/crear categorías
        print("1️⃣ Verificando categorías...")
        categorias = [
            {"name": "Economía", "slug": "economia", "color": "#16A34A", "order": 1},
            {"name": "Política", "slug": "politica", "color": "#2563EB", "order": 2},
            {"name": "Judicial", "slug": "judicial", "color": "#DC2626", "order": 3},
            {"name": "Internacional", "slug": "internacional", "color": "#9333EA", "order": 4},
            {"name": "Sociedad", "slug": "sociedad", "color": "#EA580C", "order": 5}
        ]

        for cat in categorias:
            # Check if exists
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/categorias?slug=eq.{cat['slug']}&select=id",
                headers=headers
            )

            if response.status_code == 200 and response.json():
                print(f"  ✅ {cat['name']} ya existe")
            else:
                # Create
                response = await client.post(
                    f"{SUPABASE_URL}/rest/v1/categorias",
                    headers=headers,
                    json=cat
                )
                if response.status_code in [200, 201]:
                    print(f"  ✨ {cat['name']} creada")
                else:
                    print(f"  ❌ Error creando {cat['name']}: {response.status_code}")

        print()

        # 2. Verificar/crear autor para el scraper
        print("2️⃣ Verificando autor del scraper...")
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/usuarios?email=eq.scraper@politicaargentina.com&select=id",
            headers=headers
        )

        if response.status_code == 200 and response.json():
            print("  ✅ Autor 'Redacción' ya existe")
        else:
            # Create
            author_data = {
                "email": "scraper@politicaargentina.com",
                "name": "Redacción",
                "role": "author"
            }
            response = await client.post(
                f"{SUPABASE_URL}/rest/v1/usuarios",
                headers=headers,
                json=author_data
            )
            if response.status_code in [200, 201]:
                print("  ✨ Autor 'Redacción' creado")
            else:
                print(f"  ❌ Error creando autor: {response.status_code} - {response.text}")

        print()
        print("✅ Setup completado!")

if __name__ == "__main__":
    asyncio.run(setup())
