# ePubs Accessibility Enhancement Project

This monorepo contains all components of the ePubs Accessibility Enhancement Project, which provides specialized tools for enhancing document accessibility across both historical and academic publications.

## Project Structure

The repository is organized into three main components:

- **[/scraper](./scraper/)**: Document acquisition tools for downloading PDFs from library resources
- **[/automation](./automation/)**: Workflow automation scripts for end-to-end document processing
- **[/processor](./processor/)**: Core document processing components for enhancing accessibility

## Features

- **Unified Document Processing**: Common architecture for all document types
- **Historical Document Support**: Specialized OCR and analysis for historical documents
- **Academic Paper Enhancement**: Advanced handling of complex academic layouts
- **PDF/UA Compliance**: Ensures output documents meet accessibility standards
- **Workflow Automation**: Complete pipeline from document acquisition to accessibility enhancement

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker (optional, for containerized processing)
- System dependencies: poppler-utils, tesseract-ocr

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/ePubs_Main.git
   cd ePubs_Main
   ```

2. Set up the Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r processor/unified_project/requirements.txt
   ```

3. Install system dependencies (Ubuntu/Debian):
   ```bash
   sudo apt-get update
   sudo apt-get install -y poppler-utils tesseract-ocr
   ```

## Usage

### Document Acquisition

Download documents from Purdue library resources:
```bash
python -m scraper.purdue_downloader --url https://docs.lib.purdue.edu/modvis/2024/va
```

### End-to-End Processing

Process documents using the automated workflow:
```bash
python automation/automate_workflow.py --base-url https://docs.lib.purdue.edu/modvis/2024/va
```

### Manual Processing

Process documents manually:
```bash
processor/unified_project/scripts/process_academic.sh input.pdf output.pdf
```

## Component Documentation

For more detailed information about each component, refer to their individual README files:

- [Scraper Documentation](./scraper/README.md)
- [Automation Documentation](./automation/README.md)
- [Processor Documentation](./processor/README.md)

## Docker Support

The project supports containerized processing:

```bash
# Build the Docker image
docker build -f processor/unified_project/Dockerfile -t epubs/processor:latest processor/unified_project/

# Run container
docker run --rm \
  -v /path/to/input.pdf:/data/input/document.pdf \
  -v /path/to/output:/data/output \
  epubs/processor:latest \
  --mode academic \
  /data/input/document.pdf \
  /data/output/accessible.pdf
```

## Development

### Repository Structure

```
ePubs_Main/
├── automation/           # Workflow automation scripts
├── processor/            # Document processing components
│   ├── brodie_code/      # Historical document code
│   └── unified_project/  # Main unified framework
└── scraper/              # Document acquisition tools
```

### Testing

Run tests for each component:
```bash
# Run unified_project tests
cd processor/unified_project
python -m unittest discover tests

# Run scraper tests
cd scraper
python -m unittest discover tests
```