# ePubs Accessibility Enhancement Project

A comprehensive toolset for automating PDF accessibility improvements through OCR, structural analysis, and intelligent content enhancement, designed for academic documents and publications.

## 🚀 New: PDF Accessibility Toolkit

We've added a new unified toolkit that provides a simpler interface to all accessibility tools:

```bash
# Install the toolkit
pip install -e .

# Use the toolkit
./accessibility_tools.sh enhance input.pdf output.pdf
./accessibility_tools.sh validate document.pdf --detailed
./accessibility_tools.sh batch-enhance input_dir output_dir
```

See [ACCESSIBILITY_GUIDE.md](ACCESSIBILITY_GUIDE.md) for complete documentation on the new toolkit, including:
- Document tagging with proper reading order
- Semantic structure detection (headings, paragraphs, tables)
- Image accessibility with alt text structures
- PDF/UA compliance validation
- Comprehensive accessibility reports

## Overview

This project provides a robust framework for enhancing PDF documents to meet accessibility standards. It processes scanned and digital PDFs to extract text via OCR, analyze document structure, detect and correct accessibility issues, and produce enhanced, tagged PDFs suitable for screen readers and assistive technologies.

## Key Features

- **Advanced OCR Processing**: Uses Tesseract OCR with adaptive configuration for optimal text extraction from scanned documents
- **Document Structure Analysis**: Automatically detects headings, tables, lists, and other structural elements
- **Intelligent Content Enhancement**: Applies machine learning to improve document tagging and structure
- **Comprehensive Reporting**: Generates detailed reports on accessibility issues and improvements
- **Containerized Deployment**: Docker-based workflow for consistent processing across environments
- **Customizable Resource Allocation**: Scalable processing for both small and large document batches

## System Requirements

- Docker (recommended)
- Python 3.11+
- Tesseract OCR 5.x
- 8GB RAM minimum (16GB+ recommended for large documents)

## Project Structure

```
.
├── brodie_code/              # Main project code
│   ├── input/                # Input PDFs for processing
│   ├── output/               # Processed outputs
│   │   ├── corrections/      # Correction reports
│   │   ├── reports/          # Processing reports
│   │   ├── processed_pdfs/   # Enhanced PDFs
│   │   ├── logs/             # Processing logs
│   │   ├── ocr_results/      # OCR output
│   │   ├── tagged/           # Tagged PDFs
│   │   ├── final/            # Final processed PDFs
│   │   └── analysis/         # Analysis reports
│   ├── shell_scripts/        # Automation scripts
│   │   ├── analyze.sh        # Analysis automation
│   │   ├── clean_*.sh        # Cleanup utilities
│   │   ├── container.sh      # Container management
│   │   └── docker-entrypoint.sh  # Container entry point
│   ├── src/                  # Source code
│   │   └── accessibility_checker/  # Main package
│   │       ├── api/          # API components
│   │       ├── build/        # Build process
│   │       ├── core/         # Core functionality
│   │       ├── ocr/          # OCR processing
│   │       └── utils/        # Utilities
│   ├── config.yaml           # Configuration settings
│   ├── Dockerfile            # Container definition
│   └── requirements.txt      # Python dependencies
├── input/                    # Global input directory
├── output/                   # Global output directory
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

3. **Process documents:**
   ```bash
   # Basic processing with default resources (8GB RAM, 4 CPUs)
   ./brodie_code/shell_scripts/container.sh process
   
   # Processing with higher resources for large documents
   ./brodie_code/shell_scripts/container.sh process 16g 8 14400  # 16GB RAM, 8 CPUs, 4h timeout
   ```

4. **Run diagnostics:**
   ```bash
   ./brodie_code/shell_scripts/container.sh diagnose
   ```

5. **Clean output directories:**
   ```bash
   ./brodie_code/shell_scripts/container.sh clean
   ```

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

## OCR Capabilities

The system uses an advanced OCR pipeline:

1. **Image Preprocessing**: Enhances document images for better OCR results
2. **Adaptive Configuration**: Automatically adjusts OCR parameters based on document type
3. **Page Analysis**: Processes each page to extract text with position information
4. **Quality Verification**: Validates OCR results with confidence scores

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