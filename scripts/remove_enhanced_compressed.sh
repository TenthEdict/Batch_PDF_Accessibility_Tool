#!/bin/bash

# Script to remove "_enhanced_compressed" from filenames
# Usage: ./remove_enhanced_compressed.sh [directory_path]

# Set the directory path
if [ $# -eq 0 ]; then
    # Default directory if no argument provided
    DIRECTORY="~/ePubs_Main/data/input"
else
    DIRECTORY="$1"
fi

# Check if directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Error: Directory '$DIRECTORY' does not exist."
    exit 1
fi

echo "Processing files in: $DIRECTORY"
echo "----------------------------------------"

# Initialize counters
renamed_count=0
skipped_count=0

# Process files in the directory
for file in "$DIRECTORY"/*_enhanced*; do
    # Check if file exists (handles case where no matching files found)
    if [ ! -e "$file" ]; then
        echo "No files matching pattern '*_enhanced*' found."
        break
    fi
    
    # Get the directory and filename
    dir=$(dirname "$file")
    filename=$(basename "$file")
    
    # Create new filename by removing "_enhanced"
    new_filename="${filename/_enhanced/}"
    
    # Full paths
    old_path="$file"
    new_path="$dir/$new_filename"
    
    # Check if target file already exists
    if [ -e "$new_path" ]; then
        echo "SKIP: '$new_filename' already exists"
        ((skipped_count++))
        continue
    fi
    
    # Rename the file
    if mv "$old_path" "$new_path"; then
        echo "RENAMED: '$filename' → '$new_filename'"
        ((renamed_count++))
    else
        echo "ERROR: Failed to rename '$filename'"
    fi
done

echo "----------------------------------------"
echo "Summary:"
echo "Files renamed: $renamed_count"
echo "Files skipped: $skipped_count"
echo "Done!"
