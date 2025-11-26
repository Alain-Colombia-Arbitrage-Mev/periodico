#!/bin/bash
set -e

# ============================================================================
# Entrypoint script for News Scraper - Railway optimized
# ============================================================================

echo "=========================================="
echo "  News Scraper - Starting"
echo "=========================================="

# Display environment info
echo "Python version: $(python --version)"
echo "Playwright version: $(python -c 'import playwright; print(playwright.__version__)' 2>/dev/null || echo 'Not installed')"
echo "Working directory: $(pwd)"
echo ""

# Validate required environment variables
echo "Validating environment variables..."

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ ERROR: SUPABASE_URL is not set"
    exit 1
fi

if [ -z "$SUPABASE_KEY" ]; then
    echo "❌ ERROR: SUPABASE_KEY is not set"
    exit 1
fi

echo "✅ Supabase configuration validated"

# Check LLM configuration (optional)
if [ "${LLM_REWRITE_ENABLED:-true}" = "true" ]; then
    if [ -z "$OPENROUTER_API_KEY" ]; then
        echo "⚠️  WARNING: LLM_REWRITE_ENABLED is true but OPENROUTER_API_KEY is not set"
        echo "⚠️  LLM rewriting will be disabled"
        export LLM_REWRITE_ENABLED=false
    else
        echo "✅ OpenRouter API key configured"
        echo "✅ LLM model: ${LLM_MODEL:-anthropic/claude-3.5-sonnet}"
    fi
else
    echo "ℹ️  LLM rewriting is disabled"
fi

# Display configuration
echo ""
echo "Configuration:"
echo "  - Run mode: ${RUN_MODE:-continuous}"
echo "  - Scrape interval: ${SCRAPE_INTERVAL:-43200}s ($(( ${SCRAPE_INTERVAL:-43200} / 3600 ))h)"
echo "  - Max articles per category: ${MAX_ARTICLES_PER_CATEGORY:-20}"
echo "  - Delete old articles: ${DELETE_OLD_ARTICLES:-true}"
echo "  - Old articles days: ${OLD_ARTICLES_DAYS:-3}"
echo "  - LLM rewrite enabled: ${LLM_REWRITE_ENABLED:-true}"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p /app/data/raw /app/data/processed /app/data/images /app/logs
echo "✅ Directories created"
echo ""

# Verify Playwright browser installation
echo "Verifying Playwright installation..."
if python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(); browser.close(); p.stop()" 2>/dev/null; then
    echo "✅ Playwright Chromium is ready"
else
    echo "⚠️  WARNING: Playwright Chromium verification failed"
    echo "Attempting to install browsers..."
    playwright install chromium --with-deps || echo "❌ Failed to install Chromium"
fi

echo ""
echo "=========================================="
echo "  Starting application..."
echo "=========================================="
echo ""

# Execute the command passed to the container
exec "$@"
