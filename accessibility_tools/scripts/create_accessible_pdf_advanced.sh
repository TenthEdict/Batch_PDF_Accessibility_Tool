#!/bin/bash
# Advanced PDF Accessibility Enhancement Script
# 
# This script processes PDFs using the advanced enhance_pdf_advanced.py script
# It handles dependencies installation and provides a simplified interface
#
# Usage: ./create_accessible_pdf_advanced.sh input_pdf [output_pdf] [--title "Title"] [--author "Author"]
# or
# Usage: ./create_accessible_pdf_advanced.sh --batch input_dir output_dir
# 
# Enhanced with support for historical documents:
# Usage: ./create_accessible_pdf_advanced.sh input_pdf [output_pdf] --mode historical
# or
# Usage: ./create_accessible_pdf_advanced.sh --batch input_dir output_dir --mode historical

set -e

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Path to enhancer script
ENHANCER_SCRIPT="${PROJECT_ROOT}/core/enhance_pdf_advanced.py"

# Check if enhancer script exists
if [ ! -f "$ENHANCER_SCRIPT" ]; then
    echo "Error: PDF enhancer script not found at $ENHANCER_SCRIPT"
    exit 1
fi

# Check for dependencies
check_dependencies() {
    echo "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is required but not installed. Please install Python 3."
        exit 1
    fi
    
    # Create virtual environment if needed
    VENV_DIR="${PROJECT_ROOT}/venv_accessibility"
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment for dependencies..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "${VENV_DIR}/bin/activate"
    
    # Install required packages
    echo "Installing required packages..."
    pip install pikepdf PyMuPDF opencv-python-headless pytesseract pillow
    
    # Install Tesseract if not available (macOS specific)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v tesseract &> /dev/null; then
            echo "Tesseract OCR not found. Installing with Homebrew..."
            if ! command -v brew &> /dev/null; then
                echo "Error: Homebrew not found. Please install Homebrew or Tesseract OCR manually."
                exit 1
            fi
            brew install tesseract
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if ! command -v tesseract &> /dev/null; then
            echo "Tesseract OCR not found. Please install using your package manager."
            echo "For Ubuntu/Debian: sudo apt-get install tesseract-ocr"
            echo "For CentOS/RHEL: sudo yum install tesseract"
            exit 1
        fi
    fi
    
    echo "All dependencies satisfied."
}

# Process a single PDF
process_pdf() {
    local input_path="$1"
    local output_path="$2"
    shift 2
    
    # Extract any mode parameter
    local mode="standard"
    local other_args=()
    
    for arg in "$@"; do
        if [[ "$arg" == "--mode" ]]; then
            # Get the mode parameter that follows --mode
            mode="${@[1]}"
            shift 2  # Skip both --mode and the actual mode
        else
            other_args+=("$arg")
        fi
    done
    
    # Create mode-specific output subfolder if needed
    if [[ "$mode" != "standard" ]]; then
        local output_dir=$(dirname "$output_path")
        local filename=$(basename "$output_path")
        local mode_dir="${output_dir}/${mode}"
        
        mkdir -p "$mode_dir"
        output_path="${mode_dir}/${filename}"
    fi
    
    # Activate virtual environment
    source "${PROJECT_ROOT}/venv_accessibility/bin/activate"
    
    # Run enhancer script
    echo "Processing PDF: $input_path (Mode: $mode)"
    
    if [[ "$mode" != "standard" ]]; then
        python3 "$ENHANCER_SCRIPT" --mode "$mode" "$input_path" "$output_path" "${other_args[@]}"
    else
        python3 "$ENHANCER_SCRIPT" "$input_path" "$output_path" "${other_args[@]}"
    fi
    
    echo "PDF processing complete."
    echo "Enhanced PDF saved to: $output_path"
}

# Process a directory of PDFs
process_directory() {
    local input_dir="$1"
    local output_dir="$2"
    shift 2
    
    # Extract any mode parameter
    local mode="standard"
    local other_args=()
    
    for arg in "$@"; do
        if [[ "$arg" == "--mode" ]]; then
            # Get the mode parameter that follows --mode
            mode="${@[1]}"
            shift 2  # Skip both --mode and the actual mode
        else
            other_args+=("$arg")
        fi
    done
    
    # Create mode-specific output subfolder if needed
    if [[ "$mode" != "standard" ]]; then
        output_dir="${output_dir}/${mode}"
        mkdir -p "$output_dir"
    fi
    
    # Activate virtual environment
    source "${PROJECT_ROOT}/venv_accessibility/bin/activate"
    
    # Run enhancer script in batch mode
    echo "Processing PDFs in directory: $input_dir (Mode: $mode)"
    
    if [[ "$mode" != "standard" ]]; then
        python3 "$ENHANCER_SCRIPT" --batch --mode "$mode" "$input_dir" "$output_dir" "${other_args[@]}"
    else
        python3 "$ENHANCER_SCRIPT" --batch "$input_dir" "$output_dir" "${other_args[@]}"
    fi
    
    echo "Batch processing complete."
    echo "Enhanced PDFs saved to: $output_dir"
}

# Main function
main() {
    # Check if running in batch mode
    if [ "$1" == "--batch" ]; then
        shift
        if [ $# -lt 2 ]; then
            echo "Error: Batch mode requires input and output directories."
            echo "Usage: $0 --batch input_dir output_dir [--title \"Title\"] [--author \"Author\"]"
            exit 1
        fi
        
        input_dir="$1"
        output_dir="$2"
        shift 2
        
        # Check dependencies
        check_dependencies
        
        # Process directory
        process_directory "$input_dir" "$output_dir" "$@"
    else
        # Single PDF mode
        if [ $# -lt 1 ]; then
            echo "Error: Input PDF file is required."
            echo "Usage: $0 input_pdf [output_pdf] [--title \"Title\"] [--author \"Author\"] [--mode MODE]"
            echo "   or: $0 --batch input_dir output_dir [--title \"Title\"] [--author \"Author\"] [--mode MODE]"
            echo ""
            echo "Processing Modes:"
            echo "  --mode standard    Standard OCR processing (default)"
            echo "  --mode historical  Specialized processing for historical documents"
            echo "  --mode adaptive    Automatically detect and apply optimal processing"
            echo "  --mode manuscript  Special mode for handwritten manuscripts"
            exit 1
        fi
        
        input_pdf="$1"
        
        # If output path not provided, create default
        if [ $# -eq 1 ] || [[ "$2" == --* ]]; then
            # Extract file name without extension
            input_name=$(basename -- "$input_pdf")
            input_name="${input_name%.*}"
            
            # Default output path
            output_pdf="${PROJECT_ROOT}/output/accessible/${input_name}_accessible.pdf"
            
            # Create output directory if it doesn't exist
            mkdir -p "$(dirname "$output_pdf")"
            
            # Shift arguments if needed
            if [ $# -gt 1 ] && [[ "$2" == --* ]]; then
                shift
            else
                shift 1
            fi
        else
            output_pdf="$2"
            shift 2
        fi
        
        # Check dependencies
        check_dependencies
        
        # Process PDF
        process_pdf "$input_pdf" "$output_pdf" "$@"
    fi
}

# Run main function
main "$@"