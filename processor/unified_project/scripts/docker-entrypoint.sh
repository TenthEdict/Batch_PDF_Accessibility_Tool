#!/bin/bash
#==============================================================================
# docker-entrypoint.sh - Container entry point for ePubs document processing
#==============================================================================
set -e

# Default values
MODE="academic"
TIMEOUT=1800
BATCH_MODE=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --batch)
            BATCH_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "ePubs Accessibility Enhancement Container"
            echo "Usage: docker run [options] INPUT OUTPUT"
            echo "Options:"
            echo "  --mode [academic|default]  Processing mode (default: academic)"
            echo "  --timeout SECONDS          Processing timeout (default: 1800)"
            echo "  --batch                     Process directory of files"
            echo "  --verbose                   Enable verbose output"
            echo "  --help                      Show this help"
            exit 0
            ;;
        *)
            break  # Stop processing arguments, assume remaining are input/output
            ;;
    esac
done

# Input and output paths
INPUT="$1"
OUTPUT="$2"

# Exit if no input/output specified
if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
    echo "Error: Input and output paths are required"
    echo "Usage: docker run ... [--mode academic] [--timeout SECONDS] [--batch] INPUT OUTPUT"
    exit 1
fi

# Check if input exists
if [ ! -e "$INPUT" ]; then
    echo "Error: Input path does not exist: $INPUT"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT")"

# Set up logging
LOG_FILE="/data/logs/epubs_processor_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

log "Starting ePubs accessibility enhancement"
log "Mode: $MODE"
log "Input: $INPUT"
log "Output: $OUTPUT"
log "Timeout: ${TIMEOUT}s"
log "Batch mode: $BATCH_MODE"
log "Verbose: $VERBOSE"

# Build command flags
VERBOSE_FLAG=""

if [ "$VERBOSE" = true ]; then
    VERBOSE_FLAG="--verbose"
fi

# Execute main python processing script using the unified CLI
if [ "$BATCH_MODE" = true ]; then
    log "Processing batch of documents from $INPUT to $OUTPUT"
    
    # Count files for batch processing
    FILE_COUNT=$(find "$INPUT" -type f -name "*.pdf" | wc -l)
    log "Found $FILE_COUNT PDF files to process"
    
    # Process each PDF in the input directory using the new CLI structure
    find "$INPUT" -type f -name "*.pdf" | while read -r pdf_file; do
        rel_path=$(realpath --relative-to="$INPUT" "$pdf_file")
        output_file="$OUTPUT/${rel_path%.pdf}_enhanced.pdf"
        mkdir -p "$(dirname "$output_file")"
        
        log "Processing: $rel_path"
        timeout "$TIMEOUT" epubs process "$pdf_file" "$output_file" --mode "$MODE" $VERBOSE_FLAG 2>&1 | tee -a "$LOG_FILE" || {
            log "Failed to process: $rel_path"
            continue
        }
    done
else
    log "Processing single document: $(basename "$INPUT")"
    timeout "$TIMEOUT" epubs process "$INPUT" "$OUTPUT" --mode "$MODE" $VERBOSE_FLAG 2>&1 | tee -a "$LOG_FILE"
fi

# Check for successful completion
if [ $? -eq 0 ]; then
    log "Processing completed successfully"
    exit 0
else
    log "Processing failed with error code $?"
    exit 1
fi