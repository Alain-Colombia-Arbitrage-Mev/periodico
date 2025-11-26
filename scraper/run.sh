#!/bin/bash
# Quick run script for the scraper

set -e

echo "🚀 News Scraper Launcher"
echo "========================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env with your settings before continuing!"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running"
    exit 1
fi

echo "✅ Docker is ready"
echo ""

# Menu
echo "Select an option:"
echo "1) Build and start (continuous mode)"
echo "2) Run once and exit"
echo "3) Start with pgAdmin"
echo "4) View logs"
echo "5) Stop all services"
echo "6) Export data to JSON"
echo "7) Clean all data"
echo ""

read -p "Enter option (1-7): " option

case $option in
    1)
        echo "🏗️  Building and starting scraper..."
        docker-compose up --build
        ;;
    2)
        echo "▶️  Running scraper once..."
        docker-compose run -e RUN_MODE=once --rm scraper
        ;;
    3)
        echo "🚀 Starting with pgAdmin..."
        docker-compose --profile admin up --build
        echo ""
        echo "📊 pgAdmin available at: http://localhost:5050"
        echo "   Email: admin@scraper.local"
        echo "   Password: admin123"
        ;;
    4)
        echo "📋 Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f scraper
        ;;
    5)
        echo "🛑 Stopping services..."
        docker-compose down
        echo "✅ Services stopped"
        ;;
    6)
        echo "💾 Exporting data..."
        docker-compose exec scraper python src/export_data.py --format json --limit 1000
        echo "✅ Data exported to data/processed/"
        ;;
    7)
        read -p "⚠️  This will delete all scraped data. Continue? (y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            echo "🗑️  Cleaning data..."
            rm -rf data/raw/* data/processed/* data/images/*/* logs/*
            docker-compose down -v
            echo "✅ Data cleaned"
        else
            echo "❌ Cancelled"
        fi
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
