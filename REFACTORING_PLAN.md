# ePubs Accessibility Project: Comprehensive Simplification & Refactoring Plan

**Date**: 2025-10-29
**Goal**: Simplify from overly ambitious Phase 2B to focused Option A: **Simple OCR + PDF/UA Compliance + Batch Processing**

---

## Executive Summary

The ePubs Accessibility Enhancement Project has evolved into an overly complex system with **98 Python files**, ML training infrastructure, FAISS vector database integration, and sophisticated performance monitoring. This complexity prevents the core functionality from working.

**Current State**: System cannot initialize due to FAISS type hint error
**Desired State**: Simple, reliable OCR + PDF/UA compliance + orphan tag stripping for Acrobat remediation workflow

---

## Problem Analysis

### Root Cause of Logging Failure

```
Import Chain:
test_enhancement_logging.py
  → EnhancementService
    → minimal_pdf_enhancer
      → equation_boundary_extractor
        → faiss_vector_db.py:166
          → CRASH: AttributeError: 'NoneType' object has no attribute 'Index'
```

**The Issue**: When FAISS is not installed, `faiss=None`. Type hints like `faiss.Index` are evaluated at class definition time, causing `None.Index` access which raises `AttributeError`.

### Complexity Breakdown

| Category | Current State | Needed for Option A |
|----------|--------------|---------------------|
| **Directories** | 26 subdirectories | 5-6 subdirectories |
| **Python Files** | ~98 files | ~15-20 files |
| **Dependencies** | 33+ packages (including faiss-cpu) | ~10-12 packages |
| **Features** | ML training, FAISS, hierarchical caching, monitoring | OCR, PDF/UA, batch processing |
| **Complexity** | Very High | Low-Medium |

---

## What's Working Well (Keep These)

### ✅ Excellent Features to Preserve

1. **Orphan Tag Stripping** (minimal_pdf_enhancer.py:118-238)
   - Critical for Adobe Acrobat compatibility
   - Removes malformed marked content operators
   - Clean implementation

2. **Security Utilities** (utils/security.py)
   - Path validation
   - File type validation
   - Input sanitization

3. **Performance Utilities** (utils/performance.py)
   - Memory-efficient iteration
   - Resource limits
   - Batch chunking

4. **Structured Logging** (log_formatters/json_formatter.py)
   - JSON logging with correlation IDs
   - Performance metrics
   - Well-designed infrastructure

5. **CLI Architecture** (main.py)
   - Typer-based CLI
   - Good command structure
   - Can be simplified but architecture is solid

---

## What to Remove (Phase 2B Complexity)

### ❌ Features to Eliminate

