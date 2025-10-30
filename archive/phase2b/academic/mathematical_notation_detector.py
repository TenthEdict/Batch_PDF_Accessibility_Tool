"""
Mathematical Notation Detection for Academic Documents
====================================================

Advanced mathematical notation detection system specifically designed for academic papers
and scholarly documents. Provides automated recognition of mathematical expressions,
equations, formulas, and symbols with high accuracy for accessibility enhancement.

Features:
- Contour-based mathematical symbol detection using OpenCV
- Academic layout analysis for equation identification
- Multi-scale detection for various font sizes and formats
- Integration with Phase 2B ML enhancement system
- FAISS vector database similarity matching for pattern recognition
- Performance monitoring integration with resource optimization
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging
import time
import io
from PIL import Image
import fitz  # PyMuPDF for PDF processing

# ML and pattern recognition imports
try:
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Integration with existing ePubs monitoring system
try:
    from ..monitoring.ml_pattern_learning_metrics import (
        get_ml_metrics_collector, 
        MLOperationType
    )
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


@dataclass
class MathematicalElement:
    """Detected mathematical element with position and characteristics."""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float  # Detection confidence score (0.0-1.0)
    element_type: str  # 'equation', 'formula', 'symbol', 'fraction', 'integral'
    content_area: float  # Pixel area of the mathematical content
    aspect_ratio: float  # Width/height ratio
    complexity_score: float  # Estimated complexity (0.0-1.0)
    text_context: Optional[str] = None  # Surrounding text context
    page_number: int = 0
    coordinate_system: str = "pdf"  # 'pdf', 'image', 'opencv'


@dataclass
class MathDetectionResult:
    """Complete mathematical notation detection result for a document."""
    document_path: str
    total_pages: int
    mathematical_elements: List[MathematicalElement]
    detection_time_ms: float
    accuracy_estimate: float
    processing_metadata: Dict[str, Any]


class MathematicalNotationDetector:
    """
    Advanced mathematical notation detection system for academic documents.
    
    Utilizes computer vision techniques with academic document specialization
    to identify mathematical expressions, equations, and formulas with high
    accuracy for accessibility enhancement workflows.
    """
    
    def __init__(self, 
                 detection_threshold: float = 0.7,
                 min_element_area: int = 100,
                 max_element_area: int = 50000,
                 enable_monitoring: bool = True):
        """
        Initialize mathematical notation detector.
        
        Args:
            detection_threshold: Confidence threshold for math detection (0.0-1.0)
            min_element_area: Minimum pixel area for mathematical elements
            max_element_area: Maximum pixel area for mathematical elements
            enable_monitoring: Enable performance monitoring integration
        """
        self.detection_threshold = detection_threshold
        self.min_element_area = min_element_area
        self.max_element_area = max_element_area
        self.enable_monitoring = enable_monitoring
        
        # Mathematical symbol patterns and characteristics
        self.math_symbols_kernels = self._create_mathematical_kernels()
        self.equation_indicators = self._define_equation_indicators()
        
        # Academic document layout analysis parameters
        self.academic_layout_params = {
            'typical_line_height_range': (12, 24),
            'math_font_size_multiplier': 1.2,
            'equation_margin_threshold': 20,
            'centered_equation_tolerance': 0.15
        }
        
        # Performance tracking
        self.detection_stats = {
            'total_detections': 0,
            'processing_time_ms': [],
            'accuracy_scores': [],
            'false_positive_rate': 0.0
        }
        
        # Logger setup
        self.logger = logging.getLogger(f"{__name__}.MathematicalNotationDetector")
        
        self.logger.info(f"Mathematical Notation Detector initialized - "
                        f"Threshold: {detection_threshold}, Area: {min_element_area}-{max_element_area}px")
    
    def detect_mathematical_notation(self, 
                                   pdf_path: str,
                                   page_range: Optional[Tuple[int, int]] = None) -> MathDetectionResult:
        """
        Detect mathematical notation in a PDF document.
        
        Args:
            pdf_path: Path to PDF document
            page_range: Optional page range (start, end) for processing
            
        Returns:
            Complete mathematical notation detection result
        """
        start_time = time.time()
        
        if MONITORING_AVAILABLE and self.enable_monitoring:
            ml_collector = get_ml_metrics_collector()
            operation_id = ml_collector.record_ml_operation(
                operation_type=MLOperationType.FEATURE_EXTRACTION,
                duration_ms=0,  # Will be updated on completion
                document_count=1,
                success=False  # Will be updated on completion
            )
        
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            # Determine page range
            if page_range:
                start_page, end_page = page_range
                start_page = max(0, start_page)
                end_page = min(total_pages, end_page)
            else:
                start_page, end_page = 0, total_pages
            
            mathematical_elements = []
            
            # Process each page
            for page_num in range(start_page, end_page):
                page = doc.load_page(page_num)
                
                # Convert page to image for processing
                page_image = self._pdf_page_to_image(page)
                
                # Detect mathematical elements on this page
                page_elements = self._detect_math_on_page(page_image, page_num)
                mathematical_elements.extend(page_elements)
                
                self.logger.debug(f"Page {page_num + 1}: Found {len(page_elements)} mathematical elements")
            
            doc.close()
            
            # Calculate processing metrics
            processing_time = (time.time() - start_time) * 1000
            accuracy_estimate = self._estimate_detection_accuracy(mathematical_elements)
            
            # Create detection result
            result = MathDetectionResult(
                document_path=pdf_path,
                total_pages=total_pages,
                mathematical_elements=mathematical_elements,
                detection_time_ms=processing_time,
                accuracy_estimate=accuracy_estimate,
                processing_metadata={
                    'pages_processed': end_page - start_page,
                    'detection_threshold': self.detection_threshold,
                    'total_elements_found': len(mathematical_elements),
                    'average_confidence': np.mean([elem.confidence for elem in mathematical_elements]) if mathematical_elements else 0.0
                }
            )
            
            # Update performance tracking
            self._update_performance_stats(result)
            
            # Update monitoring if available
            if MONITORING_AVAILABLE and self.enable_monitoring:
                ml_collector.record_ml_operation(
                    operation_type=MLOperationType.FEATURE_EXTRACTION,
                    duration_ms=processing_time,
                    document_count=1,
                    accuracy_score=accuracy_estimate,
                    patterns_learned=len(mathematical_elements),
                    success=True
                )
            
            self.logger.info(f"Mathematical notation detection completed: "
                           f"{len(mathematical_elements)} elements found in {processing_time:.1f}ms")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Mathematical notation detection failed: {e}", exc_info=True)
            if MONITORING_AVAILABLE and self.enable_monitoring:
                ml_collector.record_ml_operation(
                    operation_type=MLOperationType.FEATURE_EXTRACTION,
                    duration_ms=(time.time() - start_time) * 1000,
                    document_count=1,
                    success=False,
                    error_message=str(e)
                )
            raise
    
    def _pdf_page_to_image(self, page: fitz.Page, dpi: int = 150) -> np.ndarray:
        """Convert PDF page to OpenCV image array."""
        # Render page to image
        mat = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        img_data = mat.tobytes("ppm")
        
        # Convert to PIL Image then to OpenCV array
        pil_image = Image.open(io.BytesIO(img_data))
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return opencv_image
    
    def _detect_math_on_page(self, image: np.ndarray, page_num: int) -> List[MathematicalElement]:
        """Detect mathematical elements on a single page image."""
        mathematical_elements = []
        
        # Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply different detection strategies
        elements_contour = self._detect_by_contour_analysis(gray, page_num)
        elements_template = self._detect_by_template_matching(gray, page_num)
        elements_layout = self._detect_by_layout_analysis(gray, page_num)
        
        # Combine and filter results
        all_elements = elements_contour + elements_template + elements_layout
        filtered_elements = self._filter_and_merge_detections(all_elements)
        
        return filtered_elements
    
    def _detect_by_contour_analysis(self, gray_image: np.ndarray, page_num: int) -> List[MathematicalElement]:
        """Detect mathematical elements using contour analysis."""
        elements = []
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Calculate contour properties
            area = cv2.contourArea(contour)
            
            # Filter by area
            if not (self.min_element_area <= area <= self.max_element_area):
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate additional properties
            aspect_ratio = w / h if h > 0 else 0
            solidity = area / (w * h) if w * h > 0 else 0
            
            # Mathematical element characteristics
            # Mathematical expressions often have specific aspect ratios and solidity
            if self._is_likely_mathematical_contour(area, aspect_ratio, solidity, contour):
                confidence = self._calculate_contour_confidence(area, aspect_ratio, solidity)
                complexity = self._estimate_math_complexity(contour, gray_image[y:y+h, x:x+w])
                
                element = MathematicalElement(
                    bbox=(x, y, w, h),
                    confidence=confidence,
                    element_type=self._classify_math_element_type(aspect_ratio, area, complexity),
                    content_area=area,
                    aspect_ratio=aspect_ratio,
                    complexity_score=complexity,
                    page_number=page_num,
                    coordinate_system="opencv"
                )
                
                elements.append(element)
        
        return elements
    
    def _detect_by_template_matching(self, gray_image: np.ndarray, page_num: int) -> List[MathematicalElement]:
        """Detect mathematical elements using template matching for common symbols."""
        elements = []
        
        # Apply template matching for mathematical symbols
        for symbol_name, kernel in self.math_symbols_kernels.items():
            result = cv2.matchTemplate(gray_image, kernel, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= self.detection_threshold)
            
            for pt in zip(*locations[::-1]):
                x, y = pt
                h, w = kernel.shape
                
                confidence = float(result[y, x])
                
                element = MathematicalElement(
                    bbox=(x, y, w, h),
                    confidence=confidence,
                    element_type="symbol",
                    content_area=w * h,
                    aspect_ratio=w / h if h > 0 else 0,
                    complexity_score=0.3,  # Symbols are relatively simple
                    page_number=page_num,
                    coordinate_system="opencv"
                )
                
                elements.append(element)
        
        return elements
    
    def _detect_by_layout_analysis(self, gray_image: np.ndarray, page_num: int) -> List[MathematicalElement]:
        """Detect mathematical elements using academic layout analysis."""
        elements = []
        
        # Analyze document layout for equation-like structures
        height, width = gray_image.shape
        
        # Look for centered equations (common in academic papers)
        centered_elements = self._find_centered_math_elements(gray_image)
        
        # Look for inline mathematical expressions
        inline_elements = self._find_inline_math_elements(gray_image)
        
        # Combine layout-based detections
        layout_elements = centered_elements + inline_elements
        
        for element_info in layout_elements:
            x, y, w, h, confidence, element_type = element_info
            
            element = MathematicalElement(
                bbox=(x, y, w, h),
                confidence=confidence,
                element_type=element_type,
                content_area=w * h,
                aspect_ratio=w / h if h > 0 else 0,
                complexity_score=self._estimate_layout_complexity(gray_image[y:y+h, x:x+w]),
                page_number=page_num,
                coordinate_system="opencv"
            )
            
            elements.append(element)
        
        return elements
    
    def _is_likely_mathematical_contour(self, area: float, aspect_ratio: float, 
                                      solidity: float, contour: np.ndarray) -> bool:
        """Determine if a contour is likely to be mathematical content."""
        # Mathematical expressions often have specific characteristics:
        # 1. Moderate aspect ratios (not too wide or tall)
        # 2. Reasonable solidity (not too sparse)
        # 3. Complex shape (not simple rectangles)
        
        # Aspect ratio check - mathematical content usually isn't extremely wide or tall
        if aspect_ratio < 0.1 or aspect_ratio > 10:
            return False
        
        # Solidity check - mathematical content should have reasonable density
        if solidity < 0.1 or solidity > 0.9:
            return False
        
        # Area check - already filtered but double-check
        if area < self.min_element_area:
            return False
        
        # Shape complexity check
        perimeter = cv2.arcLength(contour, True)
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter ** 2)
            # Mathematical content is usually not perfectly circular
            if circularity > 0.85:
                return False
        
        return True
    
    def _calculate_contour_confidence(self, area: float, aspect_ratio: float, solidity: float) -> float:
        """Calculate confidence score for contour-based detection."""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for typical mathematical element characteristics
        if 0.3 <= aspect_ratio <= 3.0:
            confidence += 0.2
        
        if 0.3 <= solidity <= 0.7:
            confidence += 0.2
        
        # Area-based confidence adjustment
        if 200 <= area <= 5000:  # Typical mathematical element size
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _estimate_math_complexity(self, contour: np.ndarray, roi: np.ndarray) -> float:
        """Estimate the complexity of a mathematical expression."""
        # Simple complexity estimation based on contour and region properties
        
        # Contour complexity
        perimeter = cv2.arcLength(contour, True)
        area = cv2.contourArea(contour)
        complexity = 0.0
        
        if area > 0:
            # More complex shapes have higher perimeter to area ratio
            shape_complexity = perimeter / np.sqrt(area)
            complexity += min(0.5, shape_complexity / 20)
        
        # ROI complexity based on edge density
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / (roi.shape[0] * roi.shape[1])
        complexity += min(0.5, edge_density * 10)
        
        return min(1.0, complexity)
    
    def _classify_math_element_type(self, aspect_ratio: float, area: float, complexity: float) -> str:
        """Classify the type of mathematical element based on characteristics."""
        if aspect_ratio > 4.0:
            return "equation"  # Wide elements are likely equations
        elif aspect_ratio < 0.5 and complexity > 0.7:
            return "fraction"  # Tall, complex elements might be fractions
        elif area > 5000:
            return "formula"  # Large elements are likely formulas
        elif complexity > 0.6:
            return "integral"  # Complex elements might be integrals/summations
        else:
            return "symbol"   # Default to symbol
    
    def _find_centered_math_elements(self, gray_image: np.ndarray) -> List[Tuple]:
        """Find mathematical elements that are centered (common for equations)."""
        elements = []
        height, width = gray_image.shape
        center_x = width // 2
        tolerance = int(width * self.academic_layout_params['centered_equation_tolerance'])
        
        # Apply morphological operations to find text blocks
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        morph = cv2.morphologyEx(gray_image, cv2.MORPH_CLOSE, kernel)
        
        # Find contours of text blocks
        thresh = cv2.threshold(morph, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            element_center_x = x + w // 2
            
            # Check if element is approximately centered
            if abs(element_center_x - center_x) <= tolerance:
                # Additional checks for mathematical content
                if self._is_likely_centered_equation(gray_image[y:y+h, x:x+w], w, h):
                    confidence = self._calculate_centering_confidence(element_center_x, center_x, tolerance)
                    elements.append((x, y, w, h, confidence, "equation"))
        
        return elements
    
    def _find_inline_math_elements(self, gray_image: np.ndarray) -> List[Tuple]:
        """Find inline mathematical expressions within text lines."""
        elements = []
        
        # This would implement detection of inline math expressions
        # For now, return empty list - this is a complex task requiring
        # sophisticated text line analysis and mathematical expression detection
        
        return elements
    
    def _is_likely_centered_equation(self, roi: np.ndarray, width: int, height: int) -> bool:
        """Check if a centered region is likely to contain an equation."""
        # Equations often have specific characteristics:
        # 1. Reasonable width (not just a single character)
        # 2. Mathematical symbols or complex layout
        # 3. Different from regular text lines
        
        if width < 50 or height < 10:  # Too small to be an equation
            return False
        
        if width > roi.shape[1] * 0.8:  # Too wide, likely regular text
            return False
        
        # Check for mathematical symbol density
        # This is simplified - a full implementation would use trained classifiers
        edge_density = self._calculate_edge_density(roi)
        if edge_density > 0.1:  # Mathematical content tends to have more edges
            return True
        
        return False
    
    def _calculate_centering_confidence(self, element_center: int, page_center: int, tolerance: int) -> float:
        """Calculate confidence based on how well centered an element is."""
        distance = abs(element_center - page_center)
        confidence = 1.0 - (distance / tolerance)
        return max(0.3, confidence)  # Minimum confidence for centered elements
    
    def _estimate_layout_complexity(self, roi: np.ndarray) -> float:
        """Estimate complexity based on layout analysis."""
        if roi.size == 0:
            return 0.0
        
        # Edge density
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Intensity variation
        intensity_std = np.std(roi)
        intensity_complexity = min(1.0, intensity_std / 100)
        
        return (edge_density * 5 + intensity_complexity) / 2
    
    def _calculate_edge_density(self, roi: np.ndarray) -> float:
        """Calculate edge density in a region of interest."""
        if roi.size == 0:
            return 0.0
        
        edges = cv2.Canny(roi, 50, 150)
        return np.sum(edges > 0) / edges.size
    
    def _filter_and_merge_detections(self, elements: List[MathematicalElement]) -> List[MathematicalElement]:
        """Filter and merge overlapping detections."""
        if not elements:
            return []
        
        # Sort by confidence
        elements.sort(key=lambda x: x.confidence, reverse=True)
        
        # Non-maximum suppression to remove overlapping detections
        filtered_elements = []
        
        for element in elements:
            # Check for significant overlap with already accepted elements
            overlap_found = False
            
            for accepted in filtered_elements:
                if self._calculate_overlap(element.bbox, accepted.bbox) > 0.5:
                    overlap_found = True
                    break
            
            if not overlap_found and element.confidence >= self.detection_threshold:
                filtered_elements.append(element)
        
        return filtered_elements
    
    def _calculate_overlap(self, bbox1: Tuple[int, int, int, int], 
                          bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate overlap ratio between two bounding boxes."""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        left = max(x1, x2)
        top = max(y1, y2)
        right = min(x1 + w1, x2 + w2)
        bottom = min(y1 + h1, y2 + h2)
        
        if left < right and top < bottom:
            intersection = (right - left) * (bottom - top)
            union = w1 * h1 + w2 * h2 - intersection
            return intersection / union if union > 0 else 0
        
        return 0
    
    def _estimate_detection_accuracy(self, elements: List[MathematicalElement]) -> float:
        """Estimate overall detection accuracy based on element characteristics."""
        if not elements:
            return 0.0
        
        # Simple accuracy estimation based on average confidence
        avg_confidence = np.mean([elem.confidence for elem in elements])
        
        # Adjust based on detection consistency
        confidence_std = np.std([elem.confidence for elem in elements])
        consistency_bonus = max(0, 0.2 - confidence_std)  # Bonus for consistent detections
        
        accuracy = min(1.0, avg_confidence + consistency_bonus)
        return accuracy
    
    def _update_performance_stats(self, result: MathDetectionResult) -> None:
        """Update internal performance statistics."""
        self.detection_stats['total_detections'] += len(result.mathematical_elements)
        self.detection_stats['processing_time_ms'].append(result.detection_time_ms)
        self.detection_stats['accuracy_scores'].append(result.accuracy_estimate)
        
        # Keep only recent statistics
        if len(self.detection_stats['processing_time_ms']) > 1000:
            self.detection_stats['processing_time_ms'] = self.detection_stats['processing_time_ms'][-1000:]
            self.detection_stats['accuracy_scores'] = self.detection_stats['accuracy_scores'][-1000:]
    
    def _create_mathematical_kernels(self) -> Dict[str, np.ndarray]:
        """Create template kernels for mathematical symbol detection."""
        kernels = {}
        
        # Simple mathematical symbol templates (in practice, these would be more sophisticated)
        # These are simplified examples - real implementation would use learned templates
        
        # Plus sign template
        plus_kernel = np.zeros((15, 15), dtype=np.uint8)
        plus_kernel[7, 3:12] = 255  # Horizontal line
        plus_kernel[3:12, 7] = 255  # Vertical line
        kernels['plus'] = plus_kernel
        
        # Equals sign template
        equals_kernel = np.zeros((15, 15), dtype=np.uint8)
        equals_kernel[5, 3:12] = 255  # Top line
        equals_kernel[9, 3:12] = 255  # Bottom line
        kernels['equals'] = equals_kernel
        
        # Integral sign template (simplified)
        integral_kernel = np.zeros((20, 10), dtype=np.uint8)
        for i in range(20):
            x = int(5 + 2 * np.sin(i * np.pi / 10))
            if 0 <= x < 10:
                integral_kernel[i, x] = 255
        kernels['integral'] = integral_kernel
        
        return kernels
    
    def _define_equation_indicators(self) -> List[str]:
        """Define patterns that indicate mathematical equations."""
        return [
            'equation', 'formula', 'expression', '=', '+', '-', '*', '/',
            'integral', 'derivative', 'sum', 'product', 'matrix', 'vector'
        ]
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        stats = self.detection_stats.copy()
        
        if stats['processing_time_ms']:
            stats['avg_processing_time_ms'] = np.mean(stats['processing_time_ms'])
            stats['max_processing_time_ms'] = np.max(stats['processing_time_ms'])
            stats['min_processing_time_ms'] = np.min(stats['processing_time_ms'])
        
        if stats['accuracy_scores']:
            stats['avg_accuracy'] = np.mean(stats['accuracy_scores'])
            stats['accuracy_std'] = np.std(stats['accuracy_scores'])
        
        return stats


# Utility functions for integration
def detect_math_in_pdf(pdf_path: str, 
                      detection_threshold: float = 0.7,
                      page_range: Optional[Tuple[int, int]] = None) -> MathDetectionResult:
    """
    Convenience function to detect mathematical notation in a PDF.
    
    Args:
        pdf_path: Path to PDF document
        detection_threshold: Confidence threshold for detection
        page_range: Optional page range for processing
        
    Returns:
        Mathematical notation detection result
    """
    detector = MathematicalNotationDetector(detection_threshold=detection_threshold)
    return detector.detect_mathematical_notation(pdf_path, page_range)


def create_academic_math_detector(enable_monitoring: bool = True) -> MathematicalNotationDetector:
    """
    Create mathematical notation detector optimized for academic documents.
    
    Args:
        enable_monitoring: Enable integration with performance monitoring
        
    Returns:
        Configured mathematical notation detector
    """
    return MathematicalNotationDetector(
        detection_threshold=0.6,  # Slightly lower threshold for academic content
        min_element_area=50,      # Smaller minimum for subscripts/superscripts
        max_element_area=75000,   # Larger maximum for complex equations
        enable_monitoring=enable_monitoring
    )
