#!/bin/bash

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
chmod +x shell_scripts/docker-entrypoint.sh
chmod +x shell_scripts/container.sh


# Fix any line ending issues
echo "Fixing line endings..."
tr -d '\r' < shell_scripts/docker-entrypoint.sh > shell_scripts/docker-entrypoint.tmp && mv shell_scripts/docker-entrypoint.tmp shell_scripts/docker-entrypoint.sh

# Clean output directory
echo "Cleaning output directory..."
rm -rf output/*
mkdir -p output

# Rebuild
echo "Building new container..."
# Build with more detailed output
docker build --no-cache --progress=plain -t pdf-accessibility .

echo "=== Rebuild Complete ==="
echo "You can now run: ./container.sh analyze"
