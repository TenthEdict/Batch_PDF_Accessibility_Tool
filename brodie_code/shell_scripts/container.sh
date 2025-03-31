#!/bin/bash

# Get absolute paths using current directory
INPUT_DIR=$(realpath "$(pwd)/input")
OUTPUT_DIR=$(realpath "$(pwd)/output")

# Default command and resource settings
CMD=${1:-interactive}
MEMORY=${2:-"8g"}
CPUS=${3:-"4"}
TIMEOUT=${4:-"7200"}

# Check if ANTHROPIC_API_KEY is set in environment
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Warning: ANTHROPIC_API_KEY is not set. Code analysis features will be disabled."
    echo "To enable, export your API key: export ANTHROPIC_API_KEY=your-key-here"
fi

# Check if directories exist
if [ ! -d "$INPUT_DIR" ]; then
    echo "Creating input directory: $INPUT_DIR"
    mkdir -p "$INPUT_DIR"
fi

if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

echo "Using directories:"
echo "Input: $INPUT_DIR"
echo "Output: $OUTPUT_DIR"
echo "Resource allocation: ${MEMORY} memory, ${CPUS} CPUs, ${TIMEOUT}s timeout"

# Clean up any stray containers
docker ps -a | grep 'pdf-accessibility' | awk '{print $1}' | xargs -r docker rm -f

# Updated volume mounts for all commands
VOLUME_MOUNTS="-v $INPUT_DIR:/app/input -v $OUTPUT_DIR:/app/output"

case "$CMD" in
    "analyze")
        echo "Running code analysis..."
        docker run --rm \
            $VOLUME_MOUNTS \
            -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
            pdf-accessibility-tools python3 -m accessibility_checker.utils.code_analyzer
        ;;
    
    "enhance")
        echo "Enhancing PDF accessibility features..."
        PDF_PATH=${2:-""}
        OUTPUT_PATH=${3:-""}
        TITLE=${4:-""}
        AUTHOR=${5:-""}
        
        if [ -z "$PDF_PATH" ]; then
            echo "Error: PDF path is required for enhance command"
            echo "Usage: $0 enhance <pdf_path> [<output_path>] [\"title\"] [\"author\"]"
            exit 1
        fi
        
        # Resolve paths
        FULL_PDF_PATH=$(realpath "$PDF_PATH")
        PDF_DIR=$(dirname "$FULL_PDF_PATH")
        PDF_NAME=$(basename "$FULL_PDF_PATH")
        
        if [ -z "$OUTPUT_PATH" ]; then
            # Default output path is the same directory with _accessible suffix
            OUTPUT_NAME="${PDF_NAME%.*}_accessible.pdf"
            OUTPUT_DIR="$OUTPUT_DIR/enhanced"
            mkdir -p "$OUTPUT_DIR"
            FULL_OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_NAME"
        else
            FULL_OUTPUT_PATH=$(realpath "$OUTPUT_PATH")
        fi
        
        # Determine where to place the PDF for processing
        mkdir -p "$INPUT_DIR"
        cp "$FULL_PDF_PATH" "$INPUT_DIR/$PDF_NAME"
        
        echo "Enhancing PDF accessibility..."
        echo "Input: $FULL_PDF_PATH"
        echo "Output: $FULL_OUTPUT_PATH"
        
        TITLE_ARG=""
        if [ ! -z "$TITLE" ]; then
            TITLE_ARG="--title \"$TITLE\""
        fi
        
        AUTHOR_ARG=""
        if [ ! -z "$AUTHOR" ]; then
            AUTHOR_ARG="--author \"$AUTHOR\""
        fi
        
        docker run --rm \
            -v "$INPUT_DIR:/app/input" \
            -v "$OUTPUT_DIR:/app/output" \
            pdf-accessibility python3 -c "
import os
import sys
from pathlib import Path
import logging
import pikepdf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

from accessibility_checker.core.post_processor import (
    update_metadata,
    set_pdf_language,
    set_initial_view_title,
    mark_pdf_as_tagged,
    create_document_structure,
    ensure_fonts_embedded,
    append_xmp_to_multiple_pdfs
)

