# ePubs Accessibility Enhancement

**Simple, reliable PDF preprocessing for accessibility compliance**

A streamlined toolkit for transforming academic and historical PDFs into accessibility-ready documents. Designed for preparation of PDFs before manual tagging in Adobe Acrobat Pro.

---

## What This Does

This project provides **two essential components** for PDF accessibility workflows:

1. **Processor** - Prepares PDFs for accessibility tagging
   - OCR text layer generation (invisible text for screen readers)
   - Orphan tag stripping (critical for Acrobat compatibility)
   - Accurate tagging/language metadata (no false PDF/UA-1 claims)
   - Batch processing with folder preservation

2. **Scraper** - Downloads academic papers from digital repositories
   - Purdue ETD collection support
   - Automated bulk downloading
   - Metadata preservation

---

## Quick Start

### Prerequisites

**System Requirements:**
- Python 3.9+
- Tesseract OCR

**Install:**
```bash
# macOS
brew install python tesseract

# Linux (Ubuntu/Debian)
sudo apt-get install python3 python3-pip tesseract-ocr

# Windows
choco install python tesseract
```

### Installation

```bash
# Clone repository
git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
cd ePubs_Main

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify
python3 -m src.processor.main_simple version
```

---

## Usage

### PDF Processing

**Single file:**
```bash
python3 -m src.processor.main_simple process \
    input.pdf output.pdf \
    --title "Document Title" \
    --author "Author Name" \
    --language en-US
```

**Batch processing:**
```bash
python3 -m src.processor.main_simple batch-process \
    data/input/ data/output/ \
    --workers 2
```

**Common options:**
- `--skip-ocr` - Skip OCR if text already exists
- `--force-ocr` - Redo OCR even if text exists (for scans with a bad existing OCR layer). Avoid on born-digital PDFs (Word exports etc.): real text is normally left alone, but text in non-embedded fonts can get OCR'd again and read twice by screen readers
- `--language en-GB` - Document language; by default the PDF's own language is kept (en-US if it has none)
- `--verbose` - Show detailed logging
- `--workers N` - Use N parallel workers for batch
- `--dpi 400` - Higher DPI for degraded scans
- `--ocr-lang fra` - Non-English OCR (French example)

### Document Scraping

**Single collection:**
```bash
python3 -m src.scraper.purdue_collection_downloader download \
    --url "https://docs.lib.purdue.edu/roadschool/" \
    --output ~/Downloads
```

**Multiple collections from file:**
```bash
python3 -m src.scraper.purdue_collection_downloader download \
    --url-file src/scraper/urls.txt
```

**Common options:**
- `--url` - Single collection URL (can be used multiple times)
- `--url-file` - Text file with URLs (one per line)
- `--output` - Output directory (defaults to config.ini setting)
- `--username` - Purdue username for authentication
- `--verbose` - Show detailed logging
- `--dry-run` - Preview what would be downloaded

---

## Complete Workflows

### Workflow 1: Process Local PDFs

```bash
# 1. Organize PDFs
mkdir -p data/input
cp ~/Documents/papers/*.pdf data/input/

# 2. Batch process
python3 -m src.processor.main_simple batch-process \
    data/input/ data/output/ \
    --workers 2 --verbose

# 3. Check results
cat data/output/batch_processing_summary.json

# 4. Open in Acrobat Pro for manual tagging
open -a "Adobe Acrobat Pro" data/output/paper1.pdf
```

### Workflow 2: Scrape Then Process

```bash
# 1. Download papers
python3 -m src.scraper.purdue_collection_downloader download \
    --url-file src/scraper/urls.txt \
    --output data/input/

# 2. Process
python3 -m src.processor.main_simple batch-process \
    data/input/ data/output/ \
    --workers 4

# 3. Tag in Acrobat
```

### Workflow 3: Large Batch Processing

```bash
# Process in batches with logging
python3 -m src.processor.main_simple batch-process \
    data/input/batch1/ data/output/batch1/ \
    --workers 4 --verbose 2>&1 | tee logs/batch1.log

# Check failures
jq '.failed_files' data/output/batch1/batch_processing_summary.json
```

---

## Common Scenarios

### Scanned Historical Documents
Old scanned PDFs with no text layer:
```bash
python3 -m src.processor.main_simple batch-process \
    scanned_docs/ enhanced_docs/ \
    --force-ocr --dpi 400 --workers 2
```

