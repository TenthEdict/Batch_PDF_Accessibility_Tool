# ePubs Accessibility Enhancement Project

A comprehensive toolset for automating PDF accessibility improvements through OCR, structural analysis, and intelligent content enhancement, designed for academic documents and publications.

## 🚀 New: Enhanced Historical Document OCR

Our latest update brings specialized processing for historical documents:

```bash
# Process historical documents with optimized settings
./accessibility_tools/scripts/create_accessible_pdf_advanced.sh input.pdf --mode historical

# Process a batch of historical documents
./accessibility_tools/scripts/create_accessible_pdf_advanced.sh --batch input_dir output_dir --mode historical

# Run in Docker container with enhanced resources
./accessibility_tools/scripts/container_accessibility.sh historical
```

Key improvements:
- **Advanced preprocessing** for yellowed paper, faded text, and degradation
- **Historical document detection** algorithms for optimal processing
- **Specialized OCR configurations** for historical typography
- **Mathematical content detection** for complex equations

## 📊 PDF Accessibility Toolkit

Use our unified toolkit that provides a simpler interface to all accessibility tools:

```bash
# Install the toolkit
pip install -e .

# Process standard documents
./accessibility_tools.sh enhance input.pdf output.pdf
./accessibility_tools.sh validate document.pdf --detailed
./accessibility_tools.sh batch-enhance input_dir output_dir
```

See [ACCESSIBILITY_GUIDE.md](ACCESSIBILITY_GUIDE.md) for complete documentation on processing modes and features.

## 🔧 Adobe Acrobat JavaScript Tools

New JavaScript tools for Adobe Acrobat Pro to help with manual tagging and optimization:

```
acrobat_scripts/
├── BatchPreflightAndOptimize.js  # Batch process multiple documents
├── TaggingUtilities.js           # Fix tagging structure issues
└── AcademicPDFToolbox.js         # Tools specific to academic documents
```

These scripts automate common tasks like:
- Running Preflight fixups for fonts and tagging structure
- Optimizing documents with compatible settings
- Fixing heading hierarchy and table structure issues
- Adding alt text to figures
- Creating bookmarks and table of contents
- Tagging equations and citations

## Overview

This project provides a robust framework for enhancing PDF documents to meet accessibility standards. It processes scanned and digital PDFs to extract text via OCR, analyze document structure, detect and correct accessibility issues, and produce enhanced, tagged PDFs suitable for screen readers and assistive technologies.

## Key Features

- **Advanced OCR Processing**: Uses Tesseract OCR with adaptive configuration for optimal text extraction from scanned documents
- **Historical Document Support**: Specialized processing for yellowed paper, faded text, and degraded images
- **Document Structure Analysis**: Automatically detects headings, tables, lists, and other structural elements
- **Mathematical Content Detection**: Enhanced processing for equations and complex notation
- **Comprehensive Reporting**: Generates detailed reports on accessibility issues and improvements
- **Containerized Deployment**: Docker-based workflow for consistent processing across environments
- **Customizable Resource Allocation**: Scalable processing for both small and large document batches
- **Adobe Acrobat Integration**: JavaScript tools for post-processing in Adobe Acrobat Pro

## System Requirements

- Docker (recommended)
- Python 3.11+
- Tesseract OCR 5.x
- 8GB RAM minimum (16GB+ recommended for large documents)

## Project Structure

