#!/bin/bash
# Setup for local processing

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install minimal required dependencies
echo "Installing required dependencies..."
pip install pikepdf pytesseract opencv-python-headless pillow numpy tqdm pyyaml pdf2image

echo "Setup complete! You can now run the local processing script with:"
echo "./process_academic_local.py --batch /home/schipp0/ePubs_AccProj/data/input /home/schipp0/ePubs_AccProj/data/output"