# syntax=docker/dockerfile:1

# ============================================================================
# News Scraper - Using official Playwright image for browser support
# ============================================================================

FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY entrypoint.sh .

# Create necessary directories with proper permissions
RUN mkdir -p /app/data/raw /app/data/processed /app/data/images /app/logs && \
    chmod -R 755 /app && \
    chmod +x /app/entrypoint.sh

# Health check - verify Python and Chromium are working
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Expose port for Railway (optional - for future health endpoints)
EXPOSE 8080

# Use entrypoint script for flexible command handling
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command: Run pipeline continuously
CMD ["python", "-u", "-m", "src.main_with_pipeline"]
