#!/usr/bin/env python3
"""
PDF Accessibility Enhancer

This script improves PDF accessibility by:
1. Adding document tags
2. Setting document language
3. Setting initial view to document title
4. Adding PDF/UA compliance metadata
5. Implementing basic document structure (for screen readers)

Usage: python enhance_accessibility.py <input_pdf> <output_pdf> [--title "Document Title"] [--author "Author Name"]
"""

import os
import sys
import argparse
from pathlib import Path
import pikepdf
import pandas as pd
import re

def extract_title_from_filename(filename):
    """Extract a title from the filename"""
    # Remove extension and replace underscores/hyphens with spaces
    basename = os.path.splitext(os.path.basename(filename))[0]
    title = re.sub(r'[_-]', ' ', basename)
    # Remove date patterns like 1963
    title = re.sub(r'\d{4}', '', title)
    # Remove 'testing' or 'V1' patterns
    title = re.sub(r'testing|V\d+', '', title)
    # Clean up multiple spaces and strip
    title = re.sub(r'\s+', ' ', title).strip()
    # Capitalize words
    title = title.title()
    return title

def update_metadata(pdf_path, output_path, title=None, authors=None):
    """Update PDF metadata with title and authors"""
    if title is None:
        title = extract_title_from_filename(pdf_path)
    
    if authors is None:
        authors = ""
    
    if isinstance(authors, str):
        authors = [authors]
    
    print(f"Updating metadata:")
    print(f"Title: {title}")
    print(f"Authors: {', '.join(authors)}")

    with pikepdf.open(pdf_path) as pdf:
        # Update classic metadata dictionary
        docinfo = pdf.docinfo
        docinfo['/Title'] = title
        docinfo['/Author'] = "; ".join(authors)

        # Create XMP metadata
        xmp_metadata = f"""
        <x:xmpmeta xmlns:x="adobe:ns:meta/" xmlns:dc="http://purl.org/dc/elements/1.1/">
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                <rdf:Description rdf:about=""
                    xmlns:dc="http://purl.org/dc/elements/1.1/"
                    xmlns:xmp="http://ns.adobe.com/xap/1.0/">
                    <dc:title>
                        <rdf:Alt>
                            <rdf:li xml:lang="x-default">{title}</rdf:li>
                        </rdf:Alt>
                    </dc:title>
                    <dc:creator>
                        <rdf:Seq>
                            {"".join(f"<rdf:li>{author}</rdf:li>" for author in authors)}
                        </rdf:Seq>
                    </dc:creator>
                </rdf:Description>
            </rdf:RDF>
        </x:xmpmeta>
        """
        # Embed the XMP metadata
        pdf.Root.Metadata = pikepdf.Stream(pdf, xmp_metadata.encode('utf-8'))
        pdf.save(output_path)
    print(f"Metadata updated for: {output_path}")
    return output_path

def set_pdf_language(pdf_path, language="en-US"):
    """Set PDF language"""
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        pdf.Root['/Lang'] = pikepdf.String(language)
        pdf.save(pdf_path)
    print(f"Set reading language to {language}")
    return pdf_path

def set_initial_view_title(pdf_path):
    """Set initial view to show document title"""
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        if '/ViewerPreferences' not in pdf.Root:
            pdf.Root['/ViewerPreferences'] = pdf.make_indirect({})
        pdf.Root['/ViewerPreferences']['/DisplayDocTitle'] = True
        pdf.save(pdf_path)
    print("Set initial view to show document title")
    return pdf_path

def mark_pdf_as_tagged(pdf_path):
    """Mark PDF as tagged"""
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        if '/MarkInfo' not in pdf.Root:
            pdf.Root['/MarkInfo'] = pdf.make_indirect({})
        pdf.Root['/MarkInfo']['/Marked'] = True  # Indicate that the document is tagged
        
        # Create empty structure tree if it doesn't exist
        if '/StructTreeRoot' not in pdf.Root:
            pdf.Root['/StructTreeRoot'] = pdf.make_indirect({})
            pdf.Root['/StructTreeRoot']['/Type'] = '/StructTreeRoot'
            pdf.Root['/StructTreeRoot']['/ParentTree'] = pdf.make_indirect({})
            pdf.Root['/StructTreeRoot']['/ParentTree']['/Nums'] = []
            
        pdf.save(pdf_path)
    print("Marked as tagged PDF")
    return pdf_path

