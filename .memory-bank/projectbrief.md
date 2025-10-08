# Project Brief

## Overview

ePubs Accessibility Enhancement is a Python toolkit for transforming academic and historical PDFs into accessibility-compliant documents meeting PDF/UA-1, Section 508, and ADA standards.

## Core Objectives

1. **Universal Accessibility**: PDF/UA-1 compliance for screen readers and assistive technologies
2. **Academic Specialization**: Handle complex layouts, mathematical content, tables, and citations
3. **Historical Document Processing**: OCR optimization for degraded text and historical terminology
4. **Workflow Automation**: End-to-end processing pipelines from acquisition to enhancement
5. **Performance**: 5-8x processing speedup with Phase 2B advanced features

## Project Structure

### Active Components
- **processor/**: Core document enhancement engine with unified architecture
- **scraper/**: Document acquisition from library resources (Purdue-focused)
- **data/**: Input/output processing with academic paper samples
- **tests/**: Unit and integration test suites

### Archived Content
- **archived/**: Historical development files, migration scripts, deprecated tools

## Technical Stack

### Core Technologies
- **Python 3.9+**: Modern packaging with pyproject.toml
- **PyMuPDF, pikepdf**: PDF processing and structure manipulation
- **ocrmypdf**: OCR processing with Tesseract integration
- **Pillow, OpenCV**: Image processing and optimization
- **Typer, Rich**: CLI interface with progress tracking

### Advanced Features
- **FAISS**: High-performance vector similarity search
- **scikit-learn**: ML-based OCR optimization
- **pandas, numpy**: Data processing and analytics

### Architecture
- **Service Container**: Dependency injection pattern
- **Sequential Pipeline**: OCR → Compression → Accessibility
- **Enhancer Chain**: Pluggable transformation modules
- **Phase 2B**: FAISS vector database, hierarchical caching, ML optimization

## Success Criteria

### Functional Requirements ✅
- ✅ PDF/UA-1 compliant output documents
- ✅ Automated OCR and font embedding  
- ✅ Screen reader optimized content structure
- ✅ Scalable processing for document collections
- ✅ Cross-platform compatibility (Windows, macOS, Linux)

### Performance Metrics ✅
- ✅ 5-8x processing speedup (Phase 2B)
- ✅ 90.9% title extraction accuracy
- ✅ 40-80% file size reduction
- ✅ 100% processing success rate on test dataset

### Quality Standards ✅
- ✅ >99% text accuracy preservation
- ✅ Mathematical content accessibility
- ✅ Figure quality preservation
- ✅ Adobe Acrobat compatibility

## Use Cases

### Primary Users
- **Academic Libraries**: Digital commons platforms requiring accessibility compliance
- **Research Institutions**: Scholarly paper enhancement and dissemination
- **Historical Archives**: Document digitization with OCR
- **Accessibility Teams**: Institutional compliance for digital collections

### Deployment Scenarios
- Single-user development environment
- Batch processing for document collections
- Automated workflow integration
- Docker containerized deployment

## Current Status

**Production Ready**: Core functionality with validated performance
**Experimental**: Accessibility training system (untested, may be removed)
**Maintenance**: Documentation cleanup, security review, performance optimization
