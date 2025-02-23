#!/bin/bash

# Get absolute paths
INPUT_DIR=$(realpath "$(pwd)/input")
OUTPUT_DIR=$(realpath "$(pwd)/output")

# Default command
CMD=${1:-interactive}

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

case "$CMD" in
    "interactive")
        echo "Starting interactive shell..."
        # Simpler shell launch with explicit bash
        docker run --rm -it \
            -v "$INPUT_DIR:/app/input" \
            -v "$OUTPUT_DIR:/app/output" \
            -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
            --entrypoint=/bin/bash \
            pdf-accessibility
        ;;
        
    "analyze")
        echo "Running code analysis..."
        docker run --rm \
            -v "$INPUT_DIR:/app/input" \
            -v "$OUTPUT_DIR:/app/output" \
            -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
            pdf-accessibility python3 -m accessibility_checker.utils.code_analyzer
        ;;
        
    "process")
        echo "Running document processing..."
        docker run --rm \
            -v "$INPUT_DIR:/app/input" \
            -v "$OUTPUT_DIR:/app/output" \
            -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
            pdf-accessibility python3 -m accessibility_checker.main
        ;;
        
    "build")
        echo "Running full build process..."
        docker run --rm \
            -v "$INPUT_DIR:/app/input" \
            -v "$OUTPUT_DIR:/app/output" \
            -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
            pdf-accessibility python3 -m accessibility_checker.build.process
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
