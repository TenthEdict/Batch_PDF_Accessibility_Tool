#!/bin/bash

# Clean up stray pip files
cleanup_pip_files() {
    echo "Removing stray pip files..."
    rm -f /app/=*
}

# Ensure correct directory structure
setup_directories() {
    echo "Setting up directory structure..."
    mkdir -p /app/output/analysis
    mkdir -p /app/output/logs
    mkdir -p /app/input
}

# Fix permissions
fix_permissions() {
    echo "Fixing permissions..."
    chown -R root:root /app/output
    chmod -R 775 /app/output
    chown -R root:root /app/input
    chmod -R 775 /app/input
}

echo "Starting environment cleanup..."
cleanup_pip_files
setup_directories
fix_permissions
echo "Environment cleanup completed!"
