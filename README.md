# ePubs Accessibility Enhancement

PDF accessibility compliance toolkit for academic and historical publications.

## Features

- **PDF/UA-1 Compliance**: Clean accessibility structure for screen readers
- **Phase 2B Processing**: 5-8x performance improvement with FAISS and ML optimization (default)
- **Intelligent Title Extraction**: 90.9% accuracy on academic papers  
- **Mathematical Content**: Specialized handling for equations and formulas
- **Cross-Platform**: Native Windows, macOS, and Linux support
- **Smart OCR**: Automatic detection prevents unnecessary processing
- **Web Optimization**: 40-80% file size reduction for digital commons

## Quick Start

### Installation

**Windows**
```powershell
choco install python tesseract
git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
cd ePubs_Main
python -m venv venv
.\venv\Scripts\activate
pip install -e .[all]
```

**macOS**
```bash
brew install python tesseract poppler
git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
cd ePubs_Main
python3 -m venv venv
source venv/bin/activate
pip install -e .[all]
```

**Linux (Ubuntu/Debian)**
```bash
sudo apt-get install python3 python3-pip tesseract-ocr poppler-utils
git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
cd ePubs_Main
python3 -m venv venv
source venv/bin/activate
pip install -e .[all]
```

### Usage

**Single File Processing**
```bash
epubs process input.pdf output.pdf
```

**Batch Processing (Phase 2B default - 5-8x faster)**
```bash
epubs batch-process input_dir/ output_dir/
```

**Document Scraping**
```bash
epubs-scrape --url "https://docs.lib.purdue.edu/etd/" --output data/input
```

**Cache Management**
```bash
epubs cache stats
epubs cache clear
```

## Processing Modes

### Phase 2B (Default)
Advanced processing with FAISS vector database, hierarchical caching, and ML optimization.
```bash
epubs batch-process input_dir/ output_dir/
```

### Parallel (Legacy)
Standard parallel processing without Phase 2B enhancements.
```bash
epubs batch-process input_dir/ output_dir/ --mode parallel
```

### Sequential (Legacy)
Single-threaded processing for debugging or constrained environments.
```bash
epubs batch-process input_dir/ output_dir/ --mode sequential
```

## Performance

- **Processing Speed**: 5-8x improvement with Phase 2B
- **File Size**: 40.9% average reduction (6.3% to 74.8% range)
- **Title Extraction**: 90.9% accuracy on academic papers
- **Processing Time**: ~15 seconds per document average
- **Success Rate**: 100% on test dataset

## Standards Compliance

- **PDF/UA-1** (ISO 14289-1)
- **Section 508** (U.S. Federal accessibility)
- **ADA** (Americans with Disabilities Act)
- **WCAG 2.1 Level AA** (Web Content Accessibility Guidelines)

## Architecture

### Processing Pipeline
```
Input Validation → OCR Enhancement → Image Compression → 
PDF/UA-1 Enhancement → Output Generation
```

### Phase 2B Features
- **FAISS Vector Database**: 10x faster document similarity search
- **Hierarchical Caching**: Memory (512MB) → SSD (2GB) → Disk (8GB)
- **ML Optimization**: Adaptive OCR parameter tuning
- **Thread-Safe**: 6 parallel workers with concurrent-safe operations
- **Academic Patterns**: Enhanced recognition for tables, equations, citations

## System Requirements

- **Python**: 3.9 or higher
- **Tesseract OCR**: 5.5.1 or higher
- **Poppler**: (macOS/Linux only)
- **RAM**: 4GB+ recommended for batch processing
- **Storage**: Varies by cache configuration (default 10.5GB total)

## Project Structure

```
ePubs_Main/
├── processor/              # Core enhancement engine
│   └── unified_project/    # Main processing pipeline
│       ├── src/            # Source code
│       ├── config/         # Configuration files
│       └── tests/          # Test suites
├── scraper/                # Document acquisition tools
├── data/                   # Input/output directories
├── tests/                  # Project-wide tests
└── scripts/                # Utility scripts
```

## Development

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=processor --cov=scraper

# Specific test types
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m "not slow"        # Skip slow tests
```

### Code Quality
```bash
black processor/ scraper/   # Format code
isort processor/ scraper/   # Sort imports
flake8 processor/ scraper/  # Lint code
mypy processor/ scraper/    # Type check
```

## Configuration

Configuration files in `processor/unified_project/config/`:
- `academic.yaml` - Academic paper processing (default)
- `default.yaml` - Base configuration
- `windows.yaml` - Windows-specific settings
- `adaptive_ml.yaml` - ML optimization settings

## Docker Support

```bash
# Build image
docker build -t epubs-accessibility .

# Run container
docker run -v /path/to/data:/data epubs-accessibility \
  batch-process /data/input /data/output
```

## Documentation

- `README.md` - This file
- `PRODUCTION_README.md` - Production deployment guide
- `TESTING_GUIDE.md` - Testing documentation
- `FOLDER_SUPPORT_GUIDE.md` - Directory structure management
- `RESOURCE_MANAGEMENT_GUIDE.md` - Resource optimization

## Troubleshooting

### Common Issues

**Tesseract not found**
- Windows: Verify Tesseract is in PATH
- macOS: `brew install tesseract`
- Linux: `apt-get install tesseract-ocr`

**Memory errors during batch processing**
- Reduce batch size
- Increase system RAM
- Use sequential mode: `--mode sequential`

**Slow processing**
- Verify Phase 2B is active (check logs for FAISS initialization)
- Ensure ML dependencies installed: `pip install -e .[ml]`
- Check cache configuration in `academic.yaml`

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

## Support

- **Issues**: https://github.itap.purdue.edu/schipp0/ePubs_Main/issues
- **Documentation**: See docs/ directory
- **Email**: schipp0@purdue.edu
