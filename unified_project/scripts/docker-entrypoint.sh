#!/bin/bash
#==============================================================================
# docker-entrypoint.sh - Container entry point for academic processing
#==============================================================================
set -e

# Default values
MODE="academic"
TIMEOUT=1800
BATCH_MODE=false

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
LOG_FILE="/data/logs/academic_processor_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

log "Starting processing with mode: $MODE"
log "Input: $INPUT"
log "Output: $OUTPUT"
log "Timeout: ${TIMEOUT}s"
log "Batch mode: $BATCH_MODE"

# Execute main python processing script
if [ "$BATCH_MODE" = true ]; then
    log "Processing batch of documents from $INPUT to $OUTPUT"
    
    # Count files for batch processing
    FILE_COUNT=$(find "$INPUT" -type f -name "*.pdf" | wc -l)
    log "Found $FILE_COUNT PDF files to process"
    
    python3 -m src.main --mode "$MODE" --timeout "$TIMEOUT" --batch "$INPUT" "$OUTPUT" 2>&1 | tee -a "$LOG_FILE"
else
    log "Processing single document: $(basename "$INPUT")"
    python3 -m src.main --mode "$MODE" --timeout "$TIMEOUT" "$INPUT" "$OUTPUT" 2>&1 | tee -a "$LOG_FILE"
fi

# Check for successful completion
if [ $? -eq 0 ]; then
    log "Processing completed successfully"
    exit 0
else
    log "Processing failed with error code $?"
    exit 1
fi