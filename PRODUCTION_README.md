# ePubs Production Deployment

Production deployment guide for ePubs Accessibility Enhancement with specialized historical document support.

## Recent Updates

- **Historical Document Title Extraction**: Enhanced title recognition for historical documents (1800s-1900s) with specialized spatial zones and relaxed thresholds
- **Dual-Mode Architecture**: Automatic detection of document type with appropriate processing parameters
- **Zero Regression**: Maintains perfect compatibility with modern academic paper processing

## Setup

### Prerequisites
```bash
# System requirements
- Python 3.9+
- 4GB+ RAM (8GB+ for batch processing)
- 10GB+ storage
- Tesseract OCR 5.0+
```

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .[all]

# Validate installation
python scripts/production_setup.py
```

### Configuration
```bash
# Copy and customize configuration
cp processor/unified_project/config/academic.yaml config/production.yaml

# Create directories
mkdir -p data/input data/output logs cache
chmod 755 data/input data/output
chmod 700 logs cache
```

## Scraping

### Purdue ePubs Download
```bash
# Download documents
python scraper/purdue_downloader.py --url "https://docs.lib.purdue.edu/etd/" --output data/input

# Batch download with filters
python scraper/purdue_downloader.py --url "https://docs.lib.purdue.edu/etd/" --output data/input --limit 100
```

## Processing

### Single File Processing
```bash
# Academic mode (default)
python -m processor.unified_project.src.main process input.pdf output.pdf

# Basic mode
python -m processor.unified_project.src.main process input.pdf output.pdf --mode basic

# Minimal mode
python -m processor.unified_project.src.main process input.pdf output.pdf --mode minimal
```

### Batch Processing
```bash
# Process directory
python -m processor.unified_project.src.main batch-process data/input data/output --verbose

# With specific mode
python -m processor.unified_project.src.main batch-process data/input data/output --mode academic --verbose
```

## Pipeline Usage

### Docker Deployment
```bash
# Build and run
docker-compose up epubs-processor

# Process files
docker-compose run epubs-processor process /data/input/document.pdf /data/output/enhanced.pdf --mode academic

# Batch processing
docker-compose run epubs-processor batch-process /data/input /data/output --verbose
```

### Cache Management
```bash
# View cache statistics
python -m processor.unified_project.src.main cache stats

# Clear cache
python -m processor.unified_project.src.main cache clear

# Prune old cache entries
python -m processor.unified_project.src.main cache prune --days 7
```

### Performance Monitoring
```bash
# Show processing statistics
python -m processor.unified_project.src.main stats show --days 7

# Recent processing metrics
python -m processor.unified_project.src.main stats recent --limit 20
```

## Environment Variables

```bash
export EPUBS_ENV=production
export EPUBS_LOG_LEVEL=INFO
export EPUBS_CACHE_DIR=/var/cache/epubs
export EPUBS_TEMP_DIR=/tmp/epubs
export EPUBS_MAX_WORKERS=4
export EPUBS_MEMORY_LIMIT_MB=1024
```

## Maintenance

```bash
# Daily maintenance
python -m processor.unified_project.src.main cache prune --days 7
python -m processor.unified_project.src.main stats cleanup --days 30

# Weekly validation
python scripts/production_setup.py
pytest tests/ --cov=processor --cov=scraper
```
