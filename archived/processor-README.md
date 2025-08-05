# ePubs Document Processor

Core document processing components for PDF accessibility enhancement.

## Features

- PDF/UA compliance and accessibility tagging
- OCR enhancement with searchable text layer
- Cross-platform support (macOS/Ubuntu)

## Quick Start

```bash
# Process a single document
python -m processor.unified_project.src.main process input.pdf output.pdf --mode academic

# Process with Docker
docker build -f unified_project/Dockerfile.academic -t epubs/processor .
docker run --rm -v /path/to/input.pdf:/data/input.pdf -v /path/to/output:/data/output epubs/processor
```

## Requirements

- Python 3.9+
- System dependencies: `poppler-utils`, `tesseract-ocr`
