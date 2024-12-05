from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
import re
import fitz
from PIL import Image
import numpy as np
from collections import defaultdict  # Add this import

class AccessibilityLevel(Enum):
    A = "A"
    AA = "AA"
    AAA = "AAA"

class ViolationType(Enum):
    MISSING_ALT_TEXT = "Missing alternative text"
    INCORRECT_HEADING_ORDER = "Incorrect heading order"
    LOW_COLOR_CONTRAST = "Insufficient color contrast"
    MISSING_LANGUAGE = "Missing language specification"
    MISSING_TITLE = "Missing document title"
    COMPLEX_TABLE = "Complex table without proper headers"
    UNTAGGED_CONTENT = "Untagged content"

@dataclass
class AccessibilityViolation:
    type: ViolationType
    location: str
    description: str
    wcag_criterion: str
    severity: str
    suggestion: str

class EnhancedAccessibilityChecker:
    def __init__(self, min_level: AccessibilityLevel = AccessibilityLevel.AA):
        self.min_level = min_level
        self.violations: List[AccessibilityViolation] = []
        self.previous_heading_level = 0

    def _has_sufficient_contrast(self, fg_color: tuple, bg_color: tuple) -> bool:
        """Calculate color contrast ratio."""
        def luminance(color: Tuple[int, int, int]) -> float:
            r, g, b = color
            rs = r / 255
            gs = g / 255
            bs = b / 255
            return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs

        # Ensure colors are proper RGB tuples
        if not isinstance(fg_color, tuple) or len(fg_color) != 3:
            fg_color = (0, 0, 0)  # Default to black if invalid
        if not isinstance(bg_color, tuple) or len(bg_color) != 3:
            bg_color = (255, 255, 255)  # Default to white if invalid

        l1 = luminance(fg_color)
        l2 = luminance(bg_color)
        
        ratio = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
        return ratio >= 4.5  # WCAG AA standard for normal text
        
    def check_document(self, doc: fitz.Document) -> List[AccessibilityViolation]:
        """Perform comprehensive accessibility check on the document."""
        self.violations = []
        
        # Check document-level properties
        self._check_document_properties(doc)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            self._check_page(page, page_num)
            
        return self.violations
    
    def _check_text_tags(self, block: Dict, page_num: int) -> None:
        """Check text blocks for proper tagging and structure."""
        if block.get("type") == 0:  # text block
            text = ""
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text += span.get("text", "")
            
            # Check if text is meaningful
            if text.strip():
                # Check if text is properly tagged
                if not self._has_proper_tag(block):
                    self.violations.append(AccessibilityViolation(
                        type=ViolationType.UNTAGGED_CONTENT,
                        location=f"Page {page_num + 1}",
                        description=f"Text content lacks proper structural tags: '{text[:50]}...'",
                        wcag_criterion="1.3.1",
                        severity="Medium",
                        suggestion="Add appropriate structural tags (paragraph, list, etc.)"
                    ))

    def _has_proper_tag(self, block: Dict) -> bool:
        """Check if a text block has proper structural tags."""
        # Check if block has any tag information
        if not block.get("tag", {}).get("name"):
            return False
        
        # List of valid structural tags
        valid_tags = {"P", "H1", "H2", "H3", "H4", "H5", "H6", "L", "LI", "Table", "TR", "TD", "TH"}
        
        # Check if tag is valid
        tag_name = block["tag"]["name"].upper()
        return tag_name in valid_tags
    
    def _has_alt_text(self, page: fitz.Page, xref: int) -> bool:
        """Check if an image has alternative text."""
        try:
            # Try to get image metadata
            metadata = page.get_image_info(xref)
            
            # Check for alt text in metadata
            if metadata and any(('alt' in meta or 'Alt' in meta) for meta in metadata):
                return True
                
            # Check PDF structure for alt text
            image_obj = page.parent.xref_object(xref)
            if image_obj and '/Alt' in image_obj:
                return True
                
            return False
        except Exception:
            # If we can't access the image info, assume no alt text
            return False
        
    def _detect_tables(self, page: fitz.Page) -> List[Dict]:
        """Detect tables in a page."""
        tables = []
        blocks = page.get_text("dict")["blocks"]
        
        # Simple table detection based on grid-like structure
        for block in blocks:
            if block.get("type") == 1:  # image block, might be a table
                bbox = block.get("bbox")
                if bbox:
                    # Check if block has grid-like structure
                    if self._is_table_structure(page, bbox):
                        tables.append({
                            "bbox": bbox,
                            "cells": self._extract_table_cells(page, bbox)
                        })
        
        return tables

    def _is_table_structure(self, page: fitz.Page, bbox: tuple) -> bool:
        """Check if a region has a table-like structure."""
        x0, y0, x1, y1 = bbox
        
        # Get text blocks in the region
        blocks = [b for b in page.get_text("dict")["blocks"]
                if b["bbox"][0] >= x0 and b["bbox"][2] <= x1
                and b["bbox"][1] >= y0 and b["bbox"][3] <= y1]
        
        if len(blocks) < 4:  # Need at least 4 cells for a table
            return False
        
        # Check for grid alignment
        x_positions = set()
        y_positions = set()
        
        for block in blocks:
            x_positions.add(round(block["bbox"][0]))
            y_positions.add(round(block["bbox"][1]))
        
        # If we have multiple aligned rows and columns
        return len(x_positions) >= 2 and len(y_positions) >= 2

    def _has_table_headers(self, table: Dict) -> bool:
        """Check if a table has proper headers."""
        if not table.get("cells"):
            return False
        
        # Check first row for header characteristics
        first_row = [cell for cell in table["cells"] if cell.get("row") == 0]
        
        if not first_row:
            return False
        
        # Check if first row cells have header formatting
        return any(cell.get("is_header", False) for cell in first_row)

    def _extract_table_cells(self, page: fitz.Page, bbox: tuple) -> List[Dict]:
        """Extract cells from a table region."""
        x0, y0, x1, y1 = bbox
        cells = []
        
        # Get text blocks in table region
        blocks = [b for b in page.get_text("dict")["blocks"]
                if b["bbox"][0] >= x0 and b["bbox"][2] <= x1
                and b["bbox"][1] >= y0 and b["bbox"][3] <= y1]
        
        # Sort blocks by position to determine rows and columns
        blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
        
        # Group blocks into rows
        current_y = None
        row = 0
        col = 0
        
        for block in blocks:
            y = round(block["bbox"][1])
            
            if current_y is None or abs(y - current_y) > 5:
                current_y = y
                row += 1
                col = 0
            
            cells.append({
                "text": block.get("text", ""),
                "row": row,
                "col": col,
                "bbox": block["bbox"],
                "is_header": row == 1  # Assume first row is header
            })
            
            col += 1
        
        return cells
        
    def _check_document_properties(self, doc: fitz.Document):
        """Check document-level accessibility requirements."""
        metadata = doc.metadata
    
        if not metadata.get('title'):
            self.violations.append(AccessibilityViolation(
                type=ViolationType.MISSING_TITLE,
                location="Document",
                description="Document lacks a title",
                wcag_criterion="2.4.2",
                severity="High",
                suggestion="Add a descriptive title to the PDF metadata"
            ))
        
        if not metadata.get('language'):
            self.violations.append(AccessibilityViolation(
                type=ViolationType.MISSING_LANGUAGE,
                location="Document",
                description="Document language not specified",
                wcag_criterion="3.1.1",
                severity="High",
                suggestion="Specify the primary language in PDF metadata"
            ))

    def _check_page(self, page: fitz.Page, page_num: int):
        """Check accessibility of individual page elements."""
        # Check images
        self._check_images(page, page_num)
        
        # Check text elements
        self._check_text_elements(page, page_num)
        
        # Check color contrast
        self._check_color_contrast(page, page_num)
        
        # Check tables
        self._check_tables(page, page_num)

    def _check_images(self, page: fitz.Page, page_num: int):
        """Check images for accessibility compliance."""
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            
            # Check for alternative text
            if not self._has_alt_text(page, xref):
                self.violations.append(AccessibilityViolation(
                    type=ViolationType.MISSING_ALT_TEXT,
                    location=f"Page {page_num + 1}, Image {img_index + 1}",
                    description="Image lacks alternative text",
                    wcag_criterion="1.1.1",
                    severity="High",
                    suggestion="Add descriptive alternative text to the image"
                ))

    def _check_text_elements(self, page: fitz.Page, page_num: int):
        """Check text elements for accessibility issues."""
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block.get("type") == 0:  # text block
                self._check_heading_order(block, page_num)
                self._check_text_tags(block, page_num)

    def _get_heading_level(self, block: Dict) -> Optional[int]:
        """Determine heading level based on font properties."""
        if block.get("type") == 0:  # text block
            spans = []
            for line in block.get("lines", []):
                spans.extend(line.get("spans", []))
                
            if spans:
                # Get the dominant font properties
                largest_font = max(spans, key=lambda s: s.get("size", 0))
                font_size = largest_font.get("size", 0)
                is_bold = "Bold" in largest_font.get("font", "")
                
                # If text is bold and matches a known heading font size
                if is_bold and font_size in self.heading_font_sizes:
                    return self.heading_font_sizes[font_size]
        
        return None

    def _check_heading_order(self, block: Dict, page_num: int):
        """Verify heading levels are properly ordered."""
        heading_level = self._get_heading_level(block)
        if heading_level:
            if heading_level > self.previous_heading_level + 1:
                self.violations.append(AccessibilityViolation(
                    type=ViolationType.INCORRECT_HEADING_ORDER,
                    location=f"Page {page_num + 1}",
                    description=f"Heading level skips from {self.previous_heading_level} to {heading_level}",
                    wcag_criterion="1.3.1",
                    severity="Medium",
                    suggestion=f"Add an h{self.previous_heading_level + 1} heading before this h{heading_level}"
                ))
            self.previous_heading_level = heading_level

    def _check_color_contrast(self, page: fitz.Page, page_num: int):
        """Check color contrast ratios."""
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") == 0:  # text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if not self._has_sufficient_contrast(
                            span.get("color", (0, 0, 0)),
                            span.get("background", (255, 255, 255))
                        ):
                            self.violations.append(AccessibilityViolation(
                                type=ViolationType.LOW_COLOR_CONTRAST,
                                location=f"Page {page_num + 1}",
                                description="Text has insufficient color contrast",
                                wcag_criterion="1.4.3",
                                severity="Medium",
                                suggestion="Increase the color contrast to at least 4.5:1"
                            ))

    def _check_tables(self, page: fitz.Page, page_num: int):
        """Check table accessibility."""
        tables = self._detect_tables(page)
        for table_idx, table in enumerate(tables):
            if not self._has_table_headers(table):
                self.violations.append(AccessibilityViolation(
                    type=ViolationType.COMPLEX_TABLE,
                    location=f"Page {page_num + 1}, Table {table_idx + 1}",
                    description="Table lacks proper header markup",
                    wcag_criterion="1.3.1",
                    severity="High",
                    suggestion="Add proper table headers and specify header cells"
                ))

    def generate_report(self) -> Dict:
        """Generate a detailed accessibility report."""
        return {
            'summary': {
                'total_violations': len(self.violations),
                'by_severity': {
                    'High': sum(1 for v in self.violations if v.severity == 'High'),
                    'Medium': sum(1 for v in self.violations if v.severity == 'Medium'),
                    'Low': sum(1 for v in self.violations if v.severity == 'Low')
                },
                'by_type': {vtype.value: sum(1 for v in self.violations if v.type == vtype)
                           for vtype in ViolationType}
            },
            'violations': [
                {
                    'type': v.type.value,
                    'location': v.location,
                    'description': v.description,
                    'wcag_criterion': v.wcag_criterion,
                    'severity': v.severity,
                    'suggestion': v.suggestion
                }
                for v in self.violations
            ]
        }