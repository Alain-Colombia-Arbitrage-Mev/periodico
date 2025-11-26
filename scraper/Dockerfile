# syntax=docker/dockerfile:1

# ============================================================================
# Multi-stage build for optimized Python news scraper - Railway optimized
# ============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

# Set build-time environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies to /install directory
RUN pip install --prefix=/install --no-warn-script-location -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Final image
# -----------------------------------------------------------------------------
FROM python:3.11-slim

# Set runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PATH="/install/bin:$PATH" \
    PYTHONPATH="/install/lib/python3.11/site-packages:$PYTHONPATH"

# Install system dependencies for Playwright Chromium
# Only essential packages for minimal image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core dependencies
    ca-certificates \
    wget \
    # Chromium dependencies
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python dependencies from builder
COPY --from=builder /install /install

# Set working directory
WORKDIR /app

# Install Playwright Chromium (in final stage to use runtime environment)
RUN playwright install chromium --with-deps

# Copy application code
COPY src/ ./src/
COPY entrypoint.sh .

# Create necessary directories with proper permissions
RUN mkdir -p /app/data/raw /app/data/processed /app/data/images /app/logs && \
    chmod -R 755 /app && \
    chmod +x /app/entrypoint.sh

# Health check - verify Python and Chromium are working
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys, playwright; sys.exit(0)" || exit 1

# Expose port for Railway (optional - for future health endpoints)
EXPOSE 8080

# Use entrypoint script for flexible command handling
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command: Run pipeline continuously
CMD ["python", "-u", "-m", "src.main_with_pipeline"]
