# Accessibility Training System

This directory contains the Phase 2B Accessibility Training System for training machine learning models to automatically generate WCAG/PDF-UA/ADA compliant PDF documents.

## Overview

The Accessibility Training System extends the existing Phase 2B ML infrastructure to train models for automatic accessibility compliance. It leverages 1600+ compliant PDF documents as training data to learn optimal tag tree structures and compliance patterns.

## Quick Start

### 1. Organize Training Data

Place your 1600+ compliant PDF files in a source directory, then organize them for training:

```bash
# Organize training data with default 70/15/15 split
epubs organize-training-data /path/to/1600/compliant/pdfs data/training/accessibility

# Custom split ratios
epubs organize-training-data /path/to/pdfs data/training/accessibility \
  --train-ratio 0.8 --val-ratio 0.1 --test-ratio 0.1
```

### 2. Extract Accessibility Patterns

Extract tag trees and compliance patterns from the organized training data:

```bash
# Extract patterns from training set
epubs extract-accessibility-patterns data/training/accessibility/train data/training/accessibility

# Process subset for testing
epubs extract-accessibility-patterns data/training/accessibility/train data/training/accessibility \
  --max-files 100
```

### 3. Train Models (Phase 2 - Coming Soon)

```bash
# Train accessibility compliance models
epubs train-accessibility-models data/training/accessibility data/models/accessibility
```

## Architecture Integration

### Phase 2B ML Infrastructure Extension

The Accessibility Training System extends the existing Phase 2B components:

- **FAISS Vector Database**: Extended from 32 to 128 dimensions (32 existing + 96 accessibility-specific)
- **AdaptiveMLEnhancer**: Enhanced with accessibility pattern learning capabilities
- **Hierarchical Caching**: Accessibility patterns cached for rapid reuse
- **Thread-Safe Processing**: Concurrent accessibility model training and inference

### Component Architecture

```
Accessibility Training System
├── accessibility_data_extractor.py     - Extract tag trees from compliant PDFs
├── accessibility_feature_engineer.py   - [Phase 2] Create ML feature vectors
├── accessibility_model_trainer.py      - [Phase 2] Train compliance models
├── compliance_validator.py             - [Phase 2] Validate WCAG/PDF-UA/ADA compliance
└── organize_training_data.py           - Organize 1600+ PDFs for training
```

## Data Organization

### Directory Structure

```
data/training/accessibility/
├── compliant_pdfs/           - Original 1600+ compliant PDF repository
├── train/                    - Training set (70% of data)
├── validation/               - Validation set (15% of data)  
├── test/                     - Test set (15% of data)
├── metadata/                 - Extracted metadata and analysis
├── document_profiles/        - Individual document accessibility profiles
├── extracted_patterns/       - Accessibility compliance patterns
└── training_manifest.json    - Complete dataset information
```

### Training Data Manifest

The `training_manifest.json` contains:

- Dataset statistics and split information
- Metadata analysis from training sample
- Feature vector configuration (128 dimensions)
- Target compliance standards (WCAG 2.1 AA, PDF/UA-1, Section 508)
- Integration points with Phase 2B infrastructure

## Extracted Features

### Document-Level Features (12 features)

- Page count and document structure metrics
- Compliance pattern count and confidence scores
- PDF marking and XMP metadata indicators
- Tag tree depth and node density

### Accessibility-Specific Features (96 features)

- **Heading Structure**: Hierarchy compliance, H1 presence, proper nesting
- **List Structure**: List types, nesting patterns, item organization
- **Table Structure**: Header presence, row/column relationships, data organization
- **Image Accessibility**: Alt text coverage, figure descriptions, visual content handling
- **Reading Order**: Logical sequence, content flow, navigation structure
- **Language Specification**: Document language, language changes, internationalization
- **Semantic Markup**: Role assignments, structural relationships, content categorization

### Legacy Phase 2B Features (32 features)

- Document similarity and pattern matching features from existing AdaptiveMLEnhancer
- OCR optimization and text analysis characteristics
- Content type classification and academic document patterns

## Usage Examples

### Basic Training Data Setup

```bash
# 1. Organize your 1600 compliant PDFs
epubs organize-training-data /path/to/compliant/pdfs data/training/accessibility --verbose

# 2. Extract accessibility patterns from training set
epubs extract-accessibility-patterns data/training/accessibility/train data/training/accessibility --verbose

# 3. Analyze extraction results
ls data/training/accessibility/document_profiles/  # Individual PDF profiles
cat data/training/accessibility/training_manifest.json  # Dataset overview
```

### Integration with Existing Processing

Once trained models are available, they will integrate seamlessly with existing Phase 2B processing:

