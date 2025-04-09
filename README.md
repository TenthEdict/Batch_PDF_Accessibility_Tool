# ePubs Accessibility Enhancement Project

A comprehensive toolset for automating PDF accessibility improvements through OCR, structural analysis, and intelligent content enhancement, designed for academic documents and publications.

## 🚀 New: Unified Processing Framework & MCP Support

Our latest update brings significant improvements:

```bash
# Process documents with the unified framework
./unified_project/scripts/process_academic.sh input.pdf output.pdf

# Process documents with enhanced AI analysis
./process_academic_local.py --input document.pdf --output enhanced.pdf --mcp

# Run batch processing via Docker
./unified_project/scripts/docker-entrypoint.sh batch input_dir output_dir
```

Key improvements:
- **Unified architecture** with service containers and dependency injection
- **MCP integration** utilizing Claude AI for enhanced document analysis
- **SmolDocling integration** for academic paper optimization
- **Advanced academic processing** for journal articles and theses
- **JBIG2-optimized OCR** for improved text recognition
- **Comprehensive refactoring** for better performance and maintainability

## 🔍 Historical Document Processing

Specialized processing for historical documents:

```bash
# Process historical documents with optimized settings
./accessibility_tools/scripts/create_accessible_pdf_advanced.sh input.pdf --mode historical

# Process a batch of historical documents
./accessibility_tools/scripts/create_accessible_pdf_advanced.sh --batch input_dir output_dir --mode historical

# Run in Docker container with enhanced resources
./accessibility_tools/scripts/container_accessibility.sh historical
```

Features include:
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

See [README.ACCESSIBILITY.md](README.ACCESSIBILITY.md) for complete documentation on processing modes and features.

## 🔧 Academic Document Processing

New tools specifically designed for academic papers, theses, and journals:

```bash
# Process academic documents with SmolDocling
./smolDocling/run.sh --input thesis.pdf --output accessible_thesis.pdf

# Process with advanced academic features
python unified_project/src/main.py --config config/academic.yaml --input paper.pdf
```

Academic processing features:
- Multi-column layout detection and processing
- Formula and equation recognition
- Citation pattern analysis
- Figure and table detection with proper tagging
- Bibliography section optimization
- Apple Silicon optimization for mathematical content

## Overview

This project provides a robust framework for enhancing PDF documents to meet accessibility standards. It processes scanned and digital PDFs to extract text via OCR, analyze document structure, detect and correct accessibility issues, and produce enhanced, tagged PDFs suitable for screen readers and assistive technologies.

## Key Features

- **Unified Processing Framework**: Integrated pipeline for all document types with dependency injection
- **MCP AI Support**: Claude AI integration for enhanced document analysis and accessibility improvements
- **Advanced OCR Processing**: Uses Tesseract OCR with adaptive configuration for optimal text extraction
- **SmolDocling Integration**: Optimized processing for academic papers with enhanced layout analysis
- **Historical Document Support**: Specialized processing for yellowed paper, faded text, and degraded images
- **Document Structure Analysis**: Automatically detects headings, tables, lists, and other structural elements
- **Mathematical Content Detection**: Enhanced processing for equations and complex notation
- **Comprehensive Reporting**: Generates detailed reports on accessibility issues and improvements
- **Containerized Deployment**: Docker-based workflow for consistent processing across environments
- **Customizable Resource Allocation**: Scalable processing for both small and large document batches

## System Requirements

- Docker (recommended)
- Python 3.11+
- Tesseract OCR 5.x
- 8GB RAM minimum (16GB+ recommended for large documents)
- Anthropic API key (optional, for enhanced analysis)

## Project Structure

