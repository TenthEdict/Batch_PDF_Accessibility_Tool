FROM python:3.11-slim AS base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ENV PYTHONPATH=/app

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

# Create production image
FROM base AS production

WORKDIR /app

# Copy project root files for installation
COPY ../../pyproject.toml ../../README.md ./

# Copy the entire project structure to maintain proper imports
COPY ../../processor/ ./processor/
COPY ../../scraper/ ./scraper/

# Install Python dependencies from pyproject.toml
# Install with web dependencies for full functionality
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -e .[web]

# Create data directories with proper permissions
RUN mkdir -p /data/input /data/output /data/logs \
    && chmod 755 /data/input /data/output /data/logs

# Copy and make entrypoint executable
COPY processor/unified_project/scripts/docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import processor.unified_project.src.main; print('OK')" || exit 1

# Use updated entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default to showing help
CMD ["--help"]