### Modern PDFs with Text
PDFs with real text, e.g. Word exports (already-tagged files keep their tags):
```bash
python3 -m src.processor.main_simple batch-process \
    modern_pdfs/ compliant_pdfs/ \
    --skip-ocr --workers 4
```

### Mixed Quality Batch
Automatic detection (100 chars/page threshold):
```bash
python3 -m src.processor.main_simple batch-process \
    mixed_pdfs/ output_pdfs/ \
    --text-threshold 100 --workers 2
```

### Non-English Documents
French papers example:
```bash
# Install French language data first:
# macOS: brew install tesseract-lang
# Linux: sudo apt-get install tesseract-ocr-fra

python3 -m src.processor.main_simple batch-process \
    french_papers/ output/ \
    --ocr-lang fra --language fr-FR
```

### Memory-Constrained Environment
Limited RAM with large PDFs:
```bash
python3 -m src.processor.main_simple batch-process \
    large_pdfs/ output/ \
    --workers 1
```

---

## What Gets Enhanced

### PDF/UA-1 Preprocessing
- ✅ OCR text layer (invisible - for screen readers only)
- ✅ Orphan tag stripping (removes malformed marked content)
- ✅ OCR text layer flattened into page content (prevents Acrobat tagging every page as a Figure)
- ✅ No PDF/UA-1 conformance claim on untagged output (add tags in Acrobat first)
- ✅ Document properties (title, language, author)
- ✅ Clean structure for Acrobat manual tagging
- ✅ Existing valid tag trees preserved when OCR isn't needed
- ❌ No auto-generated accessibility tags (do this in Acrobat)

### Key Feature: Intelligent Tag Cleanup

After OCR with ocrmypdf's hocr renderer:
- **Preserves**: Marked content operators (BDC/EMC) - these are "hooks" for Acrobat
- **Removes**: Incomplete StructTreeRoot that interferes with manual tagging
- **Removes**: StructParents (orphan page references)
- **Result**: Clean PDF structure where Acrobat can link invisible text to tags

For non-OCR PDFs with orphan tags:
- **Removes**: All malformed marked content operators
- **Removes**: StructParents without valid structure tree
- **Result**: Clean slate for Acrobat's tagging system

---

## Project Structure

```
ePubs_Main/
├── README.md                   # This file
├── requirements.txt            # Consolidated dependencies (12 packages)
├── pyproject.toml             # Package configuration
│
├── src/
│   ├── processor/             # PDF enhancement toolkit (6 files)
│   │   ├── main_simple.py              # CLI (234 lines)
│   │   ├── simple_ocr_enhancer.py      # OCR processing
│   │   ├── simple_pdfua_enhancer.py    # PDF/UA compliance
│   │   ├── simple_enhancement_service.py  # Orchestration
│   │   └── simple_batch_processor.py   # Batch processing
│   │
│   └── scraper/               # Document acquisition
│       ├── purdue_downloader.py
│       ├── optimized_downloader.py
│       └── config.ini
│
├── data/
│   ├── input/                 # Source PDFs
│   └── output/                # Enhanced PDFs
│
├── logs/                      # Processing logs
├── tests/                     # Integration tests
│
└── archive/phase2b/           # Archived Phase 2B code (~9,000 lines)
    └── README.md
```

---

## Simplified Architecture

**Stage 2 & 3 Refactoring (2025-10-29):**
- Reduced CLI from 1,092 → 234 lines (78% reduction)
- Reduced dependencies from 33+ → 12 packages (67% reduction)
- Archived ~9,000 lines of Phase 2B complexity
- Focus on two core components: processor + scraper

**Pipeline:**
```
Input PDF → OCR Enhancement → PDF/UA-1 Enhancement → Output PDF
```

Simple, sequential processing. No ML, no caching, no complex orchestration.

**Core Dependencies:**
- PyMuPDF - PDF manipulation
- pikepdf - PDF structure modification
- ocrmypdf - OCR with proper text positioning
- Pillow/numpy - Image processing
- pytesseract - Tesseract OCR interface
- typer + rich - CLI and terminal output
- tqdm - Progress bars
- pyyaml, python-decouple - Configuration
- python-magic - File type detection

