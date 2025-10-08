# ePubs Accessibility Enhancement

PDF accessibility compliance toolkit for academic and historical publications.

## Table of Contents

- [Features](#features)
- [Quick Start Guide](#quick-start-guide)
- [Detailed Documentation](#detailed-documentation)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Processing Modes](#processing-modes)
- [Performance](#performance)
- [Standards Compliance](#standards-compliance)
- [Architecture](#architecture)
- [System Requirements](#system-requirements)
- [Project Structure](#project-structure)
- [Archived Content](#archived-content)
- [Cache Management](#cache-management)
- [Development](#development)
- [Configuration](#configuration)
- [Docker Support](#docker-support)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contributing](#contributing)
- [Support](#support)

## Features

### Core Capabilities
- **PDF/UA-1 Compliance**: Clean accessibility structure optimized for screen readers
- **Intelligent Title Extraction**: 90.9% accuracy on academic papers using ML-based analysis
- **Mathematical Content**: Specialized handling for equations, formulas, and technical notation
- **Smart OCR**: Automatic detection prevents unnecessary processing and text layer corruption
- **Cross-Platform**: Native support for Windows, macOS, and Linux with consistent results

### Performance & Optimization
- **Phase 2B Processing**: 5-8x performance improvement (default mode)
- **FAISS Vector Database**: 10x faster document similarity search
- **Hierarchical Caching**: Memory (512MB) → SSD (2GB) → Disk (8GB) for optimal speed
- **ML Optimization**: Adaptive OCR parameter tuning based on document patterns
- **Web Optimization**: 40-80% file size reduction for digital commons distribution

### Academic Specialization
- **Scholarly Paper Recognition**: Enhanced processing for tables, equations, citations
- **Figure Preservation**: JPEG quality 85%, PNG quality 90% for academic diagrams
- **Historical Documents**: OCR optimization for degraded text and historical terminology
- **Batch Processing**: Scalable processing for document collections with progress tracking

## Quick Start Guide

**New to command-line tools?** Follow these steps:

1. **Install Prerequisites** (one-time setup):
   - Windows: Install [Chocolatey](https://chocolatey.org/install), then run `choco install python tesseract`
   - macOS: Install [Homebrew](https://brew.sh), then run `brew install python tesseract poppler`
   - Linux: Run `sudo apt-get install python3 tesseract-ocr poppler-utils`

2. **Get the Code**:
   ```bash
   git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
   cd ePubs_Main
   ```

3. **Set Up Environment**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install ePubs**:
   ```bash
   pip install -e .[all]
   ```

5. **Process Your First PDF**:
   ```bash
   # Single file
   epubs process input.pdf output.pdf
   
   # Or process a folder of PDFs
   epubs batch-process input_folder/ output_folder/
   ```

**Need help?** See the [Troubleshooting](#troubleshooting) section or check `docs/guides/` for detailed setup guides.

## Detailed Documentation

### Installation

**Prerequisites**: Git, Python 3.9+, and system-specific dependencies (Tesseract OCR, Poppler)

#### Windows
```powershell
# Install Chocolatey package manager (if not already installed)
# Run as Administrator in PowerShell
# Visit https://chocolatey.org/install for instructions

# Install dependencies
choco install python tesseract

# Clone repository
git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
cd ePubs_Main

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install ePubs with all dependencies
pip install -e .[all]
```

**Note**: You may need to add Tesseract to your PATH. Default location: `C:\Program Files\Tesseract-OCR\`

#### macOS
```bash
# Install Homebrew package manager (if not already installed)
# Visit https://brew.sh for instructions

# Install dependencies
brew install python tesseract poppler

# Clone repository
git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
cd ePubs_Main

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install ePubs with all dependencies
pip install -e .[all]
```

**Apple Silicon Note**: All dependencies are optimized for M1/M2/M3 chips.

#### Linux (Ubuntu/Debian)
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv tesseract-ocr poppler-utils

# Clone repository
git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
cd ePubs_Main

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install ePubs with all dependencies
pip install -e .[all]
```

**Verification**: After installation, test with:
```bash
epubs --help
epubs-scrape --help
```

**Troubleshooting**: If commands are not found, ensure the virtual environment is activated and try:
```bash
# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Usage

**Process a Single PDF File**
```bash
# Basic usage: input file → output file
epubs process input.pdf output.pdf

# Example with actual paths
epubs process ~/Documents/paper.pdf ~/Documents/paper_enhanced.pdf
```

**Batch Process Multiple PDFs (Recommended)**
```bash
# Process all PDFs in a directory (Phase 2B default - 5-8x faster)
epubs batch-process input_directory/ output_directory/

# Example with actual paths
epubs batch-process ~/Documents/papers/ ~/Documents/enhanced_papers/

# Alternative processing modes (if needed)
epubs batch-process input_dir/ output_dir/ --mode parallel    # Legacy parallel
epubs batch-process input_dir/ output_dir/ --mode sequential  # Single-threaded
```

**Download Academic Papers**
```bash
# Scrape documents from institutional repositories
epubs-scrape --url "https://docs.lib.purdue.edu/etd/" --output data/input

# Limit number of documents to download
epubs-scrape --url "https://docs.lib.purdue.edu/etd/" --output data/input --limit 50
```

**Manage Cache for Phase 2B**
```bash
# View cache statistics and usage
epubs cache stats

# Clear all caches (use if experiencing issues)
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
│   ├── config/             # Top-level configuration
│   └── unified_project/    # Main processing pipeline
│       ├── src/            # Source code modules
│       │   ├── academic/   # Academic paper processing
│       │   ├── acceleration/ # Phase 2B FAISS/ML features
│       │   ├── batch/      # Batch processing
│       │   ├── caching/    # Hierarchical cache system
│       │   ├── enhancers/  # PDF enhancement modules
│       │   ├── ml/         # Machine learning optimization
│       │   └── training/   # Accessibility training (experimental)
│       ├── config/         # Configuration files
│       ├── resources/      # Academic terms, patterns
│       └── tests/          # Component test suites
├── scraper/                # Document acquisition tools
│   ├── optimized_downloader.py
│   └── purdue_downloader.py
├── data/                   # Input/output/training data
│   ├── input/              # Source PDFs for processing
│   ├── output/             # Enhanced PDFs
│   ├── models/             # ML models and vectors
│   └── training/           # Training data (experimental)
├── docs/                   # Project documentation
│   ├── implementation/     # Technical implementation reports
│   ├── guides/             # Setup and configuration guides
│   ├── testing/            # Testing documentation
│   └── archive/            # Historical documentation
├── tests/                  # Project-wide test suites
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── validation/         # Validation tests
├── scripts/                # Utility scripts
│   ├── setup/              # Installation scripts
│   ├── examples/           # Demo scripts
│   └── tests/              # Test utilities
├── cache/                  # Phase 2B cache directory
├── logs/                   # Processing and application logs
│   └── reports/            # Validation reports
└── archived/               # Deprecated code and docs
```

## Archived Content

The `archived/` directory contains deprecated code, migration scripts, and outdated documentation from previous development iterations. This content is preserved for reference but is **not maintained** and should **not be used** for new development:

- **Old READMEs**: Previous documentation versions (superseded by current docs/)
- **Migration Scripts**: Historical codebase transitions
- **Deprecated Tools**: Replaced by unified processor pipeline
- **Test Artifacts**: Old test files and outputs
- **Build Artifacts**: Legacy configuration and deployment files

**Note**: Current users should reference the `docs/` directory for up-to-date documentation.

## Cache Management

Phase 2B uses a hierarchical cache system for performance optimization:

**Cache Structure**:
- **Memory Cache**: 512MB (fastest, in-memory)
- **SSD Cache**: 2048MB (fast, persistent)
- **Disk Cache**: 8192MB (slower, persistent)
- **Total**: ~10.5GB default configuration

**Cache Commands**:
```bash
# View cache statistics
epubs cache stats

# Clear all caches
epubs cache clear

# Check cache location
# Default: ./cache/ in project root
```

**Configuration**: Cache settings can be adjusted in `processor/unified_project/config/academic.yaml` under the `acceleration` section.

**Note**: First-time processing builds the cache, subsequent runs benefit from 5-8x speedup.

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

**Note**: This repository contains only this README.md for remote users. Complete technical documentation, setup guides, and implementation reports are maintained locally in the `docs/` directory for development purposes but are not included in the remote repository.

For questions or detailed documentation, please contact: schipp0@purdue.edu

## Troubleshooting

### Common Issues and Solutions

#### "Tesseract not found" or "tesseract is not recognized"
**Symptoms**: Error message when processing PDFs with OCR

**Solutions**:
- **Windows**: 
  1. Verify installation: `tesseract --version` in Command Prompt
  2. If not found, add to PATH: `C:\Program Files\Tesseract-OCR\`
  3. Restart terminal after PATH modification
- **macOS**: `brew install tesseract` or `brew reinstall tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

#### Memory Errors During Batch Processing
**Symptoms**: "MemoryError", "Out of memory", or process crashes

**Solutions**:
1. Reduce batch processing parallelism (edit `academic.yaml`):
   ```yaml
   workers: 3  # Reduce from default 6
   ```
2. Use sequential mode (single-threaded):
   ```bash
   epubs batch-process input/ output/ --mode sequential
   ```
3. Process smaller batches of files at a time
4. Close other applications to free up RAM
5. Increase system swap/page file size

#### Slow Processing Performance
**Symptoms**: Processing takes much longer than expected (>30s per document)

**Solutions**:
1. Verify Phase 2B is active (check logs for "FAISS initialization")
2. Ensure ML dependencies are installed:
   ```bash
   pip install -e .[ml]
   ```
3. Check cache directory exists and is writable:
   ```bash
   ls -la cache/  # macOS/Linux
   dir cache\     # Windows
   ```
4. Review cache configuration in `processor/unified_project/config/academic.yaml`
5. Try clearing and rebuilding cache:
   ```bash
   epubs cache clear
   ```

#### Virtual Environment Issues
**Symptoms**: "Command not found", "Module not found", import errors

**Solutions**:
1. Ensure virtual environment is activated:
   ```bash
   # Check current Python location
   which python  # macOS/Linux (should show path with 'venv')
   where python  # Windows (should show path with 'venv')
   ```
2. Activate virtual environment if needed:
   ```bash
   source venv/bin/activate  # macOS/Linux
   .\venv\Scripts\activate   # Windows
   ```
3. Reinstall dependencies:
   ```bash
   pip install -e .[all]
   ```

#### PDF Processing Failures
**Symptoms**: "Failed to enhance", "PDF structure error", corrupted output

**Solutions**:
1. Verify input PDF is not corrupted:
   ```bash
   # Try opening in PDF reader first
   ```
2. Check file permissions (must be readable/writable)
3. Try processing with different mode:
   ```bash
   epubs process input.pdf output.pdf --mode sequential
   ```
4. Check logs for detailed error messages:
   ```bash
   cat logs/batch_processing.log  # macOS/Linux
   type logs\batch_processing.log # Windows
   ```

#### Permission Denied Errors
**Symptoms**: "Permission denied", "Access denied" when processing files

**Solutions**:
1. Check file/directory permissions
2. Ensure you have write access to output directory
3. On Windows, run terminal as Administrator if needed
4. Verify no other program has the files open

### Getting More Help

If problems persist:
1. Check logs in `logs/` directory for detailed error messages
2. Review full documentation in `docs/` directory
3. Open an issue at: https://github.itap.purdue.edu/schipp0/ePubs_Main/issues
4. Include: error message, operating system, Python version, and command used

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
