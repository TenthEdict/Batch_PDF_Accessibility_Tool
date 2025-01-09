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
    && rm -rf /var/lib/apt/lists/*

# Set pip configurations
ENV PIP_DEFAULT_TIMEOUT=300
ENV PIP_RETRIES=10

# Install base Python packages first
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy pandas pytesseract Pillow

# Install OpenCV based on architecture
RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        pip install --no-cache-dir opencv-python-headless; \
    else \
        pip install --no-cache-dir opencv-python; \
    fi

# Install remaining Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY setup.py config.yaml pdfUA-ID.xmp ./
COPY src/ ./src/

# Create directories and install project
RUN mkdir -p input output/corrections output/reports output/processed_pdfs \
    output/logs output/ocr_results output/tagged output/final && \
    pip install -e .

# Set volume for input/output
VOLUME ["/app/input", "/app/output"]

# Set the default command to run the PDF processor
CMD ["python", "-m", "accessibility_checker.core.batch"]
