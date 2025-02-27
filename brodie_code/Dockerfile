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
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ENV PYTHONPATH=/app/src

# Set pip configurations
ENV PIP_DEFAULT_TIMEOUT=300
ENV PIP_RETRIES=10

# Install numpy 1.x first to ensure compatibility
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir 'numpy<2.0.0'

# Install base Python packages with a longer timeout and one-by-one to avoid build issues
COPY requirements.txt ./
RUN pip install --no-cache-dir --timeout=600 pandas && \
    pip install --no-cache-dir --timeout=600 pytesseract && \
    pip install --no-cache-dir --timeout=600 Pillow && \
    pip install --no-cache-dir --timeout=600 pdf2image && \
    pip install --no-cache-dir --timeout=600 'anthropic>=0.18.0'

# Install OpenCV based on architecture
RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
    pip install --no-cache-dir --timeout=600 opencv-python-headless==4.8.0.76; \
    else \
    pip install --no-cache-dir --timeout=600 opencv-python==4.8.0.76; \
    fi

# Install remaining Python dependencies one-by-one for better reliability
RUN pip install --no-cache-dir --timeout=600 'PyMuPDF>=1.22.5' && \
    pip install --no-cache-dir --timeout=600 'pandas>=1.5.0' && \
    pip install --no-cache-dir --timeout=600 'tqdm>=4.62.0' && \
    pip install --no-cache-dir --timeout=600 'pyyaml>=6.0.0' && \
    pip install --no-cache-dir --timeout=600 'openpyxl>=3.0.0' && \
    pip install --no-cache-dir --timeout=600 'pikepdf>=8.3.0' && \
    pip install --no-cache-dir --timeout=600 'python-xmp-toolkit>=2.0.2' && \
    pip install --no-cache-dir --timeout=600 'scipy>=1.7.0' && \
    pip install --no-cache-dir --timeout=600 'scikit-image>=0.18.0'

# Verify Tesseract installation
RUN tesseract --version && \
    tesseract --list-langs && \
    python3 -c "import pytesseract; print('Pytesseract version:', pytesseract.get_tesseract_version())"

# Update the COPY commands in the Dockerfile
COPY setup.py config.yaml pdfUA-ID.xmp key.txt ./
COPY requirements.txt ./ 
COPY src/ ./src/

# Make sure the Tesseract data directory exists with correct permissions
RUN mkdir -p "$TESSDATA_PREFIX/configs" "$TESSDATA_PREFIX/historical_words" && \
    chmod -R 755 "$TESSDATA_PREFIX"

# Update directory creation
RUN mkdir -p \
    input \
    output/corrections \
    output/reports \
    output/processed_pdfs \
    output/logs \
    output/ocr_results \
    output/tagged \
    output/final \
    output/analysis && \
    chown -R root:root input output && \
    chmod -R 775 input output && \
    pip install -e . && \
    python -m src.accessibility_checker.ocr.setup_historical_resources

# Copy and configure entrypoint script
COPY shell_scripts/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Clean up any stray pip files
RUN rm -f /app/=*

# Set volume for input/output
VOLUME ["/app/input", "/app/output"]

# Use entrypoint script to handle different commands
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["process"]