| Directory/Feature | Lines of Code | Reason for Removal |
|------------------|---------------|-------------------|
| **academic/** | ~3,500 lines | Mathematical notation detection out of scope |
| **ml/** | ~1,200 lines | FAISS vector database not needed |
| **training/** | ~2,000 lines | ML training infrastructure unnecessary |
| **monitoring/** | ~800 lines | Performance dashboard overkill |
| **caching/** | ~600 lines | Hierarchical caching adds complexity |
| **acceleration/** | ~400 lines | Advanced optimizations not needed initially |
| **orchestration/** | ~300 lines | Over-engineered service layer |

**Total Removal**: ~9,000 lines of Phase 2B complexity

---

## Dependency Analysis

### Current Requirements (requirements.txt)

```python
# Core PDF processing (KEEP)
PyMuPDF>=1.23.0,<1.25.0
pikepdf>=8.3.0,<9.0.0
pdf2image>=1.16.3,<2.0.0
pdfplumber>=0.7.0,<1.0.0  # Possibly remove if not used

# Image Processing (KEEP)
Pillow>=10.0.0,<11.0.0
opencv-python-headless>=4.8.0,<5.0.0  # May be optional
scikit-image>=0.21.0,<1.0.0  # May be optional
numpy>=1.24.0,<2.0.0

# OCR (KEEP)
pytesseract>=0.3.10,<1.0.0

# Data Processing (EVALUATE)
pandas>=1.5.0,<3.0.0  # Likely not needed
scipy>=1.7.0,<2.0.0  # Likely not needed
tqdm>=4.66.0,<5.0.0  # KEEP for progress bars

# Configuration (KEEP)
pyyaml>=6.0.0,<7.0.0
python-decouple>=3.6,<4.0

# CLI (KEEP)
typer>=0.12.0,<1.0.0
rich>=13.0.0,<14.0.0

# Utilities (EVALUATE)
pathlib-mate>=1.0.0,<2.0.0  # Likely not needed
python-magic>=0.4.27,<1.0.0  # KEEP for file type validation
ocrmypdf>=16.0.0,<17.0.0  # EVALUATE - may provide better OCR

# ML (REMOVE)
faiss-cpu  # REMOVE
```

### Simplified Requirements (Proposed)

```python
# Core PDF processing
PyMuPDF>=1.23.0,<1.25.0
pikepdf>=8.3.0,<9.0.0
pdf2image>=1.16.3,<2.0.0

# Image Processing
Pillow>=10.0.0,<11.0.0
numpy>=1.24.0,<2.0.0

# OCR
pytesseract>=0.3.10,<1.0.0
# OR ocrmypdf>=16.0.0,<17.0.0 (provides integrated OCR solution)

# Progress bars
tqdm>=4.66.0,<5.0.0

# Configuration
pyyaml>=6.0.0,<7.0.0
python-decouple>=3.6,<4.0

# CLI
typer>=0.12.0,<1.0.0
rich>=13.0.0,<14.0.0

# Utilities
python-magic>=0.4.27,<1.0.0
```

**Dependency Reduction**: ~33 → ~11 packages (67% reduction)

---

## Simplified Architecture Design

### Target Directory Structure

```
processor/unified_project/src/
├── main.py                      # Simplified CLI
├── core/                        # Core domain models
│   ├── __init__.py
│   ├── document.py             # Document models
│   └── result.py               # Result types
├── enhancers/                   # Core enhancers only
│   ├── __init__.py
│   ├── enhancer_base.py        # Base class
│   ├── ocr_enhancer.py         # Simplified OCR (no ML)
│   └── pdf_ua_enhancer.py      # PDF/UA compliance + orphan tag stripping
├── services/                    # Simplified services
│   ├── __init__.py
│   └── enhancement_service.py  # Orchestration
├── batch/                       # Batch processing
│   ├── __init__.py
│   └── batch_processor.py      # Simple batch with folder structure preservation
├── utils/                       # Utilities
│   ├── __init__.py
│   ├── security.py             # Keep security validations
│   ├── performance.py          # Keep resource management
│   ├── logging_config.py       # Simplified logging setup
│   └── file_utils.py           # File operations
└── log_formatters/              # Logging
    ├── __init__.py             # Fixed exports
    └── json_formatter.py       # Keep structured logging
```

**Directory Reduction**: 26 → 6 core directories

### Component Responsibilities

#### 1. OCR Enhancer (Simplified)
```python
class OCREnhancer(EnhancerBase):
    """Simple OCR processing without ML optimization."""

    def enhance(self, input_path, output_path, **kwargs):
        """
        1. Check if PDF needs OCR (has text layer?)
        2. If needed, extract pages as images
        3. Run Tesseract OCR with standard parameters
        4. Create OCR layer in PDF
        5. Return result
        """
```

**Features**:
- Basic OCR using pytesseract or ocrmypdf
- No ML parameter optimization
- Standard DPI and preprocessing
- Simple quality checks

#### 2. PDF/UA Enhancer (Keep Core Features)
```python
class PDFUAEnhancer(EnhancerBase):
    """PDF/UA compliance with orphan tag stripping."""

    def enhance(self, input_path, output_path, **kwargs):
        """
        1. Strip orphan marked content tags (CRITICAL)
        2. Set PDF/UA metadata
        3. Set document title, author, language
        4. Basic structure tree (if needed)
        5. Return result
        """
```

**Features**:
- Orphan tag stripping (already implemented)
- PDF/UA-1 metadata
- Document properties
- Basic accessibility structure
- No mathematical notation detection

#### 3. Enhancement Service (Simplified Orchestration)
```python
class EnhancementService:
    """Orchestrates enhancement pipeline."""

    def __init__(self):
        self.ocr_enhancer = OCREnhancer()
        self.pdfua_enhancer = PDFUAEnhancer()

    def enhance_document(self, input_path, output_path, **kwargs):
        """
        1. Validate input
        2. Run OCR enhancer (if needed)
        3. Run PDF/UA enhancer (orphan tags + compliance)
        4. Return result
        """
```

**Pipeline**:
```
Input PDF
  ↓
[Step 1] OCR Enhancement (if needed)
  ↓
[Step 2] PDF/UA Enhancement (orphan tags + metadata)
  ↓
Output PDF (ready for Acrobat remediation)
```

#### 4. Batch Processor (Folder Structure Preservation)
```python
class BatchProcessor:
    """Batch process PDFs preserving folder structure."""

    def process_batch(self, input_dir, output_dir, **kwargs):
        """
        1. Walk input directory recursively
        2. Find all PDFs
        3. Recreate folder structure in output_dir
        4. Process each PDF
        5. Save to corresponding output location
        6. Generate summary report
        """
```

**Features**:
- Recursive directory walking
- Folder structure preservation
- Progress bar (tqdm)
- Error handling and logging
- Summary report (JSON)
- Optional parallel processing (simple ThreadPoolExecutor, not Phase 2B)

#### 5. Simplified CLI
```bash
# Single file processing
epubs process input.pdf output.pdf --title "Document Title" --language en-US

# Batch processing
epubs batch-process input_dir/ output_dir/ --workers 2

# Cache management (keep simple)
epubs cache clear
epubs cache stats
```

**Commands to Remove**:
- `validate-phase2b`
- `monitor-performance`
- `organize-training-data`
- `extract-accessibility-patterns`
- `train-accessibility-models`
- Complex health/stats commands

---

## Three-Stage Refactoring Plan

### Stage 1: Core Stability (Week 1) - IMMEDIATE FIXES

**Goal**: Get the system working with minimal changes

#### Task 1.1: Fix FAISS Import Error (Day 1)
```python
# processor/unified_project/src/ml/faiss_vector_db.py

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import faiss

class FAISSVectorDatabase:
    def _create_index(self, size_hint: int = 1000) -> Optional['faiss.Index']:
        if not FAISS_AVAILABLE:
            raise RuntimeError("FAISS not available")
        # ... rest of implementation
```

**Files to modify**:
- `processor/unified_project/src/ml/faiss_vector_db.py`

**Testing**: Run `test_enhancement_logging.py` to verify logging appears

#### Task 1.2: Complete Logging Migration (Day 1)
```python
# processor/unified_project/src/log_formatters/__init__.py

"""Structured JSON logging for ePubs project."""
from .json_formatter import (
    JSONFormatter,
    CorrelationContext,
    correlation_context,
    setup_json_logging,
    set_correlation_id,
    # ... all exports
)

__all__ = [
    'JSONFormatter',
    'CorrelationContext',
    # ... all exports
]
```

**Files to modify**:
- `processor/unified_project/src/log_formatters/__init__.py`

**Testing**: Verify imports work from other modules

#### Task 1.3: Make ML Features Truly Optional (Day 2-3)

**Modify enhancement_service.py**:
```python
# Import with fallback
try:
    from ..enhancers.accessibility_ml_enhancer import AccessibilityMLEnhancer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    AccessibilityMLEnhancer = None

class EnhancementService:
    def __init__(self, use_ml=False):
        # ... basic enhancers always available

        if use_ml and ML_AVAILABLE:
            self.ml_enhancer = AccessibilityMLEnhancer()
        else:
            self.ml_enhancer = None
```

**Modify minimal_pdf_enhancer.py**:
```python
# Import mathematical components with fallback
try:
    from ..academic.mathematical_notation_detector import MathematicalNotationDetector
    from ..academic.equation_boundary_extractor import EquationBoundaryExtractor
    MATH_AVAILABLE = True
except ImportError:
    MATH_AVAILABLE = False

class MinimalPDFEnhancer:
    def __init__(self, enable_math=False):
        if enable_math and MATH_AVAILABLE:
            self.math_detector = MathematicalNotationDetector()
        else:
            self.math_detector = None
```

**Files to modify**:
- `processor/unified_project/src/services/enhancement_service.py`
- `processor/unified_project/src/enhancers/minimal_pdf_enhancer.py`
- `processor/unified_project/src/main.py` (add --disable-ml flag)

**Testing**:
```bash
python3 processor/unified_project/src/main.py process \
  data/input/test.pdf \
  data/output/test_output.pdf \
  --verbose
```

#### Task 1.4: Verify Core Pipeline Works (Day 3)

**Test basic workflow**:
1. Single file processing
2. Batch processing (sequential)
3. Orphan tag stripping
4. Logging output

**Success Criteria**:
- ✅ System initializes without errors
- ✅ Logging appears in console/files
- ✅ Can process test PDFs
- ✅ Orphan tags are stripped
- ✅ PDF/UA metadata is set

---

### Stage 2: Modular Refactoring (Week 2-3) - SIMPLIFICATION

**Goal**: Remove Phase 2B complexity, create clean architecture

#### Task 2.1: Create Simplified Enhancers (Week 2, Days 1-2)

**Create `simple_ocr_enhancer.py`**:
```python
"""Simplified OCR enhancer without ML optimization."""

class SimpleOCREnhancer(EnhancerBase):
    """
    Simple OCR processing using standard tesseract parameters.
    No ML optimization, no pattern learning.
    """

    def __init__(self):
        super().__init__("simple_ocr_enhancer")
        self.default_dpi = 300
        self.default_lang = 'eng'

    def needs_ocr(self, pdf_path: Path) -> bool:
        """Check if PDF needs OCR (no text layer)."""
        # Simple text extraction check

    def enhance(self, input_path: Path, output_path: Path, **kwargs) -> bool:
        """
        Process PDF with OCR if needed.

        Steps:
        1. Check if OCR needed
        2. Extract pages as images (pdf2image)
        3. Run tesseract OCR
        4. Create PDF with text layer
        5. Validate output
        """
```

**Create `simple_pdfua_enhancer.py`**:
```python
"""Simplified PDF/UA enhancer with orphan tag stripping."""

class SimplePDFUAEnhancer(EnhancerBase):
    """
    PDF/UA compliance without mathematical notation detection.
    Focuses on:
    - Orphan tag stripping (critical for Acrobat)
    - Basic metadata (title, author, language)
    - PDF/UA-1 flags
    """

    def strip_orphan_tags(self, pdf: pikepdf.Pdf) -> int:
        """Strip orphan marked content tags."""
        # Port from minimal_pdf_enhancer.py:118-238

    def enhance(self, input_path: Path, output_path: Path, **kwargs) -> bool:
        """
        Apply PDF/UA compliance.

        Steps:
        1. Strip orphan tags
        2. Set PDF/UA metadata
        3. Set document properties
        4. Validate output
        """
```

**Files to create**:
- `processor/unified_project/src/enhancers/simple_ocr_enhancer.py`
- `processor/unified_project/src/enhancers/simple_pdfua_enhancer.py`

**Testing**: Unit tests for each enhancer

#### Task 2.2: Simplify Enhancement Service (Week 2, Day 3)

**Create `simple_enhancement_service.py`**:
```python
"""Simplified enhancement service without ML/Phase 2B features."""

class SimpleEnhancementService:
    """
    Orchestrates basic PDF enhancement pipeline.

    Pipeline:
    1. OCR (if needed)
    2. PDF/UA compliance (orphan tags + metadata)
    """

    def __init__(self):
        self.ocr_enhancer = SimpleOCREnhancer()
        self.pdfua_enhancer = SimplePDFUAEnhancer()
        self.logger = logging.getLogger(__name__)

    def enhance_document(self, input_path, output_path, **kwargs):
        """Process single PDF through enhancement pipeline."""
```

**Files to create**:
- `processor/unified_project/src/services/simple_enhancement_service.py`

#### Task 2.3: Create Simple Batch Processor (Week 2, Day 4-5)

**Create `simple_batch_processor.py`**:
```python
"""Simple batch processor with folder structure preservation."""

class SimpleBatchProcessor:
    """
    Process multiple PDFs preserving directory structure.

    Features:
    - Recursive directory walking
    - Folder structure preservation
    - Progress tracking (tqdm)
    - Error handling
    - Summary reporting
    - Optional simple parallelization (ThreadPoolExecutor)
    """

    def process_batch(self, input_dir, output_dir, workers=1):
        """
        Process all PDFs in input_dir.

        Returns:
        - Summary report (JSON)
        - List of successful/failed files
        """
```

**Files to create**:
- `processor/unified_project/src/batch/simple_batch_processor.py`

#### Task 2.4: Simplify CLI (Week 3, Day 1-2)

**Modify `main.py`**:
```python
"""Simplified CLI for core functionality."""

# Remove imports for:
# - Phase 2B processors
# - Performance monitoring
# - Training commands
# - Complex health/stats

# Keep only:
# - process (single file)
# - batch-process (simple mode)
# - cache clear/stats (basic)

@app.command()
def process(
    input_path: Path,
    output_path: Path,
    title: Optional[str] = None,
    author: Optional[str] = None,
    language: str = "en-US",
    skip_ocr: bool = False,
    verbose: bool = False
):
    """Process single PDF file."""

@app.command()
def batch_process(
    input_dir: Path,
    output_dir: Path,
    workers: int = 1,
    recursive: bool = True,
    verbose: bool = False
):
    """Process multiple PDFs preserving folder structure."""
```

**Files to modify**:
- `processor/unified_project/src/main.py` (massive simplification from 1093 → ~250 lines)

#### Task 2.5: Archive Phase 2B Code (Week 3, Day 3)

**Create archive directory**:
```bash
mkdir -p archive/phase2b
mv processor/unified_project/src/academic archive/phase2b/
mv processor/unified_project/src/ml archive/phase2b/
mv processor/unified_project/src/training archive/phase2b/
mv processor/unified_project/src/monitoring archive/phase2b/
mv processor/unified_project/src/caching archive/phase2b/
mv processor/unified_project/src/acceleration archive/phase2b/
```

**Update .gitignore**:
```
# Phase 2B archived code
/archive/
```

**Files to preserve** (move to archive):
- All Phase 2B features (don't delete, archive for potential future use)

#### Task 2.6: Update Dependencies (Week 3, Day 4)

**Create `requirements-simple.txt`**:
```python
# Simplified dependencies for core functionality
PyMuPDF>=1.23.0,<1.25.0
pikepdf>=8.3.0,<9.0.0
pdf2image>=1.16.3,<2.0.0
Pillow>=10.0.0,<11.0.0
numpy>=1.24.0,<2.0.0
pytesseract>=0.3.10,<1.0.0
tqdm>=4.66.0,<5.0.0
pyyaml>=6.0.0,<7.0.0
python-decouple>=3.6,<4.0
typer>=0.12.0,<1.0.0
rich>=13.0.0,<14.0.0
python-magic>=0.4.27,<1.0.0
```

**Testing**:
```bash
python3 -m venv venv-simple
source venv-simple/bin/activate
pip install -r requirements-simple.txt
python3 processor/unified_project/src/main.py --help
```

---

### Stage 3: Documentation & Optimization (Week 4) - POLISH

**Goal**: Document simplified system, optimize performance, add examples

#### Task 3.1: Update Documentation (Week 4, Day 1-2)

**Create `README_SIMPLE.md`**:
```markdown
# ePubs PDF Accessibility Enhancement Tool

## Overview
Simple, reliable PDF preprocessing for accessibility remediation in Adobe Acrobat.

## Features
- OCR text layer generation (Tesseract)
- Orphan tag stripping for Acrobat compatibility
- PDF/UA-1 metadata compliance
- Batch processing with folder structure preservation

## Installation
\`\`\`bash
pip install -r requirements-simple.txt
brew install tesseract  # macOS
\`\`\`

## Usage
\`\`\`bash
# Single file
epubs process input.pdf output.pdf --title "Document Title"

# Batch processing
epubs batch-process input_folder/ output_folder/ --workers 2
\`\`\`

## Workflow
1. Run epubs on scanned PDFs → Adds OCR layer, strips orphan tags
2. Open in Adobe Acrobat Pro → Manually add proper accessibility tags
3. Export fully compliant PDF → Meets WCAG 2.1 / PDF/UA standards
```

**Update Memory Bank**:
- `.memory-bank/projectbrief.md` - Update scope to reflect simplification
- `.memory-bank/systemPatterns.md` - Document new architecture
- `.memory-bank/techContext.md` - Update dependencies
- `.memory-bank/progress.md` - Reflect current state
- `.memory-bank/activeContext.md` - Focus on simple pipeline

#### Task 3.2: Create Examples (Week 4, Day 2)

**Create `examples/` directory**:
```
examples/
├── basic_processing.py
├── batch_processing.py
├── custom_metadata.py
└── error_handling.py
```

#### Task 3.3: Add Tests (Week 4, Day 3-4)

**Create test suite**:
```
tests/
├── test_simple_ocr_enhancer.py
├── test_simple_pdfua_enhancer.py
├── test_simple_enhancement_service.py
├── test_simple_batch_processor.py
└── test_cli.py
```

**Use pytest**:
```bash
pip install pytest pytest-cov
pytest tests/ --cov=processor/unified_project/src --cov-report=html
```

#### Task 3.4: Performance Optimization (Week 4, Day 5)

**Focus areas**:
1. OCR processing speed (optimize image preprocessing)
2. Batch processing efficiency (simple ThreadPoolExecutor)
3. Memory usage (process large batches without exhaustion)
4. Error recovery (handle corrupt PDFs gracefully)

#### Task 3.5: Create Migration Guide (Week 4, Day 5)

**Document differences**:
```markdown
# Migration from Phase 2B to Simple

## What Changed
- Removed ML/FAISS features
- Removed mathematical notation detection
- Simplified batch processing
- Removed performance monitoring dashboard

## Benefits
- 67% fewer dependencies
- 90% less code
- Faster startup time
- Easier to maintain
- More reliable

## What's Preserved
- Orphan tag stripping (critical feature!)
- PDF/UA compliance
- Security validations
- Structured logging
- Batch processing
```

---

## Implementation Checklist

### Stage 1: Core Stability (Week 1)
- [ ] Fix FAISS type hint error
- [ ] Complete log_formatters/__init__.py
- [ ] Make ML features optional
- [ ] Test basic pipeline
- [ ] Verify logging works
- [ ] Test on sample PDFs

### Stage 2: Modular Refactoring (Week 2-3)
- [ ] Create SimpleOCREnhancer
- [ ] Create SimplePDFUAEnhancer
- [ ] Create SimpleEnhancementService
- [ ] Create SimpleBatchProcessor
- [ ] Simplify main.py CLI
- [ ] Archive Phase 2B code
- [ ] Create requirements-simple.txt
- [ ] Test simplified system

### Stage 3: Documentation & Optimization (Week 4)
- [ ] Write README_SIMPLE.md
- [ ] Update Memory Bank
- [ ] Create examples
- [ ] Write test suite
- [ ] Optimize performance
- [ ] Create migration guide
- [ ] Final testing

---

## Risk Mitigation

### Risk 1: Breaking Existing Functionality
**Mitigation**:
- Archive all Phase 2B code (don't delete)
- Git branch for refactoring (`git checkout -b simplify-refactor`)
- Comprehensive testing at each stage
- Keep original main.py as main_phase2b.py backup

### Risk 2: Tesseract Quality Issues
**Mitigation**:
- Allow configuration of OCR parameters
- Consider ocrmypdf as alternative backend
- Add quality validation step
- Provide manual parameter override

### Risk 3: Missing Edge Cases
**Mitigation**:
- Test with diverse PDF types (scanned, native, mixed)
- Add error handling for corrupt PDFs
- Log all failures with detailed context
- Create issue templates for bug reports

---

## Success Metrics

### Technical Metrics
- [ ] System initializes without errors
- [ ] All unit tests pass
- [ ] Can process 100+ PDFs in batch
- [ ] Memory usage < 500MB for large batches
- [ ] Processing time < 30s per average PDF
- [ ] Error rate < 5% on diverse test set

### Usability Metrics
- [ ] Installation takes < 5 minutes
- [ ] CLI is intuitive (no complex flags)
- [ ] Documentation is clear and complete
- [ ] Examples cover common use cases
- [ ] Error messages are actionable

### Maintainability Metrics
- [ ] Codebase < 3,000 lines (down from ~15,000)
- [ ] Dependencies < 15 packages (down from 33)
- [ ] Test coverage > 70%
- [ ] No circular dependencies
- [ ] All modules have docstrings

---

## Next Steps

1. **Review this plan** - Ensure alignment with goals
2. **Approve Stage 1** - Get immediate fixes working
3. **Execute stages sequentially** - Don't skip ahead
4. **Test continuously** - Verify at each step
5. **Document learnings** - Update Memory Bank regularly

---

## Questions for Clarification

Before proceeding with implementation, please confirm:

1. **OCR Backend**: Prefer pytesseract (simple) or ocrmypdf (integrated solution)?
2. **Batch Parallelization**: Want simple ThreadPoolExecutor or strictly sequential?
3. **Testing Priority**: Focus on functionality first, or test coverage from start?
4. **Git Strategy**: Create new branch for refactoring, or work on main?
5. **Timeline**: Is 4-week timeline acceptable, or need faster?

---

## Conclusion

This refactoring plan transforms the ePubs project from an overly ambitious Phase 2B system into a focused, reliable tool for PDF accessibility preprocessing. The simplified architecture aligns perfectly with the end-user workflow: prepare PDFs for manual Acrobat remediation.

**Core Philosophy**: Simple, reliable, maintainable > Complex, sophisticated, broken

The orphan tag stripping feature (your recent addition) is preserved and highlighted as a critical capability. The Phase 2B ML features are archived (not deleted) for potential future exploration once the core system is stable.

**Ready to proceed with Stage 1 immediate fixes?**
