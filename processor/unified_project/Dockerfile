# Multi-stage build for ePubs Accessibility Enhancement
FROM python:3.12-slim AS base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ENV PYTHONPATH=/app
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies optimized for the current project
RUN apt-get update && apt-get install -y \
    # OCR and PDF processing (core dependencies)
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-osd \
    poppler-utils \
    libpoppler-dev \
    ghostscript \
    # Image processing libraries
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    # Image optimization tools (for OCRmyPDF)
    pngquant \
    # Utilities
    file \
    curl \
    git \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Development stage with additional tools
FROM base AS development

# Install development dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

WORKDIR /app

# Copy project files
COPY ../../pyproject.toml ../../README.md ./
COPY ../../processor/ ./processor/
COPY ../../scraper/ ./scraper/

# Install with development dependencies
RUN pip install --no-cache-dir -e .[dev,web]

# Create data directories
RUN mkdir -p /data/input /data/output /data/logs \
    && chmod 755 /data/input /data/output /data/logs

# Copy entrypoint
COPY processor/unified_project/scripts/docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Production stage (minimal)
FROM base AS production

WORKDIR /app

# Copy project files
COPY ../../pyproject.toml ../../README.md ./
COPY ../../processor/ ./processor/
COPY ../../scraper/ ./scraper/

# Install only production dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -e .[web]

# Create data directories with proper permissions
RUN mkdir -p /data/input /data/output /data/logs \
    && chmod 755 /data/input /data/output /data/logs

# Copy and make entrypoint executable
COPY processor/unified_project/scripts/docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user for security
RUN groupadd -r epubs && useradd -r -g epubs epubs \
    && chown -R epubs:epubs /app /data

# Switch to non-root user
USER epubs

# Health check - updated to use the new CLI structure
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import processor.unified_project.src.main; print('OK')" || exit 1

# Use updated entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default to showing help
CMD ["--help"]