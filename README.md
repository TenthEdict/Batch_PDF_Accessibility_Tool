# ePubs Accessibility Enhancement

PDF accessibility compliance toolkit for academic and historical publications.

## What It Does

Transforms PDFs into accessibility-compliant documents meeting PDF/UA-1, Section 508, and ADA standards. Optimized for academic papers with mathematical content, tables, and complex layouts.

## Quick Start

### Prerequisites

**Windows**:
```powershell
choco install python tesseract
```

**macOS**:
```bash
brew install python tesseract poppler
```

**Linux**:
```bash
sudo apt-get install python3 tesseract-ocr poppler-utils
```

### Installation

```bash
git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
cd ePubs_Main
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install
pip install -e .[all]
```

### Usage

**Process a single PDF**:
```bash
epubs process input.pdf output.pdf
```

**Process multiple PDFs**:
```bash
epubs batch-process input_folder/ output_folder/
```

**Download academic papers**:
```bash
epubs-scrape --url "https://docs.lib.purdue.edu/etd/" --output data/input
```

## Key Features

- PDF/UA-1 compliance for screen readers
- 5-8x faster processing with Phase 2B optimization
- 90.9% accurate title extraction for academic papers
- Smart OCR that preserves existing text layers
- 40-80% file size reduction for web distribution
- Cross-platform: Windows, macOS, Linux

## Common Issues

**"Tesseract not found"**: Add Tesseract to your system PATH
**Memory errors**: Use `--mode sequential` for large files
**Slow processing**: Ensure virtual environment is activated and ML dependencies installed

## Support

- **Issues**: https://github.itap.purdue.edu/schipp0/ePubs_Main/issues
- **Email**: schipp0@purdue.edu

## License

MIT License
