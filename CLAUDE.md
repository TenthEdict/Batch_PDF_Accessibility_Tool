# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Unix/MacOS
# venv\Scripts\activate   # Windows

# Install core dependencies (new unified system)
pip install -e .

# Install optional dependencies as needed
pip install -e .[web]      # Web scraping
pip install -e .[docs]     # Document format support
pip install -e .[ml]       # Machine learning features
pip install -e .[dev]      # Development tools
pip install -e .[all]      # All optional dependencies

# Install system dependencies (Linux)
sudo apt-get install -y poppler-utils tesseract-ocr
```

### Processing Documents
```bash
# Process academic papers (new CLI)
epubs-process-academic input.pdf output.pdf
epubs-process-academic --batch input_directory output_directory

# Legacy shell scripts (still available)
./processor/unified_project/scripts/process_academic.sh input.pdf output.pdf
./processor/unified_project/scripts/process_academic.sh --batch input_directory output_directory

# Web scraping
epubs-scrape --url https://example.com/document.pdf
epubs-scrape --file urls.txt --workers 3

# Workflow automation
epubs-automate --base-url https://library.example.com
```

### Docker
```bash
# Build Docker images
docker build -f processor/unified_project/Dockerfile.academic -t epubs/academic_processor:latest processor/unified_project/
docker build -f processor/unified_project/Dockerfile -t epubs/unified_processor:latest processor/unified_project/

# Run with Docker
docker run --rm -v /path/to/input.pdf:/data/input/document.pdf -v /path/to/output:/data/output \
  epubs/academic_processor:latest --mode academic /data/input/document.pdf /data/output/accessible.pdf
```

## Architecture

This project is focused on enhancing document accessibility for both academic and historical publications:

### Core Components
- **Service Container**: Central dependency injection system (`processor/unified_project/src/core/service_container.py`)
- **Enhancers**: Document transformation modules (`processor/unified_project/src/enhancers/`)
  - `enhancer_base.py`: Abstract base class for all enhancers
  - `basic_enhancer.py`: General document enhancements
  - `pdf_enhancer.py`: PDF-specific accessibility improvements
- **OCR**: Text recognition and processing (`processor/unified_project/src/ocr/`)
  - Specialized processors for different document types
  - Historical document optimizations in `processor/brodie_code/`
- **Validation**: Accessibility compliance checking (`processor/unified_project/src/validation/`)
  - Rules-based validation in `rules.py`
  - `accessibility_validator.py`: Main validation engine

### Project Structure
- **Configuration**: YAML files in `processor/unified_project/config/` control processing behavior
- **Academic Processing**: Specialized modules in `processor/unified_project/src/academic/` for academic papers
- **Automation**: Workflow scripts in `automation/` directory
- **Scraper**: Document acquisition tools in `scraper/` directory

### Extension Pattern
New capabilities should:
1. Implement interfaces defined in `processor/unified_project/src/core/interfaces.py`
2. Register with the service container for dependency management
3. Follow existing patterns for document type specialization