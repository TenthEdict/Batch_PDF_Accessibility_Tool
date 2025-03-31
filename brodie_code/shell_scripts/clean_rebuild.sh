#!/bin/bash

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
BRODIE_CODE_DIR="$PROJECT_ROOT/brodie_code"

echo "=== Starting Clean Rebuild Process ==="

# Stop and remove containers
echo "Cleaning up containers..."
docker ps -a | grep 'pdf-accessibility' | awk '{print $1}' | xargs -r docker stop
docker ps -a | grep 'pdf-accessibility' | awk '{print $1}' | xargs -r docker rm

# Remove image
echo "Removing old image..."
docker image rm pdf-accessibility

# Clean up dangling images
echo "Cleaning up dangling images..."
docker image prune -f

# Ensure script permissions
echo "Setting permissions..."
chmod +x "$SCRIPT_DIR/docker-entrypoint.sh"
chmod +x "$SCRIPT_DIR/container.sh"
chmod +x "$PROJECT_ROOT/accessibility_tools/scripts/container_accessibility.sh"

# Fix any line ending issues
echo "Fixing line endings..."
tr -d '\r' < "$SCRIPT_DIR/docker-entrypoint.sh" > "$SCRIPT_DIR/docker-entrypoint.tmp" && mv "$SCRIPT_DIR/docker-entrypoint.tmp" "$SCRIPT_DIR/docker-entrypoint.sh"
tr -d '\r' < "$PROJECT_ROOT/accessibility_tools/scripts/container_accessibility.sh" > "$PROJECT_ROOT/accessibility_tools/scripts/container_accessibility.tmp" && mv "$PROJECT_ROOT/accessibility_tools/scripts/container_accessibility.tmp" "$PROJECT_ROOT/accessibility_tools/scripts/container_accessibility.sh"

# Clean output directory
echo "Cleaning output directory..."
rm -rf "$PROJECT_ROOT/output"/*
mkdir -p "$PROJECT_ROOT/output"

# Rebuild
echo "Building new container..."
# Build with more detailed output
cd "$BRODIE_CODE_DIR" && docker build --no-cache --progress=plain -t pdf-accessibility .

echo "=== Rebuild Complete ==="
echo "You can now run: $SCRIPT_DIR/container.sh analyze"
