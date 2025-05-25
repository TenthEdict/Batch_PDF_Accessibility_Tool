# Installation Guide - ePubs Accessibility Enhancement Project

## Quick Installation

```bash
# Clone the repository
git clone https://github.com/schipp0/ePubs_Main.git
cd ePubs_Main

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix/MacOS
# venv\Scripts\activate   # Windows

# Install core dependencies
pip install -e .
```

## Dependency Groups

The project uses modern Python packaging with optional dependency groups:

### Core Dependencies (Always Installed)
- **PDF Processing**: PyMuPDF, pikepdf, pdf2image, pdfplumber
- **Image Processing**: Pillow, OpenCV, scikit-image, numpy
- **OCR**: pytesseract
- **Data Processing**: pandas, scipy
- **Configuration**: PyYAML, python-decouple
- **CLI/UI**: click, rich

### Optional Dependencies

#### Web Scraping (`[web]`)
```bash
pip install -e .[web]
```
Includes: selenium, requests, beautifulsoup4, urllib3

#### Document Formats (`[docs]`)
```bash
pip install -e .[docs]
```
Includes: python-docx, python-pptx, openpyxl, python-xmp-toolkit

#### Machine Learning (`[ml]`)
```bash
pip install -e .[ml]
```
⚠️ **Heavy Dependencies** (~2GB): torch, transformers, huggingface-hub, anthropic

#### Apple Silicon Optimization (`[apple]`)
```bash
pip install -e .[apple]
```
Includes: mlx-vlm (for Apple Silicon Macs)

#### Advanced Analysis (`[advanced]`)
```bash
pip install -e .[advanced]
```
Includes: docling-core

#### Development Tools (`[dev]`)
```bash
pip install -e .[dev]
```
Includes: pytest, black, isort, flake8, mypy, pre-commit

#### Testing Only (`[test]`)
```bash
pip install -e .[test]
```
Includes: pytest, pytest-cov, pytest-mock, hypothesis

#### Everything (`[all]`)
```bash
pip install -e .[all]
```
Installs all optional dependencies except ML and development tools.

## System Dependencies

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-eng python3-magic
```

### macOS
```bash
brew install poppler tesseract libmagic
```

### Windows
1. Install [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
2. Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract/wiki/Downloads)
3. Add both to your PATH

## CLI Scripts

After installation, these commands are available:

### Academic Paper Processing
```bash
# Process single PDF
epubs-process-academic input.pdf output.pdf

# Batch process directory
epubs-process-academic --batch input_dir output_dir

# With options
epubs-process-academic input.pdf output.pdf \
  --detect-math \
  --detect-citations \
  --max-workers 4 \
  --timeout 1800
```

### Web Scraping
```bash
# Single URL
epubs-scrape --url https://example.com/document.pdf

# Multiple URLs from file
epubs-scrape --file urls.txt --workers 3

# With authentication
epubs-scrape --url https://library.edu/doc.pdf \
  --username your_username \
  --password your_password
```

### Workflow Automation
```bash
# Automated download and processing
epubs-automate --base-url https://library.edu/papers/ \
  --run-id "2024-01-batch" \
  --log-level INFO
```

## Development Setup

For development work:

```bash
# Install with development dependencies
pip install -e .[dev]

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest

# Run code formatting
black .
isort .

# Run type checking
mypy processor scraper automation

# Run linting
flake8
```

## Docker Installation

### Build Images
```bash
# Academic processing
docker build -f processor/unified_project/Dockerfile.academic \
  -t epubs/academic:latest processor/unified_project/

# General processing
docker build -f processor/unified_project/Dockerfile \
  -t epubs/unified:latest processor/unified_project/
```

### Run with Docker
```bash
# Process single document
docker run --rm \
  -v /path/to/input.pdf:/data/input/document.pdf \
  -v /path/to/output:/data/output \
  epubs/academic:latest \
  --mode academic /data/input/document.pdf /data/output/accessible.pdf

# Batch processing
docker run --rm \
  -v /path/to/input_dir:/data/input \
  -v /path/to/output_dir:/data/output \
  epubs/academic:latest \
  --batch /data/input /data/output
```

## Configuration

The project uses hierarchical YAML configuration:

### Default Configuration
- Location: `processor/unified_project/config/default.yaml`
- Contains general settings for all document types

### Academic Configuration  
- Location: `processor/unified_project/config/academic.yaml`
- Optimized for modern academic papers

### Custom Configuration
```bash
# Use custom config
epubs-process-academic input.pdf output.pdf \
  --config /path/to/custom/config.yaml
```

## Troubleshooting

### Common Issues

#### 1. Tesseract Not Found
```
Error: Tesseract is not installed or it's not in your PATH
```
**Solution**: Install tesseract-ocr system package and ensure it's in PATH.

#### 2. OpenCV Installation Issues
```
Error: Failed to install opencv-python
```
**Solution**: Try opencv-python-headless instead:
```bash
pip install opencv-python-headless
```

#### 3. Permission Errors
```
Error: Permission denied
```
**Solution**: Use virtual environment or `--user` flag:
```bash
pip install --user -e .
```

#### 4. Memory Issues with Large PDFs
```
Error: Memory limit exceeded
```
**Solution**: Reduce max workers or increase system memory:
```bash
epubs-process-academic input.pdf output.pdf --max-workers 1
```

#### 5. ML Dependencies Too Large
**Solution**: Install without ML dependencies:
```bash
pip install -e .  # Core only
# Skip: pip install -e .[ml]
```

### Dependency Conflicts

If you encounter dependency conflicts:

1. **Start fresh**:
   ```bash
   rm -rf venv/
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

2. **Check versions**:
   ```bash
   pip list | grep -E "(PyMuPDF|pikepdf|opencv|numpy)"
   ```

3. **Use requirements-lock.txt** for exact versions:
   ```bash
   pip install -r requirements-lock.txt
   ```

### Performance Optimization

#### For Large Document Processing
```bash
# Reduce memory usage
epubs-process-academic input.pdf output.pdf \
  --max-workers 1 \
  --timeout 3600

# Use headless OpenCV
pip uninstall opencv-python
pip install opencv-python-headless
```

#### For Batch Processing
```bash
# Optimize for throughput
epubs-process-academic --batch input_dir output_dir \
  --max-workers 4 \
  --timeout 1800
```

## Verification

Verify your installation:

```bash
# Test core imports
python -c "
import fitz, pikepdf, cv2, pytesseract
import numpy as np, pandas as pd
print('✓ Core dependencies working')
"

# Test CLI
epubs-process-academic --help

# Test with sample document (if available)
epubs-process-academic sample.pdf output.pdf --verbose
```

## Migration from Old System

If you're upgrading from the old requirements.txt system:

1. **Backup your environment**:
   ```bash
   pip freeze > old_requirements.txt
   ```

2. **Install new system**:
   ```bash
   pip install -e .
   ```

3. **Test functionality**:
   ```bash
   # Test your existing workflows
   ```

4. **Remove deprecated files** (after testing):
   ```bash
   rm requirements.txt.deprecated
   rm processor/unified_project/requirements.txt.deprecated
   ```

For more detailed migration information, see [DEPENDENCY_MIGRATION_NOTICE.md](./DEPENDENCY_MIGRATION_NOTICE.md).

## Support

- **Issues**: [GitHub Issues](https://github.com/schipp0/ePubs_Main/issues)
- **Documentation**: [Project Wiki](https://github.com/schipp0/ePubs_Main/wiki)
- **Refactoring Plan**: [REFACTORING_PLAN.md](./REFACTORING_PLAN.md)