```
.
├── accessibility_tools/      # Core accessibility toolkit
│   ├── core/                 # Core accessibility functionality
│   ├── scripts/              # Command-line interface scripts
│   ├── utils/                # Utility functions
│   └── validation/           # Validation tools
├── brodie_code/              # OCR and text extraction tools
│   ├── shell_scripts/        # Automation scripts
│   ├── src/                  # Source code
│   │   └── accessibility_checker/
│   │       ├── api/          # API components
│   │       ├── core/         # Core functionality
│   │       ├── ocr/          # OCR processing
│   │       └── utils/        # Utilities
│   └── tessdata/             # Tesseract data
├── data/                     # Global input/output directories
│   ├── input/                # Input documents
│   └── output/               # Output processed documents
├── smolDocling/              # Academic document processing
│   ├── src/                  # Source code
│   │   ├── academic_processor.py
│   │   ├── accessibility_processor.py
│   │   └── document_enhancer.py
│   └── tests/                # Unit tests
├── unified_project/          # Unified processing framework
│   ├── config/               # YAML configuration files
│   ├── resources/            # Processing resources
│   ├── scripts/              # Processing scripts
│   └── src/                  # Source code
│       ├── academic/         # Academic document processing
│       ├── accessibility/    # Accessibility enhancement
│       ├── cli/              # Command-line interfaces
│       ├── core/             # Core framework
│       ├── enhancement/      # Enhancement modules
│       ├── metadata/         # Metadata processing
│       ├── ocr/              # OCR processing modules
│       └── validation/       # Validation modules
├── README.ACCESSIBILITY.md   # Accessibility documentation
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
   # Using unified framework with default resources
   ./unified_project/scripts/docker-entrypoint.sh process input.pdf output.pdf
   
   # Using accessibility tools with higher resources
   ./accessibility_tools/scripts/container_accessibility.sh process 16g 8 14400  # 16GB RAM, 8 CPUs, 4h timeout
   ```

4. **Process academic documents:**
   ```bash
   # Using unified academic processor
   ./unified_project/scripts/docker-entrypoint.sh academic input.pdf output.pdf
   
   # Using SmolDocling for academic papers
   ./smolDocling/run.sh --input thesis.pdf --output accessible_thesis.pdf
   ```

5. **Process historical documents:**
   ```bash
   # Process historical documents with optimized settings
   ./accessibility_tools/scripts/container_accessibility.sh historical
   
   # With custom resource allocation
   ./accessibility_tools/scripts/container_accessibility.sh process 16g 8 14400 historical
   ```

6. **Run diagnostics:**
   ```bash
   ./brodie_code/shell_scripts/container.sh diagnose
   ```

7. **Clean output directories:**
   ```bash
   ./brodie_code/shell_scripts/clean_io.sh
   ```

### Local Development

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Run unified processor:**
   ```bash
   python unified_project/src/main.py --config config/default.yaml
   ```

4. **Run academic processor with MCP:**
   ```bash
   python process_academic_local.py --input document.pdf --output enhanced.pdf --mcp
   ```

## Configuration

The unified project uses YAML configuration files in the `unified_project/config/` directory:

```yaml
# Example configuration (default.yaml)
ocr:
  engine: tesseract
  language: eng
  psm: 3
  oem: 3
  additional_params:
    preserve_interword_spaces: 1

enhancement:
  mode: standard
  tag_headings: true
  tag_tables: true
  tag_figures: true
  
mcp:
  enabled: false
  analyze_structure: true
  enhance_metadata: true
  
resources:
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
   - Academic processing for journal articles and papers
   - Adaptive mode for automatic document type detection

3. **Content Detection**: 
   - Mathematical equation detection and processing
   - Multi-column layout analysis
   - Historical typography and ligature handling
   - Table structure detection and analysis
   - Figure and chart recognition

4. **Quality Verification**: 
   - Validates OCR results with confidence scores
   - Compares OCR results across different processing modes
   - Provides detailed analysis reports

### MCP Integration

The system now integrates with Anthropic's Claude AI for enhanced document processing:

1. **Intelligent Structure Analysis**:
   - Semantic document structure extraction
   - Advanced heading level detection
   - Context-aware table of contents generation
   - Citation and reference detection

2. **Accessibility Enhancement**:
   - AI-assisted alt text generation for images
   - Equation description refinement
   - Document summary generation
   - Improved metadata extraction and enhancement

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
   - Adjust OCR configuration in unified_project/config/default.yaml

2. **Container Resource Issues:**
   - For large documents, increase resources: `./unified_project/scripts/docker-entrypoint.sh process input.pdf output.pdf 16g 8`
   - Check Docker resource allocation settings
   - Monitor container logs for memory or timeout errors

3. **MCP Integration Issues:**
   - Verify ANTHROPIC_API_KEY is set correctly
   - Check network connectivity to Anthropic API
   - Review logs for API rate limiting or timeout errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the code style guidelines in CLAUDE.md
4. Submit a pull request

## License

This project is licensed under [LICENSE INFORMATION].