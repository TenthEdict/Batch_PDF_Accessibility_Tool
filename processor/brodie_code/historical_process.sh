#!/bin/bash
# Wrapper script for historical document processing

# Check if there are at least 1 argument
if [ $# -lt 1 ]; then
    echo "Usage: $0 <command> [docker_options]"
    echo ""
    echo "Commands:"
    echo "  process         Process historical documents with specialized OCR"
    echo "  analyze <file>  Analyze a document to determine if it's historical"
    echo "  help            Show help message"
    echo ""
    echo "Docker options (optional):"
    echo "  memory          Memory limit (default: 8g)"
    echo "  cpus            CPU limit (default: 4)"
    echo "  timeout         Container timeout in seconds (default: 3600)"
    echo ""
    echo "Example:"
    echo "  $0 process 16g 8 7200  # Process with 16GB RAM, 8 CPUs, 2-hour timeout"
    exit 1
fi

COMMAND="$1"
shift

# Translate command to Docker entrypoint command
case "$COMMAND" in
    "process")
        DOCKER_COMMAND="process-historical"
        ;;
    "analyze")
        DOCKER_COMMAND="analyze"
        ;;
    "help")
        DOCKER_COMMAND="help"
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Valid commands: process, analyze, help"
        exit 1
        ;;
esac

# Parse optional Docker resource parameters
MEMORY=${1:-"8g"}
CPUS=${2:-"4"}
TIMEOUT=${3:-"3600"}
shift 3 2>/dev/null || true

# Call the main container script with the modified command
./container.sh "$DOCKER_COMMAND" "$MEMORY" "$CPUS" "$TIMEOUT" "$@"