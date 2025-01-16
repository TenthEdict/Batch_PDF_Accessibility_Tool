# PDF Processor for Screen Readable Documents

Tool for processing PDFs for accessibility workflows and generating detailed reports.

## Requirements

- Python 3.11+
- Tesseract OCR
- MuPDF

### System Dependencies

#### macOS
```bash
brew install tesseract
brew install mupdf
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install mupdf
```

#### Windows
1. Install Tesseract OCR:
   - Download installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Add to PATH: `C:\Program Files\Tesseract-OCR`

2. Install MuPDF:
   - Download from [MuPDF website](https://mupdf.com/releases/index.html)
   - Add installation directory to PATH

## Installation

1. Clone repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create virtual environment:
```bash
# macOS/Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure
```
.
├── input/          # Place PDFs here for processing
├── output/         # Processed files and reports
├── src/           
│   └── accessibility_checker/
├── config.yaml     # Configuration settings
└── requirements.txt
```

## Usage

1. Place PDFs in the `input` directory
2. Run the processor:
```bash
# macOS/Linux
python src/main.py

# Windows
python src\main.py
```

## Output

The tool generates:
- Processed PDFs with enhanced accessibility
- Accessibility violation reports
- OCR results
- Processing statistics

Results are organized in the `output` directory structure.

## Troubleshooting

### Windows-Specific Issues
- If Tesseract isn't found: Verify PATH includes `C:\Program Files\Tesseract-OCR`
- If MuPDF isn't found: Add MuPDF installation directory to PATH
- Command prompt might require admin privileges for first run


## Using container.sh
```bash
# Original behavior (process PDFs)
./container.sh process


# Run post-processing
./container.sh post-process

# Get a shell (original behavior)
./container.sh /bin/bash
```
