import os
from pathlib import Path
import concurrent.futures
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
from tqdm import tqdm
import fitz
from pdf2image import convert_from_path
import cv2
import numpy as np
from collections import defaultdict
import re
from dataclasses import dataclass
from PIL import Image
from .enhance import EnhancedAccessibilityChecker
from ..utils.retry import RetryHandler, RetryConfig, ProcessingError, OCRError
from ..ocr.processor import OCRProcessor, OCRTimeoutError


@dataclass
class TableCell:
    text: str
    row: int
    col: int
    colspan: int = 1
    rowspan: int = 1
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0


@dataclass
class TextElement:
    text: str
    x: float
    y: float
    width: float
    height: float
    font_size: float
    font_name: str
    is_bold: bool
    page_num: int
    heading_level: Optional[int] = None
    reading_order: int = 0
    table_cell: Optional[TableCell] = None
    confidence: float = 100.0


@dataclass
class OCRElement:
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    type: str
    page_num: int


class TableStructure:

    def __init__(self) ->None:
        self.rows: List[List[Optional[TableCell]]] = []
        self.bbox: Tuple[float, float, float, float] = (0, 0, 0, 0)
        self.num_cols: int = 0
        self.num_rows: int = 0
        self.column_x_positions: List[float] = []
        self.row_y_positions: List[float] = []

    def initialize_grid(self, num_rows: int, num_cols: int) ->None:
        """Initialize the table grid with the specified dimensions."""
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.rows = [[None for _ in range(num_cols)] for _ in range(num_rows)]

    def detect_column_spans(self, row_elements: List[TextElement], row_idx: int
        ) ->None:
        """Detect column spans in a row based on element widths and positions."""
        if not row_elements:
            return
        row_elements.sort(key=lambda e: e.x)
        avg_col_width = np.mean([e.width for e in row_elements if e.width > 0])
        col_idx = 0
        for element in row_elements:
            while col_idx < self.num_cols and self.rows[row_idx][col_idx
                ] is not None:
                col_idx += 1
            if col_idx >= self.num_cols:
                break
            potential_colspan = max(1, round(element.width / avg_col_width))
            actual_colspan = min(potential_colspan, self.num_cols - col_idx)
            cell = TableCell(text=element.text, row=row_idx, col=col_idx,
                colspan=actual_colspan, x=element.x, y=element.y, width=
                element.width, height=element.height)
            for span_idx in range(actual_colspan):
                if col_idx + span_idx < self.num_cols:
                    self.rows[row_idx][col_idx + span_idx] = cell
            element.table_cell = cell
            col_idx += actual_colspan

    def verify_column_spans(self) ->None:
        """Verify and adjust column spans based on overall table structure."""
        all_x_positions = []
        for row in self.rows:
            for cell in row:
                if cell and cell.col == 0:
                    all_x_positions.append(cell.x)
        if all_x_positions:
            x_std = np.std(all_x_positions)
            x_mean = np.mean(all_x_positions)
            for row_idx, row in enumerate(self.rows):
                for col_idx, cell in enumerate(row):
                    if cell and cell.col == col_idx:
                        if abs(cell.x - x_mean) > x_std * 2:
                            self._adjust_cell_span(row_idx, col_idx)

    def _adjust_cell_span(self, row_idx: int, col_idx: int) ->None:
        """Adjust cell span based on surrounding cells."""
        cell = self.rows[row_idx][col_idx]
        if not cell or cell.colspan == 1:
            return
        adjacent_cols = []
        if row_idx > 0:
            adjacent_cols.extend(c.col for c in self.rows[row_idx - 1] if c and
                c.col == c.col)
        if row_idx < len(self.rows) - 1:
            adjacent_cols.extend(c.col for c in self.rows[row_idx + 1] if c and
                c.col == c.col)
        if adjacent_cols:
            new_colspan = max(set(adjacent_cols), key=adjacent_cols.count
                ) - col_idx
            if new_colspan != cell.colspan:
                for i in range(cell.colspan):
                    if col_idx + i < self.num_cols:
                        self.rows[row_idx][col_idx + i] = None
                cell.colspan = new_colspan
                for i in range(new_colspan):
                    if col_idx + i < self.num_cols:
                        self.rows[row_idx][col_idx + i] = cell


