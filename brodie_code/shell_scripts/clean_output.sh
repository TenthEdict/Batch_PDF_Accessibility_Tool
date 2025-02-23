#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR=$(dirname "$(realpath "$0")")
OUTPUT_DIR="$SCRIPT_DIR/output"

# List of main directories to preserve
MAIN_DIRS=(
    "corrections"
    "final"
    "logs"
    "ocr_results"
    "processed_pdfs"
    "reports"
    "tagged"
)

# Check if output directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Output directory not found: $OUTPUT_DIR"
    exit 1
fi

echo "Cleaning output directory..."
echo "Removing all files and temporary subdirectories..."

# First, remove all files
find "$OUTPUT_DIR" -type f -delete

# Then, for each main directory, remove all subdirectories
for dir in "${MAIN_DIRS[@]}"; do
    if [ -d "$OUTPUT_DIR/$dir" ]; then
        # Remove all subdirectories in this main directory
        find "$OUTPUT_DIR/$dir" -mindepth 1 -type d -exec rm -rf {} +
    fi
done

echo "Done! Main directory structure preserved, all files and temporary subdirectories removed."
echo "Current output directory structure:"
ls -R "$OUTPUT_DIR"
