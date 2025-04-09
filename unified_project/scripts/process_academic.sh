#!/bin/bash
#==============================================================================
# process_academic.sh - Academic paper accessibility processing
#==============================================================================
# DESCRIPTION:
#   Processes academic papers (PDF) with specialized OCR and structure analysis
#   optimized for modern academic papers with tables, formulas, and citations.
#   Creates accessible PDF/UA compliant documents with proper structure tagging.
#
# USAGE:
#   ./process_academic.sh [OPTIONS] <input> <output>
#
# OPTIONS:
#   -b, --batch        Process a batch of documents
#   -m, --memory       Container memory limit (default: 8g)
#   -c, --cpus         CPU limit (default: 4)
#   -t, --timeout      Processing timeout (default: 1800s)
#   -h, --help         Show this help message
#
# EXAMPLES:
#   ./process_academic.sh input.pdf output.pdf
#   ./process_academic.sh --batch input_dir output_dir
#   ./process_academic.sh --memory 16g --cpus 8 input.pdf output.pdf
#==============================================================================

# Strict error handling
set -euo pipefail

# Configuration
SCRIPT_NAME=$(basename "$0")
VERSION="1.0.0"
CONFIG_FILE="../config/academic.yaml"
MODE="academic"

# Default values
MEMORY="8g"
CPUS="4"
TIMEOUT="1800"
INPUT_PATH=""
OUTPUT_PATH=""
BATCH_MODE=false

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

#==============================================================================
# UTILITY FUNCTIONS
#==============================================================================

# Display script banner
function show_banner() {
    echo -e "\n${BLUE}=======================================================${NC}"
    echo -e "${GREEN}  Academic Paper Accessibility Processor v${VERSION}${NC}"
    echo -e "${BLUE}=======================================================${NC}\n"
}

# Display help information
function show_help() {
    echo -e "${YELLOW}USAGE:${NC}"
    echo -e "  ${SCRIPT_NAME} [OPTIONS] <input> <output>"
    echo -e ""
    echo -e "${YELLOW}DESCRIPTION:${NC}"
    echo -e "  Processes academic papers optimized for modern publications (last 20 years)."
    echo -e "  Specializes in handling complex academic layout, citations, and mathematical content."
    echo -e ""
    echo -e "${YELLOW}OPTIONS:${NC}"
    echo -e "  -b, --batch        Process a batch of documents"
    echo -e "  -m, --memory       Container memory limit (default: 8g)"
    echo -e "  -c, --cpus         CPU limit (default: 4)"
    echo -e "  -t, --timeout      Processing timeout (default: 1800s)"
    echo -e "  -h, --help         Show this help message"
    echo -e ""
    echo -e "${YELLOW}EXAMPLES:${NC}"
    echo -e "  ${SCRIPT_NAME} input.pdf output.pdf"
    echo -e "  ${SCRIPT_NAME} --batch input_dir output_dir"
    echo -e "  ${SCRIPT_NAME} --memory 16g --cpus 8 input.pdf output.pdf"
}

# Check if a command exists
function command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verify dependencies
function check_dependencies() {
    local missing_deps=()
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists python3; then
        missing_deps+=("python3")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${RED}Error: Missing dependencies: ${missing_deps[*]}${NC}"
        echo -e "Please install them before running this script."
        exit 1
    fi
}

# Validate input path
function validate_input() {
    if [ -z "$INPUT_PATH" ]; then
        echo -e "${RED}Error: Input path is required${NC}"
        show_help
        exit 1
    fi
    
    if [ "$BATCH_MODE" = true ]; then
        if [ ! -d "$INPUT_PATH" ]; then
            echo -e "${RED}Error: Input path must be a directory in batch mode${NC}"
            exit 1
        fi
    else
        if [ ! -f "$INPUT_PATH" ]; then
            echo -e "${RED}Error: Input file does not exist: $INPUT_PATH${NC}"
            exit 1
        fi
        
        # Check if it's a PDF
        file_type=$(file -b --mime-type "$INPUT_PATH")
        if [[ "$file_type" != "application/pdf" ]]; then
            echo -e "${YELLOW}Warning: Input file does not appear to be a PDF: $INPUT_PATH (detected as $file_type)${NC}"
            read -p "Continue anyway? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    fi
}

# Validate output path
function validate_output() {
    if [ -z "$OUTPUT_PATH" ]; then
        echo -e "${RED}Error: Output path is required${NC}"
        show_help
        exit 1
    fi
    
    if [ "$BATCH_MODE" = true ]; then
        if [ ! -d "$OUTPUT_PATH" ] && ! mkdir -p "$OUTPUT_PATH" 2>/dev/null; then
            echo -e "${RED}Error: Cannot create output directory: $OUTPUT_PATH${NC}"
            exit 1
        fi
    else
        # Check if output directory exists
        output_dir=$(dirname "$OUTPUT_PATH")
        if [ ! -d "$output_dir" ] && ! mkdir -p "$output_dir" 2>/dev/null; then
            echo -e "${RED}Error: Cannot create output directory: $output_dir${NC}"
            exit 1
        fi
        
        # Check if output file already exists
        if [ -f "$OUTPUT_PATH" ]; then
            echo -e "${YELLOW}Warning: Output file already exists: $OUTPUT_PATH${NC}"
            read -p "Overwrite? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    fi
}