class AccessibilityDocumentProcessor:

    def __init__(self, pdf_path: str, ocr_processor: Optional[OCRProcessor]
        =None, retry_handler: Optional[RetryHandler]=None, enable_ocr: bool
        =True) ->None:
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.text_elements: List[TextElement] = []
        self.tables: List[TableStructure] = []
        self.corrections: Dict[int, List[Dict]] = {}
        self.heading_font_sizes: Dict[float, int] = {}
        self.ocr_processor = ocr_processor
        self.retry_handler = retry_handler
        self.enable_ocr = enable_ocr
        self.logger = logging.getLogger(__name__)
        if self.enable_ocr and self.ocr_processor:
            try:
                self.ocr_results = self.verify_text_with_ocr()
                self.logger.info('Initial OCR verification completed')
            except Exception as e:
                self.logger.warning(
                    f'Initial OCR verification failed: {str(e)}')
                self.ocr_results = {}

    def export_corrections(self, output_path: str) ->None:
        """
        Export corrections to a JSON file.
        
        Args:
            output_path: Path where to save the corrections file
        """
        corrections_report = {'document': self.pdf_path, 'timestamp':
            datetime.now().isoformat(), 'corrections': self.corrections}
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(corrections_report, f, indent=2)
        except Exception as e:
            self.logger.error(f'Failed to export corrections: {str(e)}')
            raise ProcessingError(f'Failed to export corrections: {str(e)}')

    def _check_images(self, page: fitz.Page, page_num: int) ->None:
        """Check images with proper error handling."""
        try:
            images = page.get_images(full=True)
            for img_index, img in enumerate(images):
                if not img or len(img) < 1:
                    continue
                xref = img[0]
                if not xref:
                    continue
        except AttributeError as e:
            self.logger.warning(f'Page {page_num} has no image data: {str(e)}')
        except Exception as e:
            self.logger.error(
                f'Error processing images on page {page_num}: {str(e)}')

    def verify_text_with_ocr(self) ->Dict[int, Dict]:
        """Improved OCR verification with better error handling"""
        results = {}
        try:
            images = convert_from_path(self.pdf_path)
            for page_num, image in enumerate(images):
                try:
                    image_np = np.array(image)
                    if self.ocr_processor:
                        ocr_results = self.ocr_processor.process_page(image_np,
                            page_num)
                        results[page_num] = {'status': 'success',
                            'corrections': [], 'confidence': np.mean([elem.
                            confidence for elem in ocr_results if hasattr(
                            elem, 'confidence')]) if ocr_results else 0}
                        self.logger.info(f'OCR completed for page {page_num}')
                    else:
                        self.logger.warning('No OCR processor available')
                except Exception as e:
                    self.logger.error(f'OCR error on page {page_num}: {str(e)}'
                        )
                    results[page_num] = {'status': 'failed', 'error': str(e)}
        except Exception as e:
            self.logger.error(f'PDF conversion error: {str(e)}')
            raise ProcessingError(f'Failed to process PDF with OCR: {str(e)}')
        return results

    def add_text_tags(self) ->None:
        for page in self.doc:
            for element in [e for e in self.text_elements if e.page_num ==
                page.number]:
                rect = fitz.Rect(element.x, element.y, element.x + element.
                    width, element.y + element.height)
                page.insert_text(rect.tl, element.text, fontsize=element.
                    font_size)

    def extract_text_with_positions(self) ->None:
        """Extract text with improved error handling and OCR triggering."""
        total_blocks = 0
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text_dict = page.get_text('dict')
            if not text_dict or 'blocks' not in text_dict:
                self.logger.warning(
                    f'No text blocks found on page {page_num + 1}')
                continue
            page_blocks = 0
            for block in text_dict['blocks']:
                if 'lines' not in block:
                    continue
                for line in block['lines']:
                    if 'spans' not in line:
                        continue
                    for span in line.get('spans', []):
                        if self._process_span(span, page_num):
                            page_blocks += 1
            if page_blocks == 0:
                self.logger.warning(
                    f'No processable text found on page {page_num + 1}')
            total_blocks += page_blocks
        if total_blocks == 0:
            self.logger.error('No text content extracted from document')
            if self.enable_ocr and self.ocr_processor:
                self.logger.info('Attempting OCR processing')
                self._force_ocr_processing()
            else:
                raise ProcessingError(
                    'Document appears to be scanned/image-based and OCR is not enabled'
                    )

    def _force_ocr_processing(self) ->None:
        """Force OCR processing on the entire document."""
        try:
            images = convert_from_path(self.pdf_path)
            for page_num, image in enumerate(images):
                image_np = np.array(image)
                if self.ocr_processor:
                    ocr_results = self.ocr_processor.process_page(image_np,
                        page_num)
                    for result in ocr_results:
                        if hasattr(result, 'text') and result.text.strip():
                            x0, y0, x1, y1 = result.bbox
                            element = TextElement(text=result.text, x=x0, y
                                =y0, width=x1 - x0, height=y1 - y0,
                                font_size=12, font_name='OCR-Extracted',
                                is_bold=False, page_num=page_num,
                                confidence=result.confidence)
                            self.text_elements.append(element)
        except Exception as e:
            raise OCRError(f'OCR processing failed: {str(e)}')

    def _process_span(self, span, page_num) ->None:
        """Process a single text span."""
        if not span or 'bbox' not in span:
            return False
        bbox = span['bbox']
        if not bbox or len(bbox) != 4:
            return False
        x0, y0, x1, y1 = bbox
        # Don't strip text to preserve original spacing
        text = span.get('text', '')
        if not text:
            return False
        element = TextElement(text=text, x=x0, y=y0, width=x1 - x0, height=
            y1 - y0, font_size=span.get('size', 12), font_name=span.get(
            'font', ''), is_bold='Bold' in span.get('font', ''), page_num=
            page_num)
        self.text_elements.append(element)
        return True

    def detect_headings(self) ->None:
        """
        Improved heading detection with stricter criteria.
        Only detects legitimate headings based on font size, style, and content.
        """
        self.heading_font_sizes.clear()
        for element in self.text_elements:
            element.heading_level = None
        potential_headings = [elem for elem in self.text_elements if elem.
            text.strip() and len(elem.text.strip()) > 1 and len(elem.text.
            strip()) < 200 and len(elem.text.split()) <= 20 and not elem.
            text.strip().endswith(':') and not elem.text.strip().endswith(
            '.') and not any(elem.text.lower().startswith(x) for x in [
            'fig', 'table', 'note:'])]
        if not potential_headings:
            return
        font_sizes = defaultdict(list)
        for elem in potential_headings:
            font_sizes[elem.font_size].append(elem)
        body_font_size = max((size for size in font_sizes.keys() if len(
            font_sizes[size]) > 3), default=min(font_sizes.keys()), key=lambda
            x: len(font_sizes[x]))
        larger_sizes = sorted([size for size in font_sizes.keys() if size >
            body_font_size * 1.1], reverse=True)
        heading_sizes = larger_sizes[:6]
        for level, size in enumerate(heading_sizes, start=1):
            for element in font_sizes[size]:
                if self._is_valid_heading(element, body_font_size):
                    element.heading_level = level

    def _is_valid_heading(self, element: TextElement, body_font_size: float
        ) ->bool:
        """
        Validate if a text element is a legitimate heading.
        
        Args:
            element: TextElement to validate
            body_font_size: Base font size for body text
        
        Returns:
            bool: True if element is a valid heading
        """
        text = element.text.strip()
        if not text or len(text) < 2:
            return False
        if len(text) > 200 or len(text.split()) > 20:
            return False
        font_size_ratio = element.font_size / body_font_size
        if font_size_ratio < 1.1:
            return False
        lower_text = text.lower()
        if any([lower_text.startswith(x) for x in ['fig', 'figure', 'table',
            'note:', 'example', 'copyright']]):
            return False
        if text.endswith(':') or text.endswith('.') or text.count('.'
            ) > 2 or text.count(',') > 2 or len(text.split('\n')
            ) > 1 or text.count('(') != text.count(')'):
            return False
        common_non_headings = ['abstract', 'keywords:', 'acknowledgments',
            'references', 'appendix', 'et al.', 'submitted to', 'prepared by']
        if any(marker in lower_text for marker in common_non_headings):
            return False
        return True

    def detect_tables(self) ->None:
        for page_num in range(len(self.doc)):
            page_elements = [te for te in self.text_elements if te and te.
                page_num == page_num and hasattr(te, 'x') and hasattr(te,
                'y') and hasattr(te, 'width')]
            if not page_elements:
                continue
            rows = defaultdict(list)
            for element in page_elements:
                try:
                    row_key = round(element.y / 5) * 5
                    rows[row_key].append(element)
                except (TypeError, AttributeError):
                    continue
            current_table = None
            consecutive_row_count = 0
            for y, row_elements in sorted(rows.items()):
                if len(row_elements) >= 2:
                    try:
                        row_elements.sort(key=lambda e: e.x)
                        spaces = []
                        for i in range(len(row_elements) - 1):
                            try:
                                current = row_elements[i]
                                next_elem = row_elements[i + 1]
                                if all(hasattr(current, attr) for attr in [
                                    'x', 'width']) and hasattr(next_elem, 'x'):
                                    space = next_elem.x - (current.x +
                                        current.width)
                                    spaces.append(space)
                            except (AttributeError, TypeError):
                                continue
                        is_table_row = False
                        if spaces:
                            space_range = max(spaces) - min(spaces)
                            is_table_row = space_range < 10
                        if not is_table_row and row_elements:
                            try:
                                mean_width = np.mean([el.width for el in
                                    row_elements if hasattr(el, 'width')])
                                is_table_row = any(hasattr(e, 'width') and 
                                    e.width > mean_width * 1.5 for e in
                                    row_elements)
                            except (AttributeError, TypeError):
                                pass
                        if is_table_row:
                            if not current_table:
                                current_table = TableStructure()
                                consecutive_row_count = 0
                            consecutive_row_count += 1
                            current_table.rows.append(row_elements)
                        elif current_table and consecutive_row_count >= 2:
                            self._finalize_table(current_table)
                            self.tables.append(current_table)
                            current_table = None
                        else:
                            current_table = None
                            consecutive_row_count = 0
                    except Exception as e:
                        self.logger.warning(
                            f'Error processing row in table detection: {str(e)}'
                            )
                        continue

    def _finalize_table(self, table: TableStructure) ->None:
        """Finalize table structure with robust error handling."""
        if not table or not table.rows:
            return
        try:
            valid_rows = [row for row in table.rows if row and isinstance(
                row, list)]
            if not valid_rows:
                return
            max_cols = max((len(row) for row in valid_rows), default=0)
            if max_cols == 0:
                return
            table.initialize_grid(len(valid_rows), max_cols)
            for row_idx, row_elements in enumerate(valid_rows):
                if row_elements:
                    self._process_row_elements(table, row_elements, row_idx)
            table.verify_column_spans()
            self._calculate_table_bbox(table)
        except Exception as e:
            self.logger.error(f'Error finalizing table: {str(e)}')
            return

    def _process_row_elements(self, table: TableStructure, row_elements:
        List[TextElement], row_idx: int) ->None:
        """Process elements in a table row with validation."""
        try:
            valid_elements = [elem for elem in row_elements if elem and all
                (hasattr(elem, attr) for attr in ['x', 'y', 'width', 'height'])
                ]
            if not valid_elements:
                return
            valid_elements.sort(key=lambda e: e.x)
            widths = [elem.width for elem in valid_elements]
            if not widths:
                return
            avg_col_width = sum(widths) / len(widths)
            col_idx = 0
            for element in valid_elements:
                try:
                    while col_idx < table.num_cols and table.rows[row_idx][
                        col_idx] is not None:
                        col_idx += 1
                    if col_idx >= table.num_cols:
                        break
                    potential_colspan = max(1, round(element.width /
                        avg_col_width))
                    actual_colspan = min(potential_colspan, table.num_cols -
                        col_idx)
                    cell = TableCell(text=element.text, row=row_idx, col=
                        col_idx, colspan=actual_colspan, x=element.x, y=
                        element.y, width=element.width, height=element.height)
                    for span_idx in range(actual_colspan):
                        if col_idx + span_idx < table.num_cols:
                            table.rows[row_idx][col_idx + span_idx] = cell
                    element.table_cell = cell
                    col_idx += actual_colspan
                except Exception as e:
                    self.logger.warning(
                        f'Error processing element in row {row_idx}: {str(e)}')
                    continue
        except Exception as e:
            self.logger.warning(f'Error processing row {row_idx}: {str(e)}')

    def _calculate_table_bbox(self, table: TableStructure) ->None:
        """Calculate table bounding box from valid elements."""
        try:
            valid_cells = []
            for row in table.rows:
                if not row:
                    continue
                for cell in row:
                    if cell and all(hasattr(cell, attr) for attr in ['x',
                        'y', 'width', 'height']):
                        valid_cells.append(cell)
            if not valid_cells:
                return
            min_x = min(cell.x for cell in valid_cells)
            max_x = max(cell.x + cell.width for cell in valid_cells)
            min_y = min(cell.y for cell in valid_cells)
            max_y = max(cell.y + cell.height for cell in valid_cells)
            table.bbox = min_x, min_y, max_x, max_y
        except Exception as e:
            self.logger.warning(f'Error calculating table bbox: {str(e)}')

    def analyze_reading_order(self) ->None:
        """Analyze and assign reading order to document elements with error handling."""
        try:
            for page_num in range(len(self.doc)):
                page_elements = [te for te in self.text_elements if te and 
                    te.page_num == page_num and all(hasattr(te, attr) for
                    attr in ['x', 'y', 'width', 'height'])]
                reading_order = 0
                for level in range(1, 7):
                    headings = [te for te in page_elements if hasattr(te,
                        'heading_level') and te.heading_level == level]
                    for heading in sorted(headings, key=lambda e: (e.y, e.x)):
                        heading.reading_order = reading_order
                        reading_order += 1
                if self.tables:
                    for table in self.tables:
                        if table and table.rows:
                            for row in table.rows:
                                if row:
                                    for cell in row:
                                        if cell and hasattr(cell, 'reading_order'):
                                            cell.reading_order = reading_order
                                            reading_order += 1
                remaining = [te for te in page_elements if (not hasattr(te,
                    'heading_level') or te.heading_level is None) and (not
                    hasattr(te, 'table_cell') or te.table_cell is None)]
                if remaining:
                    column_threshold = 50
                    columns = defaultdict(list)
                    for element in remaining:
                        try:
                            column_key = round(element.x / column_threshold
                                ) * column_threshold
                            columns[column_key].append(element)
                        except (AttributeError, TypeError):
                            continue
                    for x in sorted(columns.keys()):
                        column_elements = columns[x]
                        try:
                            for element in sorted(column_elements, key=lambda
                                e: e.y):
                                if hasattr(element, 'reading_order'):
                                    element.reading_order = reading_order
                                    reading_order += 1
                        except (AttributeError, TypeError) as e:
                            self.logger.warning(
                                f'Error sorting column elements: {str(e)}')
                            continue
        except Exception as e:
            self.logger.error(f'Error in analyze_reading_order: {str(e)}')
            raise

    def _find_closest_text_element(self, ocr_element: OCRElement, page_num: int
        ) ->Optional[TextElement]:
        page_elements = [te for te in self.text_elements if te.page_num ==
            page_num]
        if not page_elements:
            return None
        x1, y1, x2, y2 = ocr_element.bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return min(page_elements, key=lambda e: ((e.x + e.width / 2 -
            center_x) ** 2 + (e.y + e.height / 2 - center_y) ** 2) ** 0.5)

    def _add_correction(self, page_num: int, text_element: TextElement,
        ocr_element: OCRElement) ->None:
        if page_num not in self.corrections:
            self.corrections[page_num] = []
        self.corrections[page_num].append({'original_text': text_element.
            text, 'suggested_text': ocr_element.text, 'confidence':
            ocr_element.confidence, 'type': ocr_element.type, 'position': {
            'x': text_element.x, 'y': text_element.y, 'width': text_element
            .width, 'height': text_element.height}})

    def export_accessibility_report(self, output_path: str) ->None:
        report = {'document_structure': {'pages': len(self.doc),
            'heading_hierarchy': self._analyze_heading_hierarchy(),
            'tables': len(self.tables), 'reading_order': self.
            _export_reading_order()}, 'corrections': self.corrections,
            'tables': self._export_table_structures()}
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

    def _analyze_heading_hierarchy(self) ->Dict:
        hierarchy = defaultdict(int)
        previous_level = None
        skipped_levels = []
        for element in sorted(self.text_elements, key=lambda e: e.reading_order
            ):
            if element.heading_level:
                hierarchy[element.heading_level] += 1
                if (previous_level and element.heading_level -
                    previous_level > 1):
                    skipped_levels.append(
                        f'H{previous_level} to H{element.heading_level}')
                previous_level = element.heading_level
        return {'heading_counts': dict(hierarchy), 'skipped_levels':
            skipped_levels}

    def _export_reading_order(self) ->List[Dict]:
        return [{'text': element.text, 'page': element.page_num, 'order':
            element.reading_order, 'type': 'heading' if element.
            heading_level else 'table_cell' if element.table_cell else
            'content'} for element in sorted(self.text_elements, key=lambda
            e: (e.page_num, e.reading_order))]

    def _export_table_structures(self) ->List[Dict]:
        return [{'rows': table.num_rows, 'columns': table.num_cols, 'bbox':
            table.bbox, 'cells': [{'text': cell.text, 'row': cell.row,
            'col': cell.col, 'colspan': cell.colspan, 'rowspan': cell.
            rowspan, 'bbox': (cell.x, cell.y, cell.x + cell.width, cell.y +
            cell.height)} for row in table.rows for cell in row if cell and
            cell.col == cell.col]} for table in self.tables]