def append_pdfua_xmp(pdf_path, xmp_file):
    """Append PDF/UA XMP metadata"""
    if not os.path.exists(xmp_file):
        print(f"Error: The specified XMP file '{xmp_file}' does not exist.")
        return pdf_path

    # Read the XMP content
    with open(xmp_file, 'r', encoding='utf-8') as xmp:
        xmp_metadata = xmp.read()

    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        # Get existing metadata from the PDF
        existing_metadata = pdf.Root.Metadata.read_bytes().decode('utf-8') if pdf.Root.Metadata else ''

        # Parse the existing XMP to check for pdfuaid:part
        if "pdfuaid:part" in existing_metadata:
            print("PDF/UA metadata already exists, keeping existing...")
            return pdf_path

        # Combine existing metadata with the new XMP metadata
        combined_metadata = f"""
        <x:xmpmeta xmlns:x="adobe:ns:meta/" xmlns:dc="http://purl.org/dc/elements/1.1/">
            {existing_metadata}
            {xmp_metadata}
        </x:xmpmeta>
        """
        # Write the combined metadata back to the PDF
        pdf.Root.Metadata = pikepdf.Stream(pdf, combined_metadata.encode('utf-8'))
        pdf.save(pdf_path)

    print("Added PDF/UA compliance metadata")
    return pdf_path

def create_basic_structure(pdf_path):
    """Create basic document structure for accessibility"""
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        # This is simplified - real tagging is complex
        # Here we're just setting up a minimal structure
        if '/StructTreeRoot' not in pdf.Root:
            pdf.Root['/StructTreeRoot'] = pdf.make_indirect({})
        
        struct_tree = pdf.Root['/StructTreeRoot']
        struct_tree['/Type'] = '/StructTreeRoot'
        
        # Create a document element
        document = pdf.make_indirect({})
        document['/Type'] = '/StructElem'
        document['/S'] = '/Document'  # S for Structure Type
        
        # Set document as the root element
        struct_tree['/K'] = document
        
        # Add parent tree (required by PDF/UA)
        if '/ParentTree' not in struct_tree:
            struct_tree['/ParentTree'] = pdf.make_indirect({})
            struct_tree['/ParentTree']['/Nums'] = []
        
        # Create a role map (optional but good for accessibility)
        if '/RoleMap' not in struct_tree:
            struct_tree['/RoleMap'] = pdf.make_indirect({})
        
        pdf.save(pdf_path)
    
    print("Added basic document structure")
    return pdf_path

def enhance_pdf_accessibility(input_pdf, output_pdf, title=None, authors=None, xmp_file=None):
    """Enhance PDF accessibility with all available methods"""
    if not os.path.exists(input_pdf):
        print(f"Error: Input PDF '{input_pdf}' does not exist.")
        return False
    
    print(f"Enhancing accessibility for: {input_pdf}")
    print(f"Output will be saved to: {output_pdf}")
    
    # Create a copy of the input PDF first
    with pikepdf.open(input_pdf) as pdf:
        pdf.save(output_pdf)
    
    # Apply each enhancement in sequence
    try:
        output_pdf = update_metadata(output_pdf, output_pdf, title, authors)
        output_pdf = set_pdf_language(output_pdf)
        output_pdf = set_initial_view_title(output_pdf)
        output_pdf = mark_pdf_as_tagged(output_pdf)
        output_pdf = create_basic_structure(output_pdf)
        
        if xmp_file and os.path.exists(xmp_file):
            output_pdf = append_pdfua_xmp(output_pdf, xmp_file)
        else:
            print("Warning: XMP file not specified or not found. PDF/UA compliance not added.")
            
        print(f"\nAccessibility enhancements completed successfully!")
        print(f"Enhanced PDF saved to: {output_pdf}")
        return True
        
    except Exception as e:
        print(f"Error enhancing PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description='Enhance PDF accessibility')
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('output_pdf', help='Path to save enhanced PDF file')
    parser.add_argument('--title', help='Document title')
    parser.add_argument('--author', help='Document author')
    parser.add_argument('--xmp', help='Path to PDF/UA XMP file', 
                        default='/Users/broderickschipp/work/ePubs_AccProj/brodie_code/pdfUA-ID.xmp')
    
    args = parser.parse_args()
    
    enhance_pdf_accessibility(
        args.input_pdf, 
        args.output_pdf,
        args.title,
        [args.author] if args.author else None,
        args.xmp
    )

if __name__ == "__main__":
    main()