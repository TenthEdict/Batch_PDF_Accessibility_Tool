# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Build & Setup
- Install dependencies: `pip install -e .` (installs in editable mode)
- Install dev dependencies: `pip install -e .[dev]` or `pip install -e .[test]`
- Install all optional dependencies: `pip install -e .[all]`

### Testing
- Run all tests: `pytest`
- Run specific component tests: `cd processor/unified_project && python -m unittest discover tests`
- Run with coverage: `pytest --cov=epubs_accessibility --cov-report=html`
- Run only unit tests: `pytest -m unit`
- Run integration tests: `pytest -m integration`

### Code Quality
- Format code: `black .`
- Sort imports: `isort .`
- Lint code: `flake8`
- Type checking: `mypy processor scraper automation`

### Document Processing
- CLI entry point: `epubs process input.pdf output.pdf --mode academic`
- Academic processing script: `processor/unified_project/scripts/process_academic.sh input.pdf output.pdf`
- Batch processing: `processor/unified_project/scripts/process_academic.sh --batch input_dir output_dir`
- Directory processing: `python processor/unified_project/src/process_directory.py`
- Web scraping: `epubs-scrape --url https://docs.lib.purdue.edu/modvis/2024/va`

## Project Architecture

### Clean Architecture Pattern
The project follows clean architecture with clear separation of concerns:

- **Domain Layer** (`src/domain/`): Core business entities and rules
- **Application Layer** (`src/services/`): Business logic orchestration  
- **Infrastructure Layer** (`src/repositories/`, `src/enhancers/`): External dependencies
- **Interface Layer** (`src/main.py`): CLI and user interfaces

### Service Container & Dependency Injection
Uses a custom service container (`src/core/service_container.py`) for dependency management:
- Services are registered as factories with singleton behavior by default
- All services are auto-registered in `register_default_services()`
- Access services via `container.get("service_name")`

### Enhancement Pipeline
Document processing follows a multi-stage enhancement pipeline:

1. **OCR Enhancement** (`src/enhancers/ocr_enhancer.py`): Adds searchable text layer
2. **Adobe AutoTag** (`src/enhancers/adobe_autotag_enhancer.py`): AI-powered structure tagging (optional)
3. **PDF Enhancement** (`src/enhancers/pdf_enhancer.py`): Metadata and accessibility features

The `EnhancementService` orchestrates this pipeline with graceful fallbacks.

### Configuration Management
- YAML-based configuration in `config/` directory
- Schema validation using `src/config/epubs_schema.py`
- Mode-specific configs: `academic.yaml`, `default.yaml`
- Environment-aware configuration loading

### Document Types & Modes
- **Academic Mode**: Optimized for scholarly papers with citations, formulas, tables
- **Basic Mode**: General document processing
- Specialized academic processing includes citation detection, math recognition, and scholarly structure analysis

## Key Components

### Adobe PDF Services Integration
- Optional cloud-based enhancement using Adobe PDF Services AutoTag
- Credentials-based activation (falls back gracefully if unavailable)
- Generates accessibility reports and optimizes document structure
- Configuration in `adobe_autotag` section of YAML configs

### Web Scraping (`scraper/`)
- Purdue library document downloader
- Selenium-based with Chrome driver automation
- Handles authentication and batch downloads

### Batch Processing
- Advanced batch processor: `advanced_batch_processor.py`
- Cloud batch processing: `cloud_batch_process.sh`
- Docker-based containerized processing

## Testing Strategy

### Test Organization
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Pytest markers: `unit`, `integration`, `slow`, `ocr`, `gpu`

### Test Configuration
- Coverage targets all main packages
- Parallel test execution with `pytest-xdist`
- Property-based testing with `hypothesis`
- Mock-based testing with `pytest-mock`

## Docker Support

### Container Images
- Main processor: `processor/unified_project/Dockerfile`
- Academic-specific: `processor/unified_project/Dockerfile.academic`
- Entry point script: `scripts/docker-entrypoint.sh`

### Usage
```bash
docker build -f processor/unified_project/Dockerfile -t epubs/processor:latest processor/unified_project/
docker run --rm -v /input:/data/input -v /output:/data/output epubs/processor:latest --mode academic /data/input/doc.pdf /data/output/enhanced.pdf
```

## Development Notes

### System Dependencies
- poppler-utils (PDF manipulation)
- tesseract-ocr (OCR engine)
- Docker (for containerized processing)

### Python Version Support
- Minimum: Python 3.9
- Tested: 3.9, 3.10, 3.11, 3.12

### Code Conventions
- Black formatting (88 character line length)
- isort import sorting with "black" profile
- Type hints required for all functions
- Comprehensive logging using Python logging module (avoid print statements)