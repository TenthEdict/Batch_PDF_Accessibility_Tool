# System Architecture Patterns

## Core Architecture: Academic Web Distribution Pipeline

**Design Pattern**: Sequential Processing Pipeline optimized for academic papers distributed on digital commons platforms
- **Service Container**: Central dependency management system
- **Enhancer Pattern**: Pluggable document transformation modules optimized for web compression
- **Chain of Responsibility**: Sequential enhancement application with aggressive compression
- **Clean Structure Pattern**: Minimal PDF/UA-1 compliance without auto-generated content tags
- **Cross-Platform Consistency**: Identical processing on macOS Silicon and Ubuntu WSL

## Component Architecture

### Enhanced Enhancer Architecture Pattern
```
EnhancerBase (Abstract)
├── OCREnhancer - Academic OCR with aggressive web compression and enhanced Tesseract
├── CompressionEnhancer - Academic paper specific image optimization for web distribution
├── MinimalPDFEnhancer - Clean PDF/UA-1 compliance without auto-generated content structure
├── AdaptiveMLEnhancer - Python-based ML optimization for document-level OCR adaptation
└── AppleOptimizedEnhancer - Optional Apple Silicon hardware acceleration
```

**ML Architecture Decision: Python-Only Stack**
- **Language Choice**: Python maintained for all ML operations (not Julia)
- **Rationale**: Current ML tasks are lightweight and don't require Julia's performance benefits
- **Implementation**: 677-line AdaptiveMLEnhancer using scikit-learn, pandas, numpy
- **Performance**: Bottlenecks are in OCR/PDF processing, not ML computation
- **Complexity**: Adding Julia would destabilize production-ready system without proportional benefits

### Academic Web Distribution Pipeline
```
Academic Web Distribution Architecture:
├── Input Validation - Academic PDF format verification
├── OCR Enhancement - Aggressive web compression with academic Tesseract settings
├── Image Compression - Academic figure optimization and PNG→JPEG conversion
├── Minimal PDF Enhancement - Clean PDF/UA-1 compliance without content structure
└── Output Generation - Web-optimized academic paper ready for digital commons
```

### Service Layer Architecture
```
EnhancementService (Coordinator)
├── ServiceContainer - Dependency injection
├── OCREnhancer - Academic web compression
├── CompressionEnhancer - Image optimization
├── MinimalPDFEnhancer - Clean accessibility compliance
└── Validation Service - PDF/UA-1 compliance verification
```

## Enhanced Processing Flow Architecture

**Academic Web Distribution Pipeline Design**:
1. **Input Validation** → Academic PDF format verification and cross-platform compatibility check
2. **OCR Enhancement** → Academic OCR with 60% JPEG compression, 150 DPI limit, enhanced Tesseract settings
3. **Image Compression** → Academic figure optimization, PNG→JPEG conversion, web-specific compression
4. **Minimal PDF Enhancement** → Clean PDF/UA-1 compliance without auto-generated content structure
5. **Output Generation** → Web-optimized academic paper ready for digital commons distribution

**Processing Pipeline Decision Tree**:
```
Academic Paper Processing:
├── Cross-Platform Detection (macOS Silicon vs Ubuntu WSL)
├── Academic OCR → Aggressive Web Compression → Image Optimization → Clean PDF/UA-1
└── Consistent Output Regardless of Platform
```

**Enhanced Capabilities**:
- **Academic OCR Optimization**: Enhanced table detection, math symbol recognition, citation processing
- **Aggressive Web Compression**: 60-80% file size reduction optimized for digital commons
- **Clean PDF/UA-1 Structure**: Minimal compliance without dummy <div>, <p> tags
- **Cross-Platform Consistency**: Identical processing on macOS Silicon and Ubuntu WSL

## Import Structure Patterns

**Relative Import Strategy**: Internal module references use relative imports
**Absolute Import Strategy**: External library dependencies use absolute imports
**Service Resolution**: Container-based dependency injection for loose coupling
**Cross-Platform Libraries**: PyMuPDF, pikepdf, OCRMyPDF verified on both macOS and Linux

## Configuration Architecture

**Single Configuration Strategy**: academic.yaml optimized for web distribution
**No Multiple Profiles**: Hardcoded settings for academic papers on digital commons
**Cross-Platform Settings**: Consistent behavior across macOS Silicon and Ubuntu WSL
**Aggressive Compression Focus**: All settings optimized for web viewing, not print

## Error Handling Architecture

**Exception Hierarchy**: Specific exceptions for different failure modes
**Logging Strategy**: Structured logging with configurable verbosity levels
**Cross-Platform Fallbacks**: Consistent error handling across macOS and Linux
**Compression Failure Handling**: Graceful degradation when compression fails

## Deployment Patterns

**Cross-Platform Compatibility**: Works identically on macOS Silicon and Ubuntu WSL
**Academic Paper Focus**: Single use case optimization eliminates configuration complexity
**Web Distribution Optimization**: All settings designed for digital commons platforms
**CLI Interface**: Unified command-line interface with academic paper processing focus
