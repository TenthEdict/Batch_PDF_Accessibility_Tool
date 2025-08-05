# Unified PDF Accessibility Engine

Core processing engine for PDF accessibility enhancement with OCR and metadata improvements.

## Usage

```bash
# Basic processing
python -m processor.unified_project.src.main process input.pdf output.pdf --mode academic

# With enhanced features
python -m processor.unified_project.src.main process input.pdf output.pdf \
  --mode academic \
  --use-adobe-autotag \
  --generate-accessibility-report

# Docker processing
docker build -f Dockerfile.academic -t epubs/academic_processor .
docker run --rm -v /path/to/input.pdf:/data/input.pdf -v /path/to/output:/data/output epubs/academic_processor
```

## Configuration

Academic mode optimized for modern academic papers with:
- 200 DPI OCR processing
- Mathematical content detection
- Table and figure recognition
- Citation pattern analysis
