#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR=$(dirname "$(realpath "$0")")
INPUT_DIR="$SCRIPT_DIR/input"

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Input directory not found: $INPUT_DIR"
    exit 1
fi

echo "Cleaning input directory..."
echo "Removing all files and subdirectories, preserving main input directory..."

# Remove all contents of input directory while preserving the directory itself
find "$INPUT_DIR" -mindepth 1 -delete

echo "Done! Input directory cleaned."
echo "Current input directory structure:"
ls -la "$INPUT_DIR"
