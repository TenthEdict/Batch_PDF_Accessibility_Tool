# Unified PDF Accessibility Engine

The core processing engine of the ePubs Accessibility Enhancement Project, implementing clean architecture principles with AI-powered document enhancement capabilities.

## 🏗️ Architecture Overview

This engine follows **Clean Architecture** with clear separation of concerns:

### Core Layers
- **Domain Layer** (`src/domain/`): Business entities and rules
- **Application Layer** (`src/services/`): Business logic orchestration  
- **Infrastructure Layer** (`src/repositories/`, `src/enhancers/`): External dependencies
- **Interface Layer** (`src/main.py`): CLI and user interfaces

### Service Container
Uses dependency injection via `src/core/service_container.py`:
- Singleton service management
- Automatic dependency resolution
- Extensible architecture for new components

## ✨ Features

### Multi-Stage Enhancement Pipeline
1. **OCR Enhancement** (`src/enhancers/ocr_enhancer.py`)
   - Optimized OCR with file size control
   - Ghostscript 10.x compatibility fixes
   - JPEG/JBIG2 compression optimization

2. **Adobe AutoTag** (`src/enhancers/adobe_autotag_enhancer.py`)
   - AI-powered structure tagging
   - Academic document optimization
   - Accessibility report generation
   - Graceful fallback to local processing

3. **PDF Enhancement** (`src/enhancers/pdf_enhancer.py`)
   - Metadata enrichment
   - Accessibility compliance
   - Font embedding and optimization

### Academic Document Support
- **Complex Layout Analysis**: Multi-column, tables, formulas
- **Citation Recognition**: Author-year, numeric, superscript formats
- **Mathematical Content**: Inline and display equations
- **Structure Preservation**: Proper heading hierarchy and reading order

### Performance Optimizations
- **File Size Control**: Addresses 12.69x size increase issues
- **DPI Optimization**: 200 DPI for academic papers (size/quality balance)
- **Compression**: JPEG 85% quality, JBIG2 lossy compression
- **Processing Efficiency**: Disabled unnecessary image enhancements

## 🚀 Usage

### CLI Interface (Primary)

```bash
# Basic academic processing
python -m processor.unified_project.src.main process input.pdf output.pdf --mode academic

# With Adobe AutoTag and reporting
python -m processor.unified_project.src.main process input.pdf output.pdf \
  --mode academic \
  --use-adobe-autotag \
  --generate-accessibility-report \
  --shift-headings \
  --verbose

# Custom metadata
python -m processor.unified_project.src.main process input.pdf output.pdf \
  --title "Research Paper Title" \
  --author "Author Name" \
  --language "en-US"
```

### Script-Based Processing

```bash
# Academic script (Docker-based)
./scripts/process_academic.sh input.pdf output.pdf

# Batch processing
./scripts/process_academic.sh --batch input_dir output_dir

# Custom resources
./scripts/process_academic.sh --memory 16g --cpus 8 --timeout 3600 input.pdf output.pdf
```

### Directory Processing

```bash
# Process entire directories
python src/process_directory.py
```

## 🐳 Docker Support

### Build Images

```bash
# Academic processor (optimized)
docker build -f Dockerfile.academic -t epubs/academic_processor:latest .

# Standard processor
docker build -f Dockerfile -t epubs/unified_processor:latest .
```

### Container Usage

```bash
# Single document
docker run --rm \
  -v /path/to/input.pdf:/data/input/document.pdf \
  -v /path/to/output:/data/output \
  epubs/academic_processor:latest \
  --mode academic \
  /data/input/document.pdf \
  /data/output/accessible.pdf

# Batch processing
docker run --rm \
  -v /input_dir:/data/input \
  -v /output_dir:/data/output \
  epubs/academic_processor:latest \
  --mode academic --batch \
  /data/input /data/output
```

## ⚙️ Configuration

### Academic Mode (`config/academic.yaml`)

```yaml
# OCR optimized for file size and quality
ocr:
  dpi: 200                    # Balanced size/quality (reduced from 250)
  
# Academic content detection
content_detection:
  formulas: true
  tables: true
  figures: true
  citations: true

# Adobe AutoTag integration
adobe_autotag:
  enabled: true
  generate_report: true
  shift_headings: true
  academic_mode:
    preserve_math_structure: true
    optimize_table_headers: true
    enhance_figure_captions: true

# Performance optimizations
academic:
  preprocessing:
    enhance_contrast: false   # Disabled for file size
    denoise: false           
    sharpen: false           # Disabled for file size
    deskew: false            # Disabled to prevent transcoding
```

### Default Mode (`config/default.yaml`)
- Conservative settings for general documents
- Adobe AutoTag optional
- Basic accessibility enhancements

## 🧪 Development

### Project Structure

```
src/
├── academic/                 # Academic-specific processors
├── enhancers/               # Document enhancement modules
│   ├── ocr_enhancer.py     # OCR with size optimization
│   ├── adobe_autotag_enhancer.py  # AI-powered tagging
│   └── pdf_enhancer.py     # Metadata and accessibility
├── services/               # Business logic layer
│   └── enhancement_service.py  # Pipeline orchestration
├── repositories/           # Data access layer
├── domain/                # Core business entities
├── core/                  # Framework components
│   └── service_container.py  # Dependency injection
└── main.py               # CLI interface
```

### Testing

```bash
# Run tests
python -m unittest discover tests

# Specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
```

### Extending the Engine

1. **New Enhancers**: Extend `src/enhancers/enhancer_base.py`
2. **New Services**: Register in `src/core/service_container.py`
3. **Configuration**: Add YAML configs for new modes
4. **Document Types**: Create processors in appropriate directories

### Adobe PDF Services Setup

1. Obtain credentials from Adobe Developer Console
2. Place `pdfservices-api-credentials.json` in project root
3. Engine automatically detects and enables AutoTag
4. Falls back gracefully if credentials unavailable

## 🔧 Recent Optimizations

### File Size Issues Resolved
- **Ghostscript 10.x Bug**: Fixed regression with `skip_text` option
- **Compression Settings**: Optimized JPEG/JBIG2 compression
- **DPI Reduction**: Lowered from 250 to 200 DPI
- **Processing Efficiency**: Disabled size-increasing image enhancements

### Expected Performance
- **File Size**: 2-3x increase (down from 12.69x)
- **Quality**: Maintained high OCR accuracy
- **Speed**: Improved processing time
- **Compatibility**: Works with all Ghostscript versions

## 📊 Service Integration

The engine integrates with:
- **Configuration Management**: YAML-based with schema validation
- **Document Repository**: File system abstraction
- **Metadata Services**: Enrichment and validation
- **Enhancement Pipeline**: Multi-stage processing workflow

For more details on the overall project architecture, see the [main README](../../README.md).