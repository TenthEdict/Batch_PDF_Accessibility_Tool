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
chmod +x docker-entrypoint.sh
chmod +x container.sh

# Fix any line ending issues
echo "Fixing line endings..."
tr -d '\r' < ../docker-entrypoint.sh > ../docker-entrypoint.tmp && mv ../docker-entrypoint.tmp ../docker-entrypoint.sh

# Clean output directory
echo "Cleaning output directory..."
rm -rf output/*
mkdir -p output

# Rebuild
echo "Building new container..."
docker build --no-cache -t pdf-accessibility .

echo "=== Rebuild Complete ==="
echo "You can now run: ./container.sh analyze"
