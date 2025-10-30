#!/usr/bin/env python3
"""Test script to reproduce the mathematical elements error with full traceback"""

import sys
import traceback
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s'
)

# Add project to path
sys.path.insert(0, '/Users/broderickschipp/work/ePubs_Main')

try:
    from processor.unified_project.src.academic.mathematical_notation_detector import MathematicalNotationDetector
    from processor.unified_project.src.academic.equation_boundary_extractor import EquationBoundaryExtractor
    
    print("=== Testing Mathematical Elements Pipeline ===\n")
    
    # Initialize detector
    print("1. Initializing MathematicalNotationDetector...")
    math_detector = MathematicalNotationDetector(
        detection_threshold=0.7,
        min_element_area=100,
        max_element_area=50000,
        enable_monitoring=False
    )
    print("   ✓ Detector initialized\n")
    
    # Test detection
    test_pdf = "/Users/broderickschipp/work/ePubs_Main/data/input/Ahmed et al. - 2025 - Using thematic analysis in qualitative research.pdf"
    print(f"2. Running detection on: {test_pdf}")
    detection_result = math_detector.detect_mathematical_notation(test_pdf)
    print(f"   ✓ Detection complete")
    print(f"   Type: {type(detection_result)}")
    print(f"   Has mathematical_elements: {hasattr(detection_result, 'mathematical_elements')}")
    if hasattr(detection_result, 'mathematical_elements'):
        print(f"   Elements found: {len(detection_result.mathematical_elements)}\n")
    else:
        print(f"   ERROR: detection_result is {detection_result}\n")
    
    # Initialize boundary extractor
    print("3. Initializing EquationBoundaryExtractor...")
    boundary_extractor = EquationBoundaryExtractor(
        boundary_precision=0.7,
        context_expansion_ratio=0.15,
        enable_faiss_similarity=False,  # Disable FAISS to isolate error
        enable_monitoring=False
    )
    print("   ✓ Extractor initialized\n")
    
    # Test boundary extraction
    print("4. Running boundary extraction...")
    print(f"   Passing: {type(detection_result)}")
    boundary_result = boundary_extractor.extract_equation_boundaries(detection_result)
    print(f"   ✓ Extraction complete")
    print(f"   Boundaries found: {len(boundary_result.equation_boundaries)}\n")
    
    print("=== SUCCESS: No errors encountered ===")
    
except Exception as e:
    print(f"\n=== ERROR ENCOUNTERED ===")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}\n")
    print("Full traceback:")
    traceback.print_exc()
