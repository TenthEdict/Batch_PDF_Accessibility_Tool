#!/usr/bin/env python3
"""
Test script for enhanced title extraction algorithm
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "processor" / "unified_project"))

import fitz
import pikepdf
import re
import math
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_text_quality_score(text: str, font_flags: int) -> float:
    """Calculate text quality score based on academic title characteristics."""
    score = 0.0
    
    # Length scoring (optimal 50-150 characters)
    text_length = len(text)
    if 50 <= text_length <= 150:
        score += 0.3
    elif 30 <= text_length < 50 or 150 < text_length <= 200:
        score += 0.2
    elif 20 <= text_length < 30 or 200 < text_length <= 250:
        score += 0.1
    
    # Capitalization patterns (title case or sentence case preferred)
    words = text.split()
    if len(words) > 0:
        title_case_words = sum(1 for word in words if word and word[0].isupper())
        title_case_ratio = title_case_words / len(words)
        if title_case_ratio > 0.7:  # Mostly title case
            score += 0.2
        elif text[0].isupper():  # At least sentence case
            score += 0.15
    
    # Academic keywords boost
    academic_keywords = ['analysis', 'study', 'investigation', 'approach', 'method',
                       'system', 'framework', 'model', 'evaluation', 'assessment',
                       'comparative', 'novel', 'efficient', 'optimal', 'enhanced']
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in academic_keywords):
        score += 0.15
    
    # Punctuation patterns (colons common in academic titles)
    if ':' in text:
        score += 0.1
    
    # Font style bonus (bold/italic often used for titles)
    if font_flags & 2**4:  # Bold flag
        score += 0.15
    
    # Penalize all caps (less common in modern academic titles)
    if text.isupper() and len(text) > 20:
        score -= 0.2
    
    # Normalize score to [0, 1]
    return max(0.0, min(1.0, score))

def extract_document_title_enhanced(input_path: Path) -> str:
    """Enhanced title extraction with spatial filtering and journal pattern detection."""
    
    try:
        # Read-only analysis with PyMuPDF
        temp_doc = fitz.open(str(input_path))
        
        if len(temp_doc) == 0:
            temp_doc.close()
            return None
        
        first_page = temp_doc[0]
        page_height = first_page.rect.height
        
        # Define spatial exclusion zones (12% header to be more inclusive, 15% footer)
        header_zone_limit = page_height * 0.12  # Slightly more inclusive for titles
        footer_zone_limit = page_height * 0.85
        
        # Journal name patterns for detection
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
            r'\bvol\.?\s*\d+',  # Volume indicators
            r'\bissn\b',
            r'\bdoi\b',
            r'©\s*\d{4}',  # Copyright lines
        ]
        
        # Compile patterns for efficiency
        journal_regex = re.compile('|'.join(journal_patterns), re.IGNORECASE)
        
        # Get text blocks with formatting information
        blocks = first_page.get_text("dict")
        
        title_candidates = []
        
        # Look for text blocks that could be titles
        for block in blocks.get("blocks", []):
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                bbox = line.get("bbox", [0, 0, 0, 0])
                y_position = bbox[1]
                
                # Skip text in header/footer zones
                if y_position < header_zone_limit or y_position > footer_zone_limit:
                    continue
                
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    font_size = span.get("size", 0)
                    font_flags = span.get("flags", 0)
                    x_position = span.get("bbox", [0, 0, 0, 0])[0]  # X coordinate
                    
                    # Enhanced filtering for potential title text
                    if (text and 
                        len(text) > 10 and  # Reasonable title length
                        len(text) < 300 and  # Academic titles can be longer
                        font_size > 12 and   # Larger font size threshold
                        not text.lower().startswith(('abstract', 'keywords', 'introduction', 
                                                   'figure', 'table', 'contents', 'acknowledgment')) and
                        not any(char.isdigit() for char in text[:3]) and  # Avoid page numbers
                        not text.startswith(('http', 'www.', 'doi:')) and  # Avoid URLs/DOIs
                        text.count(' ') >= 2):  # Multi-word titles
                        
                        # Check if text matches journal patterns
                        is_journal = bool(journal_regex.search(text))
                        
                        # Calculate position score with Gaussian weighting
                        # Gaussian centered at 30% of page height (typical title position)
                        gaussian_center = page_height * 0.3
                        gaussian_sigma = page_height * 0.15
                        position_score = math.exp(-((y_position - gaussian_center) ** 2) / (2 * gaussian_sigma ** 2))
                        
                        # Text quality score based on characteristics
                        text_quality = calculate_text_quality_score(text, font_flags)
                        
                        # Font size normalized score (0-1)
                        font_score = min(font_size / 24.0, 1.0)  # Normalize to 24pt max
                        
                        # Composite scoring function
                        # S(t) = α·FontSize(t) + β·Position(t) + γ·Quality(t) - δ·IsJournal(t)
                        composite_score = (
                            0.4 * font_score + 
                            0.35 * position_score + 
                            0.25 * text_quality - 
                            0.5 * (1.0 if is_journal else 0.0)  # Penalty for journal patterns
                        )
                        
                        title_candidates.append({
                            'text': text,
                            'font_size': font_size,
                            'font_flags': font_flags,
                            'y_position': y_position,
                            'x_position': x_position,
                            'is_journal': is_journal,
                            'composite_score': composite_score,
                            'position_score': position_score,
                            'quality_score': text_quality
                        })
        
        temp_doc.close()
        
        if not title_candidates:
            return None
        
        # Sort by composite score (descending)
        title_candidates.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Multi-line title detection with better sorting and proximity
        best_candidate = title_candidates[0]
        
        # Find all candidates that could be part of the same title
        title_parts = [best_candidate]
        proximity_threshold = 25  # Pixels
        
        for candidate in title_candidates[1:]:
            if (not candidate['is_journal'] and
                abs(candidate['y_position'] - best_candidate['y_position']) < proximity_threshold and
                candidate['font_size'] >= best_candidate['font_size'] * 0.9 and  # Similar font size
                candidate['composite_score'] > 0.4):  # Reasonable quality threshold
                title_parts.append(candidate)
        
        # Sort title parts by Y position (top to bottom) and then X position (left to right)
        title_parts.sort(key=lambda x: (x['y_position'], x['x_position']))
        
        # Assemble the complete title
        complete_title = ' '.join([part['text'] for part in title_parts])
        
        # If we only have one part, check if there are other high-scoring candidates nearby
        if len(title_parts) == 1 and len(title_candidates) > 1:
            # Look for other strong candidates within a larger proximity
            extended_threshold = 50
            additional_parts = []
            
            for candidate in title_candidates[1:]:
                if (not candidate['is_journal'] and
                    abs(candidate['y_position'] - best_candidate['y_position']) < extended_threshold and
                    candidate['composite_score'] > 0.3):  # Lower threshold for potential title parts
                    additional_parts.append(candidate)
            
            if additional_parts:
                all_parts = [best_candidate] + additional_parts
                all_parts.sort(key=lambda x: (x['y_position'], x['x_position']))
                complete_title = ' '.join([part['text'] for part in all_parts])
        
        # Clean up the title
        complete_title = ' '.join(complete_title.split())  # Normalize whitespace
        complete_title = complete_title.strip('.,;:')      # Remove trailing punctuation
        complete_title = re.sub(r'\s*\*+\s*', ' ', complete_title)  # Remove asterisks
        complete_title = re.sub(r'\s+', ' ', complete_title).strip()  # Final cleanup
        
        logger.info(f"Enhanced algorithm extracted title: {complete_title}")
        logger.info(f"Selected from {len(title_candidates)} candidates with score: {best_candidate['composite_score']:.3f}")
        
        # Debug: Show top 5 candidates with positioning info
        print("\\nTop 5 title candidates:")
        for i, candidate in enumerate(title_candidates[:5]):
            region = "JOURNAL" if candidate['is_journal'] else "CONTENT"
            print(f"{i+1}. [{region}] Score: {candidate['composite_score']:.3f}")
            print(f"   Font: {candidate['font_size']:.1f}, Y: {candidate['y_position']:.1f}, X: {candidate['x_position']:.1f}")
            print(f"   Text: '{candidate['text'][:70]}'")
            print()
        
        return complete_title
        
    except Exception as e:
        logger.warning(f"Enhanced title extraction failed: {e}")
        return None

def main():
    """Test the enhanced title extraction on sample academic papers."""
    
    test_files = [
        Path("data/input/1-s2.0-S0148296321001661-main.pdf"),
        Path("data/input/J History Behavioral Science - 2019 - Lussier - Of Maslow  motives  and managers  The hierarchy of needs in American.pdf")
    ]
    
    for pdf_path in test_files:
        print(f"\n{'='*80}")
        print(f"Testing: {pdf_path.name}")
        print('='*80)
        
        if not pdf_path.exists():
            print(f"File not found: {pdf_path}")
            continue
            
        try:
            title = extract_document_title_enhanced(pdf_path)
            print(f"\\n🎯 EXTRACTED TITLE: {title}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
