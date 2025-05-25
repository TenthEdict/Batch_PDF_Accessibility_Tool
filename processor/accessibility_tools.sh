#!/bin/bash
#
# DEPRECATED: PDF Accessibility Tools - Main wrapper script
#
# This script has been DEPRECATED in Phase 2 of the refactoring process.
# Historical document processing is no longer required per user requirements.
#
# PLEASE USE THE UNIFIED CLI INTERFACE INSTEAD:
#
# Installation:
#   pip install -e .
#
# Usage:
#   epubs process input.pdf output.pdf --mode academic
#   epubs process-batch input_dir output_dir --mode accessibility  
#   epubs enhance input.pdf output.pdf --title "Document Title"
#   epubs validate document.pdf --report-format html
#
# For more information, see: processor/unified_project/README.md

# Show deprecation notice and exit
echo "DEPRECATED: This script has been deprecated in Phase 2 of the refactoring process."
echo ""
echo "Historical document processing is no longer required per user requirements."
echo "Please use the unified CLI interface instead:"
echo ""
echo "Installation:"
echo "  pip install -e ."
echo ""
echo "Usage:"
echo "  epubs process input.pdf output.pdf --mode academic"
echo "  epubs process-batch input_dir output_dir --mode accessibility"
echo "  epubs enhance input.pdf output.pdf --title \"Document Title\""
echo "  epubs validate document.pdf --report-format html"
echo ""
echo "For more information, see: processor/unified_project/README.md"
echo ""
exit 1

# Legacy code below - no longer executed
set -e

# Determine script location and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Function to show usage
show_usage() {
    echo "PDF Accessibility Tools"
    echo "======================"
    echo "Usage:"
    echo "  $0 enhance INPUT OUTPUT [OPTIONS]"
    echo "  $0 batch-enhance INPUT_DIR OUTPUT_DIR [OPTIONS]"
    echo "  $0 validate INPUT [OPTIONS]"
    echo "  $0 batch-validate INPUT_DIR OUTPUT_DIR [OPTIONS]"
    echo "  $0 analyze INPUT [OPTIONS]"
    echo "  $0 docker [COMMAND] [MEMORY] [CPUS] [TIMEOUT]"
    echo ""
    echo "Commands:"
    echo "  enhance           Enhance a single PDF with accessibility features"
    echo "  batch-enhance     Enhance multiple PDFs in a directory"
    echo "  validate          Validate PDF accessibility"
    echo "  batch-validate    Validate multiple PDFs in a directory"
    echo "  analyze           Analyze PDF structure and accessibility"
    echo "  docker            Run tools in Docker container with configurable resources"
    echo ""
    echo "Examples:"
    echo "  $0 enhance input.pdf output.pdf --level advanced --title \"My Document\""
    echo "  $0 batch-enhance input_dir output_dir --level journal"
    echo "  $0 validate document.pdf --detailed"
    echo "  $0 batch-validate input_dir reports_dir --workers 8"
    echo "  $0 docker enhance 16g 8 14400"
    echo ""
    echo "For detailed help on each command:"
    echo "  $0 enhance --help"
    echo "  $0 batch-enhance --help"
    echo "  $0 validate --help"
    echo "  $0 batch-validate --help"
    echo "  $0 analyze --help"
    echo "  $0 docker --help"
}

# Function to run CLI commands
run_cli() {
    COMMAND="$1"
    shift
    
    # Activate virtual environment if it exists
    if [ -d "$PROJECT_ROOT/venv_accessibility" ]; then
        source "$PROJECT_ROOT/venv_accessibility/bin/activate"
    fi
    
    # If installed as package, use the entry point
    if command -v access-cli &> /dev/null; then
        access-cli "$COMMAND" "$@"
    else
        # Otherwise run the script directly
        python3 "$PROJECT_ROOT/accessibility_tools/access_cli.py" "$COMMAND" "$@"
    fi
}

# Function to run Docker container
run_docker() {
    COMMAND=${1:-"enhance"}
    MEMORY=${2:-"8g"}
    CPUS=${3:-"4"}
    TIMEOUT=${4:-"7200"}  # Default: 2 hours (in seconds)
    
    # Check if Docker script exists
    DOCKER_SCRIPT="$PROJECT_ROOT/accessibility_tools/scripts/container_accessibility.sh"
    if [ \! -f "$DOCKER_SCRIPT" ]; then
        DOCKER_SCRIPT="$PROJECT_ROOT/brodie_code/shell_scripts/container_accessibility.sh"
    fi
    
    if [ \! -f "$DOCKER_SCRIPT" ]; then
        echo "Error: Docker script not found"
        exit 1
    fi
    
    # Run Docker container
    "$DOCKER_SCRIPT" "$COMMAND" "$MEMORY" "$CPUS" "$TIMEOUT"
}

# Check if command is provided
if [ $# -lt 1 ]; then
    show_usage
    exit 1
fi

# Get command
COMMAND="$1"
shift

# Run appropriate command
case "$COMMAND" in
    enhance|batch-enhance|validate|batch-validate|analyze)
        run_cli "$COMMAND" "$@"
        ;;
    docker)
        run_docker "$@"
        ;;
    -h|--help|help)
        show_usage
        ;;
    *)
        echo "Error: Unknown command '$COMMAND'"
        show_usage
        exit 1
        ;;
esac
