#!/bin/bash
# =============================================================================
# News Scraper - VPS Installation Script
# For Ubuntu/Debian Linux servers
# =============================================================================

set -e

echo "=========================================="
echo "  News Scraper - VPS Installation"
echo "=========================================="

# Update system
echo "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.11
echo "Installing Python 3.11..."
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install system dependencies for Playwright
echo "Installing Playwright dependencies..."
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    fonts-liberation \
    fonts-noto-color-emoji \
    xvfb

# Install OpenCV dependencies
echo "Installing OpenCV dependencies..."
sudo apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1

# Create virtual environment
echo "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright Chromium browser..."
playwright install chromium
playwright install-deps chromium

# Create directories
echo "Creating directories..."
mkdir -p data/raw data/processed data/images logs

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/news-scraper.service > /dev/null <<EOF
[Unit]
Description=News Scraper Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$(pwd)/venv/bin/python -u -m src.main_with_pipeline
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy your .env file with credentials"
echo "2. Start the service: sudo systemctl start news-scraper"
echo "3. Enable on boot: sudo systemctl enable news-scraper"
echo "4. Check logs: sudo journalctl -u news-scraper -f"
echo ""
