#!/usr/bin/env python3
"""
Script to add more comprehensive document structure to a PDF file
using PyPDF2.
"""

import os
import sys
import argparse
from pathlib import Path

try:
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.generic import (
        NameObject, BooleanObject, TextStringObject, 
        DictionaryObject, ArrayObject, NumberObject
    )
except ImportError:
    print("Error: PyPDF2 is not installed")
    print("Please install with: pip install PyPDF2")
    sys.exit(1)

def add_document_structure(input_path, output_path):
    """
    Add document structure to a PDF
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        print(f"Error: Input PDF not found: {input_path}")
        return False
    
    print(f"Adding document structure to: {input_path}")
    print(f"Output will be saved to: {output_path}")
    
    try:
        # Read input PDF
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Copy all pages to the writer
        for page in reader.pages:
            writer.add_page(page)
        
        # Copy metadata from input to output
        if hasattr(reader, 'metadata') and reader.metadata is not None:
            writer.add_metadata(reader.metadata)
        
        # Create structure tree root
        struct_tree_root = DictionaryObject()
        struct_tree_root[NameObject('/Type')] = NameObject('/StructTreeRoot')
        
        # Create parent tree
        parent_tree = DictionaryObject()
        parent_tree[NameObject('/Nums')] = ArrayObject()
        struct_tree_root[NameObject('/ParentTree')] = parent_tree
        
        # Create document root element (document)
        document_elem = DictionaryObject()
        document_elem[NameObject('/Type')] = NameObject('/StructElem')
        document_elem[NameObject('/S')] = NameObject('/Document')
                
        # Create children array for document element
        document_elem[NameObject('/K')] = ArrayObject([NumberObject(1)])
        
        # Add document element to structure tree root
        struct_tree_root[NameObject('/K')] = document_elem
        
        # Create role map
        role_map = DictionaryObject()
        struct_tree_root[NameObject('/RoleMap')] = role_map
        
        # Set structure tree root in document
        writer._root_object[NameObject('/StructTreeRoot')] = struct_tree_root
        
        # Mark document as tagged if not already
        if NameObject('/MarkInfo') not in writer._root_object:
            mark_info = DictionaryObject()
            mark_info[NameObject('/Marked')] = BooleanObject(True)
            writer._root_object[NameObject('/MarkInfo')] = mark_info
        
        # Save the enhanced PDF
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
            
        print(f"Successfully added document structure: {output_path}")
        return True
    except Exception as e:
        print(f"Error adding document structure: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description='Add document structure to a PDF')
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('output_pdf', nargs='?', help='Path to save output PDF file')
    
    args = parser.parse_args()
    
    input_path = args.input_pdf
    
    if args.output_pdf:
        output_path = args.output_pdf
    else:
        # Create default output path if not provided
        input_path_obj = Path(input_path)
        output_path = input_path_obj.parent / f"{input_path_obj.stem}_structured{input_path_obj.suffix}"
    
    result = add_document_structure(input_path, output_path)
    
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())