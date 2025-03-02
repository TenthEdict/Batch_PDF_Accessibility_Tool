#!/usr/bin/env python3
"""
Script to create a properly tagged PDF with content association
This script uses a two-step approach:
1. Extract text and structure from the original PDF
2. Create a new PDF with proper tagging and content associations
"""

import os
import sys
import argparse
from pathlib import Path
import subprocess
import tempfile

def run_command(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                               capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None

def create_tagged_pdf(input_path, output_path, title=None, author=None):
    """
    Create a properly tagged PDF using Adobe Acrobat or similar tools
    """
    print(f"Input PDF: {input_path}")
    print(f"Output PDF: {output_path}")
    
    # Check if we can use pdftron (if installed)
    try:
        # First try OCRing the PDF using tesseract
        temp_dir = tempfile.mkdtemp()
        print(f"Created temporary directory: {temp_dir}")
        
        # Extract text using OCR (if needed)
        ocr_cmd = f"ocrmypdf --force-ocr --optimize 0 --output-type pdf --skip-text '{input_path}' '{temp_dir}/ocr.pdf'"
        print("Running OCR on PDF...")
        run_command(ocr_cmd)
        
        # Check if OCR succeeded
        if os.path.exists(f"{temp_dir}/ocr.pdf"):
            print("OCR successful!")
            input_path = f"{temp_dir}/ocr.pdf"
        else:
            print("OCR failed, continuing with original PDF")
        
        # Use open source tools to attempt adding proper structure
        # First, create a simple HTML version with headers and paragraphs
        print("Converting PDF to HTML to extract structure...")
        html_path = f"{temp_dir}/out.html"
        run_command(f"pdftohtml -c -i -enc UTF-8 '{input_path}' '{html_path}'")
        
        # Next, convert back to PDF with structural tags
        if os.path.exists(html_path):
            print("Converting HTML to tagged PDF...")
            run_command(f"prince '{html_path}' -o '{temp_dir}/tagged.pdf'")
            
            if os.path.exists(f"{temp_dir}/tagged.pdf"):
                print("Successfully created tagged PDF!")
                run_command(f"cp '{temp_dir}/tagged.pdf' '{output_path}'")
                print(f"Tagged PDF saved to: {output_path}")
                return True
        
        print("Could not create tagged PDF with available tools")
        print("Here are other approaches you can try:")
        print("1. Use Adobe Acrobat Pro's 'Accessibility > Add Tags to Document' feature")
        print("2. Use axesPDF for automated tagging")
        print("3. Use PAC (PDF Accessibility Checker) to verify and fix issues")
        print("\nFor this PDF, manual tagging in Acrobat Pro may be necessary due to the complex structure")
        
        # Provide instructions for manual tagging in Acrobat
        print("\nManual tagging process in Acrobat Pro:")
        print("1. Open the PDF in Acrobat Pro")
        print("2. Go to Tools > Accessibility > Autotag Document")
        print("3. Then go to Tools > Accessibility > Reading Order")
        print("4. Use the Reading Order tool to fix the structure")
        print("5. Add alt text to images via right-click > Edit Alt Text")
        print("6. Run the Accessibility Check to identify and fix remaining issues")
        
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Create a properly tagged PDF with content association')
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('output_pdf', help='Path to save output PDF file')
    parser.add_argument('--title', help='Document title')
    parser.add_argument('--author', help='Document author')
    
    args = parser.parse_args()
    
    create_tagged_pdf(args.input_pdf, args.output_pdf, args.title, args.author)

if __name__ == "__main__":
    main()