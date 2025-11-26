#!/bin/bash

# ===========================================
# Script de Reconstrucción Docker
# Política Argentina - Next.js App
# ===========================================

set -e

echo "🔧 Política Argentina - Reconstrucción Docker"
echo "=============================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Verificar que Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    print_error "Docker no está corriendo. Por favor, inicia Docker Desktop."
    exit 1
fi

print_status "Docker está corriendo"

# Opción para limpiar todo
echo ""
echo "¿Qué deseas hacer?"
echo "1) Reconstruir solo la app web (Next.js)"
echo "2) Reconstruir solo el scraper"
echo "3) Reconstruir ambos (web + scraper)"
echo "4) Limpiar todo y reconstruir desde cero (recomendado)"
echo ""
read -p "Selecciona una opción (1-4): " option

case $option in
    1)
        echo ""
        print_status "Deteniendo contenedor web..."
        docker-compose stop web 2>/dev/null || true

        print_status "Eliminando contenedor web..."
        docker-compose rm -f web 2>/dev/null || true

        print_status "Reconstruyendo imagen web (sin caché)..."
        docker-compose build --no-cache web

        print_status "Iniciando contenedor web..."
        docker-compose up -d web

        print_status "¡Listo! App web reconstruida"
        ;;
    2)
        echo ""
        print_status "Deteniendo contenedor scraper..."
        docker-compose stop scraper 2>/dev/null || true

        print_status "Eliminando contenedor scraper..."
        docker-compose rm -f scraper 2>/dev/null || true

        print_status "Reconstruyendo imagen scraper (sin caché)..."
        docker-compose build --no-cache scraper

        print_status "Iniciando contenedor scraper..."
        docker-compose up -d scraper

        print_status "¡Listo! Scraper reconstruido"
        ;;
    3)
        echo ""
        print_status "Deteniendo todos los contenedores..."
        docker-compose down

        print_status "Reconstruyendo todas las imágenes (sin caché)..."
        docker-compose build --no-cache

        print_status "Iniciando todos los contenedores..."
        docker-compose up -d

        print_status "¡Listo! Todas las imágenes reconstruidas"
        ;;
    4)
        echo ""
        print_warning "Esta opción eliminará TODAS las imágenes y contenedores relacionados"
        read -p "¿Estás seguro? (s/n): " confirm

        if [[ $confirm == "s" || $confirm == "S" ]]; then
            print_status "Deteniendo todos los contenedores..."
            docker-compose down

            print_status "Eliminando imágenes antiguas..."
            docker rmi politica-argentina:latest 2>/dev/null || true
            docker rmi politica-argentina-scraper:latest 2>/dev/null || true

            print_status "Limpiando caché de Docker..."
            docker builder prune -f

            print_status "Reconstruyendo todo desde cero..."
            docker-compose build --no-cache --pull

            print_status "Iniciando contenedores..."
            docker-compose up -d

            print_status "¡Listo! Todo reconstruido desde cero"
        else
            print_warning "Operación cancelada"
            exit 0
        fi
        ;;
    *)
        print_error "Opción inválida"
        exit 1
        ;;
esac

# Mostrar estado
echo ""
echo "📊 Estado de los contenedores:"
docker-compose ps

# Mostrar logs
echo ""
echo "📝 Últimas líneas de logs:"
echo ""
docker-compose logs --tail=10

echo ""
print_status "Reconstrucción completada"
echo ""
echo "💡 Comandos útiles:"
echo "   - Ver logs en tiempo real:  docker-compose logs -f"
echo "   - Verificar salud:          curl http://localhost:3000/api/health"
echo "   - Reiniciar servicios:      docker-compose restart"
echo "   - Detener todo:             docker-compose down"
echo ""
