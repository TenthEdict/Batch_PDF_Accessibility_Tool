# Technical Context: ePubs Accessibility Enhancement

## Technologies Used

### Core Python Stack
- **Python 3.9+**: Minimum version for modern typing and performance features
- **pyproject.toml**: Modern Python packaging with dependency management
- **Poetry/pip**: Package management with lock file dependency resolution

### Document Processing Libraries
- **PyMuPDF (fitz) 1.22.5+**: Core PDF manipulation and text extraction
- **pikepdf 9.4.2+**: PDF structure manipulation and metadata management
- **ocrmypdf 16.10.2+**: OCR processing with Tesseract integration
- **Tesseract 5.5.1+**: OCR engine for text recognition
- **Pillow (PIL) 11.3.0+**: Image processing and manipulation

### Cloud Services Integration
- **Adobe PDF Services SDK 4.1.0+**: Cloud-based AI-powered structure tagging
- **Adobe AutoTag API**: Semantic document analysis and accessibility enhancement
- **REST API Integration**: HTTP-based cloud service communication

### CLI and Configuration
- **Typer 0.12.5+**: Modern CLI framework with type hints and validation
- **PyYAML**: Configuration management and environment-specific settings
- **Hydra**: Advanced configuration management for complex scenarios

### Development and Quality
- **pytest**: Testing framework with fixtures and parametrization
- **black**: Code formatting with 88-character line length
- **isort**: Import sorting with black profile compatibility
- **flake8**: Linting and code quality analysis
- **mypy**: Static type checking for enhanced reliability

## Development Setup

### System Dependencies

#### Windows
```powershell
# Option 1: Chocolatey (Recommended)
choco install python tesseract

# Option 2: Manual Installation
# Download and install from official sources:
# - Python: https://python.org/downloads/
# - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
```

#### macOS
```bash
brew install python tesseract poppler
```

#### Ubuntu/Debian
```bash
apt-get install python3 python3-pip tesseract-ocr poppler-utils
```

#### Docker
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y poppler-utils tesseract-ocr
```

### Python Environment Setup

#### Windows
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -e .[dev]    # Development installation
pip install -e .[test]   # Testing dependencies
pip install -e .[all]    # All optional dependencies
```

