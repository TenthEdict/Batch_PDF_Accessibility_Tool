# System Architecture Patterns

## Core Architecture

**Design Pattern**: Sequential Processing Pipeline optimized for academic papers

### Key Patterns
- **Service Container**: Central dependency management
- **Enhancer Pattern**: Pluggable document transformation modules
- **Chain of Responsibility**: Sequential enhancement application
- **Clean Structure**: Minimal PDF/UA-1 compliance without auto-generated tags

## Component Architecture

### Enhancer Hierarchy
```
EnhancerBase (Abstract)
├── OCREnhancer
│   └── Academic OCR with web compression and enhanced Tesseract
├── CompressionEnhancer  
│   └── Academic figure optimization for web distribution
├── MinimalPDFEnhancer
│   ├── PDF/UA-1 compliance (clean structure)
│   ├── Mathematical content detection
│   ├── Equation boundary extraction
│   └── Mathematical accessibility tagging
├── AdaptiveMLEnhancer
│   └── Document-level OCR optimization (Python-only stack)
└── AppleOptimizedEnhancer (Optional)
    └── Apple Silicon hardware acceleration
```

### Mathematical Accessibility Integration
- **Detection**: MathematicalNotationDetector identifies equations, formulas, symbols
- **Extraction**: EquationBoundaryExtractor determines precise boundaries
- **Tagging**: MathematicalAccessibilityTagger creates accessibility structure
- **Integration**: Clean PDF/UA-1 structure tree with mathematical elements
- **Compliance**: PDF/UA-1, Section 508, ADA, WCAG 2.1

### ML Architecture Decision: Python-Only
**Rationale**: Julia integration evaluated but not adopted
- Current ML tasks are lightweight (document pattern matching, OCR optimization)
- Bottlenecks are in OCR/PDF processing, not ML computation
- Adding Julia would destabilize production-ready system
- scikit-learn implementation meets all project needs
- Cross-platform deployment complexity would increase significantly

## Processing Pipeline

### Academic Web Distribution Flow
```
Input Validation → OCR Enhancement → Image Compression → 
PDF/UA-1 Enhancement → Output Generation
```

### Pipeline Steps
1. **Input Validation**: PDF format verification and platform compatibility
2. **OCR Enhancement**: 60% JPEG, 150 DPI, enhanced Tesseract for academics
3. **Image Compression**: Figure optimization, PNG→JPEG conversion
4. **PDF/UA-1 Enhancement**: Clean compliance without dummy tags
5. **Output Generation**: Web-optimized academic paper

### Decision Tree
```
Academic Paper Processing:
├── Platform Detection (macOS/Windows/Linux)
├── OCR → Compression → Image Optimization → PDF/UA-1
└── Consistent Output Across Platforms
```

## Service Layer

### Architecture
```
EnhancementService (Coordinator)
├── ServiceContainer - Dependency injection
├── OCREnhancer - Academic web compression
├── CompressionEnhancer - Image optimization
├── MinimalPDFEnhancer - Clean accessibility
└── ValidationService - PDF/UA-1 verification
```

## Phase 2B Infrastructure

### Advanced Processing Components
```
Phase 2B Architecture:
├── FAISS Vector Database
│   └── 32-dimensional academic feature vectors, 10x faster similarity search
├── Hierarchical Cache Manager
│   └── L1 (Memory 512MB) → L2 (SSD 2048MB) → L3 (Disk 8192MB)
├── Thread-Safe ML Enhancer
│   └── Concurrent-safe pattern learning, 6 parallel workers
└── Academic Pattern Recognition
    └── Tables, equations, citations, document similarity
```

### Performance Features
- **FAISS**: CPU-only, 32-dimensional features, automatic index optimization
- **Caching**: LRU eviction, compression, deduplication, 70-80% hit rates
- **ML Enhancement**: Document similarity analysis, OCR optimization, feedback learning
- **Resource Management**: CPU and memory throttling, intelligent optimization

## Pikepdf Parsing Architecture

### Enhanced Structure Parsing (Technical Fix)
- **Type Detection**: Comprehensive pikepdf object identification
- **Safe Accessors**: Protected attribute access with error recovery
- **Multi-Type Handlers**: Type-specific processing with graceful degradation
- **Error Recovery**: Try-catch handling with logging

### Object Type Matrix
- **pikepdf.Dictionary**: Standard accessibility structure extraction
- **pikepdf.Array**: Iterative child element processing
- **pikepdf.Name**: Direct tag type creation
- **pikepdf.Stream**: Stream object preservation
- **Unknown**: Graceful skip with logging

## Accessibility Training Infrastructure (Experimental - Untested)

### Architecture (Implementation Complete)
```
Training Infrastructure:
├── AccessibilityDataExtractor (884 lines)
│   ├── PDF structure analysis (PyMuPDF + pikepdf)
│   ├── Tag tree extraction
│   ├── Compliance pattern recognition (WCAG/PDF-UA/ADA)
│   └── Feature vector generation (128-dimensional)
├── TrainingDataOrganizer
│   ├── PDF validation and integrity checks
│   ├── Training splits (70/15/15)
│   └── Manifest generation
└── Phase 2B Integration
    ├── FAISS extended to 128 dimensions
    ├── Hierarchical caching for patterns
    └── Thread-safe concurrent processing
```

### Feature Engineering (128-dimensional vectors)
- **Document Features (12)**: Page count, compliance patterns, metadata
- **Accessibility Features (96)**: Heading structure, lists, tables, images, reading order, language
- **Legacy Features (32)**: Document similarity, OCR optimization, academic patterns

**Status**: Implementation complete but requires validation with real training data

## Import Structure

- **Relative Imports**: Internal module references
- **Absolute Imports**: External library dependencies
- **Service Resolution**: Container-based dependency injection
- **Cross-Platform**: PyMuPDF, pikepdf, OCRMyPDF verified on all platforms

## Configuration

- **Single Strategy**: academic.yaml optimized for web distribution
- **No Multiple Profiles**: Hardcoded settings for academic papers
- **Cross-Platform**: Consistent behavior across OS
- **Compression Focus**: All settings optimized for web viewing

## Error Handling

- **Exception Hierarchy**: Specific exceptions for failure modes
- **Logging Strategy**: Structured logging with configurable verbosity
- **Cross-Platform Fallbacks**: Consistent error handling
- **Graceful Degradation**: Fallback when components unavailable

## Deployment Patterns

- **Cross-Platform**: Windows, macOS, Linux with identical processing
- **Academic Focus**: Single use case optimization
- **Web Distribution**: Optimized for digital commons platforms
- **CLI Interface**: Unified command-line interface
