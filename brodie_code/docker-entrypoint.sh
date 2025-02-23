#!/bin/bash
set -e

# Setup logging
LOG_DIR="/app/output/logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/build_${TIMESTAMP}.log"

# Log both to file and console
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

echo "Starting process at $(date)"
echo "Python version: $(python3 --version)"
echo "Working directory: $(pwd)"
echo "Contents of /app:"
ls -la /app
echo "Contents of /app/input:"
ls -la /app/input
echo "Contents of /app/output:"
ls -la /app/output

# Check for Anthropic API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Warning: ANTHROPIC_API_KEY not set. Code analysis features will be disabled."
else
    echo "ANTHROPIC_API_KEY is set"
fi

# Check for key.txt
if [ -f "/app/key.txt" ]; then
    echo "key.txt exists"
else
    echo "Warning: key.txt not found"
fi

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
