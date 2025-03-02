# PDF Accessibility Tools

A comprehensive toolkit for enhancing and validating PDF accessibility features.

## Overview

This package provides tools to:

1. Enhance PDFs with accessibility features required for screen readers
2. Add proper document structure and tagging
3. Detect and tag headings, paragraphs, tables, and images
4. Validate PDFs against accessibility standards
5. Generate detailed accessibility reports
6. Run all tools in Docker containers with configurable resources

## Quick Start

The toolkit provides a unified command-line interface:

```bash
# Install the package
pip install -e .

# Use the CLI tool
./accessibility_tools.sh enhance input.pdf output.pdf
./accessibility_tools.sh validate document.pdf --detailed
./accessibility_tools.sh batch-enhance input_dir output_dir
```

## Available Commands

- `enhance` - Enhance a single PDF with accessibility features
- `batch-enhance` - Enhance multiple PDFs in a directory
- `validate` - Validate PDF accessibility
- `analyze` - Analyze PDF structure in detail
- `batch-validate` - Validate multiple PDFs and create reports
- `docker` - Run tools in Docker container with configurable resources

## Installation

### Prerequisites

- Python 3.8+
- pikepdf, PyMuPDF, opencv-python-headless, pytesseract, Pillow
- For OCR features: Tesseract OCR
- For Docker features: Docker

### Installation from Source

```bash
# Clone the repository
git clone https://github.com/your-username/pdf-accessibility-tools.git
cd pdf-accessibility-tools

# Install the package
pip install -e .

# Make the script executable
chmod +x accessibility_tools.sh
```

### Docker Installation

```bash
# Build the Docker image
./accessibility_tools.sh docker build

# Run tools in Docker
./accessibility_tools.sh docker enhance
```

## Documentation

For detailed usage information and examples, see [ACCESSIBILITY_GUIDE.md](../ACCESSIBILITY_GUIDE.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Limitations

Current implementation has some limitations:

1. Table detection is basic and may miss complex tables
2. Image alt text framework is provided but requires manual text entry
3. Complex mathematical expressions may not be fully accessible
4. PDFs with complex layouts may require manual adjustment
5. Very large documents may require additional resources

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.