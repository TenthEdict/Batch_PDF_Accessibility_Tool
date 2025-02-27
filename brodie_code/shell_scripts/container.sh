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
            pdf-accessibility python3 -m accessibility_checker.utils.code_analyzer
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
            --timeout=$TIMEOUT \
            pdf-accessibility bash -c "cd /app && python3 -c \"
import os
import sys
import asyncio
from pathlib import Path
import logging
from src.accessibility_checker.ocr.processor import OCRProcessor
from src.accessibility_checker.utils.config import OCRConfig
from src.accessibility_checker.utils.retry import RetryHandler, RetryConfig
from src.accessibility_checker.core.enhanced_batch import EnhancedBatchProcessor

async def main():
    input_dir = Path('/app/input')
    output_dir = Path('/app/output')
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
            pdf-accessibility python3 -m accessibility_checker.build.process
        ;;
        
    "diagnose")
        echo "Running OCR diagnostics..."
        docker run --rm \
            -v "$INPUT_DIR:/app/input" \
            -v "$OUTPUT_DIR:/app/output" \
            pdf-accessibility bash -c '
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
        
    *)
        echo "Usage: $0 [command]"
        echo "Commands:"
        echo "  interactive   - Start interactive shell (default)"
        echo "  build        - Run full build process"
        echo "  analyze      - Run code analysis only"
        echo "  process      - Run document processing only"
        echo "  clean        - Clean output directories"
        exit 1
        ;;
esac
