# PDF Accessibility Enhancement Tool

Tool for automating PDF accessibility improvements through OCR, structural analysis, and intelligent content enhancement.

## Features

- Advanced OCR with adaptive configuration
- Intelligent document structure analysis
- Automated accessibility improvements
- Detailed processing reports
- Container-based deployment support

## Requirements

- Python 3.11+
- Tesseract OCR
- Docker (for containerized deployment)

### System Dependencies

#### Local Development Setup

```bash
# macOS
brew install tesseract mupdf

# Ubuntu/Debian
sudo apt-get install tesseract-ocr libtesseract-dev mupdf
```

## Project Structure
```
.
├── input/                    # Input PDFs for processing
├── output/                   # Processed outputs
│   ├── corrections/         # Correction reports
│   ├── reports/            # Processing reports
│   ├── processed_pdfs/     # Enhanced PDFs
│   ├── logs/              # Processing logs
│   ├── ocr_results/       # OCR output
│   ├── tagged/           # Tagged PDFs
│   ├── final/           # Final processed PDFs
│   └── analysis/       # Analysis reports
├── shell_scripts/          # Automation scripts
│   ├── analyze.sh         # Analysis automation
│   ├── clean_*.sh        # Cleanup utilities
│   ├── container.sh      # Container management
│   └── docker-entrypoint.sh  # Container entry point
├── src/                    # Source code
│   └── accessibility_checker/
├── config.yaml             # Configuration settings
├── Dockerfile             # Container definition
└── requirements.txt       # Python dependencies
```

## Usage

### Docker Container (Recommended)

1. Build and run the container:
```bash
./shell_scripts/container.sh process
```

2. For post-processing:
```bash
./shell_scripts/container.sh post-process
```

3. For interactive shell:
```bash
./shell_scripts/container.sh /bin/bash
```

### Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

3. Run processor:
```bash
python src/main.py
```

## Configuration

The `config.yaml` file controls processing behavior:

- OCR settings
- Adaptive processing parameters
- Worker configuration
- Timeout settings

## Output Structure

- `/output/corrections/`: Detailed correction reports
- `/output/reports/`: Processing summaries
- `/output/processed_pdfs/`: Enhanced PDFs
- `/output/logs/`: Processing logs
- `/output/ocr_results/`: Raw OCR output
- `/output/tagged/`: Structure-tagged PDFs
- `/output/final/`: Final processed documents
- `/output/analysis/`: Analysis reports

## Development

The project uses a modular architecture with components for:
- OCR processing
- Document enhancement
- Accessibility checking
- Report generation

## Troubleshooting

### Common Issues

1. OCR Quality:
   - Verify Tesseract installation
   - Check language packs
   - Adjust confidence thresholds in config.yaml

2. Container Issues:
   - Ensure Docker is running
   - Check volume mounts
   - Verify file permissions

3. Processing Errors:
   - Check input PDF format
   - Verify sufficient disk space
   - Review logs in output/logs/
