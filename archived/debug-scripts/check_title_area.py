#!/usr/bin/env python3
"""
Check all spans around Y:74.5 position to see title structure.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "processor" / "unified_project"))

import fitz  # PyMuPDF

def check_title_area():
    """Check all spans in title area."""
    test_file = project_root / "test_batch_input" / "10-1108_ccij-12-2017-0123.pdf"
    
    temp_doc = fitz.open(str(test_file))
    first_page = temp_doc[0]
    
    blocks = first_page.get_text("dict")
    
    title_spans = []
    
    for block in blocks.get("blocks", []):
        if "lines" not in block:
            continue
            
        for line in block["lines"]:
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                font_size = span.get("size", 0)
                y_position = span.get("bbox", [0, 0, 0, 0])[1]
                x_position = span.get("bbox", [0, 0, 0, 0])[0]
                
                # Focus on title area (Y: 70-180)
                if 70 <= y_position <= 180 and font_size > 10:
                    title_spans.append({
                        'text': text,
                        'y': y_position,
                        'x': x_position,
                        'font': font_size
                    })
    
    # Sort by Y then X position
    title_spans.sort(key=lambda s: (s['y'], s['x']))
    
    print("🔍 ALL SPANS IN TITLE AREA (Y: 70-180, Font > 10):")
    print("-" * 60)
    
    for i, span in enumerate(title_spans):
        print(f"{i:2d}. Y:{span['y']:6.1f} X:{span['x']:6.1f} Font:{span['font']:4.1f} | '{span['text']}'")
    
    temp_doc.close()

if __name__ == "__main__":
    check_title_area()
