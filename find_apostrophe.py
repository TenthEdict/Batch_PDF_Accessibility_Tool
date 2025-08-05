#!/usr/bin/env python3
"""
Quick script to find the apostrophe span.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "processor" / "unified_project"))

import fitz  # PyMuPDF

def find_apostrophe():
    """Find apostrophe span."""
    test_file = project_root / "test_batch_input" / "10-1108_ccij-12-2017-0123.pdf"
    
    temp_doc = fitz.open(str(test_file))
    first_page = temp_doc[0]
    
    blocks = first_page.get_text("dict")
    
    print("🔍 LOOKING FOR APOSTROPHE:")
    print("-" * 40)
    
    for block in blocks.get("blocks", []):
        if "lines" not in block:
            continue
            
        for line in block["lines"]:
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if "'" in text or "'" in text:  # Both straight and curly apostrophes
                    font_size = span.get("size", 0)
                    y_position = span.get("bbox", [0, 0, 0, 0])[1]
                    print(f"Found apostrophe: '{text}' Y:{y_position:.1f} Font:{font_size:.1f}")
    
    temp_doc.close()

if __name__ == "__main__":
    find_apostrophe()
