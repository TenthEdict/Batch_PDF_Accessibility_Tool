# Active Context

## Current Project State (October 2025)

**Project**: ePubs Accessibility Enhancement - PDF accessibility compliance toolkit for academic publications

**Status**: ✅ PRODUCTION READY - All 3 stages complete (2025-10-29)

**Final State**: Two core components, fully documented, tested, ready for use

**Stage 3 Completion**: Documentation & Optimization (2025-10-29)
- Removed 215MB obsolete files
- Complete README rewrite
- Created USAGE_GUIDE.md (400+ lines)
- Integration tests passing (5/5)
- Project ready for production deployment

### ✅ Production Features
- **Phase 2B Processing**: Default processing mode with 5-8x performance improvement
- **Academic OCR Pipeline**: Specialized for scholarly papers with mathematical content
- **PDF/UA-1 Compliance**: Clean accessibility structure without auto-generated tags
- **Cross-Platform Support**: Windows, macOS, Linux with consistent processing
- **Intelligent Title Extraction**: 90.9% accuracy on academic papers
- **Web Optimization**: 40-80% file size reduction for digital commons distribution
- **Mathematical Accessibility**: Integrated support for equations and formulas

### ⚠️ Experimental (Untested)
- **Accessibility Training System**: ML-based compliance generation (implementation complete, untested)
- **Automated WCAG/PDF-UA/ADA Generation**: Requires validation with training data

### Recent Fixes
- **Filename Convention**: Fixed "_enhanced" suffix naming (was incorrectly using "enhanced_" prefix)
- **Pikepdf Parsing**: Enhanced object type handling for diverse PDF structures
- **Image Corruption**: Eliminated black box artifacts in figure processing
- **OCR Detection**: Intelligent decision-making prevents unnecessary text layer corruption

## Current CLI Commands

```bash
# Single file processing
epubs process input.pdf output.pdf

# Batch processing (Phase 2B default)
epubs batch-process input_dir/ output_dir/

# Cache management
epubs cache stats
epubs cache clear

# Scraping
epubs-scrape --url "https://docs.lib.purdue.edu/etd/" --output data/input
```

## Active Development Context

### Simplified Architecture (Stage 2)
- **Pipeline**: OCR → PDF/UA-1 Enhancement (2-step, no compression)
- **Processing Mode**: Sequential with optional parallelization
- **No Service Container**: Direct instantiation for simplicity
- **No Enhancer Chain**: Simple service orchestration

### Simplified Components (New)
- **SimpleOCREnhancer**: Basic Tesseract OCR without ML (~220 lines)
- **SimplePDFUAEnhancer**: Orphan tag stripping + metadata (~350 lines)
- **SimpleEnhancementService**: Pipeline orchestration (~140 lines)
- **SimpleBatchProcessor**: Folder structure preservation (~400 lines)
- **main_simple.py**: Simplified CLI (~234 lines)

### Legacy Components (Archived)
- **Phase 2B Code**: Moved to /archive/phase2b/ (~9,000 lines)
- **MinimalPDFEnhancer**: Still exists, orphan stripping logic ported to Simple version
- **OCREnhancer**: Still exists, simplified version uses pytesseract directly
- **ML/FAISS/Caching**: All archived for potential future use

### Performance
- **Processing Speed**: 5-8x improvement with Phase 2B
- **File Size Reduction**: 40.9% average (6.3% to 74.8% range)
- **Processing Time**: 15.6s average per document
- **Success Rate**: 100% on test dataset (11/11 files)

## Next Priority Actions

1. **Documentation Cleanup**: Remove outdated verbose context (current task)
2. **Security Review**: Identify and fix vulnerabilities
3. **Performance Optimization**: Analyze bottlenecks
4. **Git Hygiene**: Update .gitignore, commit changes

## Technical Debt
- Accessibility training system needs validation or removal decision
- Memory bank has accumulated significant context rot
- Multiple deprecated README files need consolidation
- Archived directory contains outdated migration info

## 2026-11-03: Acrobat "difficult pages" → every page tagged as Figure
- Report: after our tool, Acrobat's Tagged PDF fix said "Some difficult pages were encountered requiring all graphics on those pages to be labeled as figures".
- Cause (probable): ocrmypdf grafts the invisible text into a Form XObject (`/OCR-...`) painted *under* the page image; we also set MarkInfo Marked=True/Suspects=True with no StructTreeRoot.
- Fix in `simple_pdfua_enhancer.py`: `_flatten_ocr_text_layers()` inlines the OCR text into the page content stream after the image (Acrobat-OCR layout); MarkInfo Marked now reflects whether a StructTreeRoot exists, Suspects removed. Rendering and text positions verified identical.
- Side benefit: `--force-ocr` on already-processed output no longer duplicates the text layer (ocrmypdf redo_ocr can't strip text inside forms).
- Not yet confirmed in Acrobat by the reporter.
- Follow-up (same day): `ocr_performed` now comes from `SimpleOCREnhancer.enhance_file_with_status()` (True only if ocrmypdf actually ran; tuple return keeps shared-service threads safe). Regex marked-content stripper replaced with a parsed-operator version (keeps /OC and /Artifact, recurses into forms, clears annotation StructParent). Flatten now always runs, and runs on the input before --force-ocr. Tool no longer writes pdfuaid:part or the GTS_PDFUA1 OutputIntent, and removes them from untagged files.

## 2026-11-11: Reporter's before/after spreadsheet + 4 test PDFs
- Ran c7bf0aa8 ("v1") and e83660f3 ("v2") on the reporter's files (catalog scan, newspaper with Acrobat Paper Capture OCR, two PDFium born-digital exports). None has a StructTreeRoot.
- Honors thesis (PDFium poster export): the reporter's bad v2 numbers (Tables/Lists/Alt Text all failing, "no fix option", 78 Tagged content failures) were taken on the *untagged* file; Acrobat fails every structure rule until the Tagged PDF fix is run. After autotagging, v2 output fails only Character encoding, Figures alt text and Appropriate nesting, same as the untouched original. Not a regression.
- Tried stripping orphan /Artifact too (the thesis paints body-text forms inside `/Artifact BMC`). Compared Acrobat-autotagged results: identical tag tree and identical tagged text either way; keeping /Artifact left 8 more decorative shape blocks as artifacts. Reverted: `_KEEP_MARKED_CONTENT` stays `/OC` + `/Artifact`.
- Fallback title came from the temp OCR file name ("Tmp4Bhwjsgv") in both versions whenever OCR wasn't skipped. Fix: `enhance_file(title_source=...)`, passed by the service.
- Catalog: v1's 0 table/heading errors are probably vacuous (every page tagged as one Figure, so nothing else to check); unconfirmed.
- Newspaper: already has Acrobat OCR text, so neither version OCRs or flattens; v2 only strips 307 `/Suspect` marks. Why its Acrobat results differ from untouched is unexplained.
