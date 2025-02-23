# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install build tools and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    make \
    libjpeg-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    libtesseract-dev \
    tesseract-ocr \
    tesseract-ocr-eng \ 
    tesseract-ocr-osd \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    poppler-utils \
    poppler-data \
    libpoppler-dev \
    libpoppler-cpp-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV PYTHONPATH=/app/src

# Set pip configurations
ENV PIP_DEFAULT_TIMEOUT=300
ENV PIP_RETRIES=10

# Install numpy 1.x first to ensure compatibility
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir 'numpy<2.0.0'

# Install base Python packages
COPY requirements.txt ./
RUN pip install --no-cache-dir pandas pytesseract Pillow pdf2image anthropic>=0.18.0

# Install OpenCV based on architecture
RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
    pip install --no-cache-dir opencv-python-headless==4.8.0.76; \
    else \
    pip install --no-cache-dir opencv-python==4.8.0.76; \
    fi

# Install remaining Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Verify Tesseract installation
RUN tesseract --version && \
    tesseract --list-langs && \
    python3 -c "import pytesseract; print('Pytesseract version:', pytesseract.get_tesseract_version())"

# Copy project files
COPY setup.py config.yaml pdfUA-ID.xmp key.txt ./
COPY src/ ./src/

# Create directories and install project
RUN mkdir -p input \
    output/corrections \
    output/reports \
    output/processed_pdfs \
    output/logs \
    output/ocr_results \
    output/tagged \
    output/final \
    output/analysis && \
    pip install -e .

# Create and configure entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set volume for input/output
VOLUME ["/app/input", "/app/output"]

# Use entrypoint script to handle different commands
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["process"]