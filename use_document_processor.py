#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add the project code to path
project_root = Path(__file__).parent
sys.path.append(str(project_root / 'brodie_code'))
sys.path.append(str(project_root / 'brodie_code/src'))


def analyze_pdf_accessibility(pdf_path):
    """
    Analyze PDF using the project's document processor
    """
    try:
        # Try to import the document processor
        from accessibility_checker.core.document import AccessibilityDocumentProcessor
        
        print(f"Analyzing PDF: {pdf_path}")
        
        # Create the document processor
        processor = AccessibilityDocumentProcessor(pdf_path)
        
        # Extract basic PDF information
        print("\n=== DOCUMENT PROPERTIES ===")
        print(f"Pages: {len(processor.doc)}")
        
        # Extract text elements
        processor.extract_text_with_positions()
        print(f"Text elements extracted: {len(processor.text_elements)}")
        
        # Detect headings
        processor.detect_headings()
        headings = {}
        for elem in processor.text_elements:
            if elem.heading_level is not None:
                headings[elem.heading_level] = headings.get(elem.heading_level, 0) + 1
        
        print("\n=== HEADING STRUCTURE ===")
        if headings:
            for level in sorted(headings.keys()):
                print(f"H{level}: {headings[level]} occurrences")
        else:
            print("No headings detected")
        
        # Detect tables
        processor.detect_tables()
        print(f"\n=== TABLE STRUCTURE ===")
        print(f"Tables detected: {len(processor.tables)}")
        
        # Reading order analysis
        processor.analyze_reading_order()
        print("\n=== READING ORDER ===")
        if processor.reading_order_violations:
            print(f"Reading order issues: {len(processor.reading_order_violations)}")
            for i, violation in enumerate(processor.reading_order_violations[:3]):
                print(f"- {violation}")
            if len(processor.reading_order_violations) > 3:
                print(f"  ...and {len(processor.reading_order_violations) - 3} more")
        else:
            print("No reading order issues detected")
        
        # Overall assessment
        print("\n=== ACCESSIBILITY ASSESSMENT ===")
        issues = len(processor.reading_order_violations)
        
        if len(headings) == 0:
            print("⚠️ Document lacks proper heading structure")
            issues += 1
        
        if issues == 0:
            print("✅ Basic accessibility checks passed")
        else:
            print(f"❌ {issues} accessibility issues detected")
        
        # Recommendations
        print("\n=== RECOMMENDATIONS ===")
        if len(headings) == 0:
            print("- Add proper heading structure with H1, H2, etc.")
        if 1 not in headings:
            print("- Add H1 heading(s) for document title/main sections")
        if processor.reading_order_violations:
            print("- Fix reading order issues")
        print("- Ensure all images have alt text")
        print("- Review table structures for accessibility")
        
    except ImportError as e:
        print(f"Error: Could not import required modules: {e}")
        print("Make sure you're running this script from the project root directory")
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python use_document_processor.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    analyze_pdf_accessibility(pdf_path)