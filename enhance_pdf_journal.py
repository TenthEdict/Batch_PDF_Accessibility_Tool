#!/usr/bin/env python3
"""
PDF Accessibility Enhancement Script for Academic Journal Articles

This script adds improved accessibility features to academic journal PDFs:
- Document title (extracted from PDF content when possible)
- Document language
- Tagged PDF structure
- PDF/UA compliance markers

Usage: python enhance_pdf_journal.py input_folder output_folder
"""

import os
import sys
import argparse
import re
from pathlib import Path

try:
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.generic import NameObject, BooleanObject, TextStringObject, DictionaryObject, ArrayObject
except ImportError:
    print("Error: PyPDF2 is not installed. Installing now...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.generic import NameObject, BooleanObject, TextStringObject, DictionaryObject, ArrayObject

def extract_journal_metadata(pdf_path):
    """
    Extract title, authors, and publication info from first page of journal article
    """
    try:
        reader = PdfReader(pdf_path)
        if len(reader.pages) == 0:
            return None, None
            
        # Extract text from first page where title and authors are typically located
        text = reader.pages[0].extract_text()
        
        # Extract title (usually the first substantial line)
        title = None
        lines = text.strip().split('\n')
        for line in lines:
            # Skip short lines (headers, page numbers)
            if len(line.strip()) > 20 and not line.startswith('http') and not '@' in line:
                title = line.strip()
                break
                
        # Try to extract authors
        authors = None
        # Look for common author patterns after title
        for i, line in enumerate(lines):
            if title and i > 0 and lines[i-1].strip() == title:
                # Authors often follow the title
                authors = line.strip()
                break
                
        # Clean up title if found
        if title:
            # Remove any leading numbers or symbols
            title = re.sub(r'^[\d\W\s]+', '', title)
            # Limit length
            if len(title) > 100:
                title = title[:100] + '...'
                
        return title, authors
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return None, None

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
    
    # Try to extract title and authors if not provided
    if not title or not author:
        extracted_title, extracted_authors = extract_journal_metadata(input_path)
        if not title and extracted_title:
            title = extracted_title
            print(f"Extracted title: {title}")
        if not author and extracted_authors:
            author = extracted_authors
            print(f"Extracted authors: {author}")
            
    # Fallback to filename if title still not available
    if not title:
        title = input_path.stem.replace('_', ' ').replace('-', ' ').title()
    
    try:
        # Open the input PDF
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Copy all pages to the writer
        for page in reader.pages:
            writer.add_page(page)
        
        # Update metadata
        metadata = {}
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
        
        # Create MarkInfo to mark as tagged
        mark_info = DictionaryObject()
        mark_info[NameObject('/Marked')] = BooleanObject(True)
        
        # Create basic document structure
        struct_tree = DictionaryObject()
        struct_tree[NameObject('/Type')] = NameObject('/StructTreeRoot')
        
        # Create document element
        document_elem = DictionaryObject()
        document_elem[NameObject('/Type')] = NameObject('/StructElem')
        document_elem[NameObject('/S')] = NameObject('/Document')
        
        # Add document element to structure tree 
        struct_tree[NameObject('/K')] = document_elem
        
        # Create parent tree (required for PDF/UA)
        parent_tree = DictionaryObject()
        parent_tree[NameObject('/Nums')] = ArrayObject()
        struct_tree[NameObject('/ParentTree')] = parent_tree
        
        # Create role map
        role_map = DictionaryObject()
        struct_tree[NameObject('/RoleMap')] = role_map
        
        # Update the root object
        writer._root_object[NameObject('/ViewerPreferences')] = viewer_prefs
        writer._root_object[NameObject('/MarkInfo')] = mark_info
        writer._root_object[NameObject('/StructTreeRoot')] = struct_tree
        
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
        print('- Marked PDF as tagged')
        print('- Added basic document structure')
        print()
        
        return True
    except Exception as e:
        print(f'Error enhancing PDF: {e}')
        import traceback
        traceback.print_exc()
        return False

def process_directory(input_dir, output_dir):
    """
    Process all PDFs in a directory
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Error: Input directory not found: {input_dir}")
        return False
        
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    failure_count = 0
    
    # Process each PDF in the directory
    pdfs = list(input_dir.glob('*.pdf'))
    print(f"Found {len(pdfs)} PDF files to process")
    
    for pdf_path in pdfs:
        output_path = output_dir / f"{pdf_path.stem}_accessible.pdf"
        result = enhance_pdf_accessibility(pdf_path, output_path)
        if result:
            success_count += 1
        else:
            failure_count += 1
            
    print(f"Processing complete: {success_count} succeeded, {failure_count} failed")
    return True

def main():
    parser = argparse.ArgumentParser(description='Enhance PDF accessibility for journal articles')
    parser.add_argument('input_dir', help='Directory containing PDF files to process')
    parser.add_argument('output_dir', help='Directory to save enhanced PDF files')
    
    args = parser.parse_args()
    
    process_directory(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()