# Process a single PDF file
function process_single_file() {
    local input_file="$1"
    local output_file="$2"
    
    echo -e "${BLUE}Processing:${NC} $(basename "$input_file")"
    echo -e "  ${YELLOW}Input:${NC}  $input_file"
    echo -e "  ${YELLOW}Output:${NC} $output_file"
    
    # Create absolute paths for Docker volume mounting
    local abs_input=$(realpath "$input_file")
    local abs_output=$(realpath "$output_file")
    local abs_output_dir=$(dirname "$abs_output")
    
    # Ensure output directory exists
    mkdir -p "$abs_output_dir"
    
    # Run container with academic processing
    docker run --rm \
        -m "$MEMORY" \
        --cpus "$CPUS" \
        -v "$abs_input:/data/input/$(basename "$input_file")" \
        -v "$abs_output_dir:/data/output" \
        --name "academic_processor_$(date +%s)" \
        ePubs/academic_processor:latest \
        --mode academic \
        --timeout "$TIMEOUT" \
        "/data/input/$(basename "$input_file")" \
        "/data/output/$(basename "$output_file")"
    
    echo -e "${GREEN}✓ Processing complete:${NC} $(basename "$input_file")"
}

# Process a batch of PDF files
function process_batch() {
    local input_dir="$1"
    local output_dir="$2"
    
    echo -e "${BLUE}Processing batch:${NC}"
    echo -e "  ${YELLOW}Input directory:${NC}  $input_dir"
    echo -e "  ${YELLOW}Output directory:${NC} $output_dir"
    
    # Create absolute paths for Docker volume mounting
    local abs_input_dir=$(realpath "$input_dir")
    local abs_output_dir=$(realpath "$output_dir")
    
    # Ensure output directory exists
    mkdir -p "$abs_output_dir"
    
    # Count PDF files
    local pdf_files=()
    while IFS= read -r -d '' file; do
        pdf_files+=("$file")
    done < <(find "$input_dir" -type f -name "*.pdf" -print0)
    
    local file_count=${#pdf_files[@]}
    
    if [ "$file_count" -eq 0 ]; then
        echo -e "${YELLOW}Warning: No PDF files found in input directory${NC}"
        exit 0
    fi
    
    echo -e "${BLUE}Found${NC} $file_count ${BLUE}PDF files to process${NC}"
    
    # Run container with academic processing in batch mode
    docker run --rm \
        -m "$MEMORY" \
        --cpus "$CPUS" \
        -v "$abs_input_dir:/data/input" \
        -v "$abs_output_dir:/data/output" \
        --name "academic_processor_batch_$(date +%s)" \
        ePubs/academic_processor:latest \
        --mode academic \
        --timeout "$TIMEOUT" \
        --batch \
        "/data/input" \
        "/data/output"
    
    echo -e "${GREEN}✓ Batch processing complete${NC}"
}

#==============================================================================
# MAIN FUNCTION
#==============================================================================

# Parse command line arguments
function parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -b|--batch)
                BATCH_MODE=true
                shift
                ;;
            -m|--memory)
                MEMORY="$2"
                shift 2
                ;;
            -c|--cpus)
                CPUS="$2"
                shift 2
                ;;
            -t|--timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            -h|--help)
                show_banner
                show_help
                exit 0
                ;;
            *)
                if [ -z "$INPUT_PATH" ]; then
                    INPUT_PATH="$1"
                elif [ -z "$OUTPUT_PATH" ]; then
                    OUTPUT_PATH="$1"
                else
                    echo -e "${RED}Error: Unexpected argument: $1${NC}"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
}

# Main execution
function main() {
    show_banner
    check_dependencies
    parse_args "$@"
    validate_input
    validate_output
    
    echo -e "${BLUE}Processing with settings:${NC}"
    echo -e "  ${YELLOW}Mode:${NC}     Academic papers"
    echo -e "  ${YELLOW}Memory:${NC}   $MEMORY"
    echo -e "  ${YELLOW}CPUs:${NC}     $CPUS"
    echo -e "  ${YELLOW}Timeout:${NC}  ${TIMEOUT}s"
    echo -e "  ${YELLOW}Batch:${NC}    $BATCH_MODE"
    echo
    
    if [ "$BATCH_MODE" = true ]; then
        process_batch "$INPUT_PATH" "$OUTPUT_PATH"
    else
        process_single_file "$INPUT_PATH" "$OUTPUT_PATH"
    fi
}

# Run main with all arguments
main "$@"