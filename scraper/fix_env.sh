#!/bin/bash
# Script para corregir nombres de variables en .env

echo "🔧 Corrigiendo nombres de variables en .env..."

# Crear backup
cp .env .env.backup
echo "✅ Backup creado: .env.backup"

# Reemplazar SUPABASE_ANON_KEY por SUPABASE_KEY
sed -i '' 's/^SUPABASE_ANON_KEY=/SUPABASE_KEY=/' .env
echo "✅ SUPABASE_ANON_KEY → SUPABASE_KEY"

# Reemplazar SUPABASE_SERVICE_ROLE_KEY por SUPABASE_SERVICE_KEY
sed -i '' 's/^SUPABASE_SERVICE_ROLE_KEY=/SUPABASE_SERVICE_KEY=/' .env
echo "✅ SUPABASE_SERVICE_ROLE_KEY → SUPABASE_SERVICE_KEY"

# Eliminar líneas duplicadas de RUN_MODE (mantener la última)
sed -i '' '1,/^RUN_MODE=/d' .env.tmp 2>/dev/null || true

echo ""
echo "✅ Variables corregidas!"
echo ""
echo "Verificando configuración:"
grep -E "^(SUPABASE_URL|SUPABASE_KEY|SUPABASE_SERVICE_KEY|OPENROUTER_API_KEY)=" .env | head -4
