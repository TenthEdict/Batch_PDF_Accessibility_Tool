#!/usr/bin/env python3
"""
Debug script to specifically track why "Employees'" is being filtered out.
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "processor" / "unified_project"))

import fitz  # PyMuPDF
import re
import math

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_employees_filtering():
    """Debug why 'Employees' is being filtered out."""
    
    test_file = project_root / "test_batch_input" / "10-1108_ccij-12-2017-0123.pdf"
    
    print("🔍 DEBUGGING WHY 'Employees' IS FILTERED OUT")
    print("=" * 80)
    
    # Open document
    temp_doc = fitz.open(str(test_file))
    first_page = temp_doc[0]
    page_height = first_page.rect.height
    page_width = first_page.rect.width
    
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
    
    # Step 1: Find all "Employees" text spans
    employees_spans = []
    
    for block in blocks.get("blocks", []):
        if "lines" not in block:
            continue
            
        for line in block["lines"]:
            bbox = line.get("bbox", [0, 0, 0, 0])
            y_position = bbox[1]
            
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                font_size = span.get("size", 0)
                font_flags = span.get("flags", 0)
                span_bbox = span.get("bbox", [0, 0, 0, 0])
                x_position = span_bbox[0]
                
                if "employees" in text.lower():
                    employees_spans.append({
                        'text': text,
                        'font_size': font_size,
                        'font_flags': font_flags,
                        'y_position': y_position,
                        'x_position': x_position,
                        'bbox': span_bbox
                    })
    
    print(f"Found {len(employees_spans)} spans containing 'employees':")
    print("-" * 80)
    
    for i, span in enumerate(employees_spans):
        print(f"{i+1}. Text: '{span['text']}'")
        print(f"   Y: {span['y_position']:.1f}, Font: {span['font_size']:.1f}")
        print(f"   Bbox: {span['bbox']}")
        
        # Check all filtering conditions
        print("   Filtering checks:")
        
        # Zone check
        in_header = span['y_position'] < header_zone_limit
        in_footer = span['y_position'] > footer_zone_limit
        in_content = not in_header and not in_footer
        print(f"   - Zone: {'HEADER' if in_header else 'FOOTER' if in_footer else 'CONTENT'} ✅" if in_content else f"   - Zone: {'HEADER' if in_header else 'FOOTER'} ❌")
        
        # Length check
        length_ok = len(span['text']) > 5 and len(span['text']) < 400
        print(f"   - Length: {len(span['text'])} {'✅' if length_ok else '❌'}")
        
        # Font size check
        font_ok = span['font_size'] > 11
        print(f"   - Font size: {span['font_size']:.1f} {'✅' if font_ok else '❌'}")
        
        # Word count check
        word_count = span['text'].count(' ') + 1
        words_ok = span['text'].count(' ') >= 1
        print(f"   - Word count: {word_count} words {'✅' if words_ok else '❌'}")
        
        # Journal pattern check
        is_journal = bool(journal_regex.search(span['text']))
        print(f"   - Journal pattern: {'YES ❌' if is_journal else 'NO ✅'}")
        
        # Candidate score calculation
        if in_content and length_ok and font_ok and words_ok:
            # Calculate position score
            gaussian_center = page_height * 0.25
            gaussian_sigma = page_height * 0.15
            position_score = math.exp(-((span['y_position'] - gaussian_center) ** 2) / (2 * gaussian_sigma ** 2))
            
            # Text quality score (simplified)
            text_quality = 0.8  # Assume good quality
            
            # Font size normalized score
            font_score = min(span['font_size'] / 24.0, 1.0)
            
            # Individual candidate scoring
            candidate_score = (
                0.4 * font_score + 
                0.35 * position_score + 
                0.25 * text_quality - 
                0.6 * (1.0 if is_journal else 0.0)
            )
            
            score_ok = candidate_score > 0.2
            print(f"   - Candidate score: {candidate_score:.3f} {'✅' if score_ok else '❌'}")
            
            if score_ok:
                print(f"   ✅ SHOULD BE INCLUDED AS CANDIDATE")
            else:
                print(f"   ❌ FILTERED OUT BY SCORE")
        else:
            print(f"   ❌ FILTERED OUT BY BASIC CHECKS")
        
        print()
    
    temp_doc.close()

if __name__ == "__main__":
    debug_employees_filtering()
