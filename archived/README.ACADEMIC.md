# Academic Paper Processing

Specialized processing for modern academic papers with enhanced structure detection.

## Features

- Smart structure detection for academic sections
- Multi-column layout processing
- Mathematical content enhancement
- Citation pattern recognition
- Table structure preservation

## Usage

```bash
# Process academic paper
./scripts/process_academic.sh input.pdf output.pdf

# Batch processing
./scripts/process_academic.sh --batch input_directory output_directory

# Docker processing
docker run --rm -v /path/to/input.pdf:/data/input.pdf -v /path/to/output:/data/output epubs/academic_processor
```

## Supported Citation Formats

- Author-year: `(Smith et al., 2018)`
- Numeric: `[1, 2, 5-8]`
- In-text: `Jones and Miller (2020) found...`