class BatchPDFProcessor:

    def __init__(self, input_dir: str, output_dir: str, max_workers: int=4,
        ocr_processor: Optional[OCRProcessor]=None, retry_handler: Optional
        [RetryHandler]=None) ->None:
        self.input_dir = Path(input_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.max_workers = max_workers
        self.ocr_processor = ocr_processor
        self.retry_handler = retry_handler
        self.processing_stats: Dict[str, Dict] = {}
        self.corrections_dir = self.output_dir / 'corrections'
        self.reports_dir = self.output_dir / 'reports'
        self.processed_dir = self.output_dir / 'processed_pdfs'
        self.logs_dir = self.output_dir / 'logs'
        self.ocr_dir = self.output_dir / 'ocr_results'
        for directory in [self.corrections_dir, self.reports_dir, self.
            processed_dir, self.logs_dir, self.ocr_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        self.setup_logging()


def process_single_pdf(self, pdf_path: Path) ->Dict:
    """Process a single PDF file and return statistics."""
    start_time = time.time()
    stats = {'filename': pdf_path.name, 'size_mb': pdf_path.stat().st_size /
        (1024 * 1024), 'status': 'failed', 'errors': [], 'warnings': [],
        'stats': {}, 'ocr_applied': False, 'ocr_stats': {}}
    try:
        logging.debug(f'Starting to process: {pdf_path}')
        base_name = pdf_path.stem
        corrections_path = (self.corrections_dir /
            f'{base_name}_corrections.json')
        report_path = self.reports_dir / f'{base_name}_report.json'
        processed_path = self.processed_dir / f'{base_name}_processed.pdf'
        logging.debug(f'Will write corrections to: {corrections_path}')
        logging.debug(f'Will write report to: {report_path}')
        logging.debug(f'Will write processed PDF to: {processed_path}')
        if not pdf_path.exists():
            raise FileNotFoundError(f'PDF file not found: {pdf_path}')
        try:
            doc = fitz.open(str(pdf_path))
            if doc is None:
                raise ValueError('Failed to open PDF document')
            if len(doc) == 0:
                raise ValueError('PDF document is empty')
        except Exception as e:
            raise ValueError(f'Invalid PDF document: {str(e)}')
        processor = AccessibilityDocumentProcessor(str(pdf_path),
            ocr_processor=self.ocr_processor, retry_handler=self.retry_handler)
        processor.extract_text_with_positions()
        if not processor.text_elements:
            stats['warnings'].append('No text elements extracted')
        processor.detect_headings()
        processor.detect_tables()
        processor.analyze_reading_order()
        processor.add_text_tags()
        try:
            processor.doc.save(str(processed_path), garbage=4, deflate=True,
                clean=True, pretty=True, linear=True, ascii=False, expand=
                True, copy_streams=True)
            logging.info(f'Saved processed PDF to: {processed_path}')
        except Exception as e:
            stats['warnings'].append(f'Failed to save processed PDF: {str(e)}')
            logging.warning(
                f'Could not save processed PDF for {pdf_path.name}: {str(e)}')
        if self.ocr_processor:
            try:
                ocr_results = processor.verify_text_with_ocr()
                if ocr_results is not None:
                    stats['ocr_applied'] = True
                    stats['ocr_stats'] = {'pages_processed': len(
                        ocr_results), 'successful_pages': sum(1 for page in
                        ocr_results.values() if page.get('status') ==
                        'success'), 'failed_pages': sum(1 for page in
                        ocr_results.values() if page.get('status') ==
                        'failed'), 'average_confidence': np.mean([page.get(
                        'confidence', 0) for page in ocr_results.values() if
                        page.get('status') == 'success'])}
            except Exception as e:
                stats['warnings'].append(f'OCR processing issue: {str(e)}')
                logging.warning(f'OCR issue for {pdf_path.name}: {str(e)}')
        if processor.doc is not None:
            stats['stats'] = {'num_pages': len(processor.doc), 'num_tables':
                len(processor.tables) if processor.tables is not None else 
                0, 'num_headings': sum(1 for elem in processor.
                text_elements if elem is not None and getattr(elem,
                'heading_level', None) is not None), 'num_corrections': sum
                (len(corr) for corr in processor.corrections.values() if
                corr), 'processing_time': time.time() - start_time}
            try:
                processor.export_accessibility_report(str(report_path))
                if not report_path.exists():
                    stats['warnings'].append(
                        'Failed to create accessibility report')
            except Exception as e:
                stats['warnings'].append(f'Failed to export report: {str(e)}')
            stats['status'] = 'success'
        else:
            raise ValueError(
                'Document processing failed: no valid document object')
    except Exception as e:
        error_msg = f'Error processing {pdf_path.name}: {str(e)}'
        logging.error(error_msg)
        stats['status'] = 'failed'
        stats['errors'].append(error_msg)
    return stats


def main() ->None:
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    input_dir = project_root / 'input'
    output_dir = project_root / 'output'
    logging.basicConfig(level=logging.DEBUG, format=
        '%(asctime)s - %(levelname)s - %(message)s')
    logging.debug(f'Starting processing with:')
    logging.debug(f'Project root: {project_root}')
    logging.debug(f'Input directory: {input_dir}')
    logging.debug(f'Output directory: {output_dir}')
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        processor = BatchPDFProcessor(str(input_dir), str(output_dir))
        for dir_name in ['corrections', 'reports', 'processed_pdfs', 'logs',
            'ocr_results']:
            dir_path = output_dir / dir_name
            logging.debug(f'Checking if directory exists: {dir_path}')
            if not dir_path.exists():
                raise RuntimeError(
                    f'Output directory was not created: {dir_path}')
        summary_df = processor.process_directory()
        print('\nProcessing Summary:')
        print(f'Total files processed: {len(summary_df)}')
        if not summary_df.empty:
            success_count = sum(summary_df['status'] == 'success')
            failed_count = sum(summary_df['status'] == 'failed')
            print(f'Successfully processed: {success_count}')
            print(f'Failed: {failed_count}')
            print('\nProcessed files:')
            for idx, row in summary_df.iterrows():
                print(f"  - {idx}: {row['status']}")
                if row['errors']:
                    print(f"    Errors: {row['errors']}")
            print(f'\nOutput files located in: {output_dir}')
            print('\nOutput directory contents:')
            for dir_name in ['corrections', 'reports', 'processed_pdfs',
                'logs', 'ocr_results']:
                dir_path = output_dir / dir_name
                print(f'\n{dir_name}:')
                if dir_path.exists():
                    for file in dir_path.glob('*'):
                        print(f'  - {file.name}')
                else:
                    print('  Directory not found!')
        else:
            print('\nNo files were processed.')
            print(f'Input directory: {input_dir}')
            print('Please ensure PDF files are present in the input directory')
    except Exception as e:
        logging.error(f'Error in main process: {str(e)}')
        raise


if __name__ == '__main__':
    main()
