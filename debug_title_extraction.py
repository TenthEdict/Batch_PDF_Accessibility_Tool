#!/usr/bin/env python3
"""
Debug script to analyze why the first part of the CSR title is being missed.

This script will provide detailed debugging information about text extraction
and candidate filtering to understand the clustering issue.
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "processor" / "unified_project"))

import fitz  # PyMuPDF
import re

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_text_extraction():
    """Debug the text extraction to see all candidates."""
    
    test_file = project_root / "test_batch_input" / "10-1108_ccij-12-2017-0123.pdf"
    
    if not test_file.exists():
        logger.error(f"Test file not found: {test_file}")
        return
    
    print("🔍 DEBUGGING TEXT EXTRACTION FOR CSR DOCUMENT")
    print("=" * 80)
    
    # Open document
    temp_doc = fitz.open(str(test_file))
    first_page = temp_doc[0]
    page_height = first_page.rect.height
    page_width = first_page.rect.width
    
    print(f"Page dimensions: {page_width:.1f} x {page_height:.1f}")
    
    # Define spatial exclusion zones
    header_zone_limit = page_height * 0.08
    footer_zone_limit = page_height * 0.85
    
    print(f"Header zone limit: {header_zone_limit:.1f}")
    print(f"Footer zone limit: {footer_zone_limit:.1f}")
    print("=" * 80)
    
    # Journal patterns
    journal_patterns = [
        r'\bjournal\s+of\b',
        r'\bproceedings\s+of\b',
        r'\btransactions\s+on\b',
        r'\bieee\s+',
        r'\bacm\s+',
        r'\breview\s+of\b',
        r'\bannals\s+of\b',
        r'\binternational\s+(journal|conference)\b',
        r'\bsymposium\s+on\b',
        r'\bworkshop\s+on\b',
        r'\bvol\.?\s*\d+',
        r'\bissn\b',
        r'\bdoi\b',
        r'©\s*\d{4}',
        r'\binsight\s+at\b',
    ]
    
    journal_regex = re.compile('|'.join(journal_patterns), re.IGNORECASE)
    
    # Get text blocks
    blocks = first_page.get_text("dict")
    
    print("📄 ALL TEXT BLOCKS ANALYSIS:")
    print("-" * 80)
    
    all_text_spans = []
    
    for block_idx, block in enumerate(blocks.get("blocks", [])):
        if "lines" not in block:
            continue
            
        for line_idx, line in enumerate(block["lines"]):
            bbox = line.get("bbox", [0, 0, 0, 0])
            y_position = bbox[1]
            
            for span_idx, span in enumerate(line.get("spans", [])):
                text = span.get("text", "").strip()
                font_size = span.get("size", 0)
                font_flags = span.get("flags", 0)
                span_bbox = span.get("bbox", [0, 0, 0, 0])
                x_position = span_bbox[0]
                
                if text:  # Any text, regardless of filtering
                    all_text_spans.append({
                        'text': text,
                        'font_size': font_size,
                        'font_flags': font_flags,
                        'y_position': y_position,
                        'x_position': x_position,
                        'bbox': span_bbox,
                        'block_idx': block_idx,
                        'line_idx': line_idx,
                        'span_idx': span_idx
                    })
    
    # Sort by Y position to analyze top-down
    all_text_spans.sort(key=lambda x: x['y_position'])
    
    print("📋 ALL TEXT SPANS (Top to Bottom):")
    print("-" * 80)
    
    for i, span in enumerate(all_text_spans[:15]):  # Show first 15 spans
        y_pos = span['y_position']
        font_size = span['font_size']
        text = span['text']
        
        # Check zones
        in_header = y_pos < header_zone_limit
        in_footer = y_pos > footer_zone_limit
        in_content = not in_header and not in_footer
        
        zone_status = "HEADER" if in_header else "FOOTER" if in_footer else "CONTENT"
        
        # Check if it's journal pattern
        is_journal = bool(journal_regex.search(text))
        journal_status = " [JOURNAL]" if is_journal else ""
        
        print(f"{i:2d}. Y:{y_pos:6.1f} Font:{font_size:4.1f} [{zone_status:7s}]{journal_status}")
        print(f"    Text: '{text}'")
        print()
    
    print("=" * 80)
    print("🎯 LOOKING FOR 'Employees' TEXT:")
    print("-" * 80)
    
    employees_spans = [span for span in all_text_spans if 'employees' in span['text'].lower()]
    
    if employees_spans:
        for span in employees_spans:
            y_pos = span['y_position']
            font_size = span['font_size']
            text = span['text']
            
            in_header = y_pos < header_zone_limit
            in_footer = y_pos > footer_zone_limit
            in_content = not in_header and not in_footer
            
            zone_status = "HEADER" if in_header else "FOOTER" if in_footer else "CONTENT"
            
            print(f"FOUND 'Employees': Y:{y_pos:6.1f} Font:{font_size:4.1f} [{zone_status}]")
            print(f"Text: '{text}'")
            print(f"Bbox: {span['bbox']}")
            print()
    else:
        print("❌ No text containing 'employees' found!")
    
    print("=" * 80)
    print("🎯 LOOKING FOR TITLE-LIKE TEXT:")
    print("-" * 80)
    
    # Filter for title-like characteristics
    title_like_spans = []
    
    for span in all_text_spans:
        text = span['text']
        font_size = span['font_size']
        y_position = span['y_position']
        
        # Apply basic title filtering
        if (text and 
            len(text) > 3 and
            font_size > 10 and
            y_position >= header_zone_limit and
            y_position <= footer_zone_limit and
            not any(char.isdigit() for char in text[:3])):
            title_like_spans.append(span)
    
    print(f"Found {len(title_like_spans)} title-like spans:")
    print("-" * 80)
    
    for i, span in enumerate(title_like_spans[:10]):  # Show first 10
        y_pos = span['y_position']
        font_size = span['font_size']
        text = span['text']
        
        is_journal = bool(journal_regex.search(text))
        journal_status = " [JOURNAL]" if is_journal else ""
        
        print(f"{i:2d}. Y:{y_pos:6.1f} Font:{font_size:4.1f}{journal_status}")
        print(f"    Text: '{text}'")
        print()
    
    temp_doc.close()

if __name__ == "__main__":
    debug_text_extraction()
