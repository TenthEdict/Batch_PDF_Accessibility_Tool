#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
import time
import asyncio

# Add project to path
sys.path.append(str(Path(__file__).parent / 'brodie_code'))
sys.path.append(str(Path(__file__).parent / 'brodie_code/src'))

try:
    from accessibility_checker.core.anthropic_processor import create_enhanced_processor
    from accessibility_checker.utils.anthropic_client import AnthropicClient
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure to run this script from the project root directory")
    sys.exit(1)

async def analyze_single_pdf(pdf_path):
    """Analyze a single PDF file and output accessibility assessment."""
    start_time = time.time()
    pdf_path = Path(pdf_path).resolve()
    
    if not pdf_path.exists():
        print(f"Error: File {pdf_path} does not exist")
        return
    
    print(f"Analyzing {pdf_path.name}...")
    
    # Get API key from environment or use a fallback value for testing
    api_key = os.environ.get('ANTHROPIC_API_KEY') or "fallback_for_testing"
    
    try:
        # Create processor without making API calls
        processor = create_enhanced_processor(str(pdf_path), api_key=api_key)
        
        # Basic document analysis
        processor.extract_text_with_positions()
        processor.detect_headings()
        processor.detect_tables() 
        processor.analyze_reading_order()
        
        # Print basic statistics
        print("\n=== ACCESSIBILITY ANALYSIS ===")
        print(f"PDF Pages: {len(processor.doc)}")
        print(f"Text elements extracted: {len(processor.text_elements)}")
        
        # Heading hierarchy
        headings = {}
        for elem in processor.text_elements:
            if elem.heading_level is not None:
                headings[elem.heading_level] = headings.get(elem.heading_level, 0) + 1
        
        print("\n=== HEADING STRUCTURE ===")
        for level in sorted(headings.keys()):
            print(f"H{level}: {headings[level]} occurrences")
        
        if not headings:
            print("WARNING: No headings detected in the document")
        elif 1 not in headings:
            print("WARNING: No H1 headings found - document may lack proper structure")
        
        # Table analysis
        print(f"\n=== TABLE STRUCTURE ===")
        print(f"Tables detected: {len(processor.tables)}")
        for i, table in enumerate(processor.tables):
            print(f"Table {i+1}: {table.get('rows', '?')}×{table.get('columns', '?')} cells")
        
        # Check reading order
        print("\n=== READING ORDER ===")
        if processor.reading_order_violations:
            print(f"Reading order issues: {len(processor.reading_order_violations)}")
            for violation in processor.reading_order_violations[:5]:  # Show first 5
                print(f"- {violation}")
            if len(processor.reading_order_violations) > 5:
                print(f"  ...and {len(processor.reading_order_violations) - 5} more issues")
        else:
            print("No reading order issues detected")
        
        # Accessibility violations
        print("\n=== ACCESSIBILITY COMPLIANCE ===")
        if processor.violations:
            print(f"Violations detected: {len(processor.violations)}")
            for i, violation in enumerate(processor.violations[:5]):  # Show first 5
                print(f"- {violation.type}: {violation.description}")
            if len(processor.violations) > 5:
                print(f"  ...and {len(processor.violations) - 5} more violations")
        else:
            print("No accessibility violations detected")
            
        print("\n=== OVERALL ASSESSMENT ===")
        total_issues = len(processor.reading_order_violations) + len(processor.violations)
        
        if total_issues == 0:
            print("✅ This PDF appears to meet basic accessibility standards")
        elif total_issues < 5:
            print("⚠️ This PDF has minor accessibility issues")
        else:
            print("❌ This PDF has significant accessibility issues")
            
        print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"Error analyzing PDF: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_pdf.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    asyncio.run(analyze_single_pdf(pdf_path))