# src/accessibility_checker/ocr/adaptive_config.py

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
import logging
from dataclasses import dataclass
import fitz
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

@dataclass
class DocumentCharacteristics:
    """Stores analyzed characteristics of a document"""
    avg_text_density: float
    avg_font_size: float
    has_math_content: bool
    has_tables: bool
    image_quality_score: float
    language_script: str
    layout_complexity: float
    skew_angle: float

class AdaptiveOCRConfig:
    """Adaptive OCR configuration handler that optimizes settings based on document characteristics."""
    
    def __init__(self, base_config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.base_config = base_config
        
        # Define PSM mode mappings based on document characteristics
        self.psm_mappings = {
            'simple': 3,  # Simple layout - Fully automatic page segmentation
            'complex': 6,  # Complex layout - Uniform block of text
            'table_heavy': 4,  # Tables - Assume a variable-sized page
            'mixed': 11,  # Mixed content - Sparse text with OSD
            'single_column': 1,  # Single column - Automatic page segmentation with OSD
            'multi_column': 2,  # Multi-column - Automatic page segmentation without OSD
        }
        
    def analyze_document(self, pdf_path: str) -> DocumentCharacteristics:
        """Analyze document characteristics with improved error handling and detection."""
        try:
            # Convert first few pages to images for analysis
            pages = convert_from_path(pdf_path, first_page=1, last_page=min(5, self._get_page_count(pdf_path)))
            
            metrics = {
                'text_density': [],
                'font_size': [],
                'quality': [],
                'complexity': [],
                'skew': []
            }
            
            math_content_detected = False
            tables_detected = False
            
            for page in pages:
                try:
                    # Convert PIL image to OpenCV format
                    img_np = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
                    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
                    
                    # Calculate metrics for this page
                    page_metrics = self._calculate_page_metrics(gray)
                    for key in metrics:
                        if key in page_metrics:
                            metrics[key].append(page_metrics[key])
                    
                    # Update content detection flags
                    if self._detect_math_symbols(gray):
                        math_content_detected = True
                    if self._detect_tables(gray):
                        tables_detected = True
                        
                except Exception as e:
                    self.logger.warning(f"Error analyzing page: {str(e)}")
                    continue
            
            # Calculate aggregate metrics
            return DocumentCharacteristics(
                avg_text_density=np.mean(metrics['text_density']) if metrics['text_density'] else 0,
                avg_font_size=np.mean(metrics['font_size']) if metrics['font_size'] else 0,
                has_math_content=math_content_detected,
                has_tables=tables_detected,
                image_quality_score=np.mean(metrics['quality']) if metrics['quality'] else 0,
                language_script=self._detect_primary_script(pages[0]),
                layout_complexity=np.mean(metrics['complexity']) if metrics['complexity'] else 0,
                skew_angle=np.mean(metrics['skew']) if metrics['skew'] else 0
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing document: {str(e)}")
            raise

    def _calculate_page_metrics(self, image: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive page metrics."""
        metrics = {}
        
        try:
            # Calculate text density
            _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            metrics['text_density'] = np.sum(binary == 0) / binary.size
            
            # Estimate font size using connected components
            components = cv2.connectedComponentsWithStats(cv2.bitwise_not(binary), 4, cv2.CV_32S)
            if components[0] > 1:
                heights = components[2][1:, cv2.CC_STAT_HEIGHT]
                metrics['font_size'] = np.median(heights[heights < np.percentile(heights, 95)])
            
            # Calculate image quality
            metrics['quality'] = self._calculate_image_quality(image)
            
            # Calculate layout complexity
            metrics['complexity'] = self._calculate_layout_complexity(image)
            
            # Calculate skew angle
            metrics['skew'] = abs(self._calculate_skew_angle(image))
            
        except Exception as e:
            self.logger.warning(f"Error calculating page metrics: {str(e)}")
            
        return metrics

    def _get_page_count(self, pdf_path: str) -> int:
        """Get the total number of pages in the PDF."""
        try:
            with fitz.open(pdf_path) as doc:
                return len(doc)
        except Exception as e:
            self.logger.error(f"Error getting page count: {str(e)}")
            return 1  # Default to 1 page if we can't determine the count        
  
    def get_optimal_config(self, characteristics: DocumentCharacteristics) -> Dict[str, Any]:
        """Generate optimal OCR configuration based on document characteristics."""
        config = self.base_config.copy()
        
        # Adjust PSM mode based on layout complexity
        if characteristics.layout_complexity > 0.7:
            config['psm'] = self.psm_mappings['complex']
        elif characteristics.has_tables:
            config['psm'] = self.psm_mappings['table_heavy']
        elif characteristics.layout_complexity < 0.3:
            config['psm'] = self.psm_mappings['simple']
        else:
            config['psm'] = self.psm_mappings['mixed']
            
        # Adjust image preprocessing parameters
        if characteristics.image_quality_score < 0.6:
            config['preprocessing'] = {
                'enhance_contrast': True,
                'denoise': True,
                'sharpen': True
            }
        
        # Adjust character whitelist based on content
        if characteristics.has_math_content:
            # src/accessibility_checker/ocr/adaptive_config.py (continued)

            # Continuing from previous get_optimal_config method...
            config['char_whitelist'] += '+-=×÷()[]{}πΣ∫∂√∞∈∀∃≠≤≥±αβγδεθλμπσφω'
            
        # Adjust language settings
        if characteristics.language_script != 'Latin':
            config['oem'] = 1  # Use LSTM engine for non-Latin scripts
            
        # Adjust for skewed documents
        if characteristics.skew_angle > 0.5:
            config['deskew'] = True
            
        # Optimize for text density
        if characteristics.avg_text_density > 0.4:
            config['textord_min_linesize'] = 2.5
            
        # Adjust based on font size
        if characteristics.avg_font_size < 10:
            config['textord_min_xheight'] = 4
            config['enhance_resolution'] = True
            
        return config
        
    def _detect_math_symbols(self, image: np.ndarray) -> bool:
        """Detect presence of mathematical symbols in image."""
        # Use template matching for common math symbols
        math_symbols = ['Σ', '∫', '∂', '√', '∞', '≠', '≤', '≥', '±']
        text = pytesseract.image_to_string(
            image,
            config='--psm 11 --oem 3'
        )
        return any(symbol in text for symbol in math_symbols)
        
    def _detect_tables(self, image: np.ndarray) -> bool:
        """Detect presence of tables using line detection."""
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        if lines is not None:
            horizontal_lines = 0
            vertical_lines = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y2 - y1) < 10:  # Horizontal line
                    horizontal_lines += 1
                if abs(x2 - x1) < 10:  # Vertical line
                    vertical_lines += 1
            return horizontal_lines > 3 and vertical_lines > 3
        return False
        
    def _calculate_image_quality(self, image: np.ndarray) -> float:
        """Calculate image quality score."""
        # Calculate various quality metrics
        blur_score = cv2.Laplacian(image, cv2.CV_64F).var()
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contrast = np.std(image)
        
        # Normalize and combine scores
        blur_score_norm = min(1.0, blur_score / 500)
        contrast_norm = min(1.0, contrast / 127)
        
        return (blur_score_norm + contrast_norm) / 2
        
    def _calculate_layout_complexity(self, image: np.ndarray) -> float:
        """Calculate layout complexity score."""
        # Use connected components analysis
        _, labels, stats, _ = cv2.connectedComponentsWithStats(
            cv2.bitwise_not(image), 
            connectivity=8
        )
        
        if len(stats) < 2:  # No components found
            return 0.0
            
        # Calculate distribution of component sizes and positions
        heights = stats[1:, cv2.CC_STAT_HEIGHT]  # Skip background
        widths = stats[1:, cv2.CC_STAT_WIDTH]
        positions = stats[1:, [cv2.CC_STAT_LEFT, cv2.CC_STAT_TOP]]
        
        # Calculate variance in sizes and positions
        size_variance = np.var(heights) + np.var(widths)
        position_variance = np.var(positions, axis=0).sum()
        
        # Normalize and combine scores
        size_score = min(1.0, size_variance / (image.shape[0] * image.shape[1]))
        position_score = min(1.0, position_variance / (image.shape[0] * image.shape[1]))
        
        return (size_score + position_score) / 2
        
    def _calculate_skew_angle(self, image: np.ndarray) -> float:
        """Calculate document skew angle."""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) < 2:  # Not enough points
            return 0.0
            
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        return angle
        
    def _detect_primary_script(self, image: Image.Image) -> str:
        """Detect primary script (writing system) used in the document."""
        text = pytesseract.image_to_string(
            image,
            config='--psm 1 --oem 1'
        )
        
        # Simple script detection based on character ranges
        latin_chars = sum(1 for c in text if ord('a') <= ord(c.lower()) <= ord('z'))
        total_chars = len([c for c in text if c.strip()])
        
        return 'Latin' if total_chars == 0 or latin_chars / total_chars > 0.5 else 'Other'

    def _enhance_image_quality(self, image: np.ndarray, preprocessing_config: Dict[str, bool]) -> np.ndarray:
        """Apply image enhancement based on preprocessing configuration."""
        enhanced = image.copy()
        
        if preprocessing_config.get('enhance_contrast'):
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(enhanced)
            
        if preprocessing_config.get('denoise'):
            # Apply non-local means denoising
            enhanced = cv2.fastNlMeansDenoising(enhanced)
            
        if preprocessing_config.get('sharpen'):
            # Apply unsharp masking for sharpening
            blur = cv2.GaussianBlur(enhanced, (0, 0), 3)
            enhanced = cv2.addWeighted(enhanced, 1.5, blur, -0.5, 0)
            
        return enhanced

    def update_base_config(self, new_config: Dict[str, Any]) -> None:
        """Update the base configuration with new settings."""
        self.base_config.update(new_config)
        self.logger.info(f"Updated base configuration: {new_config}")
        
    def get_available_optimizations(self) -> Dict[str, str]:
        """Return dictionary of available optimization strategies."""
        return {
            'psm_modes': {
                str(mode): desc for mode, desc in {
                    3: 'Fully automatic page segmentation without OSD',
                    6: 'Assume a uniform block of text',
                    4: 'Assume a single column of variable-sized text',
                    11: 'Sparse text with OSD',
                    1: 'Automatic page segmentation with OSD',
                    2: 'Automatic page segmentation, no OSD or OCR'
                }.items()
            },
            'preprocessing': {
                'enhance_contrast': 'Improve image contrast using CLAHE',
                'denoise': 'Remove image noise',
                'sharpen': 'Enhance text edges'
            },
            'engine_modes': {
                '0': 'Legacy engine only',
                '1': 'Neural nets LSTM engine only',
                '2': 'Legacy + LSTM engines',
                '3': 'Default, based on what is available'
            }
        }
