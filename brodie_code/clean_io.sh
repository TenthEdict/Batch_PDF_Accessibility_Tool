#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR=$(dirname "$(realpath "$0")")
INPUT_DIR="$SCRIPT_DIR/00input"
OUTPUT_DIR="$SCRIPT_DIR/00output"

# List of main output directories to preserve
MAIN_DIRS=(
    "corrections"
    "final"
    "logs"
    "ocr_results"
    "processed_pdfs"
    "reports"
    "tagged"
)

# Function to clean input directory
clean_input() {
    echo "=== Cleaning Input Directory ==="
    if [ ! -d "$INPUT_DIR" ]; then
        echo "Input directory not found: $INPUT_DIR"
        return 1
    fi

    echo "Removing all files and subdirectories from input..."
    find "$INPUT_DIR" -mindepth 1 -delete

    echo "Input directory cleaned."
    echo "Current input directory structure:"
    ls -la "$INPUT_DIR"
    echo
}

# Function to clean output directory
clean_output() {
    echo "=== Cleaning Output Directory ==="
    if [ ! -d "$OUTPUT_DIR" ]; then
        echo "Output directory not found: $OUTPUT_DIR"
        return 1
    fi

    echo "Removing all files and temporary subdirectories from output..."
    
    # First, remove all files
    find "$OUTPUT_DIR" -type f -delete

    # Then, for each main directory, remove all subdirectories
    for dir in "${MAIN_DIRS[@]}"
    do
        if [ -d "$OUTPUT_DIR/$dir" ]; then
            find "$OUTPUT_DIR/$dir" -mindepth 1 -type d -exec rm -rf {} +
        fi
    done

    echo "Output directory cleaned."
    echo "Current output directory structure:"
    ls -R "$OUTPUT_DIR"
    echo
}

# Main execution
echo "Starting cleanup of input and output directories..."
echo

# Clean input directory
clean_input
input_status=$?

# Clean output directory
clean_output
output_status=$?

# Final status report
echo "=== Cleanup Complete ==="
if [ $input_status -eq 0 ] && [ $output_status -eq 0 ]; then
    echo "All directories successfully cleaned."
else
    echo "Some errors occurred during cleanup."
    exit 1
fi
