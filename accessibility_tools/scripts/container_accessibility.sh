#!/bin/bash
# Container script for PDF accessibility enhancement
# 
# This script builds and runs the Docker container with accessibility tools
# It handles timeouts and resource allocation
#
# Usage: ./container_accessibility.sh [command] [memory] [cpus] [timeout]
# Example: ./container_accessibility.sh process 16g 8 14400

set -e

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PARENT_ROOT="$(dirname "$PROJECT_ROOT")"

# Default values
COMMAND=${1:-"process"}
MEMORY=${2:-"8g"}
CPUS=${3:-"4"}
TIMEOUT=${4:-"7200"}  # Default: 2 hours (in seconds)

# Docker image name
IMAGE_NAME="pdf-accessibility-enhancer"

# Function to print usage
print_usage() {
    echo "PDF Accessibility Docker Container"
    echo "=================================="
    echo "Usage: $0 [command] [memory] [cpus] [timeout]"
    echo ""
    echo "Commands:"
    echo "  process       Process PDFs in input directory (default)"
    echo "  shell         Start a shell in the container"
    echo "  enhance       Run enhanced PDF accessibility processing"
    echo "  diagnose      Run system diagnostics"
    echo "  help          Show this help message"
    echo ""
    echo "Resources:"
    echo "  memory        Memory limit (default: 8g)"
    echo "  cpus          CPU limit (default: 4)"
    echo "  timeout       Timeout in seconds (default: 7200 = 2 hours)"
    echo ""
    echo "Examples:"
    echo "  $0                       # Run with default settings"
    echo "  $0 process 16g 8 14400   # Process with 16GB RAM, 8 CPUs, 4 hour timeout"
    echo "  $0 enhance               # Run enhanced accessibility processing"
    echo "  $0 shell                 # Start a shell in the container"
}

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker is not installed or not in PATH"
        echo "Please install Docker and try again"
        exit 1
    fi
}

# Function to build Docker image if needed
build_image() {
    echo "Checking for Docker image: $IMAGE_NAME"
    
    if ! docker images | grep -q "$IMAGE_NAME"; then
        echo "Building Docker image: $IMAGE_NAME"
        
        # Navigate to project root to build from Dockerfile.accessibility
        cd "$PROJECT_ROOT"
        
        # Build Docker image with longer timeout
        DOCKER_BUILDKIT=1 docker build \
            --progress=plain \
            --network=host \
            --tag "$IMAGE_NAME" \
            --file Dockerfile.accessibility \
            --build-arg BUILDKIT_INLINE_CACHE=1 \
            .
            
        echo "Docker image built successfully"
    else
        echo "Using existing Docker image: $IMAGE_NAME"
    fi
}

# Function to run Docker container
run_container() {
    local input_dir="$PARENT_ROOT/input"
    local output_dir="$PARENT_ROOT/output"
    
    echo "Starting container with settings:"
    echo "- Command: $COMMAND"
    echo "- Memory: $MEMORY"
    echo "- CPUs: $CPUS"
    echo "- Timeout: $TIMEOUT seconds"
    echo "- Input directory: $input_dir"
    echo "- Output directory: $output_dir"
    
    # Check directories
    if [ ! -d "$input_dir" ]; then
        echo "Creating input directory: $input_dir"
        mkdir -p "$input_dir"
    fi
    
    if [ ! -d "$output_dir" ]; then
        echo "Creating output directory: $output_dir"
        mkdir -p "$output_dir"
    fi
    
    # For shell command, run interactive container
    if [ "$COMMAND" = "shell" ]; then
        docker run --rm -it \
            --memory="$MEMORY" \
            --cpus="$CPUS" \
            -v "$input_dir:/app/input" \
            -v "$output_dir:/app/output" \
            -v "$PARENT_ROOT/enhance_pdf_advanced.py:/app/enhance_pdf_advanced.py" \
            "$IMAGE_NAME" bash
        return
    fi
    
    # For enhanced accessibility processing
    if [ "$COMMAND" = "enhance" ]; then
        docker run --rm \
            --memory="$MEMORY" \
            --cpus="$CPUS" \
            --name="pdf-accessibility-enhancement" \
            -v "$input_dir:/app/input" \
            -v "$output_dir:/app/output" \
            -v "$PARENT_ROOT/enhance_pdf_advanced.py:/app/enhance_pdf_advanced.py" \
            "$IMAGE_NAME" python3 /app/enhance_pdf_advanced.py --batch /app/input /app/output/accessible
        return
    fi
    
    # For normal processing or other commands
    timeout --preserve-status "$TIMEOUT" \
        docker run --rm \
            --memory="$MEMORY" \
            --cpus="$CPUS" \
            --name="pdf-accessibility-${COMMAND}" \
            -v "$input_dir:/app/input" \
            -v "$output_dir:/app/output" \
            "$IMAGE_NAME" "$COMMAND"
}

# Main function
main() {
    if [ "$COMMAND" = "help" ]; then
        print_usage
        exit 0
    fi
    
    check_docker
    build_image
    run_container
}

# Run main function
main