def enhance_single_pdf(input_path, output_path=None, title=None, author=None):
    input_path = Path(input_path)
    
    if not input_path.exists():
        logger.error(f'Input PDF not found: {input_path}')
        return False
    
    if output_path is None:
        output_dir = Path('/app/output/enhanced')
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f'{input_path.stem}_accessible.pdf'
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True, parents=True)
    
    logger.info(f'Enhancing PDF: {input_path}')
    logger.info(f'Output will be saved to: {output_path}')
    
    # Copy the input PDF
    with pikepdf.open(input_path) as pdf:
        pdf.save(output_path)
    
    # Apply accessibility enhancements
    try:
        update_metadata(output_path, title, [author] if author else None)
        set_pdf_language(output_path)
        set_initial_view_title(output_path)
        mark_pdf_as_tagged(output_path)
        create_document_structure(output_path)
        ensure_fonts_embedded(output_path)
        
        # Apply PDF/UA metadata
        xmp_path = Path('/app/pdfUA-ID.xmp')
        if xmp_path.exists():
            # Create temp directory for processing
            temp_dir = output_path.parent / '.temp'
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / output_path.name
            
            # Copy enhanced PDF to temp dir
            with pikepdf.open(output_path) as pdf:
                pdf.save(temp_path)
            
            # Apply PDF/UA XMP
            append_xmp_to_multiple_pdfs(str(temp_dir), str(xmp_path))
            
            # Copy back to output
            import shutil
            shutil.copy2(temp_path, output_path)
            
            # Clean up
            if temp_path.exists():
                temp_path.unlink()
            if temp_dir.exists():
                temp_dir.rmdir()
        
        logger.info(f'Successfully enhanced PDF accessibility: {output_path}')
        return True
    
    except Exception as e:
        logger.error(f'Error enhancing PDF: {e}')
        import traceback
        traceback.print_exc()
        return False

# Find PDF in input directory
pdf_name = '$PDF_NAME'
input_path = Path('/app/input') / pdf_name

# Process PDF
title = '$TITLE' or None
author = '$AUTHOR' or None
output_path = Path('/app/output/enhanced') / f'{Path(pdf_name).stem}_accessible.pdf'

result = enhance_single_pdf(input_path, output_path, title, author)
print('PDF enhancement', 'successful' if result else 'failed')
"
        
        # Copy the result back if needed
        if [ -f "$OUTPUT_DIR/enhanced/${PDF_NAME%.*}_accessible.pdf" ]; then
            cp "$OUTPUT_DIR/enhanced/${PDF_NAME%.*}_accessible.pdf" "$FULL_OUTPUT_PATH"
            echo "Enhanced PDF saved to: $FULL_OUTPUT_PATH"
        else
            echo "Error: Enhanced PDF was not created"
        fi
        ;;
        
    "process")
        echo "Running document processing with OCR..."
        docker run --rm \
            -v "$INPUT_DIR:/app/input" \
            -v "$OUTPUT_DIR:/app/output" \
            -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
            -e ENABLE_OCR=1 \
            -e TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata \
            --memory=$MEMORY --cpus=$CPUS \
            pdf-accessibility-tools bash -c "cd /app && python3 -c \"
import os
import sys
import asyncio
from pathlib import Path
import logging
from src.accessibility_checker.ocr.processor import OCRProcessor
from src.accessibility_checker.utils.config import OCRConfig
from src.accessibility_checker.utils.retry import RetryHandler, RetryConfig
from src.accessibility_checker.core.enhanced_batch import EnhancedBatchProcessor
from src.accessibility_checker.core.post_processor import (
    batch_process_pdfs, 
    update_metadata,
    set_pdf_language,
    set_initial_view_title,
    mark_pdf_as_tagged,
    create_document_structure
)

