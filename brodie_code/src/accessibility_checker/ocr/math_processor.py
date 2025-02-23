import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
import pytesseract
from dataclasses import dataclass
import logging

@dataclass
class MathRegion:
    """Represents a detected mathematical expression."""
    bbox: Tuple[int, int, int, int]
    content: str
    confidence: float
    type: str  # 'inline', 'display', 'equation'
    symbols: List[str]

class MathOCRProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Math-specific OCR configuration
        self.math_config = {
            'preserve_interword_spaces': '1',
            'tessedit_char_whitelist': (
                '0123456789+-=×÷()[]{}πΣ∫∂√∞∈∀∃≠≤≥±' +
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' +
                'αβγδεθλμπσφω'  # Common Greek letters
            ),
            'tessedit_pageseg_mode': '6'  # Assume uniform text block
        }
        
        # Common math symbols patterns
        self.math_patterns = {
            'operators': r'[+\-×÷=]',
            'brackets': r'[\(\)\[\]\{\}]',
            'greek': r'[πΣ∫∂√αβγδεθλμσφω]',
            'relations': r'[=≠<>≤≥∈]'
        }

    def detect_math(self, image: np.ndarray) -> List[MathRegion]:
        """Detect and process mathematical content in an image."""
        try:
            # Ensure grayscale format
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Preprocess image
            processed = self._preprocess_image(gray)
            
            # Detect potential math regions
            regions = self._detect_math_regions(processed)
            
            # Process each region
            math_regions = []
            for region in regions:
                try:
                    math_region = self._process_region(processed, region)
                    if math_region:
                        math_regions.append(math_region)
                except Exception as e:
                    self.logger.warning(f"Error processing region: {str(e)}")
                    continue
            
            return math_regions
            
        except Exception as e:
            self.logger.error(f"Error in math detection: {str(e)}")
            raise

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better math detection."""
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            15,
            2
        )
        
        # Remove noise
        kernel = np.ones((2,2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return cleaned

    def _detect_math_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect regions likely to contain mathematical content."""
        regions = []
        
        # Find connected components
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            cv2.bitwise_not(image), 
            connectivity=8
        )
        
        for i in range(1, num_labels):
            x = stats[i, cv2.CC_STAT_LEFT]
            y = stats[i, cv2.CC_STAT_TOP]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]
            area = stats[i, cv2.CC_STAT_AREA]
            
            # Filter based on size and aspect ratio
            if self._is_valid_math_region(w, h, area):
                regions.append((x, y, w, h))
        
        # Merge overlapping regions
        return self._merge_regions(regions)

    def _is_valid_math_region(self, width: int, height: int, area: int) -> bool:
        """Check if region has characteristics of mathematical content."""
        aspect_ratio = width / height if height > 0 else float('inf')
        
        return (
            width >= 20 and  # Minimum width
            height >= 15 and  # Minimum height
            aspect_ratio <= 8.0 and  # Maximum width/height ratio
            area >= 200  # Minimum area
        )

    def _merge_regions(self, regions: List[Tuple[int, int, int, int]])  -> List[Tuple[int, int, int, int]]:
        """Merge overlapping regions."""
        if not regions:
            return []
            
        def overlaps(r1, r2):
            x1, y1, w1, h1 = r1
            x2, y2, w2, h2 = r2
            return not (x1 + w1 < x2 or x2 + w2 < x1 or
                       y1 + h1 < y2 or y2 + h2 < y1)
        
        merged = []
        regions = sorted(regions, key=lambda r: r[0])  # Sort by x coordinate
        
        current = list(regions[0])
        
        for region in regions[1:]:
            if overlaps(current, region):
                # Merge regions
                x = min(current[0], region[0])
                y = min(current[1], region[1])
                w = max(current[0] + current[2], region[0] + region[2]) - x
                h = max(current[1] + current[3], region[1] + region[3]) - y
                current = [x, y, w, h]
            else:
                merged.append(tuple(current))
                current = list(region)
        
        merged.append(tuple(current))
        return merged

    def _process_region(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> Optional[MathRegion]:
        """Process a detected math region."""
        x, y, w, h = region
        roi = image[y:y+h, x:x+w]
        
        # Perform OCR with math-specific settings
        config = ' '.join([f'-c {k}={v}' for k, v in self.math_config.items()])
        ocr_data = pytesseract.image_to_data(
            roi,
            config=config,
            output_type=pytesseract.Output.DICT
        )
        
        # Extract text and confidence
        text_parts = []
        confidences = []
        symbols = []
        
        for i, text in enumerate(ocr_data['text']):
            if text.strip():
                conf = float(ocr_data['conf'][i])
                if conf > 0:
                    text_parts.append(text)
                    confidences.append(conf)
                    if self._is_math_symbol(text):
                        symbols.append(text)
        
        if not text_parts:
            return None
            
        content = ' '.join(text_parts)
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        # Determine math type based on region characteristics
        math_type = self._determine_math_type(w, h, content)
        
        return MathRegion(
            bbox=(x, y, w, h),
            content=content,
            confidence=avg_confidence,
            type=math_type,
            symbols=symbols
        )

    def _is_math_symbol(self, text: str) -> bool:
        """Check if text contains mathematical symbols."""
        import re
        
        for pattern in self.math_patterns.values():
            if re.search(pattern, text):
                return True
        return False

    def _determine_math_type(self, width: int, height: int, content: str) -> str:
        """Determine type of mathematical content."""
        if width > 200 or '=' in content:
            return 'equation'
        elif height > 50:
            return 'display'
        else:
            return 'inline'

    def process_document(self, image: np.ndarray) -> Dict:
        """Process a document image and return math regions with metadata."""
        math_regions = self.detect_math(image)
        
        return {
            'total_regions': len(math_regions),
            'regions': [
                {
                    'type': region.type,
                    'content': region.content,
                    'confidence': region.confidence,
                    'location': region.bbox,
                    'symbols': region.symbols
                }
                for region in math_regions
            ]
        }
