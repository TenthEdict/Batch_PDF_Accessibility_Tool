# Technical Context

## Core Technology Stack

### Python Environment
- **Python**: 3.9+ (tested on 3.9, 3.10, 3.11, 3.12)
- **Packaging**: pyproject.toml with setuptools
- **Dependency Management**: pip with requirements.txt and lock files

### PDF Processing
- **PyMuPDF (fitz) 1.23+**: Core PDF manipulation and text extraction
- **pikepdf 8.3+**: PDF structure manipulation and metadata
- **ocrmypdf 16+**: OCR processing with Tesseract integration
- **pdf2image 1.16+**: PDF to image conversion
- **pdfplumber 0.7+**: Text and table extraction

### Image Processing
- **Pillow 10+**: Image manipulation and format conversion
- **opencv-python-headless 4.8+**: Advanced image processing
- **scikit-image 0.21+**: Scientific image analysis

### OCR
- **Tesseract 5.5.1+**: Text recognition engine
- **pytesseract 0.3.10+**: Python wrapper for Tesseract

### Machine Learning
- **scikit-learn 1.3+**: ML algorithms and pattern recognition
- **pandas 1.5+**: Data processing and analysis
- **numpy 1.24+**: Numerical computing
- **faiss-cpu 1.7.4+**: High-performance vector similarity search
- **scipy 1.7+**: Scientific computing

### CLI and Interface
- **Typer 0.12+**: Modern CLI framework with type hints
- **Rich 13+**: Terminal formatting and progress bars
- **PyYAML 6+**: Configuration management

### Development Tools
- **pytest 7+**: Testing framework
- **black 23+**: Code formatting
- **isort 5.12+**: Import sorting
- **flake8 6+**: Linting
- **mypy 1+**: Static type checking
- **pytest-cov 4+**: Code coverage

## System Dependencies

### Windows
```powershell
# Option 1: Chocolatey (Recommended)
choco install python tesseract

# Option 2: Manual
# Download Python from python.org
# Download Tesseract from github.com/UB-Mannheim/tesseract/wiki
```

### macOS
```bash
brew install python tesseract poppler
```

### Linux (Ubuntu/Debian)
```bash
apt-get install python3 python3-pip tesseract-ocr poppler-utils
```

## Installation

### Standard Installation
```bash
# Clone repository
git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
cd ePubs_Main

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -e .[all]      # All features
pip install -e .[dev]      # Development
pip install -e .[test]     # Testing only
pip install -e .[ml]       # ML features (Phase 2B)
```

### Dependency Groups

#### Core (Required)
```toml
dependencies = [
    "PyMuPDF>=1.23.0,<1.25.0",
    "pikepdf>=8.3.0,<9.0.0",
    "ocrmypdf>=16.0.0,<17.0.0",
    "Pillow>=10.0.0,<11.0.0",
    "opencv-python-headless>=4.8.0,<5.0.0",
    "typer>=0.12.0,<1.0.0",
    # ... (see pyproject.toml for complete list)
]
```

#### Optional: Machine Learning
```toml
ml = [
    "scikit-learn>=1.3.0,<2.0.0",
    "pandas>=1.5.0,<3.0.0",
    "numpy>=1.24.0,<2.0.0",
    "faiss-cpu>=1.7.4,<2.0.0",
    "joblib>=1.3.0,<2.0.0",
]
```

#### Optional: Development
```toml
dev = [
    "pytest>=7.0.0,<8.0.0",
    "black>=23.0.0,<24.0.0",
    "mypy>=1.0.0,<2.0.0",
    # ... (see pyproject.toml for complete list)
]
```

## Architecture Patterns

### Clean Architecture
- **Domain Layer**: Core entities and rules (`src/domain/`)
- **Application Layer**: Business logic (`src/services/`)
- **Infrastructure Layer**: External dependencies (`src/enhancers/`, `src/repositories/`)
- **Interface Layer**: CLI and APIs (`src/main.py`)