async def main():
    input_dir = Path('/app/input')
    output_dir = Path('/app/output')
    processed_dir = output_dir / 'processed_pdfs'
    tagged_dir = output_dir / 'tagged'
    final_dir = output_dir / 'final'
    
    # Create required directories
    for dir_path in [processed_dir, tagged_dir, final_dir]:
        dir_path.mkdir(exist_ok=True, parents=True)
    
    print(f'Looking for PDFs in: {input_dir}')
    
    try:
        print('Setting up OCR...')
        ocr_config = OCRConfig(
            language='eng',
            psm=3,
            oem=3,
            char_whitelist='',
            additional_params={'preserve_interword_spaces': '1'}
        )
        retry_handler = RetryHandler(RetryConfig(
            max_attempts=3,
            base_delay=2.0,
            max_delay=30.0,
            jitter=True
        ))
        
        print('Creating OCR processor...')
        ocr_processor = OCRProcessor(
            config=ocr_config,
            retry_handler=retry_handler,
            timeout=300
        )
        
        print('Testing OCR processor...')
        print(f'OCR processor configured with language: {ocr_config.language}')
        print('OCR is enabled and ready')
        
        print('Initializing batch processor with OCR capability...')
        processor = EnhancedBatchProcessor(
            str(input_dir),
            str(output_dir),
            max_workers=4,
            ocr_processor=ocr_processor,
            retry_handler=retry_handler,
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
        print('Processing files with OCR enabled...')
        summary_df = await processor.process_directory()
        
        print('\\nProcessing Summary:')
        print(f'Total files processed: {len(summary_df)}')
        if not summary_df.empty:
            success_count = sum(summary_df['status'] == 'success')
            failed_count = sum(summary_df['status'] == 'failed')
            print(f'Successfully processed: {success_count}')
            print(f'Failed: {failed_count}')
            
            # Copy processed PDFs to tagged directory for accessibility enhancement
            if success_count > 0:
                print('\\nCopying processed PDFs to tagged directory for accessibility enhancement...')
                import shutil
                for pdf_file in processed_dir.glob('*.pdf'):
                    tagged_path = tagged_dir / pdf_file.name
                    shutil.copy2(pdf_file, tagged_path)
                    print(f'  Copied {pdf_file.name} to tagged directory')
                
                # Now enhance PDFs with accessibility features
                print('\\nEnhancing PDFs with accessibility features...')
                xmp_path = Path('/app/pdfUA-ID.xmp')
                if xmp_path.exists():
                    print(f'Using PDF/UA template: {xmp_path}')
                    batch_process_pdfs(str(tagged_dir), str(final_dir), str(xmp_path))
                else:
                    print('PDF/UA template not found, skipping batch enhancement')
        else:
            print('\\nNo files were processed.')
            
    except Exception as e:
        logging.error(f'Error in OCR process: {str(e)}')
        raise

asyncio.run(main())
\"" 
        ;;
        
    "build")
        echo "Running full build process..."
        docker run --rm \
            -v "$INPUT_DIR:/app/input" \
            -v "$OUTPUT_DIR:/app/output" \
            -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
            pdf-accessibility-tools python3 -m accessibility_checker.build.process
        ;;
        
    "diagnose")
        echo "Running OCR diagnostics..."
        docker run --rm \
            -v "$INPUT_DIR:/app/input" \
            -v "$OUTPUT_DIR:/app/output" \
            pdf-accessibility-tools bash -c '
                echo "Python version:" && python3 --version && 
                echo -e "\nPython path:" && python3 -c "import sys; print(sys.path)" && 
                echo -e "\nTesseract version:" && tesseract --version && 
                echo -e "\nPytesseract availability:" && 
                python3 -c "
