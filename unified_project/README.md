# Unified PDF Accessibility Project

## Overview
The unified project combines capabilities for enhancing document accessibility across both historical documents and modern academic publications. This integrated framework provides consistent processing while offering specialized handling for different document types.

## Features

### Core Capabilities
- **Unified Processing Framework**: Common architecture for all document types
- **PDF/UA Compliance**: Ensures output documents meet accessibility standards
- **Screen Reader Optimization**: Proper tagging and reading order
- **Docker Support**: Containerized execution for consistent processing
- **Extensible Architecture**: Service container for dependency injection

### Academic Document Support
- **Modern Academic Layout Analysis**: Specialized handling for complex layouts
- **Mathematical Content Processing**: Enhanced handling of equations and formulas
- **Table Structure Preservation**: Maintains semantic structure with proper headers
- **Citation Pattern Recognition**: Detects various citation formats
- **Multi-Column Processing**: Correctly handles academic journal layouts

### Historical Document Support
- **Historical Document Detection**: Automatic document characteristics analysis
- **Specialized OCR Processing**: Optimized for mid-20th century documents and degraded text
- **Mid-Century Terminology Support**: Optimized for documents from 1950s onward

## Directory Structure
- `/src` - Core source code
  - `/academic` - Academic paper specific processors
  - `/enhancers` - Document enhancement modules
  - `/core` - Core framework components
  - `/ocr` - OCR processors
  - `/validation` - Accessibility validation tools
- `/tests` - Test files and validation scripts
- `/config` - Configuration files
- `/scripts` - Automation and utility scripts
- `/resources` - Dictionaries and reference data

## Setup and Usage

### Installation
1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`

### Academic Paper Processing
Process a single academic paper:
```bash
./scripts/process_academic.sh input.pdf output.pdf
```

Process a batch of academic papers:
```bash
./scripts/process_academic.sh --batch input_directory output_directory
```

Customize resource allocation for large or complex papers:
```bash
./scripts/process_academic.sh --memory 16g --cpus 8 --timeout 3600 input.pdf output.pdf
```

For detailed information on academic paper processing, see [README.ACADEMIC.md](README.ACADEMIC.md).

### Historical Document Processing
Process historical documents using the unified framework:
```bash
./scripts/process_document.sh --mode historical input.pdf output.pdf
```

For detailed information on the refactoring plan and architecture, see [README.REFACTORING.md](README.REFACTORING.md).

## Docker Support
The project is optimized for containerized execution:

### Build the Docker Images
```bash
# Academic paper processor
docker build -f Dockerfile.academic -t epubs/academic_processor:latest .

# Standard processor
docker build -f Dockerfile -t epubs/unified_processor:latest .
```

### Run with Docker
```bash
# Academic paper processing
docker run --rm \
  -v /path/to/input.pdf:/data/input/document.pdf \
  -v /path/to/output:/data/output \
  epubs/academic_processor:latest \
  --mode academic \
  /data/input/document.pdf \
  /data/output/accessible.pdf

# Historical document processing
docker run --rm \
  -v /path/to/input.pdf:/data/input/document.pdf \
  -v /path/to/output:/data/output \
  epubs/unified_processor:latest \
  --mode historical \
  /data/input/document.pdf \
  /data/output/accessible.pdf
```

## Configuration
- Academic paper processing: `config/academic.yaml`
- Default configuration: `config/default.yaml`

Key configuration options include:
- OCR settings optimized for document type
- Content detection toggles for formulas, tables, etc.
- Structure detection settings for document analysis
- Performance tuning parameters
- Mode-specific processing options

## Integration with Other Components
The unified project serves as the integration point for all document processing capabilities:

- Uses OCR components from `brodie_code` for historical document detection
- Integrates accessibility validation from `accessibility_tools`
- Extends academic paper processing with enhanced algorithms

## Development
- Use the service container (`src/core/service_container.py`) for dependency injection
- Implement new enhancers by extending `src/enhancers/enhancer_base.py`
- Add document type support by creating processors in the appropriate directories