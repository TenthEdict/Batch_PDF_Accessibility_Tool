# ePubs Accessibility Enhancement Project

A comprehensive toolkit for enhancing document accessibility with specialized support for academic publications. This project provides AI-powered document processing, OCR enhancement, and PDF/UA compliance tools designed for modern research workflows.

## ✨ Key Features

- **🤖 OCR Enhancement**: Intelligent text recognition and searchable PDF generation
- **📚 Academic Optimization**: Specialized processing for complex academic layouts, formulas, tables, and citations
- **♿ PDF/UA Compliance**: Ensures output documents meet accessibility standards for screen readers
- **🔄 Two-Stage Pipeline**: OCR → Accessibility Enhancement workflow
- **🏗️ Clean Architecture**: Service container with dependency injection and clean separation of concerns
- **📦 Containerized Processing**: Docker support for consistent, scalable document processing
- **⚡ Optimized Performance**: File size optimization with quality preservation (addresses Ghostscript 10.x issues)
- **🌐 Cross-Platform Pipeline**: Unified scraper-processor workflow supporting macOS and WSL
- **🚫 Duplicate Detection**: Intelligent file tracking to avoid reprocessing existing documents
- **📡 Optimized Downloads**: Prioritized direct HTTP downloads with browser fallback

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
2. **PDF Enhancement** (`pdf_enhancer.py`): Metadata and accessibility features

### Unified Scraper-Processor Pipeline
1. **Document Acquisition** (`scraper/`): Cross-platform document downloading with S: drive coordination
2. **Optimized Downloads** (`optimized_downloader.py`): Direct HTTP priority with browser fallback
3. **Duplicate Detection** (`duplicate_detection.py`): Intelligent tracking to avoid reprocessing
4. **Cross-Platform Orchestration** (`orchestration/`): Unified workflow for macOS and WSL

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (tested up to 3.12)
- **System Dependencies**: `poppler-utils`, `tesseract-ocr`
- **Docker** (optional, for containerized processing)

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

# Academic script (Docker-based)
processor/unified_project/scripts/process_academic.sh input.pdf output.pdf
processor/unified_project/scripts/process_academic.sh --batch input_dir output_dir
```

### Unified Scraper-Processor Pipeline

```bash
# End-to-end pipeline: scrape and process documents
python processor/unified_project/src/orchestration/scrape_and_process.py \
  --url https://docs.lib.purdue.edu/modvis/2024/va \
  --mode academic \
  --username your_username

# Process multiple URLs with optimized downloads
python processor/unified_project/src/orchestration/scrape_and_process.py \
  --urls-file urls.txt \
  --mode academic \
  --verbose

# Force local directory instead of S: drive
python processor/unified_project/src/orchestration/scrape_and_process.py \
  --url https://docs.lib.purdue.edu/modvis/2024/va \
  --force-local \
  --working-dir ./my_pipeline
```

### Document Acquisition (Standalone)

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

### Cross-Platform Features

The unified pipeline automatically detects and optimizes for your platform:

#### **macOS Support**
- Automatic S: drive detection via Finder mounts (`/Volumes/Accessibility_Project`)
- Optimized Chrome driver management for Intel and Apple Silicon
- Native file system integration

#### **WSL Support** 
- S: drive access via `/mnt/s/Departments/ePubs/Accessibility_Project`
- Headless Chrome for better WSL compatibility
- Cross-platform path handling

#### **Smart Directory Management**
```bash
# Automatically uses S: drive if available
# macOS: /Volumes/Accessibility_Project
# WSL:   /mnt/s/Departments/ePubs/Accessibility_Project

# Fallback to local directories if S: drive unavailable
# macOS: ~/Documents/ePubs_Pipeline
# WSL:   ~/ePubs_Pipeline
```

### Academic Mode (`config/academic.yaml`)
- **OCR**: 200 DPI, optimized for modern academic papers
- **Content Detection**: Formulas, tables, figures, citations
- **Local Processing**: Pure local processing without cloud dependencies
- **Performance**: Optimized for file size and quality


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

### Document Processing Optimizations
- **Ghostscript 10.x Compatibility**: Resolved regression issues with `skip_text`
- **Compression Settings**: JPEG quality (85%), JBIG2 lossy compression
- **DPI Optimization**: Reduced to 200 DPI for academic papers
- **Processing Efficiency**: Disabled unnecessary image enhancement steps

### Scraper-Processor Pipeline Optimizations
- **Direct HTTP Priority**: Downloads prioritize direct HTTP over browser automation (3-5x faster)
- **Cross-Platform ChromeDriver**: Optimized driver management for macOS and WSL environments
- **Intelligent Duplicate Detection**: SQLite-based tracking prevents reprocessing existing files
- **S: Drive Coordination**: Seamless handoff between scraper and processor via shared storage
- **Concurrent Operations**: Overlapping download and processing operations where possible

### Performance Benchmarks
- **Single Document Processing**: 30-60 seconds (depending on complexity)
- **Direct HTTP Downloads**: 2-5 seconds per document (vs 10-15 seconds with browser automation)
- **Duplicate Detection**: <100ms lookup time for existing files
- **Cross-Platform Compatibility**: 95% feature parity between macOS and WSL

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