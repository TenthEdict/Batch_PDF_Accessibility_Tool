# ePubs Accessibility Enhancement

**Simple, reliable PDF preprocessing for accessibility compliance**

A streamlined toolkit for transforming academic and historical PDFs into accessibility-ready documents. Designed for preparation of PDFs before manual tagging in Adobe Acrobat Pro.

---

## What This Does

This project provides **two essential components** for PDF accessibility workflows:

1. **Processor** - Prepares PDFs for accessibility tagging
   - OCR text layer generation
   - Orphan tag stripping (critical for Acrobat compatibility)
   - PDF/UA-1 metadata compliance
   - Batch processing with folder preservation

2. **Scraper** - Downloads academic papers from digital repositories
   - Purdue ETD collection support
   - Automated bulk downloading
   - Metadata preservation

## Quick Start

### Prerequisites

**System Requirements:**
- Python 3.9+
- Tesseract OCR

**macOS:**
```bash
brew install python tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3 python3-pip tesseract-ocr
```

**Windows:**
```powershell
choco install python tesseract
```

### Installation

```bash
# Clone repository
git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
cd ePubs_Main

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install simplified dependencies
pip install -r requirements-simple.txt
```

## Usage

### PDF Processing

**Process a single PDF:**
```bash
python3 -m processor.unified_project.src.main_simple process \
    input.pdf output.pdf \
    --title "Document Title" \
    --language en-US
```

**Process multiple PDFs (preserves folder structure):**
```bash
python3 -m processor.unified_project.src.main_simple batch-process \
    input_folder/ output_folder/ \
    --workers 2
```

**Common options:**
- `--skip-ocr` - Skip OCR if text already exists
- `--force-ocr` - Force OCR even if text exists
- `--verbose` - Show detailed logging
- `--workers N` - Use N parallel workers for batch processing

### Document Scraping

**Download papers from Purdue ETD:**
```bash
cd scraper
python3 purdue_downloader.py
```

The scraper will:
- Prompt for collection URL
- Download PDFs to configured directory
- Preserve metadata and folder structure
- Handle authentication if required

**Configure download location:**
Edit `scraper/config.ini`:
```ini
[PurdueDownloader]
download_directory = /path/to/output
```

## Workflow

The typical workflow for creating accessible PDFs:

1. **Scrape** documents (if needed):
   ```bash
   cd scraper && python3 purdue_downloader.py
   ```

2. **Process** PDFs:
   ```bash
   python3 -m processor.unified_project.src.main_simple batch-process \
       data/input/ data/output/
   ```

3. **Manual tagging** in Adobe Acrobat Pro:
   - Open processed PDFs in Acrobat
   - Use Tags panel to add proper accessibility structure
   - The orphan tag stripping ensures clean tagging

4. **Export** compliant PDFs meeting WCAG 2.1/PDF/UA standards

## What Gets Enhanced

### PDF/UA-1 Preprocessing
- ✅ OCR text layer (using Tesseract)
- ✅ Orphan tag stripping (removes malformed marked content)
- ✅ PDF/UA-1 metadata
- ✅ Document properties (title, language, author)
- ✅ Clean StructTreeRoot for manual tagging
- ❌ No auto-generated accessibility tags (do this in Acrobat)

### Key Feature: Orphan Tag Stripping

Many PDFs have malformed tagging where pages have `StructParents` entries but no proper structure tree. This creates "orphan tags" that confuse Adobe Acrobat's tagging system.

**This tool aggressively removes orphan tags** (BDC/BMC/EMC operators), ensuring:
- Clean PDF structure for Acrobat
- Proper tag tree creation
- No interference with manual tagging workflow

## Project Structure

```
ePubs_Main/
├── processor/                  # PDF enhancement toolkit
│   └── unified_project/src/
│       ├── enhancers/
│       │   ├── simple_ocr_enhancer.py         # Basic OCR
│       │   └── simple_pdfua_enhancer.py       # PDF/UA compliance
│       ├── services/
│       │   └── simple_enhancement_service.py  # Pipeline orchestration
│       ├── batch/
│       │   └── simple_batch_processor.py      # Batch processing
│       └── main_simple.py                     # CLI (234 lines)
│
├── scraper/                    # Document acquisition
│   ├── purdue_downloader.py                   # Main scraper
│   ├── optimized_downloader.py                # Enhanced download logic
│   └── config.ini                             # Configuration
│
├── data/                       # Input/output files
│   ├── input/                  # Source PDFs
│   └── output/                 # Enhanced PDFs
│
├── archive/phase2b/            # Archived Phase 2B code (~9,000 lines)
│
├── requirements-simple.txt     # Core dependencies (11 packages)
└── README.md                   # This file
```

## Simplified Architecture

**Stage 2 Refactoring (2025-10-29):**
- Reduced CLI from 1,092 → 234 lines (78% reduction)
- Reduced dependencies from 33+ → 11 packages (67% reduction)
- Archived ~9,000 lines of Phase 2B complexity
- Focus on two core components: processor + scraper

**Pipeline:**
```
Input PDF → OCR Enhancement → PDF/UA-1 Enhancement → Output PDF
```

Simple, sequential processing. No ML, no caching, no complex orchestration.

## Dependencies

**Core packages** (see `requirements-simple.txt`):
- PyMuPDF - PDF manipulation
- pikepdf - PDF structure modification
- Pillow - Image processing
- pytesseract - OCR interface
- typer + rich - CLI and terminal output
- tqdm - Progress bars
- 5 more utilities

**Total:** 11 packages (vs 33+ in Phase 2B)

## Troubleshooting

**"Tesseract not found"**
- macOS: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`
- Windows: Add Tesseract to system PATH

**Import errors**
- Ensure virtual environment is activated
- Run: `pip install -r requirements-simple.txt`

**Slow processing**
- Use `--workers 2` or `--workers 4` for batch processing
- Consider `--skip-ocr` if PDFs already have text

**Memory errors with large batches**
- Process in smaller batches
- Reduce number of workers

## Documentation

- **USAGE_GUIDE.md** - Detailed examples and workflows
- **REFACTORING_PLAN.md** - Simplification strategy
- **STAGE1_COMPLETION.md** - Core stability fixes
- **STAGE2_COMPLETION.md** - Modular refactoring results

## Architecture History

This project went through major simplification:

**Phase 2B** (Complex):
- 98 Python files, 33+ dependencies
- FAISS vector database, ML training, hierarchical caching
- Performance monitoring dashboard
- Mathematical notation detection
- Result: Too complex to maintain reliably

**Current** (Simplified):
- 2 core components (processor + scraper)
- 11 dependencies, ~1,100 lines of new code
- Focus on essential functionality
- Result: Simple, reliable, maintainable

See `/archive/phase2b/` for archived advanced features.

## License

MIT License

## Support

- **Issues**: https://github.itap.purdue.edu/schipp0/ePubs_Main/issues
- **Email**: schipp0@purdue.edu
- **Documentation**: See USAGE_GUIDE.md

---

**Philosophy**: Simple, reliable tools that prepare PDFs for manual accessibility tagging in Adobe Acrobat Pro. We handle the tedious preprocessing; you handle the proper tagging.