try:
    import pytesseract
    print(f\"PyTesseract version: {pytesseract.get_tesseract_version()}\")
except Exception as e:
    print(f\"Error: {e}\")
" && 
                echo -e "\nOpenCV availability:" && 
                python3 -c "
try:
    import cv2
    print(f\"OpenCV version: {cv2.__version__}\")
except Exception as e:
    print(f\"Error: {e}\")
" && 
                echo -e "\nNumpy availability:" && 
                python3 -c "
try:
    import numpy
    print(f\"NumPy version: {numpy.__version__}\")
except Exception as e:
    print(f\"Error: {e}\")
" && 
                echo -e "\nPyMuPDF availability:" && 
                python3 -c "
try:
    import fitz
    print(f\"PyMuPDF version: {fitz.version}\")
except Exception as e:
    print(f\"Error: {e}\")
" && 
                echo -e "\nModule import test:" && 
                python3 -c "
try:
    from accessibility_checker.ocr.processor import OCRProcessor
    print(\"OCR module imported successfully\")
except Exception as e:
    print(f\"Import error: {e}\")
"'
        ;;
        
    "clean")
        echo "Cleaning output directories..."
        rm -rf "$OUTPUT_DIR"/*
        mkdir -p "$OUTPUT_DIR"/{corrections,reports,processed_pdfs,logs,ocr_results,tagged,final}
        ;;
        
    "enhance-single")
        echo "Enhancing a single PDF with accessibility features..."
        PDF_PATH=${2:-""}
        
        if [ -z "$PDF_PATH" ]; then
            echo "Error: PDF path is required for enhance-single command"
            echo "Usage: $0 enhance-single <pdf_path>"
            exit 1
        fi
        
        # Resolve paths
        FULL_PDF_PATH=$(realpath "$PDF_PATH")
        PDF_DIR=$(dirname "$FULL_PDF_PATH")
        PDF_NAME=$(basename "$FULL_PDF_PATH")
        OUTPUT_NAME="${PDF_NAME%.*}_accessible.pdf"
        OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_NAME"
        
        # Copy PDF to input directory for processing
        mkdir -p "$INPUT_DIR"
        cp "$FULL_PDF_PATH" "$INPUT_DIR/$PDF_NAME"
        
        echo "Enhancing PDF accessibility..."
        echo "Input: $FULL_PDF_PATH"
        echo "Output: $OUTPUT_PATH"
        
        # Run container with post_processor script
        docker run --rm \
            -v "$INPUT_DIR:/app/input" \
            -v "$OUTPUT_DIR:/app/output" \
            pdf-accessibility python3 -c "
import os
import sys
from pathlib import Path
import logging
from accessibility_checker.core.post_processor import (
    update_metadata,
    set_pdf_language,
    set_initial_view_title,
    mark_pdf_as_tagged,
    create_document_structure,
    ensure_fonts_embedded,
    append_xmp_to_multiple_pdfs
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def enhance_single_pdf(input_path, output_path, title=None):
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        logger.error(f'Input PDF not found: {input_path}')
        return False
    
    logger.info(f'Enhancing PDF: {input_path}')
    
    try:
        # Create a copy of the input PDF
        import pikepdf
        with pikepdf.open(input_path) as pdf:
            pdf.save(output_path)
        
        # Extract title from filename if not provided
        if not title:
            import re
            basename = input_path.stem
            # Remove date patterns and testing/version markers
            basename = re.sub(r'\\d{4}|testing|V\\d+', '', basename)
            # Replace underscores/hyphens with spaces
            title = re.sub(r'[_-]', ' ', basename)
            # Clean up and capitalize
            title = re.sub(r'\\s+', ' ', title).strip().title()
        
        # Apply accessibility enhancements
        update_metadata(output_path, title)
        set_pdf_language(output_path)
        set_initial_view_title(output_path)
        mark_pdf_as_tagged(output_path)
        create_document_structure(output_path)
        ensure_fonts_embedded(output_path)
        
        # Apply PDF/UA metadata
        xmp_path = Path('/app/pdfUA-ID.xmp')
        if xmp_path.exists():
            # Create temp directory for processing
            temp_dir = output_path.parent / '.temp'
            temp_dir.mkdir(exist_ok=True)
            temp_file = temp_dir / output_path.name
            
            # Copy enhanced PDF to temp dir
            with pikepdf.open(output_path) as pdf:
                pdf.save(temp_file)
            
            # Add PDF/UA XMP
            append_xmp_to_multiple_pdfs(str(temp_dir), str(xmp_path))
            
            # Copy back to output
            import shutil
            shutil.copy2(temp_file, output_path)
            
            # Clean up temp files
            temp_file.unlink(missing_ok=True)
            temp_dir.rmdir()
            
        logger.info(f'Successfully enhanced PDF accessibility: {output_path}')
        return True
    except Exception as e:
        logger.error(f'Error enhancing PDF: {e}')
        import traceback
        traceback.print_exc()
        return False

# Process the PDF
pdf_name = '$PDF_NAME'
input_path = Path(f'/app/input/{pdf_name}')
output_path = Path(f'/app/output/{pdf_name.rsplit(\".\", 1)[0]}_accessible.pdf')

success = enhance_single_pdf(input_path, output_path)
print('PDF enhancement', 'successful' if success else 'failed')
"
        
        if [ -f "$OUTPUT_PATH" ]; then
            echo "Enhanced PDF saved to: $OUTPUT_PATH"
        else
            echo "Error: Enhanced PDF was not created"
        fi
        ;;

    *)
        echo "Usage: $0 [command]"
        echo "Commands:"
        echo "  interactive   - Start interactive shell (default)"
        echo "  build        - Run full build process"
        echo "  analyze      - Run code analysis only"
        echo "  process      - Run document processing only"
        echo "  enhance      - Enhance PDF accessibility"
        echo "  enhance-single - Enhance a single PDF with full accessibility"
        echo "  clean        - Clean output directories"
        exit 1
        ;;
esac