#### macOS/Linux
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .[dev]    # Development installation
pip install -e .[test]   # Testing dependencies
pip install -e .[all]    # All optional dependencies
```

### Adobe PDF Services Configuration
```bash
# Environment variables for cloud services
export ADOBE_CLIENT_ID="your_client_id"
export ADOBE_CLIENT_SECRET="your_client_secret"
export ADOBE_ORGANIZATION_ID="your_org_id"
export ADOBE_ACCOUNT_ID="your_account_id"
```

## Technical Constraints

### Memory and Performance
- **Large Document Handling**: PyMuPDF memory efficiency for documents >100MB
- **Batch Processing**: Parallel processing limited by available system memory
- **OCR Performance**: Tesseract processing time scales with document image complexity
- **Cloud API Limits**: Adobe PDF Services quota and rate limiting considerations

### Platform Compatibility
- **Operating Systems**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python Versions**: 3.9, 3.10, 3.11, 3.12 (tested and supported)
- **Container Platforms**: Docker, Podman, Kubernetes deployment ready
- **Architecture**: x86_64, ARM64 (M1/M2 Mac, ARM64 Windows) compatibility
- **Windows Notes**: Native Windows support with PowerShell and Command Prompt

### Document Format Support
- **Input Formats**: PDF (all versions), with focus on PDF 1.4+ for accessibility features
- **Output Standards**: PDF/UA-1 compliance, PDF 1.7+ for accessibility metadata
- **Text Encoding**: UTF-8 with Unicode support for international content
- **Image Handling**: JPEG, PNG, TIFF embedded images with accessibility descriptions

## Dependencies Architecture

### Core Dependencies (Required)
```toml
[project]
dependencies = [
    "typer>=0.12.5,<1.0.0",
    "PyMuPDF>=1.22.5,<2.0.0",
    "pikepdf>=9.4.2,<10.0.0",
    "ocrmypdf>=16.10.2,<17.0.0",
    "Pillow>=11.3.0,<12.0.0",
    "PyYAML>=6.0.1,<7.0.0",
]
```

### Optional Dependencies (Cloud Services)
```toml
[project.optional-dependencies]
cloud = [
    "pdfservices-sdk>=4.1.0,<5.0.0",
    "requests>=2.31.0,<3.0.0",
    "openpyxl>=3.1.0,<4.0.0",  # For accessibility reports
]
```

### Development Dependencies
```toml
dev = [
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.3.0",  # Parallel testing
]
```

### Machine Learning Dependencies
```toml
ml = [
    "scikit-learn>=1.7.1,<2.0.0",
    "pandas>=2.0.0,<3.0.0",
    "numpy>=1.24.0,<2.0.0",
    "joblib>=1.3.0,<2.0.0",  # Model persistence
]
```

## Architecture Patterns

### Clean Architecture Implementation
- **Domain Layer**: Core business entities and rules (`src/domain/`)
- **Application Layer**: Business logic orchestration (`src/services/`)
- **Infrastructure Layer**: External dependencies (`src/repositories/`, `src/enhancers/`)
- **Interface Layer**: CLI and user interfaces (`src/main.py`)

### Dependency Injection Pattern
- **Service Container**: Central dependency management (`src/core/service_container.py`)
- **Factory Pattern**: Service instantiation with singleton behavior
- **Interface Segregation**: Abstract base classes for component interfaces

### Enhancement Pipeline Architecture
- **Chain of Responsibility**: Sequential enhancement processing
- **Strategy Pattern**: Configurable enhancement strategies
- **Observer Pattern**: Progress tracking and logging
- **Command Pattern**: Encapsulated document operations

### Machine Learning Architecture
- **AdaptiveMLEnhancer**: Document-level learning and OCR optimization (677 lines)
- **Python ML Stack**: scikit-learn, pandas, numpy for all ML operations
- **Knowledge Base**: Persistent document profiles with similarity matching
- **Performance Focus**: Lightweight ML suitable for document processing workloads

**Architectural Decision: Python-Only ML Stack**
*Decision Date: August 2025*
*Reasoning*: After comprehensive analysis, Julia integration was evaluated but not adopted because:
- Current Python ML operations are not computationally intensive enough to benefit from Julia's performance
- System bottlenecks are in OCR/PDF processing, not ML computation
- Adding Julia would introduce unnecessary complexity to a production-ready system (100% success rate)
- Current scikit-learn implementation meets all project needs effectively
- Cross-platform deployment complexity would increase significantly
*Future Consideration*: Julia integration may be reconsidered if requirements expand to include deep learning, large-scale matrix operations, or computationally intensive scientific computing tasks.

## Configuration Management

### Environment-Specific Configuration
```yaml
# config/academic.yaml
processing:
  mode: "academic"
  ocr:
    enabled: true
    language: "eng"
    preserve_interword_spaces: true
  adobe_autotag:
    enabled: true
    generate_accessibility_report: true
```

### Configuration Schema Validation
- **Pydantic Models**: Type-safe configuration validation
- **Environment Variables**: Override configuration with env vars
- **Configuration Inheritance**: Base configuration with mode-specific overrides

## Integration Points

### External Service Integration
- **Adobe PDF Services**: Cloud-based document analysis and enhancement
- **Tesseract OCR**: Local text recognition and extraction
- **File System**: Document input/output with path validation
- **Logging System**: Structured logging with configurable levels

### API Compatibility
- **REST APIs**: HTTP-based cloud service communication
- **CLI Interface**: Command-line tool integration for automation
- **Docker API**: Container orchestration and deployment
- **File System API**: Cross-platform file operations

## Performance Considerations

### Optimization Strategies
- **Memory Management**: Efficient PDF processing with resource cleanup
- **Parallel Processing**: Batch operations with concurrent document handling
- **Caching**: Configuration and metadata caching for improved performance
- **Lazy Loading**: On-demand component initialization

### Scalability Patterns
- **Horizontal Scaling**: Container-based deployment for load distribution
- **Vertical Scaling**: Memory and CPU optimization for large documents
- **Queue Processing**: Asynchronous batch processing capabilities
- **Resource Monitoring**: Memory and processing time tracking

## Security Considerations

### Credential Management
- **Environment Variables**: Secure credential storage
- **No Hardcoded Secrets**: Configuration-based credential management
- **API Key Rotation**: Support for credential updates without code changes

### Input Validation
- **File Type Validation**: PDF format verification and sanitization
- **Path Sanitization**: Secure file path handling
- **Content Validation**: PDF structure verification before processing

This technical foundation provides the reliability and scalability needed for institutional deployment while maintaining the flexibility required for diverse academic document processing requirements.