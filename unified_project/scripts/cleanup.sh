#!/bin/bash
# Script to archive old code and clean up the project structure

# Use the current directory as the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PARENT_DIR="$(cd "$BASE_DIR/.." && pwd)"
ARCHIVE_DIR="$PARENT_DIR/archive"

# Create necessary directories
mkdir -p "$ARCHIVE_DIR/code"

# Move the MoslerThesis project to archive (if not already done)
if [ -d "$PARENT_DIR/MoslerThesis" ]; then
    echo "Archiving MoslerThesis directory..."
    mv "$PARENT_DIR/MoslerThesis" "$ARCHIVE_DIR/MoslerThesis"
fi

# Archive old code directories (after migrating functionality)
echo "Archiving old code directories..."

# Archive accessibility_tools
if [ -d "$PARENT_DIR/accessibility_tools" ]; then
    echo "Archiving accessibility_tools..."
    mv "$PARENT_DIR/accessibility_tools" "$ARCHIVE_DIR/code/"
fi

# Archive brodie_code
if [ -d "$PARENT_DIR/brodie_code" ]; then
    echo "Archiving brodie_code..."
    mv "$PARENT_DIR/brodie_code" "$ARCHIVE_DIR/code/"
fi

# Archive mai_code
if [ -d "$PARENT_DIR/mai_code" ]; then
    echo "Archiving mai_code..."
    mv "$PARENT_DIR/mai_code" "$ARCHIVE_DIR/code/"
fi

# Archive smolDocling
if [ -d "$PARENT_DIR/smolDocling" ]; then
    echo "Archiving smolDocling..."
    mv "$PARENT_DIR/smolDocling" "$ARCHIVE_DIR/code/"
fi

# Remove old test files from root
echo "Removing old test files..."
rm -f "$PARENT_DIR"/*test*.py

# Clean up input/output directories
echo "Cleaning up input/output directories..."
mkdir -p "$PARENT_DIR/data/input" "$PARENT_DIR/data/output"

# If there are files in the input directory, move them to the new location
if [ -d "$PARENT_DIR/input" ]; then
    mv "$PARENT_DIR/input"/* "$PARENT_DIR/data/input/" 2>/dev/null
    rmdir "$PARENT_DIR/input"
fi

if [ -d "$PARENT_DIR/output" ]; then
    mv "$PARENT_DIR/output"/* "$PARENT_DIR/data/output/" 2>/dev/null
    rmdir "$PARENT_DIR/output"
fi

echo "Cleanup complete!"