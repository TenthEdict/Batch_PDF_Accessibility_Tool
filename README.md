# ePubs Accessibility Enhancement

PDF accessibility enhancement toolkit for academic and historical publications with specialized title extraction.

## Features

- **Intelligent Title Extraction**: Automatic detection and extraction of document titles from both modern academic papers and historical documents
- **Dual-Mode Processing**: Specialized parameters for historical documents (1800s-1900s) and modern academic papers  
- **ML-Enhanced OCR**: Adaptive machine learning optimization for document-specific OCR configuration
- **PDF/UA-1 Compliance**: Clean accessibility compliance without auto-generated content structure
- **Cross-Platform Support**: Native Windows, macOS, and Linux compatibility

## Setup

### Windows
```powershell
# Install dependencies
choco install python tesseract

# Setup project
git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
cd ePubs_Main
python -m venv venv
.\venv\Scripts\activate
pip install -e .[all]
```

### Mac/Linux
```bash
# Install dependencies
brew install python tesseract poppler  # macOS
sudo apt-get install python3 python3-pip tesseract-ocr poppler-utils  # Ubuntu

# Setup project
git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
cd ePubs_Main
python3 -m venv venv
source venv/bin/activate
pip install -e .[all]
```

## Scraping

Download documents from Purdue ePubs:
```bash
python scraper/purdue_downloader.py --url "https://docs.lib.purdue.edu/etd/" --output data/input
```

## Processing

### Single File
```bash
python -m processor.unified_project.src.main process input.pdf output.pdf --mode academic
```

### Batch Processing
```bash
python -m processor.unified_project.src.main batch-process data/input data/output --verbose
```

## Pipeline Usage

### Academic Documents (Default)
```bash
# Uses intelligent ML-based OCR and enhancement
python -m processor.unified_project.src.main process document.pdf enhanced.pdf
```

### Basic Processing
```bash
python -m processor.unified_project.src.main process document.pdf enhanced.pdf --mode basic
```

### Minimal Processing
```bash
python -m processor.unified_project.src.main process document.pdf enhanced.pdf --mode minimal
```

### Cache Management
```bash
python -m processor.unified_project.src.main cache stats
python -m processor.unified_project.src.main cache clear
```

## System Requirements

- Python 3.9+
- Tesseract OCR
- Poppler (Mac/Linux)
- 4GB+ RAM for batch processing