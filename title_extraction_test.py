#!/usr/bin/env python3
"""
Title Extraction Diagnostic Script

This script tests the title extraction functionality in isolation
to diagnose why it might be defaulting to filename instead of
extracting actual document titles.
"""

import sys
import logging
from pathlib import Path

# Add the project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "processor" / "unified_project" / "src"))

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

import pikepdf
from enhancers.minimal_pdf_enhancer import MinimalPDFEnhancer

def test_title_extraction(pdf_path: str):
    """Test title extraction on a specific PDF file."""
    print(f"\n{'='*60}")
    print(f"TESTING TITLE EXTRACTION: {pdf_path}")
    print(f"{'='*60}")
    
    try:
        # Load the PDF
        pdf_path = Path(pdf_path)
        print(f"Loading PDF: {pdf_path}")
        
        with pikepdf.open(pdf_path) as doc:
            print(f"PDF loaded successfully. Pages: {len(doc.pages)}")
            
            # Create enhancer and test title extraction
            enhancer = MinimalPDFEnhancer()
            
            print(f"\nTesting _extract_document_title method...")
            extracted_title = enhancer._extract_document_title(doc, pdf_path)
            
            print(f"\n{'='*40}")
            print(f"RESULT:")
            print(f"{'='*40}")
            if extracted_title:
                print(f"✅ Successfully extracted title: '{extracted_title}'")
            else:
                print(f"❌ Title extraction failed - would fall back to filename")
                
            # Show what filename fallback would be
            filename_fallback = pdf_path.stem.replace("_", " ").replace("-", " ").title().strip()
            print(f"📁 Filename fallback would be: '{filename_fallback}'")
            
            # Test existing metadata
            print(f"\n📋 Checking existing PDF metadata...")
            try:
                with doc.open_metadata() as meta:
                    existing_title = meta.get("dc:title") or doc.docinfo.get("/Title")
                    if existing_title:
                        print(f"📄 Existing PDF title metadata: '{existing_title}'")
                    else:
                        print(f"📄 No existing title metadata found")
            except Exception as e:
                print(f"📄 Could not read metadata: {e}")
                
    except Exception as e:
        print(f"❌ Error testing file: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run title extraction tests on available PDF files."""
    
    # Test files to check
    test_files = [
        "data/batch_test_input/10-1108_01435121011046326.pdf",
        "data/batch_test_input/2371-LibraryFall2024Pre10_BroderickSchipp_Profile.pdf", 
        "data/input/1860_roadschool_1925_proceedings.pdf"
    ]
    
    print("TITLE EXTRACTION DIAGNOSTIC TEST")
    print("This script tests the title extraction functionality to diagnose issues.")
    
    for test_file in test_files:
        test_path = project_root / test_file
        if test_path.exists():
            test_title_extraction(test_path)
        else:
            print(f"⚠️  File not found: {test_path}")
    
    print(f"\n{'='*60}")
    print("DIAGNOSTIC COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
