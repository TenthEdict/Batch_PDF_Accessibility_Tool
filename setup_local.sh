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

# Check and install system dependencies
if ! command -v pdftoppm &> /dev/null; then
    echo "poppler-utils is required but not installed."
    echo "Please install it with: sudo apt-get install -y poppler-utils"
    echo "This is needed for PDF to image conversion."
fi

echo "Setup complete! You can now run the local processing script with:"
echo "./process_academic_local.py --batch /home/schipp0/ePubs_AccProj/data/input /home/schipp0/ePubs_AccProj/data/output"