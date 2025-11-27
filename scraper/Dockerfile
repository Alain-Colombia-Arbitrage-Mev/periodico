# syntax=docker/dockerfile:1

# ============================================================================
# News Scraper - Full featured with Playwright browser support
# Optimized for Linux VPS deployment
# ============================================================================

FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# Install system dependencies for Playwright and OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Essential
    ca-certificates \
    wget \
    curl \
    gnupg \
    # Playwright browser dependencies
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
    # Fonts for proper rendering
    fonts-liberation \
    fonts-noto-color-emoji \
    # OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only for smaller size)
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy application code
COPY src/ ./src/
COPY entrypoint.sh .

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/processed /app/data/images /app/logs && \
    chmod -R 755 /app && \
    chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Expose port
EXPOSE 8080

# Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["python", "-u", "-m", "src.main_with_pipeline"]
