# PDF Accessibility Enhancement Guide

This guide explains the PDF accessibility features implemented in this project, tools available, and how to use them to enhance academic journal PDFs.

## Overview

The PDF Accessibility Project provides tools to enhance PDFs with accessibility features required for PDF/UA compliance and improved accessibility for screen readers and assistive technologies. The advanced implementation includes:

1. **Semantic Structure**: Identifies and tags document structure elements (headings, paragraphs, tables)
2. **Reading Order**: Establishes a logical reading order through tagging
3. **Metadata**: Sets essential document metadata (title, language, author)
4. **PDF/UA Compliance**: Adds PDF/UA compliance markers for validation
5. **Image Accessibility**: Detects images and provides structure for alternative text
6. **Table Recognition**: Identifies and tags tables with proper structure
7. **Validation**: Checks PDFs against accessibility standards

## Project Structure

The PDF Accessibility Tools project is now organized into a structured package:

```
accessibility_tools/
├── core/            # Core enhancement modules
├── validation/      # Validation and analysis tools
├── scripts/         # Shell scripts and utilities
├── utils/           # Helper functions and utilities
└── access_cli.py    # Unified command-line interface
```

## Unified Command-Line Interface

All tools are now accessible through a single unified command-line interface:

**Script**: `accessibility_tools.sh`

This main script provides easy access to all functionality:

```bash
./accessibility_tools.sh <command> [arguments] [options]
```

Available commands:
- `enhance` - Enhance a single PDF with accessibility features
- `batch-enhance` - Enhance multiple PDFs in a directory
- `validate` - Validate PDF accessibility
- `analyze` - Analyze PDF structure in detail
- `batch-validate` - Validate multiple PDFs and create reports
- `docker` - Run tools in Docker container with configurable resources

### Examples:

```bash
# Enhance a single PDF with advanced accessibility features
./accessibility_tools.sh enhance input.pdf output.pdf --level advanced --title "Document Title"

# Batch enhance all PDFs in a directory
./accessibility_tools.sh batch-enhance input_directory output_directory

# Validate a PDF's accessibility
./accessibility_tools.sh validate document.pdf --detailed

# Analyze PDF structure
./accessibility_tools.sh analyze document.pdf

# Batch validate all PDFs in a directory
./accessibility_tools.sh batch-validate input_directory reports_directory

# Run in Docker with custom resources
./accessibility_tools.sh docker enhance 16g 8 14400
```

## Individual Tools

While the unified CLI is recommended, the individual tools are still available:

### 1. Basic Enhancement

**Module**: `accessibility_tools.core.enhance_pdf`

This module adds basic accessibility enhancements to PDFs:
- Document tagging
- Language setting
- DisplayDocTitle preference
- Minimal document structure

### 2. Journal-Specific Enhancement

**Module**: `accessibility_tools.core.enhance_pdf_journal`

Enhanced version specifically for academic journals:
- Extracts titles from content when possible
- Creates more appropriate metadata
- Same accessibility features as the basic enhancer

### 3. Advanced Enhancement

**Module**: `accessibility_tools.core.enhance_pdf_advanced`

Comprehensive accessibility enhancement with:
- Document structure detection (headings, paragraphs)
- Table detection and tagging
- Reading order optimization
- Image detection with alt text structure
- PDF/UA compliance

### 4. Validation

**Module**: `accessibility_tools.validation.validate_accessibility`

Validates PDFs against accessibility standards:
- Checks document tagging
- Verifies structure elements
- Validates language setting
- Checks PDF/UA compliance markers
- Reports issues and scores compliance

### 5. Batch Validation

**Module**: `accessibility_tools.validation.batch_validate`

Processes multiple PDFs and generates comprehensive reports:
- Processes PDFs in parallel
- Generates CSV summaries
- Creates interactive HTML reports with charts
- Provides detailed JSON data

### 6. Docker Container

**Script**: `accessibility_tools/scripts/container_accessibility.sh`

Runs the accessibility tools in a Docker container with improved resources:
- Configurable memory and CPU allocation
- Extended timeouts for large documents
- All dependencies pre-installed

## Accessibility Features Explained

### Document Tagging

Document tagging provides a structured representation of content for screen readers and assistive technologies. Our implementation:

1. **Tag Marking**: Sets the `/Marked` flag in the PDF to indicate it contains tags
2. **Structure Tree**: Creates a `/StructTreeRoot` to hold the document structure
3. **Document Node**: Establishes a root `/Document` structural element as the base for content

### Semantic Structure

Semantic structure identifies content elements by their role rather than appearance:

1. **Heading Detection**: Detects headings based on font size, position, and content length
2. **Paragraph Identification**: Groups related text as paragraphs
3. **Table Recognition**: Identifies tabular data with rows and cells
4. **Figure Tagging**: Tags images as figures for alternative text

### Reading Order

The document tagging establishes a logical reading order that screen readers should follow:

1. Headings precede their related content
2. Tables are read in logical row/column order
3. Content flows in a logical manner based on the document layout

### PDF/UA Compliance

PDF/UA (Universal Accessibility) is the ISO standard for accessible PDFs. Our tools ensure compliance by:

1. Adding proper tags and structure
2. Including PDF/UA identifiers in XMP metadata
3. Setting required document properties
4. Ensuring fonts are embedded

## Validation Reports

The validation tools produce reports that help identify accessibility issues:

1. **Summary Score**: Overall accessibility score (0-100)
2. **Critical Issues**: High-priority issues that must be fixed
3. **PDF/UA Compliance**: Whether the document meets PDF/UA standards
4. **Detailed Analysis**: Specific elements that need attention

## Best Practices

When creating accessible PDFs:

1. **Always provide titles**: Every document should have a meaningful title
2. **Set the language**: Specify the document language for screen readers
3. **Use heading structure**: Properly tag headings in hierarchical order (H1, H2, etc.)
4. **Add alt text**: Provide alternative text for images and figures
5. **Table headers**: Ensure tables have properly marked headers
6. **Reading order**: Check that the content reads in a logical order

## Requirements

- Python 3.8+
- Libraries: pikepdf, PyMuPDF, opencv-python-headless, pytesseract, pillow
- For Docker: Docker Desktop or Docker Engine

## Limitations

Current implementation has some limitations:

1. Table detection is basic and may miss complex tables
2. Image alt text framework is provided but requires manual text entry
3. Complex mathematical expressions may not be fully accessible
4. PDFs with complex layouts may require manual adjustment
5. Very large documents may require additional resources