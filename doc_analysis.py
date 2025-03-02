#!/usr/bin/env python3
"""
PDF Accessibility Analysis Tool
This script provides a summary of accessibility features for a PDF
"""

import os
import sys
import subprocess
from pathlib import Path


def run_cmd(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"


def check_pdf_file(pdf_path):
    """Perform basic PDF accessibility checks"""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"Error: File {pdf_path} does not exist")
        return
        
    print(f"Analyzing PDF: {pdf_path}")
    print(f"File size: {pdf_path.stat().st_size / (1024*1024):.2f} MB")
    
    # Check basic PDF info
    pdf_info = run_cmd(f"pdfinfo {pdf_path}")
    
    print("\n=== PDF METADATA ===")
    print(pdf_info)
    
    # Extract key info from pdfinfo output
    is_tagged = "Tagged: yes" in pdf_info
    
    # Check for structured tags (for accessibility)
    try:
        # Look for structure elements in the PDF
        tagged_check = run_cmd(f"strings {pdf_path} | grep -c '/StructElem'")
        struct_tree_check = run_cmd(f"strings {pdf_path} | grep -c '/StructTreeRoot'")
        
        has_structure = int(tagged_check) > 0 or int(struct_tree_check) > 0
    except:
        has_structure = False
    
    # Check for alt text
    try:
        alt_text_check = run_cmd(f"strings {pdf_path} | grep -c '/Alt'")
        has_alt_text = int(alt_text_check) > 0
    except:
        has_alt_text = False
    
    # Check for language metadata
    try:
        lang_check = run_cmd(f"strings {pdf_path} | grep -c '/Lang'")
        has_language = int(lang_check) > 0
    except:
        has_language = False
    
    # Check for PDF/UA marker
    try:
        ua_check = run_cmd(f"strings {pdf_path} | grep -c 'PDF/UA'")
        is_pdfua = int(ua_check) > 0
    except:
        is_pdfua = False
    
    # Output accessibility features
    print("\n=== ACCESSIBILITY FEATURES ===")
    print(f"Tagged PDF: {'Yes' if is_tagged else 'No'}")
    print(f"Structure elements: {'Yes' if has_structure else 'No'}")
    print(f"Alt text: {'Yes' if has_alt_text else 'No'}")
    print(f"Language specified: {'Yes' if has_language else 'No'}")
    print(f"PDF/UA compliant: {'Yes' if is_pdfua else 'No'}")
    
    # Calculate accessibility score
    score = 0
    max_score = 5
    
    if is_tagged: score += 1
    if has_structure: score += 1
    if has_alt_text: score += 1
    if has_language: score += 1
    if is_pdfua: score += 1
    
    score_percentage = (score / max_score) * 100
    
    # Output final assessment
    print("\n=== ACCESSIBILITY ASSESSMENT ===")
    print(f"Accessibility score: {score}/{max_score} ({score_percentage:.0f}%)")
    
    if score_percentage >= 80:
        print("🟢 Good: This PDF appears to have good accessibility features")
    elif score_percentage >= 40:
        print("🟡 Fair: This PDF has some accessibility features but needs improvement")
    else:
        print("🔴 Poor: This PDF lacks essential accessibility features")
    
    # Recommendations
    print("\n=== RECOMMENDATIONS ===")
    if not is_tagged:
        print("- Add document tagging")
    if not has_structure:
        print("- Add structural elements for screen readers")
    if not has_alt_text:
        print("- Add alternative text for images and graphics")
    if not has_language:
        print("- Specify document language")
    if not is_pdfua:
        print("- Update to PDF/UA standard for better accessibility")
    
    print("\nNote: This is a basic analysis. For more comprehensive accessibility")
    print("evaluation, use the project's full accessibility checker with OCR and")
    print("AI analysis capabilities or specialized tools like PAC.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python doc_analysis.py <path_to_pdf>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    check_pdf_file(pdf_path)