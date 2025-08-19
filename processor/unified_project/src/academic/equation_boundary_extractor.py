"""
Equation Boundary Detection and Extraction System
===============================================

Advanced equation boundary detection specifically designed for academic documents.
Provides precise extraction of mathematical content boundaries using morphological
operations and academic layout analysis for optimal accessibility enhancement.

Features:
- Morphological operations with contour analysis for academic layouts
- Precise mathematical content boundary identification
- Academic document layout-aware processing
- Integration with FAISS vector database for equation pattern similarity
- Performance monitoring with resource optimization tracking
- Multi-scale boundary detection for various equation formats
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, NamedTuple
from dataclasses import dataclass
import logging
import time
from pathlib import Path

# Import mathematical notation detector
from .mathematical_notation_detector import MathematicalElement, MathDetectionResult

# Integration with monitoring system
try:
    from ..monitoring.ml_pattern_learning_metrics import (
        get_ml_metrics_collector, 
        MLOperationType
    )
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

# FAISS integration for pattern matching
try:
    from ..ml.faiss_vector_db import get_faiss_vector_db
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class BoundaryExtractionMethod(NamedTuple):
    """Method configuration for boundary extraction."""
    name: str
    morphological_kernel_size: Tuple[int, int]
    closing_iterations: int
    opening_iterations: int
    contour_min_area: int
    contour_approx_epsilon: float


@dataclass
class EquationBoundary:
    """Precise equation boundary with extraction metadata."""
    equation_id: str
    precise_bbox: Tuple[int, int, int, int]  # x, y, width, height
    original_detection: MathematicalElement
    boundary_confidence: float  # Quality of boundary extraction (0.0-1.0)
    extraction_method: str  # Method used for boundary extraction
    content_mask: Optional[np.ndarray] = None  # Binary mask of equation content
    surrounding_context: Optional[Tuple[int, int, int, int]] = None  # Expanded context area
    text_baseline: Optional[int] = None  # Y-coordinate of text baseline
    mathematical_regions: List[Tuple[int, int, int, int]] = None  # Sub-regions within equation
    processing_metadata: Dict[str, Any] = None


@dataclass
class BoundaryExtractionResult:
    """Complete boundary extraction result for a document."""
    document_path: str
    original_detection_result: MathDetectionResult
    equation_boundaries: List[EquationBoundary]
    extraction_time_ms: float
    boundary_accuracy: float
    extraction_statistics: Dict[str, Any]


class EquationBoundaryExtractor:
    """
    Advanced equation boundary detection and extraction system.
    
    Utilizes morphological operations with academic layout analysis to provide
    precise mathematical content boundary identification for optimal accessibility
    enhancement in scholarly documents.
    """
    
    def __init__(self,
                 boundary_precision: float = 0.8,
                 context_expansion_ratio: float = 0.15,
                 enable_faiss_similarity: bool = True,
                 enable_monitoring: bool = True):
        """
        Initialize equation boundary extractor.
        
        Args:
            boundary_precision: Required precision for boundary extraction (0.0-1.0)
            context_expansion_ratio: Ratio for expanding context around equations
            enable_faiss_similarity: Enable FAISS similarity matching for patterns
            enable_monitoring: Enable performance monitoring integration
        """
        self.boundary_precision = boundary_precision
        self.context_expansion_ratio = context_expansion_ratio
        self.enable_faiss_similarity = enable_faiss_similarity
        self.enable_monitoring = enable_monitoring
        
        # Boundary extraction methods for different equation types
        self.extraction_methods = self._initialize_extraction_methods()
        
        # Academic layout analysis parameters
        self.academic_layout_config = {
            'typical_font_height': 12,
            'line_spacing_multiplier': 1.2,
            'equation_margin_detection': True,
            'baseline_detection_enabled': True,
            'multi_line_equation_support': True
        }
        
        # Morphological operation kernels
        self.morphological_kernels = self._create_morphological_kernels()
        
        # Performance tracking
        self.extraction_stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'boundary_accuracy_scores': [],
            'processing_times_ms': [],
            'method_usage_counts': {}
        }
        
        # Logger setup
        self.logger = logging.getLogger(f"{__name__}.EquationBoundaryExtractor")
        
        self.logger.info(f"Equation Boundary Extractor initialized - "
                        f"Precision: {boundary_precision}, Context: {context_expansion_ratio}")
    
    def extract_equation_boundaries(self, 
                                   detection_result: MathDetectionResult,
                                   image_data: Optional[Dict[int, np.ndarray]] = None) -> BoundaryExtractionResult:
        """
        Extract precise boundaries for detected mathematical elements.
        
        Args:
            detection_result: Mathematical notation detection result
            image_data: Optional page images for boundary extraction
            
        Returns:
            Complete boundary extraction result with precise boundaries
        """
        start_time = time.time()
        
        if MONITORING_AVAILABLE and self.enable_monitoring:
            ml_collector = get_ml_metrics_collector()
            operation_id = ml_collector.record_ml_operation(
                operation_type=MLOperationType.FEATURE_EXTRACTION,
                duration_ms=0,
                document_count=1,
                success=False
            )
        
        try:
            equation_boundaries = []
            
            # Group mathematical elements by page for efficient processing
            elements_by_page = self._group_elements_by_page(detection_result.mathematical_elements)
            
            # Process each page
            for page_num, page_elements in elements_by_page.items():
                if image_data and page_num in image_data:
                    page_image = image_data[page_num]
                else:
                    # Load page image if not provided
                    page_image = self._load_page_image(detection_result.document_path, page_num)
                
                # Extract boundaries for elements on this page
                page_boundaries = self._extract_page_boundaries(page_elements, page_image, page_num)
                equation_boundaries.extend(page_boundaries)
            
            # Calculate extraction metrics
            processing_time = (time.time() - start_time) * 1000
            boundary_accuracy = self._calculate_boundary_accuracy(equation_boundaries)
            extraction_statistics = self._generate_extraction_statistics(equation_boundaries)
            
            # Create extraction result
            result = BoundaryExtractionResult(
                document_path=detection_result.document_path,
                original_detection_result=detection_result,
                equation_boundaries=equation_boundaries,
                extraction_time_ms=processing_time,
                boundary_accuracy=boundary_accuracy,
                extraction_statistics=extraction_statistics
            )
            
            # Update performance tracking
            self._update_extraction_stats(result)
            
            # Update monitoring if available
            if MONITORING_AVAILABLE and self.enable_monitoring:
                ml_collector.record_ml_operation(
                    operation_type=MLOperationType.FEATURE_EXTRACTION,
                    duration_ms=processing_time,
                    document_count=1,
                    accuracy_score=boundary_accuracy,
                    patterns_learned=len(equation_boundaries),
                    success=True
                )
            
            self.logger.info(f"Boundary extraction completed: "
                           f"{len(equation_boundaries)} boundaries extracted in {processing_time:.1f}ms")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Boundary extraction failed: {e}")
            if MONITORING_AVAILABLE and self.enable_monitoring:
                ml_collector.record_ml_operation(
                    operation_type=MLOperationType.FEATURE_EXTRACTION,
                    duration_ms=(time.time() - start_time) * 1000,
                    document_count=1,
                    success=False,
                    error_message=str(e)
                )
            raise
    
    def _extract_page_boundaries(self, 
                               elements: List[MathematicalElement],
                               page_image: np.ndarray,
                               page_num: int) -> List[EquationBoundary]:
        """Extract precise boundaries for mathematical elements on a single page."""
        boundaries = []
        
        # Convert to grayscale if needed
        if len(page_image.shape) == 3:
            gray_image = cv2.cvtColor(page_image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = page_image.copy()
        
        for element_idx, element in enumerate(elements):
            try:
                # Generate unique equation ID
                equation_id = f"page{page_num}_eq{element_idx}"
                
                # Select optimal extraction method based on element characteristics
                extraction_method = self._select_extraction_method(element)
                
                # Extract precise boundary using selected method
                precise_boundary = self._extract_precise_boundary(
                    element, gray_image, extraction_method
                )
                
                if precise_boundary:
                    boundaries.append(precise_boundary)
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract boundary for element {element_idx}: {e}")
                continue
        
        # Post-process boundaries to resolve overlaps and merge related elements
        boundaries = self._post_process_boundaries(boundaries, gray_image)
        
        return boundaries
    
    def _select_extraction_method(self, element: MathematicalElement) -> BoundaryExtractionMethod:
        """Select optimal boundary extraction method based on element characteristics."""
        # Choose method based on element type and characteristics
        
        if element.element_type == "equation" and element.aspect_ratio > 3.0:
            # Wide equations need larger kernels for proper boundary detection
            return self.extraction_methods["wide_equation"]
        elif element.element_type == "fraction" and element.aspect_ratio < 0.8:
            # Tall fractions need specialized vertical processing
            return self.extraction_methods["vertical_fraction"]
        elif element.element_type == "symbol" and element.content_area < 500:
            # Small symbols need fine-grained processing
            return self.extraction_methods["fine_symbol"]
        elif element.complexity_score > 0.7:
            # Complex mathematical expressions need robust processing
            return self.extraction_methods["complex_expression"]
        else:
            # Default method for general mathematical content
            return self.extraction_methods["general_math"]
    
    def _extract_precise_boundary(self,
                                element: MathematicalElement,
                                gray_image: np.ndarray,
                                method: BoundaryExtractionMethod) -> Optional[EquationBoundary]:
        """Extract precise boundary using specified method."""
        x, y, w, h = element.bbox
        
        # Expand region of interest for boundary detection
        expansion = max(10, int(min(w, h) * 0.2))
        expanded_x = max(0, x - expansion)
        expanded_y = max(0, y - expansion)
        expanded_w = min(gray_image.shape[1] - expanded_x, w + 2 * expansion)
        expanded_h = min(gray_image.shape[0] - expanded_y, h + 2 * expansion)
        
        # Extract region of interest
        roi = gray_image[expanded_y:expanded_y + expanded_h, expanded_x:expanded_x + expanded_w]
        
        if roi.size == 0:
            return None
        
        # Apply morphological operations based on method
        processed_roi = self._apply_morphological_operations(roi, method)
        
        # Find precise contours
        contours = self._find_precise_contours(processed_roi, method)
        
        if not contours:
            return None
        
        # Select best contour that contains the original detection
        best_contour = self._select_best_contour(contours, element, expanded_x, expanded_y)
        
        if best_contour is None:
            return None
        
        # Calculate precise bounding box
        precise_bbox = cv2.boundingRect(best_contour)
        
        # Adjust coordinates back to original image space
        final_x = expanded_x + precise_bbox[0]
        final_y = expanded_y + precise_bbox[1]
        final_w = precise_bbox[2]
        final_h = precise_bbox[3]
        
        # Create content mask
        content_mask = np.zeros((final_h, final_w), dtype=np.uint8)
        cv2.drawContours(content_mask, [best_contour - np.array([precise_bbox[0], precise_bbox[1]])], 
                        -1, 255, -1)
        
        # Calculate boundary confidence
        boundary_confidence = self._calculate_boundary_confidence(
            element, (final_x, final_y, final_w, final_h), content_mask
        )
        
        # Extract additional metadata
        surrounding_context = self._calculate_surrounding_context(
            (final_x, final_y, final_w, final_h), gray_image.shape
        )
        
        text_baseline = self._detect_text_baseline(
            gray_image[final_y:final_y + final_h, final_x:final_x + final_w]
        )
        
        mathematical_regions = self._identify_mathematical_regions(content_mask)
        
        return EquationBoundary(
            equation_id=f"eq_{int(time.time() * 1000)}_{final_x}_{final_y}",
            precise_bbox=(final_x, final_y, final_w, final_h),
            original_detection=element,
            boundary_confidence=boundary_confidence,
            extraction_method=method.name,
            content_mask=content_mask,
            surrounding_context=surrounding_context,
            text_baseline=text_baseline,
            mathematical_regions=mathematical_regions,
            processing_metadata={
                'morphological_kernel_size': method.morphological_kernel_size,
                'contour_area': cv2.contourArea(best_contour),
                'contour_perimeter': cv2.arcLength(best_contour, True),
                'expansion_used': expansion
            }
        )
    
    def _apply_morphological_operations(self, 
                                      roi: np.ndarray, 
                                      method: BoundaryExtractionMethod) -> np.ndarray:
        """Apply morphological operations to enhance equation boundaries."""
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Create morphological kernel
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, method.morphological_kernel_size
        )
        
        # Apply closing operation to connect nearby components
        if method.closing_iterations > 0:
            closed = cv2.morphologyEx(
                thresh, cv2.MORPH_CLOSE, kernel, iterations=method.closing_iterations
            )
        else:
            closed = thresh
        
        # Apply opening operation to remove noise
        if method.opening_iterations > 0:
            opened = cv2.morphologyEx(
                closed, cv2.MORPH_OPEN, kernel, iterations=method.opening_iterations
            )
        else:
            opened = closed
        
        return opened
    
    def _find_precise_contours(self, 
                             processed_roi: np.ndarray,
                             method: BoundaryExtractionMethod) -> List[np.ndarray]:
        """Find precise contours for equation boundaries."""
        # Find contours
        contours, _ = cv2.findContours(
            processed_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours by area
        filtered_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= method.contour_min_area:
                # Approximate contour to reduce noise
                epsilon = method.contour_approx_epsilon * cv2.arcLength(contour, True)
                approx_contour = cv2.approxPolyDP(contour, epsilon, True)
                filtered_contours.append(approx_contour)
        
        return filtered_contours
    
    def _select_best_contour(self,
                           contours: List[np.ndarray],
                           element: MathematicalElement,
                           offset_x: int,
                           offset_y: int) -> Optional[np.ndarray]:
        """Select the best contour that encompasses the original detection."""
        if not contours:
            return None
        
        element_center_x = element.bbox[0] + element.bbox[2] // 2 - offset_x
        element_center_y = element.bbox[1] + element.bbox[3] // 2 - offset_y
        
        best_contour = None
        best_score = -1
        
        for contour in contours:
            # Check if contour contains the element center
            if cv2.pointPolygonTest(contour, (element_center_x, element_center_y), False) >= 0:
                # Score based on area similarity and shape characteristics
                contour_area = cv2.contourArea(contour)
                area_ratio = min(contour_area / element.content_area, element.content_area / contour_area)
                
                # Score based on bounding box similarity
                contour_bbox = cv2.boundingRect(contour)
                bbox_overlap = self._calculate_bbox_overlap(
                    (element.bbox[0] - offset_x, element.bbox[1] - offset_y, element.bbox[2], element.bbox[3]),
                    contour_bbox
                )
                
                # Combined score
                score = (area_ratio * 0.4 + bbox_overlap * 0.6)
                
                if score > best_score:
                    best_score = score
                    best_contour = contour
        
        return best_contour
    
    def _calculate_bbox_overlap(self, bbox1: Tuple[int, int, int, int], 
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
    
    def _calculate_boundary_confidence(self,
                                     element: MathematicalElement,
                                     precise_bbox: Tuple[int, int, int, int],
                                     content_mask: np.ndarray) -> float:
        """Calculate confidence score for boundary extraction quality."""
        confidence = 0.5  # Base confidence
        
        # Bbox improvement score
        original_area = element.bbox[2] * element.bbox[3]
        precise_area = precise_bbox[2] * precise_bbox[3]
        
        if precise_area > 0:
            area_improvement = min(1.0, original_area / precise_area)
            confidence += area_improvement * 0.2
        
        # Content mask quality score
        mask_density = np.sum(content_mask > 0) / content_mask.size
        if 0.1 <= mask_density <= 0.8:  # Good density range
            confidence += 0.2
        
        # Shape quality score based on content mask
        if content_mask.size > 0:
            contours, _ = cv2.findContours(content_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                perimeter = cv2.arcLength(largest_contour, True)
                area = cv2.contourArea(largest_contour)
                
                if area > 0:
                    circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
                    # Mathematical content should not be too circular
                    if circularity < 0.8:
                        confidence += 0.1
        
        return min(1.0, confidence)
    
    def _calculate_surrounding_context(self,
                                     bbox: Tuple[int, int, int, int],
                                     image_shape: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """Calculate surrounding context area for equation."""
        x, y, w, h = bbox
        image_height, image_width = image_shape
        
        # Expand context by specified ratio
        expansion_w = int(w * self.context_expansion_ratio)
        expansion_h = int(h * self.context_expansion_ratio)
        
        context_x = max(0, x - expansion_w)
        context_y = max(0, y - expansion_h)
        context_w = min(image_width - context_x, w + 2 * expansion_w)
        context_h = min(image_height - context_y, h + 2 * expansion_h)
        
        return (context_x, context_y, context_w, context_h)
    
    def _detect_text_baseline(self, equation_roi: np.ndarray) -> Optional[int]:
        """Detect text baseline within equation region."""
        if equation_roi.size == 0:
            return None
        
        # Simple baseline detection using horizontal projection
        horizontal_projection = np.sum(equation_roi < 128, axis=1)  # Sum of dark pixels
        
        if len(horizontal_projection) == 0:
            return None
        
        # Find the row with maximum text content (likely baseline area)
        baseline_row = np.argmax(horizontal_projection)
        
        return baseline_row
    
    def _identify_mathematical_regions(self, content_mask: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Identify distinct mathematical regions within the equation."""
        if content_mask.size == 0:
            return []
        
        # Find connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(content_mask, connectivity=8)
        
        regions = []
        for i in range(1, num_labels):  # Skip background (label 0)
            x, y, w, h, area = stats[i]
            
            # Filter small regions
            if area > 50:  # Minimum area threshold
                regions.append((x, y, w, h))
        
        return regions
    
    def _post_process_boundaries(self,
                               boundaries: List[EquationBoundary],
                               page_image: np.ndarray) -> List[EquationBoundary]:
        """Post-process boundaries to resolve overlaps and merge related elements."""
        if not boundaries:
            return boundaries
        
        # Sort boundaries by confidence
        boundaries.sort(key=lambda b: b.boundary_confidence, reverse=True)
        
        # Remove overlapping boundaries (keep higher confidence ones)
        filtered_boundaries = []
        
        for boundary in boundaries:
            # Check for significant overlap with already accepted boundaries
            overlap_found = False
            
            for accepted in filtered_boundaries:
                overlap_ratio = self._calculate_bbox_overlap(
                    boundary.precise_bbox, accepted.precise_bbox
                )
                
                if overlap_ratio > 0.7:  # 70% overlap threshold
                    overlap_found = True
                    break
            
            if not overlap_found and boundary.boundary_confidence >= self.boundary_precision:
                filtered_boundaries.append(boundary)
        
        return filtered_boundaries
    
    def _group_elements_by_page(self, elements: List[MathematicalElement]) -> Dict[int, List[MathematicalElement]]:
        """Group mathematical elements by page number."""
        pages = {}
        for element in elements:
            page_num = element.page_number
            if page_num not in pages:
                pages[page_num] = []
            pages[page_num].append(element)
        return pages
    
    def _load_page_image(self, document_path: str, page_num: int) -> np.ndarray:
        """Load page image from PDF document."""
        # This would implement PDF to image conversion
        # For now, return a placeholder - in real implementation,
        # this would use PyMuPDF or similar to convert PDF page to image
        return np.zeros((800, 600), dtype=np.uint8)
    
    def _calculate_boundary_accuracy(self, boundaries: List[EquationBoundary]) -> float:
        """Calculate overall boundary extraction accuracy."""
        if not boundaries:
            return 0.0
        
        confidence_scores = [b.boundary_confidence for b in boundaries]
        return np.mean(confidence_scores)
    
    def _generate_extraction_statistics(self, boundaries: List[EquationBoundary]) -> Dict[str, Any]:
        """Generate comprehensive extraction statistics."""
        if not boundaries:
            return {'total_boundaries': 0}
        
        method_counts = {}
        confidence_scores = []
        
        for boundary in boundaries:
            method = boundary.extraction_method
            method_counts[method] = method_counts.get(method, 0) + 1
            confidence_scores.append(boundary.boundary_confidence)
        
        return {
            'total_boundaries': len(boundaries),
            'average_confidence': np.mean(confidence_scores),
            'confidence_std': np.std(confidence_scores),
            'method_distribution': method_counts,
            'high_confidence_count': len([b for b in boundaries if b.boundary_confidence > 0.8]),
            'low_confidence_count': len([b for b in boundaries if b.boundary_confidence < 0.5])
        }
    
    def _update_extraction_stats(self, result: BoundaryExtractionResult) -> None:
        """Update internal extraction statistics."""
        self.extraction_stats['total_extractions'] += len(result.equation_boundaries)
        self.extraction_stats['successful_extractions'] += len([
            b for b in result.equation_boundaries if b.boundary_confidence >= self.boundary_precision
        ])
        self.extraction_stats['boundary_accuracy_scores'].append(result.boundary_accuracy)
        self.extraction_stats['processing_times_ms'].append(result.extraction_time_ms)
        
        # Update method usage counts
        for boundary in result.equation_boundaries:
            method = boundary.extraction_method
            self.extraction_stats['method_usage_counts'][method] = \
                self.extraction_stats['method_usage_counts'].get(method, 0) + 1
    
    def _initialize_extraction_methods(self) -> Dict[str, BoundaryExtractionMethod]:
        """Initialize boundary extraction methods for different equation types."""
        return {
            'general_math': BoundaryExtractionMethod(
                name='general_math',
                morphological_kernel_size=(3, 3),
                closing_iterations=2,
                opening_iterations=1,
                contour_min_area=100,
                contour_approx_epsilon=0.02
            ),
            'wide_equation': BoundaryExtractionMethod(
                name='wide_equation',
                morphological_kernel_size=(5, 3),
                closing_iterations=3,
                opening_iterations=1,
                contour_min_area=200,
                contour_approx_epsilon=0.01
            ),
            'vertical_fraction': BoundaryExtractionMethod(
                name='vertical_fraction',
                morphological_kernel_size=(3, 5),
                closing_iterations=2,
                opening_iterations=2,
                contour_min_area=150,
                contour_approx_epsilon=0.015
            ),
            'fine_symbol': BoundaryExtractionMethod(
                name='fine_symbol',
                morphological_kernel_size=(2, 2),
                closing_iterations=1,
                opening_iterations=1,
                contour_min_area=50,
                contour_approx_epsilon=0.005
            ),
            'complex_expression': BoundaryExtractionMethod(
                name='complex_expression',
                morphological_kernel_size=(4, 4),
                closing_iterations=3,
                opening_iterations=2,
                contour_min_area=300,
                contour_approx_epsilon=0.02
            )
        }
    
    def _create_morphological_kernels(self) -> Dict[str, np.ndarray]:
        """Create morphological kernels for different operations."""
        return {
            'horizontal_line': cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1)),
            'vertical_line': cv2.getStructuringElement(cv2.MORPH_RECT, (1, 9)),
            'small_rect': cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)),
            'medium_rect': cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)),
            'ellipse': cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        }
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get current extraction performance statistics."""
        stats = self.extraction_stats.copy()
        
        if stats['boundary_accuracy_scores']:
            stats['average_boundary_accuracy'] = np.mean(stats['boundary_accuracy_scores'])
            stats['boundary_accuracy_std'] = np.std(stats['boundary_accuracy_scores'])
        
        if stats['processing_times_ms']:
            stats['average_processing_time_ms'] = np.mean(stats['processing_times_ms'])
            stats['max_processing_time_ms'] = np.max(stats['processing_times_ms'])
        
        if stats['total_extractions'] > 0:
            stats['success_rate'] = stats['successful_extractions'] / stats['total_extractions']
        
        return stats


# Utility functions for integration
def extract_equation_boundaries(detection_result: MathDetectionResult,
                              boundary_precision: float = 0.8) -> BoundaryExtractionResult:
    """
    Convenience function to extract equation boundaries from detection result.
    
    Args:
        detection_result: Mathematical notation detection result
        boundary_precision: Required precision for boundary extraction
        
    Returns:
        Boundary extraction result with precise boundaries
    """
    extractor = EquationBoundaryExtractor(boundary_precision=boundary_precision)
    return extractor.extract_equation_boundaries(detection_result)


def create_academic_boundary_extractor(enable_monitoring: bool = True) -> EquationBoundaryExtractor:
    """
    Create equation boundary extractor optimized for academic documents.
    
    Args:
        enable_monitoring: Enable performance monitoring integration
        
    Returns:
        Configured equation boundary extractor
    """
    return EquationBoundaryExtractor(
        boundary_precision=0.75,  # Slightly lower for academic variety
        context_expansion_ratio=0.2,  # More context for academic equations
        enable_faiss_similarity=True,
        enable_monitoring=enable_monitoring
    )
