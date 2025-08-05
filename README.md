# ePubs Accessibility Enhancement Project

This is a web scraper that pipes into an accessibility/OCR enhancement framework for use by the Academic Publishing Division of Purdue University Libraries and School of Information Studies. It is co-authored by Claude Code by Anthropic. 

## Key Features

- **OCR Enhancement**: Intelligent text recognition and searchable PDF generation
- **PDF/UA Compliance**: Ensures output documents meet accessibility standards for screen readers
- **Two-Stage Pipeline**: OCR → Accessibility Enhancement workflow
- **Cross-Platform Pipeline**: Unified scraper-processor workflow supporting macOS and WSL
- **Optimized Downloads**: Prioritized direct HTTP downloads with browser fallback

## 🏗️ Project Architecture

### Repository Structure
```
ePubs_Main/
├── processor/unified_project/    # Core processing engine
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
```

### Enhancement Pipeline
1. **OCR Enhancement** (`ocr_enhancer.py`): Adds searchable text layer
2. **PDF Enhancement** (`pdf_enhancer.py`): Metadata and accessibility features

### Unified Scraper-Processor Pipeline
1. **Document Acquisition** (`scraper/`): Cross-platform document downloading to Purdue Libraries' shared drive. This would need configuring for other universities
2. **Optimized Downloads** (`optimized_downloader.py`): Direct HTTP priority with browser fallback
3. **Cross-Platform Orchestration** (`orchestration/`): Unified workflow for macOS and WSL. Windows specifically is not supported but is intended in the future. WSL is based in Ubuntu. 

## Quick Start

### Prerequisites

- **Python 3.9+** (tested up to 3.12)
- **System Dependencies**: `poppler-utils`, `tesseract-ocr`
- **Docker** (optional, for containerized processing)

### Installation

```bash
# Clone the repository
git clone https://github.com/itap.purdue.edu/your-directory/ePubs_Main.git
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

## Usage


### Unified Scraper-Processor Pipeline

```bash
# End-to-end pipeline: scrape and process documents (for Purdue ePubs)
python processor/unified_project/src/orchestration/scrape_and_process.py \
  --url https://docs.lib.purdue.edu/modvis/2024/va \
  --manual-login

# Process multiple URLs with optimized downloads (for Purdue ePubs)
python processor/unified_project/src/orchestration/scrape_and_process.py \
  --urls urls.txt \
  --manual-login

# Force local directory instead of S: drive
python processor/unified_project/src/orchestration/scrape_and_process.py \
  --url https://docs.lib.purdue.edu/modvis/2024/va \
  --force-local \
  --working-dir ./my_pipeline
```

## ⚙️ Configuration

### Academic Mode (`config/academic.yaml`)
- **OCR**: 200 DPI, optimized for modern academic papers
- **Content Detection**: Formulas, tables, figures, citations
- **Local Processing**: Pure local processing without cloud dependencies
- **Performance**: Optimized for file size and quality

### Architecture

The project follows **Clean Architecture** principles:

- **Domain Layer**: Core business entities (`src/domain/`)
- **Application Layer**: Business logic orchestration (`src/services/`)
- **Infrastructure Layer**: External dependencies (`src/repositories/`, `src/enhancers/`)
- **Interface Layer**: CLI and user interfaces (`src/main.py`)

## 📊 Performance Optimizations

### Scraper-Processor Pipeline Optimizations
- **Direct HTTP Priority**: Downloads prioritize direct HTTP over browser automation (3-5x faster)
- **Cross-Platform ChromeDriver**: Optimized driver management for macOS and WSL environments
- **S: Drive Coordination**: Seamless handoff between scraper and processor via shared storage (Purdue Only)

### Performance Benchmarks
- **Single Document Processing**: 30-60 seconds (depending on complexity)
- **Direct HTTP Downloads**: 2-5 seconds per document (vs 10-15 seconds with browser automation)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
