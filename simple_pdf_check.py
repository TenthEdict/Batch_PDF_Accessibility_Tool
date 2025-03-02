#!/usr/bin/env python3
import sys
import os
import subprocess

def check_pdf_accessibility(pdf_path):
    """Check basic PDF properties using pdfinfo (if available)"""
    print(f"Analyzing PDF: {pdf_path}")
    
    # Check if file exists
    if not os.path.isfile(pdf_path):
        print(f"Error: File {pdf_path} does not exist")
        return
    
    # Try to use pdfinfo if available
    try:
        result = subprocess.run(['pdfinfo', pdf_path], 
                               capture_output=True, 
                               text=True)
        if result.returncode == 0:
            print("\n=== PDF METADATA ===")
            print(result.stdout)
        else:
            print("Error running pdfinfo")
    except FileNotFoundError:
        print("pdfinfo not available - install poppler-utils for more detailed analysis")
    
    # Check PDF/UA status
    try:
        # Simple grep to check for PDF/UA marker
        result = subprocess.run(['strings', pdf_path], 
                               capture_output=True, 
                               text=True)
        
        if "PDF/UA" in result.stdout:
            print("✓ PDF/UA detected - Document includes PDF/UA compliance marker")
        else:
            print("✗ PDF/UA not detected - Document doesn't appear to be PDF/UA compliant")
            
        # Check for tagged PDF
        if "/StructTreeRoot" in result.stdout:
            print("✓ Tagged PDF detected - Document includes structural tags")
        else:
            print("✗ Tagged PDF not detected - Document doesn't appear to have proper structure tags")
        
        # Check for alt text
        if "/Alt" in result.stdout:
            print("✓ Alt text detected - Document includes alternative text for images")
        else:
            print("✗ Alt text not detected - Images may not have alternative text")
            
    except FileNotFoundError:
        print("strings command not available")
    
    print("\nNote: This is a basic analysis. For comprehensive accessibility checking,")
    print("use specialized tools like PAC (PDF Accessibility Checker) or the project's")
    print("dedicated analysis pipeline.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python simple_pdf_check.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    check_pdf_accessibility(pdf_path)