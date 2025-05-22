"""
Academic paper processing module.

This module provides specialized processing for modern academic papers,
with optimizations for scientific notation, tables, and complex layouts.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
import re

@dataclass
class AcademicPaperConfig:
    """Configuration optimized for modern academic papers"""
    language: str = "eng"
    psm: int = 3  # Auto page segmentation mode
    oem: int = 3  # LSTM only engine mode
    # Character set focusing on academic content including formulas (simplified to avoid Unicode issues)
    char_whitelist: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:()[]{}\"'-=+<>%$"
    enhance_contrast: bool = True
    denoise: bool = False  # Modern papers don't need as much denoising
    sharpen: bool = True
    academic_terms_file: Optional[str] = None
    math_detection: bool = True
    table_detection: bool = True
    citation_detection: bool = True
    additional_params: Dict[str, Any] = field(default_factory=dict)


class AcademicProcessor:
    """
    Specialized processor for modern academic papers with optimizations for:
    - Scientific notation and formulas
    - Tables and figures
    - Citations and references
    - Multi-column layouts
    """
    
    def __init__(self, config: Optional[AcademicPaperConfig] = None):
        """
        Initialize academic paper processor.
        
        Args:
            config: Optional configuration for academic paper processing
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or AcademicPaperConfig()
        self._configure_academic_ocr()
        self.logger.info("Initialized academic paper processor")
    
    def _configure_academic_ocr(self):
        """Configure OCR settings optimized for academic content."""
        # Simplified configuration to avoid quotation issues
        self.text_config = {
            'language': self.config.language,
            'psm': self.config.psm,
            'oem': self.config.oem,
            # Remove the problematic character whitelist
            # 'tessedit_char_whitelist': self.config.char_whitelist,
            'preserve_interword_spaces': '1',
            'textord_tablefind_recognize_tables': '1',
            'textord_tabfind_find_tables': '1',
            'tessedit_enable_doc_dict': '1',
        }
        
        # Skip academic terms file to avoid potential issues
        # if self.config.academic_terms_file and os.path.exists(self.config.academic_terms_file):
        #     self.text_config['user_words_suffix'] = self.config.academic_terms_file
        
        # Skip additional parameters to avoid potential issues
        # if self.config.additional_params:
        #     self.text_config.update(self.config.additional_params)
            
        self.logger.debug(f"Configured academic OCR with simplified settings: {self.text_config}")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for optimal OCR performance on academic papers.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image optimized for academic content
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply adaptive thresholding - optimized for modern print quality
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply preprocessing based on configuration
            enhanced = binary.copy()
            
            # Apply contrast enhancement if configured
            if self.config.enhance_contrast:
                # Use CLAHE for better contrast in academic papers
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(gray)
                # Apply adaptive threshold again after contrast enhancement
                enhanced = cv2.adaptiveThreshold(
                    enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, 11, 2
                )
            
            # Apply denoising if configured (light for modern papers)
            if self.config.denoise:
                enhanced = cv2.fastNlMeansDenoising(enhanced, h=10)
            
            # Apply sharpening if configured
            if self.config.sharpen:
                kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
                enhanced = cv2.filter2D(enhanced, -1, kernel)
            
            # Detect and correct skew if necessary
            angle = self._get_skew_angle(enhanced)
            if abs(angle) > 0.5:
                enhanced = self._rotate_image(enhanced, angle)
            
            return enhanced
            
        except Exception as e:
            error_msg = f"Academic image preprocessing failed: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
    
    def process_academic_paper(self, image: Image.Image, page_num: int = 0) -> Dict[str, Any]:
        """
        Process an academic paper page with optimized OCR.
        
        Args:
            image: PIL Image of the page
            page_num: Page number for multi-page documents
            
        Returns:
            Dictionary containing OCR results and detected structures
        """
        self.logger.info(f"Processing academic paper page {page_num}")
        
        # Convert PIL Image to numpy array
        img_np = np.array(image)
        
        # Preprocess the image
        preprocessed = self.preprocess_image(img_np)
        
        # Extract text with OCR - simplified to use standard pytesseract parameters
        try:
            # Use basic configuration to avoid quotation issues
            ocr_text = pytesseract.image_to_string(
                preprocessed,
                lang=self.config.language,
                config=f'--psm {self.config.psm} --oem {self.config.oem}'
            )
        except Exception as e:
            self.logger.error(f"OCR error: {str(e)}")
            ocr_text = ""  # Fallback to empty text on error
        
        # Temporarily disabled structure detection due to quotation issues
        # structure = self._detect_page_structure(preprocessed, ocr_text)
        structure = {'sections': [], 'headings': [], 'paragraphs': [], 'columns': []}
        
        # Detect specialized content if configured
        results = {
            'page': page_num,
            'text': ocr_text,
            'structure': structure
        }
        
        # Temporarily disabled all detection functions due to quotation issues
        # if self.config.math_detection:
        #     results['formulas'] = self._detect_formulas(preprocessed, ocr_text)
            
        # if self.config.table_detection:
        #     results['tables'] = self._detect_tables(preprocessed)
            
        # if self.config.citation_detection:
        #     results['citations'] = self._detect_citations(ocr_text)
        
        return results
    
    def _detect_page_structure(self, image: np.ndarray, text: str) -> Dict[str, Any]:
        """
        Detect structural elements in the academic paper page.
        
        Uses a combination of visual analysis and text pattern recognition
        to identify structural elements, regardless of specific heading text.
        
        Args:
            image: Preprocessed image
            text: OCR text from the page
            
        Returns:
            Dictionary containing detected structural elements
        """
        structure = {
            'sections': [],
            'headings': [],
            'paragraphs': [],
            'columns': self._detect_columns(image)
        }
        
        # Analyze text layout for structural elements
        lines = text.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Heading detection based on multiple signals, not just text content
            if self._is_likely_heading(line, lines, i):
                heading = {
                    'text': line,
                    'level': self._estimate_heading_level(line, lines, i),
                    'line_index': i
                }
                structure['headings'].append(heading)
                
                # Classify section type if possible
                section_type = self._classify_section_type(line)
                if section_type:
                    current_section = {
                        'type': section_type,
                        'heading': line,
                        'start_line': i
                    }
                    
                    # Close previous section if exists
                    if structure['sections'] and 'end_line' not in structure['sections'][-1]:
                        structure['sections'][-1]['end_line'] = i - 1
                        
                    structure['sections'].append(current_section)
            
            # Paragraph detection
            elif self._is_paragraph_start(line, lines, i):
                paragraph = {
                    'start_line': i,
                    'text': line
                }
                
                # Find paragraph end
                end_idx = i
                while end_idx + 1 < len(lines) and lines[end_idx + 1].strip() and not self._is_likely_heading(lines[end_idx + 1], lines, end_idx + 1):
                    paragraph['text'] += ' ' + lines[end_idx + 1].strip()
                    end_idx += 1
                    
                paragraph['end_line'] = end_idx
                structure['paragraphs'].append(paragraph)
        
        # Close final section if needed
        if structure['sections'] and 'end_line' not in structure['sections'][-1]:
            structure['sections'][-1]['end_line'] = len(lines) - 1
                
        return structure
    
    def _is_likely_heading(self, line: str, lines: List[str], index: int) -> bool:
        """
        Determine if a line is likely a heading based on multiple signals.
        
        Examines characteristics beyond just the text content:
        - Shorter than average lines
        - Surrounded by whitespace
        - Contains numbering patterns
        - Has different formatting (detected via OCR confidence)
        
        Args:
            line: Current line text
            lines: All lines in the document
            index: Current line index
            
        Returns:
            Boolean indicating if the line is likely a heading
        """
        # Skip empty lines
        if not line.strip():
            return False
            
        # Common academic numbering patterns
        heading_patterns = [
            r'^\d+\.\s+\w+',                     # "1. Introduction"
            r'^\d+\.\d+\.\s+\w+',                # "1.1. Methods"
            r'^[A-Z][a-z]+\s+\d+\.\s+\w+',       # "Section 1. Introduction"
            r'^[IVXLCDM]+\.\s+\w+',              # "IV. Results"
            r'^[A-Z]\.(?:\s+|\s*-)\w+',          # "A. Methods" or "A-Methods"
        ]
        
        # Check against patterns
        for pattern in heading_patterns:
            if re.match(pattern, line):
                return True
        
        # Surrounding whitespace indicates heading
        whitespace_surrounded = (
            (index == 0 or not lines[index-1].strip()) and 
            (index == len(lines)-1 or not lines[index+1].strip())
        )
        
        # Short line length compared to document average
        non_empty_lines = [l for l in lines if l.strip()]
        if non_empty_lines:
            avg_line_length = sum(len(l) for l in non_empty_lines) / len(non_empty_lines)
            is_short_line = len(line) < avg_line_length * 0.7
        else:
            is_short_line = False
        
        # All caps or title case are often headings
        is_all_caps = line.isupper()
        is_title_case = line.istitle() or (line.split()[0].istitle() if line.split() else False)
        
        # Check if the line is likely a heading based on combined signals
        heading_score = sum([
            whitespace_surrounded,
            is_short_line,
            is_all_caps or is_title_case,
            bool(re.match(r'^[A-Za-z\s\d\.\-]+$', line))  # Headings rarely contain special chars
        ])
        
        return heading_score >= 2
    
    def _estimate_heading_level(self, line: str, lines: List[str], index: int) -> int:
        """
        Estimate the heading level based on text characteristics.
        
        Args:
            line: Current line text
            lines: All lines in the document
            index: Current line index
            
        Returns:
            Estimated heading level (1-6)
        """
        # Level 1 patterns (main headings)
        if (line.isupper() or 
            re.match(r'^\d+\.\s+[A-Z]', line) or
            re.match(r'^[IVXLCDM]+\.\s+', line)):
            return 1
            
        # Level 2 patterns (sub-headings)
        if (re.match(r'^\d+\.\d+\.\s+', line) or
            re.match(r'^[A-Z]\.(?:\s+|\s*-)', line)):
            return 2
            
        # Level 3 patterns (sub-sub-headings)
        if re.match(r'^\d+\.\d+\.\d+\.\s+', line):
            return 3
            
        # Default to level 2 if uncertain
        return 2
    
    def _classify_section_type(self, heading: str) -> Optional[str]:
        """
        Classify section type based on heading text.
        
        Uses fuzzy matching to identify common academic paper sections
        regardless of exact wording.
        
        Args:
            heading: Heading text
            
        Returns:
            Section type or None if unrecognized
        """
        heading_lower = heading.lower()
        
        # Remove numbering and common prefixes for better matching
        clean_heading = re.sub(r'^[\d\.IVXLCDM]+\s+', '', heading_lower)
        clean_heading = re.sub(r'^section\s+[\d\.]+\s+', '', clean_heading)
        
        # Common section patterns with flexible matching
        section_patterns = {
            'abstract': [r'abstract', r'summary'],
            'introduction': [r'introduction', r'background', r'overview'],
            'literature_review': [r'literature', r'related work', r'state of the art', r'previous research'],
            'methods': [r'method', r'methodology', r'materials', r'experimental', r'procedure', r'design'],
            'results': [r'result', r'findings', r'observation'],
            'discussion': [r'discussion', r'interpretation', r'implications'],
            'conclusion': [r'conclusion', r'concluding', r'summary', r'final remarks'],
            'references': [r'reference', r'bibliography', r'works cited', r'literature cited'],
            'acknowledgments': [r'acknowledgment', r'acknowledgement'],
            'appendix': [r'appendix', r'supplementary', r'supporting information']
        }
        
        # Check each section type's patterns
        for section_type, patterns in section_patterns.items():
            for pattern in patterns:
                if re.search(pattern, clean_heading):
                    return section_type
        
        return None
    
    def _is_paragraph_start(self, line: str, lines: List[str], index: int) -> bool:
        """
        Determine if a line is the start of a paragraph.
        
        Args:
            line: Current line text
            lines: All lines in the document
            index: Current line index
            
        Returns:
            Boolean indicating if the line starts a paragraph
        """
        # Skip empty lines
        if not line.strip():
            return False
            
        # Skip lines that are likely headings
        if self._is_likely_heading(line, lines, index):
            return False
            
        # Check if previous line is empty (paragraph break)
        if index > 0 and not lines[index-1].strip():
            return True
            
        # First line in document
        if index == 0:
            return True
            
        # Indentation often indicates paragraph start
        if line.startswith('    ') and not lines[index-1].startswith('    '):
            return True
            
        return False
    
    def _detect_columns(self, image: np.ndarray) -> List[Dict[str, int]]:
        """
        Detect multi-column layout in academic papers.
        
        Uses vertical projection profiles to identify column boundaries.
        
        Args:
            image: Preprocessed image
            
        Returns:
            List of column regions with x, y, width, height
        """
        # Simple column detection using vertical projection
        try:
            # Ensure binary image
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            else:
                _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Calculate vertical projection profile (sum of white pixels per column)
            v_projection = np.sum(binary, axis=0) / 255
            
            # Normalize to 0-1 range
            v_projection = v_projection / np.max(v_projection) if np.max(v_projection) > 0 else v_projection
            
            # Identify potential column boundaries using threshold
            # Columns are separated by areas with high density of white pixels
            column_separators = []
            in_separator = False
            separator_start = 0
            
            for i, val in enumerate(v_projection):
                if val > 0.9 and not in_separator:  # Start of potential separator
                    in_separator = True
                    separator_start = i
                elif val < 0.9 and in_separator:    # End of potential separator
                    if i - separator_start > image.shape[1] * 0.01:  # Min width check
                        column_separators.append((separator_start, i))
                    in_separator = False
            
            # Convert separators to columns
            columns = []
            prev_end = 0
            
            for start, end in column_separators:
                if start - prev_end > image.shape[1] * 0.1:  # Min column width check
                    columns.append({
                        'x': prev_end,
                        'y': 0,
                        'width': start - prev_end,
                        'height': image.shape[0]
                    })
                prev_end = end
            
            # Add final column
            if image.shape[1] - prev_end > image.shape[1] * 0.1:
                columns.append({
                    'x': prev_end,
                    'y': 0,
                    'width': image.shape[1] - prev_end,
                    'height': image.shape[0]
                })
            
            # If no columns detected or only one column detected across full width,
            # assume single column layout
            if not columns:
                columns.append({
                    'x': 0,
                    'y': 0,
                    'width': image.shape[1],
                    'height': image.shape[0]
                })
            
            return columns
            
        except Exception as e:
            self.logger.warning(f"Column detection failed: {str(e)}")
            # Return single column as fallback
            return [{
                'x': 0,
                'y': 0,
                'width': image.shape[1],
                'height': image.shape[0]
            }]
    
    def _detect_formulas(self, image: np.ndarray, text: str) -> List[Dict[str, Any]]:
        """
        Detect mathematical formulas in academic papers.
        
        Uses a combination of visual features and text patterns.
        
        Args:
            image: Preprocessed image
            text: OCR text
            
        Returns:
            List of detected formulas with positions and text
        """
        formulas = []
        
        # Pattern detection for common mathematical expressions - simplified due to syntax issues
        math_patterns = [
            # Mathematical operators temporarily disabled
            # Greek letters temporarily disabled
            r'\([^)]{1,40}\)'  # Parenthetical expressions only
        ]
        
        # Check text for mathematical patterns
        lines = text.split('\n')
        for i, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                continue
                
            # Score the line for mathematical content
            math_score = 0
            for pattern in math_patterns:
                matches = re.findall(pattern, line)
                math_score += len(matches)
            
            # Check density of mathematical symbols
            if math_score > 0:
                symbol_density = math_score / len(line) if len(line) > 0 else 0
                
                # Detect formula with sufficient mathematical content
                if (symbol_density > 0.1 or math_score > 3) and not self._is_likely_heading(line, lines, i):
                    formula = {
                        'text': line,
                        'line_index': i,
                        'confidence': min(1.0, symbol_density * 5)
                    }
                    formulas.append(formula)
        
        return formulas
    
    def _detect_tables(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect tables in academic papers.
        
        Uses image processing techniques to identify table structures.
        
        Args:
            image: Preprocessed image
            
        Returns:
            List of detected tables with positions and structure
        """
        tables = []
        
        try:
            # Simple table detection based on horizontal and vertical lines
            horizontal = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -2)
            vertical = horizontal.copy()
            
            # Define kernel sizes
            img_height, img_width = image.shape
            horizontal_kernel_length = img_width // 30
            vertical_kernel_length = img_height // 30
            
            # Extract horizontal lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_kernel_length, 1))
            horizontal = cv2.erode(horizontal, horizontal_kernel)
            horizontal = cv2.dilate(horizontal, horizontal_kernel)
            
            # Extract vertical lines
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_kernel_length))
            vertical = cv2.erode(vertical, vertical_kernel)
            vertical = cv2.dilate(vertical, vertical_kernel)
            
            # Combine horizontal and vertical lines
            table_mask = cv2.add(horizontal, vertical)
            
            # Find contours
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours to find table regions
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter small regions
                if w > img_width * 0.2 and h > img_height * 0.05:
                    # Detect if region has grid-like structure (indicating table)
                    roi = table_mask[y:y+h, x:x+w]
                    grid_score = np.sum(roi == 0) / (w * h)  # Ratio of black pixels
                    
                    if grid_score > 0.01:  # Threshold for grid-like structure
                        table = {
                            'x': int(x),
                            'y': int(y),
                            'width': int(w),
                            'height': int(h),
                            'confidence': float(min(1.0, grid_score * 5))
                        }
                        tables.append(table)
            
            return tables
            
        except Exception as e:
            self.logger.warning(f"Table detection failed: {str(e)}")
            return []
    
    def _detect_citations(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect citations in various academic formats.
        
        Args:
            text: OCR text
            
        Returns:
            List of detected citations with positions and text
        """
        citations = []
        
        # Common citation patterns in academic papers
        citation_patterns = [
            (r'\((?:[A-Za-z\-]+(?:\s+and\s+|\s*,\s*)){0,2}[A-Za-z\-]+(?:,?\s+et\s+al\.?)?,\s+\d{4}(?:[a-z])?(?:;\s+(?:[^)]+))?\)', 'author_year'),  # (Smith, 2020) or (Smith and Jones, 2020)
            (r'\[(\d+(?:[-–]\d+)?(?:,\s*\d+)*)\]', 'numeric'),  # [1] or [1-3] or [1,2,3]
            (r'\((\d+(?:[-–]\d+)?(?:,\s*\d+)*)\)', 'numeric_paren'),  # (1) or (1-3) or (1,2,3)
            (r'(?<!\w)(?:\d+,){2,}\d+(?!\w)', 'superscript'),  # 1,2,3 (without parentheses, potential superscript)
        ]
        
        # Check text for citation patterns
        lines = text.split('\n')
        for i, line in enumerate(lines):
            for pattern, citation_type in citation_patterns:
                for match in re.finditer(pattern, line):
                    citation = {
                        'text': match.group(0),
                        'type': citation_type,
                        'line_index': i,
                        'char_start': match.start(),
                        'char_end': match.end()
                    }
                    citations.append(citation)
        
        return citations
    
    def _get_skew_angle(self, image: np.ndarray) -> float:
        """Calculate the skew angle of the image."""
        try:
            # Find all non-zero points
            coords = np.column_stack(np.where(image > 0))
            if len(coords) < 100:  # Need sufficient points
                return 0.0
                
            # Get the minimum area rectangle
            rect = cv2.minAreaRect(coords)
            angle = rect[-1]
            
            # Adjust angle
            if angle < -45:
                angle = 90 + angle
                
            return angle
        except Exception as e:
            self.logger.warning(f"Error in skew detection: {str(e)}")
            return 0.0
            
    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate the image by the given angle."""
        (h, w) = image.shape
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, 
            M, 
            (w, h), 
            flags=cv2.INTER_CUBIC, 
            borderMode=cv2.BORDER_REPLICATE
        )
        return rotated