#!/usr/bin/env python3
"""Test script to reproduce OCR error with full traceback"""

import sys
import traceback
import logging

# Detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')

sys.path.insert(0, '/Users/broderickschipp/work/ePubs_Main')

try:
    from processor.unified_project.src.enhancers.intelligent_ocr_enhancer import IntelligentOCREnhancer
    
    print("=== Testing OCR Processing ===\n")
    
    # Initialize OCR enhancer
    print("1. Initializing IntelligentOCREnhancer...")
    ocr_enhancer = IntelligentOCREnhancer(component_name="test_ocr")
    print("   ✓ OCR enhancer initialized\n")
    
    # Test OCR on PDF
    test_pdf = "/Users/broderickschipp/work/ePubs_Main/data/input/Ahmed et al. - 2025 - Using thematic analysis in qualitative research.pdf"
    print(f"2. Running OCR on: {test_pdf}")
    
    result = ocr_enhancer.process_pdf_with_ocr(test_pdf)
    
    print(f"   ✓ OCR complete")
    print(f"   Success: {result.success}")
    print(f"   Text length: {len(result.text_content)}")
    print(f"   Confidence: {result.confidence_score}")
    
    print("\n=== SUCCESS: No errors encountered ===")
    
except Exception as e:
    print(f"\n=== ERROR ENCOUNTERED ===")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}\n")
    print("Full traceback:")
    traceback.print_exc()
