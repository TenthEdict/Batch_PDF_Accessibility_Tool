from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
import re
import fitz
from PIL import Image
import numpy as np
from collections import defaultdict


class AccessibilityLevel(Enum):
    A = 'A'
    AA = 'AA'
    AAA = 'AAA'


class ViolationType(Enum):
    MISSING_ALT_TEXT = 'Missing alternative text'
    INCORRECT_HEADING_ORDER = 'Incorrect heading order'
    LOW_COLOR_CONTRAST = 'Insufficient color contrast'
    MISSING_LANGUAGE = 'Missing language specification'
    MISSING_TITLE = 'Missing document title'
    COMPLEX_TABLE = 'Complex table without proper headers'
    UNTAGGED_CONTENT = 'Untagged content'


@dataclass
class AccessibilityViolation:
    type: ViolationType
    location: str
    description: str
    wcag_criterion: str
    severity: str
    suggestion: str


class EnhancedAccessibilityChecker:

    def __init__(self, min_level: AccessibilityLevel=AccessibilityLevel.AA
        ) ->None:
        self.min_level = min_level
        self.violations: List[AccessibilityViolation] = []
        self.previous_heading_level = 0

    def _has_sufficient_contrast(self, fg_color: tuple, bg_color: tuple
        ) ->bool:
        """Calculate color contrast ratio."""

        def luminance(color: Tuple[int, int, int]) ->float:
            r, g, b = color
            rs = r / 255
            gs = g / 255
            bs = b / 255
            return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
        if not isinstance(fg_color, tuple) or len(fg_color) != 3:
            fg_color = 0, 0, 0
        if not isinstance(bg_color, tuple) or len(bg_color) != 3:
            bg_color = 255, 255, 255
        l1 = luminance(fg_color)
        l2 = luminance(bg_color)
        ratio = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
        return ratio >= 4.5

    def check_document(self, doc: fitz.Document) ->List[AccessibilityViolation
        ]:
        """Perform comprehensive accessibility check on the document."""
        self.violations = []
        self._check_document_properties(doc)
        for page_num in range(len(doc)):
            page = doc[page_num]
            self._check_page(page, page_num)
        return self.violations

    def _check_text_tags(self, block: Dict, page_num: int) ->None:
        """Check text blocks for proper tagging and structure."""
        if block.get('type') == 0:
            text = ''
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    text += span.get('text', '')
            if text.strip():
                if not self._has_proper_tag(block):
                    self.violations.append(AccessibilityViolation(type=
                        ViolationType.UNTAGGED_CONTENT, location=
                        f'Page {page_num + 1}', description=
                        f"Text content lacks proper structural tags: '{text[:50]}...'"
                        , wcag_criterion='1.3.1', severity='Medium',
                        suggestion=
                        'Add appropriate structural tags (paragraph, list, etc.)'
                        ))

    def _has_proper_tag(self, block: Dict) ->bool:
        """Check if a text block has proper structural tags."""
        if not block.get('tag', {}).get('name'):
            return False
        valid_tags = {'P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'L', 'LI',
            'Table', 'TR', 'TD', 'TH'}
        tag_name = block['tag']['name'].upper()
        return tag_name in valid_tags

    def _has_alt_text(self, page: fitz.Page, xref: int) ->bool:
        """Check if an image has alternative text."""
        try:
            metadata = page.get_image_info(xref)
            if metadata and any('alt' in meta or 'Alt' in meta for meta in
                metadata):
                return True
            image_obj = page.parent.xref_object(xref)
            if image_obj and '/Alt' in image_obj:
                return True
            return False
        except Exception:
            return False

    def _detect_tables(self, page: fitz.Page) ->List[Dict]:
        """Detect tables in a page."""
        tables = []
        blocks = page.get_text('dict')['blocks']
        for block in blocks:
            if block.get('type') == 1:
                bbox = block.get('bbox')
                if bbox:
                    if self._is_table_structure(page, bbox):
                        tables.append({'bbox': bbox, 'cells': self.
                            _extract_table_cells(page, bbox)})
        return tables

    def _is_table_structure(self, page: fitz.Page, bbox: tuple) ->bool:
        """Check if a region has a table-like structure."""
        x0, y0, x1, y1 = bbox
        blocks = [b for b in page.get_text('dict')['blocks'] if b['bbox'][0
            ] >= x0 and b['bbox'][2] <= x1 and b['bbox'][1] >= y0 and b[
            'bbox'][3] <= y1]
        if len(blocks) < 4:
            return False
        x_positions = set()
        y_positions = set()
        for block in blocks:
            x_positions.add(round(block['bbox'][0]))
            y_positions.add(round(block['bbox'][1]))
        return len(x_positions) >= 2 and len(y_positions) >= 2

    def _has_table_headers(self, table: Dict) ->bool:
        """Check if a table has proper headers."""
        if not table.get('cells'):
            return False
        first_row = [cell for cell in table['cells'] if cell.get('row') == 0]
        if not first_row:
            return False
        return any(cell.get('is_header', False) for cell in first_row)

    def _extract_table_cells(self, page: fitz.Page, bbox: tuple) ->List[Dict]:
        """Extract cells from a table region."""
        x0, y0, x1, y1 = bbox
        cells = []
        blocks = [b for b in page.get_text('dict')['blocks'] if b['bbox'][0
            ] >= x0 and b['bbox'][2] <= x1 and b['bbox'][1] >= y0 and b[
            'bbox'][3] <= y1]
        blocks.sort(key=lambda b: (b['bbox'][1], b['bbox'][0]))
        current_y = None
        row = 0
        col = 0
        for block in blocks:
            y = round(block['bbox'][1])
            if current_y is None or abs(y - current_y) > 5:
                current_y = y
                row += 1
                col = 0
            cells.append({'text': block.get('text', ''), 'row': row, 'col':
                col, 'bbox': block['bbox'], 'is_header': row == 1})
            col += 1
        return cells

    def _check_document_properties(self, doc: fitz.Document) ->None:
        """Check document-level accessibility requirements."""
        metadata = doc.metadata
        if not metadata.get('title'):
            self.violations.append(AccessibilityViolation(type=
                ViolationType.MISSING_TITLE, location='Document',
                description='Document lacks a title', wcag_criterion=
                '2.4.2', severity='High', suggestion=
                'Add a descriptive title to the PDF metadata'))
        if not metadata.get('language'):
            self.violations.append(AccessibilityViolation(type=
                ViolationType.MISSING_LANGUAGE, location='Document',
                description='Document language not specified',
                wcag_criterion='3.1.1', severity='High', suggestion=
                'Specify the primary language in PDF metadata'))

    def _check_page(self, page: fitz.Page, page_num: int) ->None:
        """Check accessibility of individual page elements."""
        self._check_images(page, page_num)
        self._check_text_elements(page, page_num)
        self._check_color_contrast(page, page_num)
        self._check_tables(page, page_num)

    def _check_images(self, page: fitz.Page, page_num: int) ->None:
        """Check images for accessibility compliance."""
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            if not self._has_alt_text(page, xref):
                self.violations.append(AccessibilityViolation(type=
                    ViolationType.MISSING_ALT_TEXT, location=
                    f'Page {page_num + 1}, Image {img_index + 1}',
                    description='Image lacks alternative text',
                    wcag_criterion='1.1.1', severity='High', suggestion=
                    'Add descriptive alternative text to the image'))

    def _check_text_elements(self, page: fitz.Page, page_num: int) ->None:
        """Check text elements for accessibility issues."""
        blocks = page.get_text('dict')['blocks']
        for block in blocks:
            if block.get('type') == 0:
                self._check_heading_order(block, page_num)
                self._check_text_tags(block, page_num)

    def _get_heading_level(self, block: Dict) ->Optional[int]:
        """Determine heading level based on font properties."""
        if block.get('type') == 0:
            spans = []
            for line in block.get('lines', []):
                spans.extend(line.get('spans', []))
            if spans:
                largest_font = max(spans, key=lambda s: s.get('size', 0))
                font_size = largest_font.get('size', 0)
                is_bold = 'Bold' in largest_font.get('font', '')
                if is_bold and font_size in self.heading_font_sizes:
                    return self.heading_font_sizes[font_size]
        return None

    def _check_heading_order(self, block: Dict, page_num: int) ->None:
        """Verify heading levels are properly ordered."""
        heading_level = self._get_heading_level(block)
        if heading_level:
            if heading_level > self.previous_heading_level + 1:
                self.violations.append(AccessibilityViolation(type=
                    ViolationType.INCORRECT_HEADING_ORDER, location=
                    f'Page {page_num + 1}', description=
                    f'Heading level skips from {self.previous_heading_level} to {heading_level}'
                    , wcag_criterion='1.3.1', severity='Medium', suggestion
                    =
                    f'Add an h{self.previous_heading_level + 1} heading before this h{heading_level}'
                    ))
            self.previous_heading_level = heading_level

    def _check_color_contrast(self, page: fitz.Page, page_num: int) ->None:
        """Check color contrast ratios."""
        for block in page.get_text('dict')['blocks']:
            if block.get('type') == 0:
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        if not self._has_sufficient_contrast(span.get(
                            'color', (0, 0, 0)), span.get('background', (
                            255, 255, 255))):
                            self.violations.append(AccessibilityViolation(
                                type=ViolationType.LOW_COLOR_CONTRAST,
                                location=f'Page {page_num + 1}',
                                description=
                                'Text has insufficient color contrast',
                                wcag_criterion='1.4.3', severity='Medium',
                                suggestion=
                                'Increase the color contrast to at least 4.5:1'
                                ))

    def _check_tables(self, page: fitz.Page, page_num: int) ->None:
        """Check table accessibility."""
        tables = self._detect_tables(page)
        for table_idx, table in enumerate(tables):
            if not self._has_table_headers(table):
                self.violations.append(AccessibilityViolation(type=
                    ViolationType.COMPLEX_TABLE, location=
                    f'Page {page_num + 1}, Table {table_idx + 1}',
                    description='Table lacks proper header markup',
                    wcag_criterion='1.3.1', severity='High', suggestion=
                    'Add proper table headers and specify header cells'))

    def generate_report(self) ->Dict:
        """Generate a detailed accessibility report."""
        return {'summary': {'total_violations': len(self.violations),
            'by_severity': {'High': sum(1 for v in self.violations if v.
            severity == 'High'), 'Medium': sum(1 for v in self.violations if
            v.severity == 'Medium'), 'Low': sum(1 for v in self.violations if
            v.severity == 'Low')}, 'by_type': {vtype.value: sum(1 for v in
            self.violations if v.type == vtype) for vtype in ViolationType}
            }, 'violations': [{'type': v.type.value, 'location': v.location,
            'description': v.description, 'wcag_criterion': v.
            wcag_criterion, 'severity': v.severity, 'suggestion': v.
            suggestion} for v in self.violations]}

    def check_heading_structure(self, doc: fitz.Document) ->List[
        AccessibilityViolation]:
        heading_levels = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text('dict')['blocks']
            for block in blocks:
                if block.get('type') == 0:
                    font_size = block.get('font_size', 0)
                    is_bold = block.get('font', '').lower().find('bold') >= 0
                    if font_size > 20:
                        level = 1
                    elif font_size > 18 and is_bold:
                        level = 2
                    elif font_size > 16 and is_bold:
                        level = 3
                    elif font_size > 14 and is_bold:
                        level = 4
                    elif font_size > 12 and is_bold:
                        level = 5
                    elif font_size > 10 and is_bold:
                        level = 6
                    else:
                        continue
                    heading_levels.append((level, page_num))
        violations = []
        prev_level = 0
        for level, page_num in heading_levels:
            if level > prev_level + 1:
                violations.append(AccessibilityViolation(type=ViolationType
                    .INCORRECT_HEADING_ORDER, location=f'Page {page_num}',
                    description=
                    f'Heading level skipped from {prev_level} to {level}',
                    wcag_criterion='1.3.1', severity='Error', suggestion=
                    f'Use proper heading order - level {prev_level + 1} should come before level {level}'
                    ))
            prev_level = level
        return violations

    def check_color_contrast(self, doc: fitz.Document) ->List[
        AccessibilityViolation]:
        violations = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text('dict')['blocks']
            for block in blocks:
                if block.get('type') == 0:
                    text_color = block.get('color')
                    bg_color = self._get_background_color(page, block['bbox'])
                    if text_color and bg_color:
                        contrast_ratio = self._calculate_contrast_ratio(
                            text_color, bg_color)
                        min_ratio = 4.5
                        if contrast_ratio < min_ratio:
                            violations.append(AccessibilityViolation(type=
                                ViolationType.LOW_COLOR_CONTRAST, location=
                                f'Page {page_num}', description=
                                f'Contrast ratio {contrast_ratio:.2f}:1 is below minimum {min_ratio}:1'
                                , wcag_criterion='1.4.3', severity='Error',
                                suggestion=
                                f'Increase contrast between text and background'
                                ))
        return violations

    def _calculate_contrast_ratio(self, fg: tuple, bg: tuple) ->float:

        def luminance(rgb):
            rgb = [(c / 255) for c in rgb]
            rgb = [(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) **
                2.4) for c in rgb]
            return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
        l1 = luminance(fg)
        l2 = luminance(bg)
        return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)

    def check_table_structure(self, doc: fitz.Document) ->List[
        AccessibilityViolation]:
        violations = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            tables = self._detect_tables(page)
            for table_idx, table in enumerate(tables):
                has_headers = False
                has_complex_structure = False
                row_headers = []
                col_headers = []
                cells = table.get('cells', [])
                if cells:
                    first_row = [c for c in cells if c['row'] == 0]
                    has_headers = any(c.get('is_header', False) for c in
                        first_row)
                    first_col = [c for c in cells if c['col'] == 0]
                    has_row_headers = any(c.get('is_header', False) for c in
                        first_col)
                    spans = any(c.get('colspan', 1) > 1 or c.get('rowspan',
                        1) > 1 for c in cells)
                    if spans and not (has_headers and has_row_headers):
                        violations.append(AccessibilityViolation(type=
                            ViolationType.COMPLEX_TABLE, location=
                            f'Page {page_num}', description=
                            'Complex table structure without proper headers',
                            wcag_criterion='1.3.1', severity='Error',
                            suggestion=
                            'Add proper row and column headers for complex table structure'
                            ))
        return violations
