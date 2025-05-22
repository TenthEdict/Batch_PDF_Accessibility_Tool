# ePubs Document Processor

Core document processing components for the ePubs Accessibility Enhancement Project, providing specialized tools for enhancing document accessibility across both historical and academic publications.

## Project Structure

The processor directory contains multiple components:

- **[/brodie_code](./brodie_code/)**: Historical document processing specialized code
- **[/unified_project](./unified_project/)**: Unified document processing framework

## Features

### Core Capabilities
- **Unified Processing Framework**: Common architecture for all document types
- **PDF/UA Compliance**: Ensures output documents meet accessibility standards
- **Screen Reader Optimization**: Proper tagging and reading order
- **Docker Support**: Containerized execution for consistent processing
- **Extensible Architecture**: Service container for dependency injection

### Document Type Support
- **Academic Documents**: Specialized handling for complex academic layouts, mathematical content, tables, citations, and multi-column formatting
- **Historical Documents**: Automatic document characteristic analysis, specialized OCR processing optimized for degraded text and historical terminology

## Setup and Usage

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix/MacOS
   # venv\Scripts\activate   # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r unified_project/requirements.txt
   ```

3. Install system dependencies:
   ```bash
   sudo apt-get install -y poppler-utils
   ```

### Processing Documents

```bash
# Process academic papers
./unified_project/scripts/process_academic.sh input.pdf output.pdf

# Process with batch mode
./unified_project/scripts/process_academic.sh --batch input_directory output_directory

# Process historical documents
./unified_project/scripts/process_document.sh --mode historical input.pdf output.pdf
```

### Docker Support

```bash
# Build Docker images
docker build -f unified_project/Dockerfile.academic -t epubs/academic_processor:latest unified_project/
docker build -f unified_project/Dockerfile -t epubs/unified_processor:latest unified_project/

# Run with Docker
docker run --rm -v /path/to/input.pdf:/data/input/document.pdf -v /path/to/output:/data/output \
  epubs/academic_processor:latest --mode academic /data/input/document.pdf /data/output/accessible.pdf
```

## Architecture

### Core Components
- **Service Container**: Central dependency injection system (`unified_project/src/core/service_container.py`)
- **Enhancers**: Document transformation modules (`unified_project/src/enhancers/`)
  - `enhancer_base.py`: Abstract base class for all enhancers
  - `basic_enhancer.py`: General document enhancements
  - `pdf_enhancer.py`: PDF-specific accessibility improvements
- **OCR**: Text recognition and processing (`unified_project/src/ocr/`)
  - Specialized processors for different document types
  - Historical document optimizations in `brodie_code/`
- **Validation**: Accessibility compliance checking (`unified_project/src/validation/`)
  - Rules-based validation in `rules.py`
  - `accessibility_validator.py`: Main validation engine

### Project Structure
- **Configuration**: YAML files in `unified_project/config/` control processing behavior
- **Academic Processing**: Specialized modules in `unified_project/src/academic/` for academic papers

## Development

### Extension Pattern
New capabilities should:
1. Implement interfaces defined in `unified_project/src/core/interfaces.py`
2. Register with the service container for dependency management
3. Follow existing patterns for document type specialization

### Testing
Run the test suite:
```bash
cd unified_project
python -m unittest discover tests
```

## Documentation

For more detailed information, see:
- [Unified Project README](./unified_project/README.md)
- [Academic Processing Documentation](./unified_project/README.ACADEMIC.md)