```bash
# Standard Phase 2B processing with accessibility enhancement
epubs batch-process input_dir/ output_dir/  # Automatically includes accessibility models

# Single file processing with accessibility compliance
epubs process input.pdf output.pdf  # Enhanced with WCAG/PDF-UA/ADA compliance
```

## Training Data Requirements

### Compliant PDF Characteristics

Your 1600+ training PDFs should have:

- **WCAG 2.1 AA Compliance**: Proper heading structure, alt text, color contrast
- **PDF/UA-1 Compliance**: Complete tag trees, semantic structure, OutputIntent metadata
- **Section 508/ADA Compliance**: Screen reader compatibility, keyboard navigation support

### Recommended Dataset Composition

- **Academic Papers**: 40% (journal articles, conference papers, theses)
- **Technical Documentation**: 25% (user manuals, API documentation, reports)
- **Forms and Interactive Content**: 20% (accessible forms, interactive PDFs)
- **General Documents**: 15% (books, newsletters, general publications)

## Performance Expectations

### Phase 1 (Current Implementation)

- **Data Extraction**: ~2-5 seconds per PDF for tag tree analysis
- **Pattern Recognition**: ~30-50 patterns extracted per document
- **Feature Vector Generation**: 128-dimensional vectors with accessibility characteristics
- **Batch Processing**: Parallel extraction with progress tracking

### Phase 2 (Model Training)

- **Training Time**: Estimated 2-4 hours for 1600 PDF dataset
- **Model Types**: DocumentClassifier, TagTreePredictor, ComplianceValidator
- **Accuracy Target**: >90% compliance pattern prediction, >95% WCAG validation
- **Integration**: Seamless integration with existing Phase 2B 5-8x performance enhancement

## Development Status

### ✅ Phase 1: Data Extraction Infrastructure (COMPLETE)

- ✅ AccessibilityDataExtractor with comprehensive tag tree analysis
- ✅ Training data organization and split management
- ✅ CLI integration with existing Phase 2B commands
- ✅ Feature vector generation (128 dimensions)
- ✅ Pattern extraction for WCAG/PDF-UA/ADA compliance

### 🔄 Phase 2: Model Training (In Progress)

- 🚧 AccessibilityFeatureEngineer for ML-ready feature processing
- 🚧 AccessibilityModelTrainer with scikit-learn integration
- 🚧 ComplianceValidator for automated WCAG/PDF-UA/ADA validation
- 🚧 FAISS integration for accessibility pattern similarity search

### 🎯 Phase 3: Production Integration (Planned)

- 🎯 AccessibilityMLEnhancer integration into existing Phase 2B pipeline
- 🎯 Automatic tag tree generation during PDF processing
- 🎯 Real-time compliance validation and correction
- 🎯 Performance optimization maintaining 5-8x Phase 2B speedup

## Contributing

When working with the training system:

1. **Test with Small Datasets**: Start with 10-50 PDFs for development and testing
2. **Validate Compliance**: Ensure training PDFs meet WCAG/PDF-UA/ADA standards
3. **Monitor Performance**: Training data extraction should maintain fast processing
4. **Document Patterns**: Record interesting accessibility patterns discovered during extraction

## Troubleshooting

### Common Issues

**"PDF dependencies not available"**
```bash
pip install PyMuPDF pikepdf  # Install PDF processing libraries
```

**"ML dependencies not available"** 
```bash
pip install scikit-learn pandas numpy  # Install ML libraries
```

**"No valid PDF files found"**
- Verify source directory contains PDF files
- Check file permissions and accessibility
- Ensure PDFs are not corrupted or password-protected

**"Training data organization failed"**
- Verify sufficient disk space for organized data
- Check write permissions for output directory
- Ensure train/validation/test ratios sum to 1.0

### Performance Optimization

- **Large Datasets**: Use `--max-files` option for testing with subsets
- **Parallel Processing**: Extraction leverages existing Phase 2B parallel infrastructure
- **Memory Management**: Large training datasets cached efficiently with hierarchical system
- **Progress Tracking**: Verbose logging provides detailed extraction progress

## Next Steps

After completing Phase 1 data extraction:

1. **Analyze Extracted Patterns**: Review `training_manifest.json` and pattern distributions
2. **Validate Data Quality**: Check document profiles for proper tag tree extraction
3. **Prepare for Phase 2**: Organize training data for model training implementation
4. **Integration Planning**: Design integration points with existing Phase 2B enhancers

The training system is designed to seamlessly extend the existing Phase 2B infrastructure while providing the foundation for automated WCAG/PDF-UA/ADA compliance generation.