# ePubs Accessibility Enhancement Project

A comprehensive toolkit for enhancing document accessibility with specialized support for academic publications. This project provides AI-powered document processing, OCR enhancement, and PDF/UA compliance tools designed for modern research workflows.

## ✨ Key Features

- **🤖 AI-Powered Enhancement**: Adobe PDF Services AutoTag integration for intelligent document structure tagging
- **📚 Academic Optimization**: Specialized processing for complex academic layouts, formulas, tables, and citations
- **♿ PDF/UA Compliance**: Ensures output documents meet accessibility standards for screen readers
- **🔄 Multi-Stage Pipeline**: OCR → AI Tagging → Accessibility Enhancement workflow
- **🏗️ Clean Architecture**: Service container with dependency injection and clean separation of concerns
- **📦 Containerized Processing**: Docker support for consistent, scalable document processing
- **⚡ Optimized Performance**: File size optimization with quality preservation (addresses Ghostscript 10.x issues)

## 🏗️ Project Architecture

### Repository Structure
```
ePubs_Main/
├── processor/unified_project/    # Core processing engine (clean architecture)
│   ├── src/
│   │   ├── enhancers/           # Document enhancement modules
│   │   ├── services/            # Business logic layer
│   │   ├── repositories/        # Data access layer
│   │   ├── domain/             # Core business entities
│   │   └── core/               # Framework and dependency injection
│   ├── config/                 # YAML configuration files
│   └── scripts/                # Processing automation scripts
├── scraper/                     # Document acquisition tools
├── advanced_batch_processor.py  # High-performance batch processing
└── cloud_batch_process.sh      # Cloud-based batch automation
```

### Enhancement Pipeline
1. **OCR Enhancement** (`ocr_enhancer.py`): Adds searchable text layer with optimized settings
2. **Adobe AutoTag** (`adobe_autotag_enhancer.py`): AI-powered structure tagging (optional)
3. **PDF Enhancement** (`pdf_enhancer.py`): Metadata and accessibility features

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (tested up to 3.12)
- **System Dependencies**: `poppler-utils`, `tesseract-ocr`
- **Docker** (optional, for containerized processing)
- **Adobe PDF Services** (optional, for AI-powered enhancement)

### Installation

```bash
# Clone the repository
git clone https://github.com/itap.purdue.edu/your-org/ePubs_Main.git
cd ePubs_Main

# Set up Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with all features
pip install -e .[all]

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr
```

## 💻 Usage

### CLI Interface

```bash
# Process single document (academic mode)
epubs process input.pdf output.pdf --mode academic

# Enable Adobe AutoTag with accessibility report
epubs process input.pdf output.pdf \
  --use-adobe-autotag \
  --generate-accessibility-report \
  --shift-headings

# Verbose processing with custom metadata
epubs process input.pdf output.pdf \
  --mode academic \
  --title "Research Paper Title" \
  --author "Author Name" \
  --language "en-US" \
  --verbose
```

### Batch Processing

```bash
# Advanced batch processor (local)
python advanced_batch_processor.py

# Cloud-based batch processing
./cloud_batch_process.sh

# Academic script (Docker-based)
processor/unified_project/scripts/process_academic.sh input.pdf output.pdf
processor/unified_project/scripts/process_academic.sh --batch input_dir output_dir
```

### Document Acquisition

```bash
# Download from Purdue library resources
epubs-scrape --url https://docs.lib.purdue.edu/modvis/2024/va

# Process directory of documents
python processor/unified_project/src/process_directory.py
```

## 🐳 Docker Support

### Build Images

```bash
# Academic processor
docker build -f processor/unified_project/Dockerfile.academic \
  -t epubs/academic_processor:latest processor/unified_project/

# Standard processor  
docker build -f processor/unified_project/Dockerfile \
  -t epubs/processor:latest processor/unified_project/
```

### Run Containers

```bash
# Single document processing
docker run --rm \
  -v /path/to/input.pdf:/data/input/document.pdf \
  -v /path/to/output:/data/output \
  epubs/academic_processor:latest \
  --mode academic \
  /data/input/document.pdf \
  /data/output/accessible.pdf

# Batch processing
docker run --rm \
  -v /path/to/input_dir:/data/input \
  -v /path/to/output_dir:/data/output \
  epubs/academic_processor:latest \
  --mode academic --batch \
  /data/input /data/output
```

## ⚙️ Configuration

### Academic Mode (`config/academic.yaml`)
- **OCR**: 200 DPI, optimized for modern academic papers
- **Content Detection**: Formulas, tables, figures, citations
- **Adobe AutoTag**: Enabled with academic optimizations
- **Performance**: Optimized for file size and quality

### Adobe PDF Services Setup
1. Obtain credentials from Adobe Developer Console
2. Place `pdfservices-api-credentials.json` in project root
3. AutoTag will be automatically detected and enabled

## 🧪 Development

### Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# With coverage
pytest --cov=epubs_accessibility --cov-report=html
```

### Code Quality

```bash
# Format code
black .
isort .

# Type checking
mypy processor scraper

# Linting
flake8
```

### Architecture

The project follows **Clean Architecture** principles:

- **Domain Layer**: Core business entities (`src/domain/`)
- **Application Layer**: Business logic orchestration (`src/services/`)
- **Infrastructure Layer**: External dependencies (`src/repositories/`, `src/enhancers/`)
- **Interface Layer**: CLI and user interfaces (`src/main.py`)

## 📊 Performance Optimizations

Recent optimizations address file size concerns:

- **Ghostscript 10.x Compatibility**: Resolved regression issues with `skip_text`
- **Compression Settings**: JPEG quality (85%), JBIG2 lossy compression
- **DPI Optimization**: Reduced to 200 DPI for academic papers
- **Processing Efficiency**: Disabled unnecessary image enhancement steps

## 📄 Documentation

- **[CLAUDE.md](CLAUDE.md)**: Development guide for AI assistants
- **[Processor Documentation](processor/unified_project/README.md)**: Detailed processor information
- **[Scraper Documentation](scraper/README.md)**: Document acquisition tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Adobe PDF Services** for AI-powered document enhancement
- **OCRmyPDF** for high-quality OCR processing
- **Purdue University Libraries** for document access and research support