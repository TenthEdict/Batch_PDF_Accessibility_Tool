#!/usr/bin/env python3
"""
Test script for enhanced cluster-first title extraction algorithm.

This script validates the improved title extraction on the CSR document
and compares results between old and new algorithms.
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "processor" / "unified_project"))

from src.enhancers.minimal_pdf_enhancer import MinimalPDFEnhancer
from src.enhancers.pdf_enhancer import PDFEnhancer
import pikepdf

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_title_extraction_on_csr_document():
    """Test the enhanced title extraction on the CSR document."""
    
    # Test file path
    test_file = project_root / "test_batch_input" / "10-1108_ccij-12-2017-0123.pdf"
    
    if not test_file.exists():
        logger.error(f"Test file not found: {test_file}")
        return
    
    logger.info(f"Testing enhanced title extraction on: {test_file.name}")
    logger.info("=" * 80)
    
    # Expected title (visible in the image)
    expected_title = "Employees' perceived benefits from participating in CSR activities and implications for increasing employees engagement in CSR"
    
    print(f"Expected title: {expected_title}")
    print("=" * 80)
    
    # Test with MinimalPDFEnhancer
    print("\n🔍 Testing MinimalPDFEnhancer:")
    print("-" * 40)
    
    try:
        enhancer = MinimalPDFEnhancer()
        document = pikepdf.open(str(test_file))
        
        extracted_title = enhancer._extract_document_title(document, test_file)
        document.close()
        
        print(f"✅ Extracted title: {extracted_title}")
        
        # Check if we got the complete title
        if extracted_title and "Employees'" in extracted_title and "CSR activities" in extracted_title:
            print("✅ SUCCESS: Complete title extracted including first part!")
        elif extracted_title and "CSR" in extracted_title:
            print("⚠️  PARTIAL: Title extracted but missing first part")
        else:
            print("❌ FAILED: No valid title extracted")
            
    except Exception as e:
        print(f"❌ ERROR in MinimalPDFEnhancer: {e}")
    
    # Test with PDFEnhancer
    print("\n🔍 Testing PDFEnhancer:")
    print("-" * 40)
    
    try:
        enhancer = PDFEnhancer()
        document = pikepdf.open(str(test_file))
        
        extracted_title = enhancer._extract_document_title_advanced(document, test_file)
        document.close()
        
        print(f"✅ Extracted title: {extracted_title}")
        
        # Check if we got the complete title
        if extracted_title and "Employees'" in extracted_title and "CSR activities" in extracted_title:
            print("✅ SUCCESS: Complete title extracted including first part!")
        elif extracted_title and "CSR" in extracted_title:
            print("⚠️  PARTIAL: Title extracted but missing first part")
        else:
            print("❌ FAILED: No valid title extracted")
            
    except Exception as e:
        print(f"❌ ERROR in PDFEnhancer: {e}")

def test_additional_documents():
    """Test on additional documents to ensure robustness."""
    
    test_dir = project_root / "test_batch_input"
    
    if not test_dir.exists():
        logger.info("No test_batch_input directory found")
        return
    
    pdf_files = list(test_dir.glob("*.pdf"))
    
    if len(pdf_files) <= 1:
        logger.info("Only one test file found, skipping additional tests")
        return
    
    print("\n" + "=" * 80)
    print("🔍 Testing on additional documents:")
    print("=" * 80)
    
    enhancer = MinimalPDFEnhancer()
    
    for pdf_file in pdf_files[:3]:  # Test first 3 files
        if "0123" in pdf_file.name:  # Skip the CSR document (already tested)
            continue
            
        print(f"\n📄 Testing: {pdf_file.name}")
        print("-" * 60)
        
        try:
            document = pikepdf.open(str(pdf_file))
            extracted_title = enhancer._extract_document_title(document, pdf_file)
            document.close()
            
            if extracted_title:
                print(f"✅ Extracted: {extracted_title[:100]}...")
            else:
                print("⚠️  No title extracted")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

def main():
    """Main test function."""
    print("🚀 Enhanced Cluster-First Title Extraction Test")
    print("=" * 80)
    print("Testing the improved algorithm that addresses multi-line title detection")
    print("Key improvements:")
    print("- Cluster candidates by proximity first")
    print("- Assemble complete titles before scoring")
    print("- Enhanced multi-line detection")
    print("- Better spatial filtering")
    print("=" * 80)
    
    # Test on the specific CSR document
    test_title_extraction_on_csr_document()
    
    # Test on additional documents for robustness
    test_additional_documents()
    
    print("\n" + "=" * 80)
    print("✅ Testing completed!")
    print("If the CSR document now shows 'SUCCESS: Complete title extracted',")
    print("the cluster-first algorithm has resolved the multi-line title issue.")
    print("=" * 80)

if __name__ == "__main__":
    main()
