#!/bin/bash

# Script de Verificación de Stealth Mode
# Ejecutar después de: docker-compose up -d

echo "🔍 Verificando Stealth Mode..."
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check logs
check_log() {
    local pattern=$1
    local description=$2

    if docker-compose logs scraper 2>&1 | grep -q "$pattern"; then
        echo -e "${GREEN}✅${NC} $description"
        return 0
    else
        echo -e "${RED}❌${NC} $description"
        return 1
    fi
}

# Check if container is running
echo "1. Container Status:"
if docker ps | grep -q "periodico-scraper"; then
    echo -e "${GREEN}✅${NC} Container is running"
else
    echo -e "${RED}❌${NC} Container is NOT running"
    echo ""
    echo "Por favor ejecuta: docker-compose up -d"
    exit 1
fi

echo ""
echo "2. Stealth Features:"
sleep 2

# Check stealth mode enabled
check_log "Stealth mode: ENABLED" "Stealth mode activado"

# Check user agent rotation
check_log "User-Agent: Mozilla" "User-Agent configurado"

# Check viewport
check_log "Viewport: (" "Viewport variable"

# Check rate limiting
check_log "Rate limit: " "Rate limiting activo"

# Check delays
check_log "Human-like delay" "Delays aleatorios con jitter"

# Check rate limit stats
check_log "Rate limit stats" "Rate limiting funcionando"

# Check article processing
check_log "waiting.*before next" "Delays entre artículos"

echo ""
echo "3. Performance Metrics:"

# Get last 50 lines of logs
logs=$(docker-compose logs --tail=50 scraper 2>&1)

# Count articles scraped
articles=$(echo "$logs" | grep -c "Scraped article:")
if [ "$articles" -gt 0 ]; then
    echo -e "${GREEN}✅${NC} Artículos scrapeados: $articles"
else
    echo -e "${YELLOW}⚠️${NC}  Aún no hay artículos scrapeados (puede estar iniciando)"
fi

# Check for errors
errors=$(echo "$logs" | grep -c "ERROR")
if [ "$errors" -eq 0 ]; then
    echo -e "${GREEN}✅${NC} Sin errores"
else
    echo -e "${RED}❌${NC} Errores detectados: $errors"
    echo ""
    echo "Últimos errores:"
    docker-compose logs --tail=50 scraper 2>&1 | grep "ERROR" | tail -5
fi

# Check for image uploads
images=$(echo "$logs" | grep -c "✅.*uploaded to Supabase")
if [ "$images" -gt 0 ]; then
    echo -e "${GREEN}✅${NC} Imágenes subidas a Supabase: $images"
else
    echo -e "${YELLOW}⚠️${NC}  Aún no hay imágenes subidas"
fi

echo ""
echo "4. Rate Limiting Stats:"

# Get rate limit utilization
rate_stats=$(docker-compose logs --tail=100 scraper 2>&1 | grep "Rate limit stats" | tail -1)
if [ -n "$rate_stats" ]; then
    echo -e "${GREEN}✅${NC} $rate_stats"
else
    echo -e "${YELLOW}⚠️${NC}  Aún no hay estadísticas de rate limiting"
fi

echo ""
echo "5. Last 10 Log Lines:"
echo "─────────────────────────────────────────────────────"
docker-compose logs --tail=10 scraper 2>&1
echo "─────────────────────────────────────────────────────"

echo ""
echo "📊 Resumen:"
echo "• Stealth mode debe estar ENABLED"
echo "• User-Agent debe rotar aleatoriamente"
echo "• Delays deben ser entre 2-5 segundos"
echo "• Rate limit debe mostrar utilización < 100%"
echo ""
echo "Para ver logs en tiempo real:"
echo "  docker-compose logs -f scraper"
echo ""
echo "Para detener:"
echo "  docker-compose down"
echo ""