```
.
├── accessibility_tools/      # Unified accessibility toolkit
│   ├── core/                 # Core accessibility functionality
│   │   ├── enhance_pdf.py                # Basic PDF enhancement
│   │   ├── enhance_pdf_advanced.py       # Advanced PDF processing
│   │   ├── enhance_pdf_journal.py        # Journal-specific processing
│   │   └── enhance_pdf_ua.py             # PDF/UA compliance
│   ├── scripts/              # Command-line interface scripts
│   │   ├── accessibility_tools.sh        # Main CLI entry point
│   │   ├── container_accessibility.sh    # Docker container management
│   │   └── create_accessible_pdf_advanced.sh  # Advanced PDF processing
│   ├── utils/                # Utility functions
│   └── validation/           # Validation tools
│       ├── batch_validate.py             # Batch validation
│       └── validate_accessibility.py     # Single file validation
├── acrobat_scripts/          # Adobe Acrobat JavaScript tools
│   ├── BatchPreflightAndOptimize.js      # Process multiple documents
│   ├── TaggingUtilities.js               # Fix tagging structure
│   ├── AcademicPDFToolbox.js             # Academic document tools
│   └── README.md                         # Usage documentation
├── brodie_code/              # OCR and text extraction tools
│   ├── shell_scripts/        # Automation scripts
│   │   ├── analyze.sh                    # Analysis automation
│   │   ├── clean_*.sh                    # Cleanup utilities
│   │   ├── container.sh                  # Container management
│   │   └── docker-entrypoint.sh          # Container entry point
│   ├── src/                  # Source code
│   │   └── accessibility_checker/        # Main package
│   │       ├── api/                      # API components
│   │       ├── core/                     # Core functionality
│   │       ├── ocr/                      # OCR processing
│   │       │   ├── adaptive_config.py    # Adaptive OCR configuration
│   │       │   ├── math_processor.py     # Math equation detection
│   │       │   └── processor.py          # Main OCR processor
│   │       └── utils/                    # Utilities
│   ├── tessdata/             # Tesseract data
│   │   └── configs/                      # OCR configurations
│   │       └── historical.config         # Historical document config
│   ├── config.yaml           # Configuration settings
│   └── requirements.txt      # Python dependencies
├── input/                    # Global input directory
├── output/                   # Global output directory
├── ACCESSIBILITY_GUIDE.md    # Comprehensive guide to accessibility features
└── CLAUDE.md                 # Development guidelines
```

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ePubs_AccProj
   ```

2. **Set up environment:**
   ```bash
   export ANTHROPIC_API_KEY=<your-api-key>  # Optional, for enhanced analysis
   ```

3. **Process regular documents:**
   ```bash
   # Basic processing with default resources (8GB RAM, 4 CPUs)
   ./accessibility_tools/scripts/container_accessibility.sh process
   
   # Processing with higher resources for large documents
   ./accessibility_tools/scripts/container_accessibility.sh process 16g 8 14400  # 16GB RAM, 8 CPUs, 4h timeout
   ```

4. **Process historical documents:**
   ```bash
   # Process historical documents with optimized settings
   ./accessibility_tools/scripts/container_accessibility.sh historical
   
   # With custom resource allocation
   ./accessibility_tools/scripts/container_accessibility.sh process 16g 8 14400 historical
   ```

5. **Run diagnostics:**
   ```bash
   ./brodie_code/shell_scripts/container.sh diagnose
   ```

6. **Clean output directories:**
   ```bash
   ./brodie_code/shell_scripts/container.sh clean
   ```

7. **Post-process in Adobe Acrobat Pro:**
   - Open processed PDF in Adobe Acrobat Pro
   - Use the Acrobat Scripts from the menu:
     - File > Batch Preflight and Optimize
     - Advanced > Tagging Utilities
     - Document > Academic PDF Toolbox

### Local Development

1. **Create virtual environment:**
   ```bash
   cd brodie_code
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Run processor:**
   ```bash
   python src/main.py
   ```

## Configuration

The `config.yaml` file controls processing behavior:

```yaml
# Example configuration
ocr:
  language: eng
  psm: 3
  oem: 3
  char_whitelist: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:()[]{}\"'-"
  additional_params:
    preserve_interword_spaces: 1

max_workers: 4
batch_size: 10
timeout: 600
retry_count: 3
```

## Document Processing Capabilities

The system uses an advanced document processing pipeline:

### OCR Processing 

1. **Image Preprocessing**: Enhances document images for better OCR results
   - Background normalization to address yellowing in historical documents
   - Contrast enhancement for faded text
   - Specialized filtering to preserve text edges in degraded documents
   - Deskewing for warped pages

2. **Adaptive Configuration**: Automatically adjusts OCR parameters based on document type
   - Standard processing for modern documents
   - Historical processing for aged documents
   - Manuscript processing for handwritten content
   - Adaptive mode for automatic document type detection

3. **Content Detection**: 
   - Mathematical equation detection and processing
   - Historical typography and ligature handling
   - Specialized dictionaries for different time periods
   - Table structure detection and analysis

4. **Quality Verification**: 
   - Validates OCR results with confidence scores
   - Compares OCR results across different processing modes
   - Provides detailed analysis reports

### Adobe Acrobat Integration

Post-processing tools for Adobe Acrobat Pro:

1. **Automated Accessibility Fixes**:
   - Fixes potential font problems using Preflight
   - Fixes problems in PDF tagging structure
   - Repairs heading hierarchy and table structure issues
   
2. **Academic Document Enhancement**:
   - Automatic section detection (abstract, methods, results)
   - Equation tagging with proper Formula elements
   - Citation structure enhancement
   - Table of contents generation

## Development Guidelines

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines, including:
- Build and test commands
- Docker environment configuration
- Code style guidelines
- Resource allocation recommendations

## Troubleshooting

### Common Issues

1. **OCR Quality Issues:**
   - Verify Tesseract installation with `./brodie_code/shell_scripts/container.sh diagnose`
   - Check TESSDATA_PREFIX environment variable is correctly set
   - Adjust OCR configuration in config.yaml

2. **Container Resource Issues:**
   - For large documents, increase resources: `./brodie_code/shell_scripts/container.sh process 16g 8 14400`
   - Check Docker resource allocation settings
   - Monitor container logs for memory or timeout errors

3. **Processing Errors:**
   - Check input PDF format and quality
   - Review logs in output/logs/ directory
   - Verify file permissions for input and output directories

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the code style guidelines in CLAUDE.md
4. Submit a pull request

## License

This project is licensed under [LICENSE INFORMATION].