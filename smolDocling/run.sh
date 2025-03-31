#!/bin/bash
# SmolDocling document processing runner for Apple Silicon

set -e  # Exit on error

# Define directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="${SCRIPT_DIR}/data/input"
OUTPUT_DIR="${SCRIPT_DIR}/data/output"

# Create virtual environment if it doesn't exist
if [ ! -d "${SCRIPT_DIR}/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "${SCRIPT_DIR}/venv"
fi

# Activate virtual environment
source "${SCRIPT_DIR}/docling_venv/bin/activate"

# Install requirements if needed
if [ ! -f "${SCRIPT_DIR}/docling_venv/.requirements_installed" ]; then
    echo "Installing requirements..."
    pip install -r "${SCRIPT_DIR}/requirements.txt"
    touch "${SCRIPT_DIR}/docling_venv/.requirements_installed"
fi

# Function to show usage
show_usage() {
    echo "SmolDocling Document Processing Tool"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  process     Process documents in the input directory"
    echo "  visualize   Visualize processed documents"
    echo "  install     Only install requirements"
    echo ""
    echo "Options:"
    echo "  --input, -i       Input directory or file (default: data/input)"
    echo "  --output, -o      Output directory (default: data/output)"
    echo "  --max-size        Maximum image dimension (default: 1024)"
    echo "  --document-type   Document type for preprocessing (general, old_scan, faded)"
    echo "  --academic        Enable specialized academic paper processing"
    echo "  --parallel        Enable parallel processing for multi-page documents"
    echo "  --use-jbig2       Use JBIG2-optimized OCR (automatically enabled for old_scan/faded)"
    echo ""
    echo "Examples:"
    echo "  $0 process -i data/input -o data/output"
    echo "  $0 process -i data/input/paper.pdf --academic --parallel"
    echo "  $0 process -i data/input/old_document.jpg --document-type old_scan"
    echo "  $0 visualize -d data/output/document.json -i data/input/document.jpg"
}

# Check for command
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

COMMAND=$1
shift  # Remove command from arguments

case "$COMMAND" in
    process)
        # Set default input/output directories if not provided
        INPUT_ARG="--input"
        OUTPUT_ARG="--output"
        INPUT_PATH="${INPUT_DIR}"
        OUTPUT_PATH="${OUTPUT_DIR}"
        MAX_SIZE=1024
        
        # Parse arguments
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --input|-i)
                    INPUT_PATH="$2"
                    shift 2
                    ;;
                --output|-o)
                    OUTPUT_PATH="$2"
                    shift 2
                    ;;
                --max-size)
                    MAX_SIZE="$2"
                    shift 2
                    ;;
                --document-type)
                    DOCUMENT_TYPE="$2"
                    shift 2
                    ;;
                --academic)
                    ACADEMIC="--academic"
                    shift 1
                    ;;
                --parallel)
                    PARALLEL="--parallel"
                    shift 1
                    ;;
                *)
                    echo "Unknown option: $1"
                    show_usage
                    exit 1
                    ;;
            esac
        done
        
        # Set default document type if not provided
        DOCUMENT_TYPE="${DOCUMENT_TYPE:-general}"
        ACADEMIC="${ACADEMIC:-}"
        PARALLEL="${PARALLEL:-}"
        
        # Run document processing
        echo "Processing documents from ${INPUT_PATH}..."
        echo "Document type: ${DOCUMENT_TYPE}"
        if [ -n "$ACADEMIC" ]; then
            echo "Academic paper processing: Enabled"
        fi
        if [ -n "$PARALLEL" ]; then
            echo "Parallel processing: Enabled"
        fi
        
        # Run the appropriate script based on document type
        if [ "${DOCUMENT_TYPE}" = "old_scan" ] || [ "${DOCUMENT_TYPE}" = "faded" ]; then
            # For old scans or faded documents, use simple_enhance.py with OCR
            echo "Using enhanced mode with JBIG2-optimized OCR for historical document processing"
            python "${SCRIPT_DIR}/src/simple_enhance.py" \
                --input "${INPUT_PATH}" \
                --output "${OUTPUT_PATH}" \
                --document-type "${DOCUMENT_TYPE}" \
                --dpi 400 \
                --use-jbig2 \
                ${PARALLEL}
        else
            # For general documents, use process_documents.py
            python "${SCRIPT_DIR}/src/process_documents.py" \
                --input "${INPUT_PATH}" \
                --output "${OUTPUT_PATH}" \
                --max-size "${MAX_SIZE}" \
                --document-type "${DOCUMENT_TYPE}" \
                ${ACADEMIC} ${PARALLEL}
        fi
        ;;
        
    visualize)
        # Run visualization with all arguments passed through
        python "${SCRIPT_DIR}/src/visualize_results.py" "$@"
        ;;
        
    install)
        echo "Dependencies installed successfully."
        ;;
        
    *)
        echo "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac

# Deactivate virtual environment
deactivate

echo "Done!"