### Design Patterns
- **Service Container**: Central dependency management
- **Factory Pattern**: Service instantiation
- **Strategy Pattern**: Configurable enhancement strategies
- **Chain of Responsibility**: Sequential processing
- **Observer Pattern**: Progress tracking and logging

### ML Architecture
- **AdaptiveMLEnhancer**: 677-line document-level learning system
- **Python-Only Stack**: scikit-learn, pandas, numpy (Julia not needed)
- **Knowledge Base**: Persistent document profiles
- **Performance Focus**: Lightweight ML suitable for document processing

## Configuration Management

### Environment-Specific Config
```yaml
# config/academic.yaml
processing:
  mode: "academic"
  ocr:
    enabled: true
    language: "eng"
    preserve_interword_spaces: true
```

### Configuration Loading
- **Pydantic Models**: Type-safe validation
- **Environment Variables**: Override with env vars
- **Configuration Inheritance**: Base + mode-specific overrides

## Platform Compatibility

### Operating Systems
- **Windows**: 10/11 (native support, PowerShell setup)
- **macOS**: 10.15+ (Intel and Apple Silicon)
- **Linux**: Ubuntu 20.04+, Debian-based distributions

### Architectures
- **x86_64**: Intel/AMD 64-bit
- **ARM64**: M1/M2/M3 Mac, ARM64 Windows

## Performance Considerations

### Optimization Strategies
- **Memory Management**: Efficient PDF processing with resource cleanup
- **Parallel Processing**: Batch operations with 6 concurrent workers
- **FAISS Acceleration**: 10x faster similarity search
- **Hierarchical Caching**: 70-80% cache hit rates
- **Lazy Loading**: On-demand component initialization

### Scalability
- **Horizontal**: Container-based deployment
- **Vertical**: Memory and CPU optimization
- **Batch**: Queue processing with progress tracking
- **Monitoring**: Resource usage tracking

## Security

### Credential Management
- **Environment Variables**: Secure credential storage
- **No Hardcoded Secrets**: Configuration-based management
- **API Key Rotation**: Support for credential updates

### Input Validation
- **File Type**: PDF format verification
- **Path Sanitization**: Secure file path handling
- **Content Validation**: PDF structure verification

## Technical Constraints

### Performance
- **Large Documents**: PyMuPDF efficient for >100MB files
- **Batch Processing**: Memory-limited (4GB+ recommended)
- **OCR Performance**: Scales with image complexity

### Compatibility
- **PDF Formats**: PDF 1.4+ (focus on PDF 1.7+ for accessibility)
- **Text Encoding**: UTF-8 with Unicode support
- **Image Formats**: JPEG, PNG, TIFF embedded images

## Integration Points

### External Services
- **Tesseract OCR**: Local text recognition
- **File System**: Document input/output
- **Logging System**: Structured logging

### APIs
- **CLI Interface**: Command-line automation
- **Docker API**: Container orchestration
- **File System API**: Cross-platform operations

## Development Workflow

### Setup
1. Install system dependencies (Python, Tesseract, Poppler)
2. Clone repository
3. Create virtual environment
4. Install Python dependencies
5. Run tests to verify setup

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=processor --cov=scraper

# Run specific test types
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m "not slow"     # Skip slow tests
```

### Code Quality
```bash
# Format code
black processor/ scraper/

# Sort imports
isort processor/ scraper/

# Lint
flake8 processor/ scraper/

# Type check
mypy processor/ scraper/
```

## Deployment

### Docker
```bash
# Build image
docker build -t epubs-accessibility .

# Run container
docker run -v /path/to/data:/data epubs-accessibility \
  batch-process /data/input /data/output
```

### Production Considerations
- 4GB+ RAM recommended for batch processing
- Tesseract and Poppler must be installed
- Virtual environment isolation recommended
- Log rotation for long-running services
