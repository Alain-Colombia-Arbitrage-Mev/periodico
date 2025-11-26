"""
Aplicar schema.sql a Supabase
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

async def apply_schema():
    print("🔧 Aplicando schema a Supabase...\\n")

    # Leer el schema.sql
    schema_path = Path("../supabase/schema.sql")
    if not schema_path.exists():
        print("❌ No se encontró el archivo schema.sql")
        return

    schema_sql = schema_path.read_text()

    # Separar en statements individuales (aproximado)
    statements = []
    current = []
    in_function = False

    for line in schema_sql.split("\\n"):
        stripped = line.strip()

        # Detectar inicio de función
        if "CREATE OR REPLACE FUNCTION" in line or "CREATE FUNCTION" in line:
            in_function = True

        # Detectar fin de función
        if in_function and stripped.endswith("$$;"):
            in_function = False
            current.append(line)
            statements.append("\\n".join(current))
            current = []
            continue

        # Agregar línea
        current.append(line)

        # Si no estamos en función y termina con ;, es un statement completo
        if not in_function and stripped.endswith(";") and not stripped.startswith("--"):
            statements.append("\\n".join(current))
            current = []

    # Agregar cualquier statement pendiente
    if current:
        statements.append("\\n".join(current))

    print(f"📋 Encontrados {len(statements)} statements SQL\\n")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    async with httpx.AsyncClient(timeout=60) as client:
        success_count = 0
        error_count = 0

        for i, statement in enumerate(statements, 1):
            stmt = statement.strip()
            if not stmt or stmt.startswith("--") or stmt == "":
                continue

            # Mostrar preview del statement
            preview = stmt.split("\\n")[0][:60]
            print(f"{i:3d}. {preview}...", end=" ")

            try:
                # Ejecutar via SQL Editor de Supabase
                # Nota: Supabase no tiene un endpoint REST directo para ejecutar SQL arbitrario
                # Tendremos que usar el endpoint de query
                response = await client.post(
                    f"{SUPABASE_URL}/rest/v1/rpc/query",
                    headers=headers,
                    json={"query": stmt}
                )

                if response.status_code in [200, 201, 204]:
                    print("✅")
                    success_count += 1
                else:
                    # Algunos errores son esperados (ya existe, etc)
                    error_text = response.text[:100]
                    if "already exists" in error_text.lower() or "duplicate" in error_text.lower():
                        print("⚠️  (ya existe)")
                        success_count += 1
                    else:
                        print(f"❌ {response.status_code}")
                        error_count += 1
                        if response.status_code != 404:  # 404 = endpoint no existe
                            print(f"    Error: {error_text}")

            except Exception as e:
                print(f"❌ {str(e)[:50]}")
                error_count += 1

    print(f"\\n✅ Completado: {success_count} exitosos, {error_count} errores")
    print("\\n⚠️  NOTA: Si ves muchos errores 404, es porque el endpoint /rpc/query no existe.")
    print("    En ese caso, debes aplicar el schema manualmente desde el Dashboard de Supabase:")
    print("    https://supabase.com/dashboard/project/dnacsmoubqrzpbvjhary/sql")
    print("\\n    1. Abre el SQL Editor")
    print("    2. Copia el contenido de supabase/schema.sql")
    print("    3. Ejecuta el SQL")

if __name__ == "__main__":
    asyncio.run(apply_schema())
