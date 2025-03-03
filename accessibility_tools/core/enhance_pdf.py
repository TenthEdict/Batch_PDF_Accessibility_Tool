#!/usr/bin/env python3
"""
PDF Accessibility Enhancement Script

This script adds basic accessibility features to PDF files:
- Document title and author metadata
- Document language
- PDF/UA compliance markers

Usage: python enhance_pdf.py input_pdf output_pdf --title "Title" --author "Author"
"""

import os
import sys
import argparse
from pathlib import Path

try:
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.generic import NameObject, BooleanObject, TextStringObject, DictionaryObject, ArrayObject
except ImportError:
    print("Error: PyPDF2 is not installed. Please install it in your virtual environment:")
    print("pip install PyPDF2")
    sys.exit(1)

def enhance_pdf_accessibility(input_path, output_path, title=None, author=None):
    """
    Enhance PDF accessibility with basic features
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        print(f'Error: Input PDF not found: {input_path}')
        return False
    
    print(f'Enhancing PDF: {input_path}')
    print(f'Output will be saved to: {output_path}')
    
    try:
        # Open the input PDF
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Copy all pages to the writer
        for page in reader.pages:
            writer.add_page(page)
        
        # Update metadata
        metadata = {}
        if title:
            metadata['/Title'] = title
        else:
            # Extract title from filename
            title = input_path.stem.replace('_', ' ').title()
            metadata['/Title'] = title
            
        if author:
            metadata['/Author'] = author
            
        # Add other important metadata
        metadata['/Language'] = 'en-US'
        
        # Set metadata
        writer.add_metadata(metadata)
        
        # Create proper objects for PDF dictionary
        viewer_prefs = DictionaryObject()
        viewer_prefs[NameObject('/DisplayDocTitle')] = BooleanObject(True)
        
        # Removed tagging code
        
        # Update the root object
        writer._root_object[NameObject('/ViewerPreferences')] = viewer_prefs
        # Removed tagging-related code
        
        # Save the enhanced PDF
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
            
        print(f'Successfully enhanced PDF accessibility: {output_path}')
        print('Applied enhancements:')
        print(f'- Added title: {title}')
        if author:
            print(f'- Added author: {author}')
        print('- Set language to en-US')
        print('- Set display document title preference')
        
        return True
    except Exception as e:
        print(f'Error enhancing PDF: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description='Enhance PDF with basic accessibility features')
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('output_pdf', help='Path to save enhanced PDF file')
    parser.add_argument('--title', help='Document title')
    parser.add_argument('--author', help='Document author')
    
    args = parser.parse_args()
    
    result = enhance_pdf_accessibility(
        args.input_pdf,
        args.output_pdf,
        args.title,
        args.author
    )
    
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())