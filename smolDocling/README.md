# SmolDocling Document Processing

A document processing environment optimized for Apple Silicon that enhances the capabilities of the SmolDocling model.

## Features

- **Document Format Conversion**: Convert various document formats (DOC, DOCX, PPT, PPTX, images) to PDF
- **Scanned Document Enhancement**: Specialized preprocessing for old or faded documents
  - Deskewing (straightening tilted scans)
  - Contrast enhancement and adaptive thresholding
  - Noise reduction and speckle removal
  - Border cleanup and margin normalization
  - JBIG2-optimized OCR with invisible searchable text layer
- **Academic Paper Processing**: Specialized handling for academic papers
  - Two-column layout detection
  - Mathematical formula recognition
  - Figure and table extraction
  - Metadata extraction (title, authors, abstract, keywords)
  - Headers/footers recognition
- **Parallel Processing**: Process multi-page documents faster using multiple cores
- **Apple Silicon Optimized**: Uses MLX for efficient processing on Apple Silicon chips

## Getting Started

### Prerequisites

- Python 3.8 or higher
- LibreOffice (optional, for improved Office document conversion)
- Apple Silicon Mac (for optimal performance with MLX)

### Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd smolDocling
   ```

2. Run the setup script to create a virtual environment and install dependencies:
   ```bash
   ./run.sh install
   ```

## Usage

### Basic Usage

Process documents in the input directory:
```bash
./run.sh process -i data/input -o data/output
```

Process a single document:
```bash
./run.sh process -i path/to/document.pdf -o data/output
```

### Advanced Usage

Process an academic paper with parallel processing:
```bash
./run.sh process -i path/to/paper.pdf --academic --parallel
```

Process an old scanned document with enhancement:
```bash
./run.sh process -i path/to/old_document.jpg --document-type old_scan
```

Visualize processed documents:
```bash
./run.sh visualize -d data/output/document.json -i data/input/document.jpg
```

### Command Line Options

- `--input, -i`: Input directory or file (default: data/input)
- `--output, -o`: Output directory (default: data/output)
- `--max-size`: Maximum image dimension (default: 1024)
- `--document-type`: Document type for preprocessing (general, old_scan, faded)
- `--academic`: Enable specialized academic paper processing
- `--parallel`: Enable parallel processing for multi-page documents
- `--use-jbig2`: Use JBIG2-optimized OCR for better text recognition in scanned documents (automatically enabled for old_scan/faded document types)

## Project Structure

```
smolDocling/
├── data/
│   ├── input/         # Place input documents here
│   └── output/        # Processed documents will be saved here
├── src/
│   ├── process_documents.py       # Main processing script
│   ├── document_converter.py      # Document format conversion utilities
│   ├── document_enhancer.py       # Image enhancement utilities
│   ├── academic_processor.py      # Academic paper processing utilities
│   ├── jbig2_ocr_processor.py     # JBIG2-optimized OCR processor
│   ├── simple_enhance.py          # OCR-focused enhancement for historical documents
│   └── visualize_results.py       # Visualization utilities
├── requirements.txt   # Python dependencies
└── run.sh             # Main execution script
```

## Dependencies

- docling-core: Core document processing library
- mlx-vlm: Apple Silicon optimized vision-language model
- pymupdf: PDF processing and manipulation
- python-docx: Microsoft Word document processing
- python-pptx: Microsoft PowerPoint document processing
- opencv-python: Image processing and computer vision
- scikit-image: Advanced image processing algorithms
- pillow: Python Imaging Library
- numpy: Numerical computing
- tqdm: Progress bar visualization
- pytesseract: OCR engine wrapper for Tesseract
- pdf2image: Convert PDF to image for OCR processing

## License

This project is licensed under the MIT License - see the LICENSE file for details.