**Total:** 12 packages (vs 33+ in Phase 2B)

---

## Troubleshooting

### Common Errors

**"ModuleNotFoundError: No module named 'src'"**
```bash
# Ensure you're in project root
cd /path/to/ePubs_Main

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**"TesseractNotFoundError"**
```bash
# Verify installation
which tesseract  # Should show path

# Install if missing:
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
# Windows: Add C:\Program Files\Tesseract-OCR to PATH
```

**"Permission denied" errors**
```bash
# Check file permissions
ls -l input.pdf

# Make readable
chmod 644 input.pdf

# Ensure output directory writable
chmod 755 data/output/
```

**Slow processing**
```bash
# Check system resources
top  # or htop

# Solutions:
# - Reduce workers: --workers 1
# - Skip OCR if not needed: --skip-ocr
# - Process smaller batches
# - Check disk I/O (SSD vs HDD)
```

**PDFs look identical after processing**

This is normal! The enhancements are structural:
- OCR text layer (invisible to sighted users)
- Title, author and language (in document properties)
- Orphan tag removal (in PDF structure)

Verify enhancements:
```bash
# Check PDF properties
pdfinfo output.pdf | grep -i "tagged\|pdfua"

# Or in Python:
python3 -c "import pikepdf; pdf = pikepdf.open('output.pdf'); \
print(f'Tagged: {pdf.Root.get(\"/MarkInfo\", {}).get(\"/Marked\", False)}'); \
print(f'Language: {pdf.Root.get(\"/Lang\", \"Not set\")}')"
```

---

## Tips and Best Practices

### Performance Tips

1. **Worker count:**
   - 2-4 workers for most systems
   - 1 worker for memory-constrained environments
   - Don't exceed CPU core count

2. **Skip OCR when possible:**
   - Modern PDFs usually have text
   - Use `--skip-ocr` to save 70-80% processing time

3. **Batch size:**
   - Process 50-100 PDFs at a time
   - Monitor memory usage
   - Use batch_processing_summary.json to track progress

### Quality Tips

1. **OCR quality:**
   - Use `--dpi 400` for degraded scans
   - Use `--ocr-lang` for non-English documents
   - Clean scans = better OCR results

2. **Metadata:**
   - Always provide `--title` for better accessibility
   - Include `--author` when known
   - Set correct `--language` code

3. **Verification:**
   - Spot-check processed PDFs
   - Open in Acrobat to verify structure
   - Check batch_processing_summary.json for failures

### Workflow Tips

**Organization:**
```
project/
├── 01_original/     # Source PDFs
├── 02_processed/    # After enhancement
├── 03_tagged/       # After Acrobat tagging
└── 04_final/        # Ready for distribution
```

**Naming conventions:**
- Use descriptive names
- Include dates or versions
- Avoid spaces (use underscores)

**Backup:**
- Always keep originals
- Version processed files
- Save batch_processing_summary.json reports

---

## Next Steps After Processing

1. **Open in Adobe Acrobat Pro**
2. **Use Tags panel** to add proper structure:
   - Headings (H1, H2, etc.)
   - Paragraphs
   - Lists
   - Tables
   - Figures with alt text
3. **Run Accessibility Checker**
4. **Fix any issues**
5. **Export compliant PDF**

The orphan tag stripping and OCR layer flattening from this tool ensure clean tagging in Acrobat!

---

## Architecture History

This project underwent major simplification:

**Phase 2B** (Complex):
- 98 Python files, 33+ dependencies
- FAISS vector database, ML training, hierarchical caching
- Performance monitoring dashboard
- Mathematical notation detection
- Result: Too complex to maintain reliably

**Current** (Simplified):
- 2 core components (processor + scraper)
- 12 dependencies, ~1,100 lines of new code
- Focus on essential functionality
- Result: Simple, reliable, maintainable

See `/archive/phase2b/` for archived advanced features.

---

## License

MIT License

## Support

- **Issues**: https://github.itap.purdue.edu/schipp0/ePubs_Main/issues
- **Email**: schipp0@purdue.edu

---

**Philosophy**: Simple, reliable tools that prepare PDFs for manual accessibility tagging in Adobe Acrobat Pro. We handle the tedious preprocessing (OCR, metadata, tag cleanup); you handle the proper tagging.
