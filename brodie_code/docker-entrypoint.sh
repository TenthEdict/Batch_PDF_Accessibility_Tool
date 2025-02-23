#!/bin/bash
set -e

ensure_directories() {
    for dir in "input" \
              "output/corrections" \
              "output/reports" \
              "output/processed_pdfs" \
              "output/logs" \
              "output/ocr_results" \
              "output/tagged" \
              "output/final" \
              "output/analysis"; do
        mkdir -p "/app/$dir"
        chmod 775 "/app/$dir"
    done
}

# Clean up pip files
cleanup_pip_files() {
    rm -f /app/=*
}

# Setup logging
setup_logging() {
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    LOG_FILE="/app/output/logs/build_${TIMESTAMP}.log"
    
    # Ensure parent directory exists
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Setup logging to both file and console
    exec 1> >(tee -a "$LOG_FILE")
    exec 2> >(tee -a "$LOG_FILE" >&2)
}

echo "Starting process at $(date)"

# Run initialization
ensure_directories
cleanup_pip_files
setup_logging

# Check for Anthropic API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Warning: ANTHROPIC_API_KEY not set. Code analysis features will be disabled."
fi

# Execute command
case "$1" in
    "analyze")
        echo "Running code analysis..."
        python3 -m accessibility_checker.utils.code_analyzer
        ;;
    "process")
        echo "Running document processing..."
        python3 -m accessibility_checker.main
        ;;
    "build")
        echo "Running full build process..."
        python3 -m accessibility_checker.build.process
        ;;
    *)
        exec "$@"
        ;;
esac

echo "Process completed at $(date)"