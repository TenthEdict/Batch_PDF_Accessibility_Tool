# Academic Paper Accessibility Processing

This module provides specialized accessibility processing for modern academic papers published within the last 20 years. It focuses on the unique elements and structure of academic content to create properly tagged and accessible PDF documents.

## Features

- **Smart Structure Detection**: Identifies common academic paper sections through heading analysis and text patterns without relying on specific section names
- **Multi-Column Layout Processing**: Detects and correctly processes papers with multiple columns
- **Mathematical Content Enhancement**: Identifies and properly tags mathematical notation and formulas
- **Citation Pattern Recognition**: Detects different citation formats (author-year, numeric, superscript)
- **Table Structure Preservation**: Maintains the semantic structure of tables, including headers and data cells
- **Academic Terminology Optimization**: Includes specialized dictionaries for academic and scientific terms

## Usage

### Command Line

Process a single academic paper:
```bash
./scripts/process_academic.sh input.pdf output.pdf
```

Process a batch of academic papers:
```bash
./scripts/process_academic.sh --batch input_directory output_directory
```

Custom resource allocation:
```bash
./scripts/process_academic.sh --memory 16g --cpus 8 --timeout 3600 input.pdf output.pdf
```

### Docker

Build the Docker image:
```bash
docker build -f Dockerfile.academic -t epubs/academic_processor:latest .
```

Run the container directly:
```bash
docker run --rm -v /path/to/input.pdf:/data/input/input.pdf -v /path/to/output:/data/output epubs/academic_processor:latest --mode academic /data/input/input.pdf /data/output/output.pdf
```

## Configuration

The academic paper processing is configured in `config/academic.yaml`. Key configuration options include:

- **OCR Settings**: Optimized for modern academic print quality
- **Content Detection**: Toggle features for detecting formulas, tables, citations, etc.
- **Structure Detection**: Configure heading and section detection
- **Performance Settings**: Configure workers, batch size, and timeouts
- **Academic-specific Settings**: Customize citation patterns and math detection

## Technical Implementation

The academic paper processing uses several specialized components:

1. **Academic Processor** (`src/academic/processor.py`): Core processing module optimized for academic content
2. **Structure Analyzer** (`src/academic/structure_analyzer.py`): Advanced document structure analysis
3. **Academic Terms Dictionary** (`resources/academic_terms.txt`): Specialized OCR vocabulary

## Limitations

The current implementation has some limitations to be aware of:

- Very complex mathematical equations may not be fully captured in accessible form
- Papers with unconventional layouts may not be properly structured
- Non-English papers are only partially supported
- Very large tables may be processed as images rather than structured content

## Examples

### Structure Detection Example

The structure analyzer can detect sections even with non-standard headings:

```
1. Introduction → Identified as introduction
Background and Problem Statement → Also identified as introduction
Methodology → Identified as methods
3.1 Experimental Setup → Identified as methods (subsection)
```

### Citation Detection Example

Various citation formats are detected:

```
(Smith et al., 2018) → Author-year format
[1, 2, 5-8] → Numeric format
Jones and Miller (2020) found... → In-text citation
```