#!/bin/bash

# ===========================================
# Script de Limpieza de Caché de Next.js
# Política Argentina
# ===========================================

set -e

echo "🧹 Limpieza de Caché de Next.js"
echo "================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Detener proceso en puerto 3000 si existe
print_status "Verificando puerto 3000..."
if lsof -i:3000 > /dev/null 2>&1; then
    print_warning "Proceso en puerto 3000 detectado, deteniendo..."
    kill -9 $(lsof -t -i:3000) 2>/dev/null || true
    print_status "Puerto 3000 liberado"
else
    print_status "Puerto 3000 está libre"
fi

# Eliminar directorios de caché
print_status "Eliminando .next..."
rm -rf .next

print_status "Eliminando caché de node_modules..."
rm -rf node_modules/.cache

# Limpiar caché de npm
print_status "Limpiando caché de npm..."
npm cache clean --force

# Verificar/corregir archivo eslint
if [ -f ".eslintrc.js" ]; then
    print_warning "Detectado .eslintrc.js, renombrando a .eslintrc.cjs..."
    mv .eslintrc.js .eslintrc.cjs
    print_status "Archivo renombrado"
fi

# Reinstalar dependencias
print_status "Reinstalando dependencias..."
npm install --legacy-peer-deps

# Build
print_status "Construyendo proyecto..."
npm run build

echo ""
print_status "¡Limpieza completada!"
echo ""
echo "💡 Puedes iniciar el servidor con:"
echo "   npm run dev"
echo ""
