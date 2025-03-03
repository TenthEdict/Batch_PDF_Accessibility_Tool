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
    type: str
    symbols: List[str]


class MathOCRProcessor:

    def __init__(self) ->None:
        self.logger = logging.getLogger(__name__)
        self.math_config = {'preserve_interword_spaces': '1',
            'tessedit_char_whitelist': '0123456789+-=×÷()[]{}πΣ∫∂√∞∈∀∃≠≤≥±' +
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' +
            'αβγδεθλμπσφω', 'tessedit_pageseg_mode': '6'}
        self.math_patterns = {'operators': '[+\\-×÷=]', 'brackets':
            '[\\(\\)\\[\\]\\{\\}]', 'greek': '[πΣ∫∂√αβγδεθλμσφω]',
            'relations': '[=≠<>≤≥∈]'}

    def detect_math(self, image: np.ndarray) ->List[MathRegion]:
        """Detect and process mathematical content in an image."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape
                ) == 3 else image
            processed = self._preprocess_image(gray)
            regions = self._detect_math_regions(processed)
            math_regions = []
            for region in regions:
                try:
                    math_region = self._process_region(processed, region)
                    if math_region:
                        math_regions.append(math_region)
                except Exception as e:
                    self.logger.warning(f'Error processing region: {str(e)}')
                    continue
            return math_regions
        except Exception as e:
            self.logger.error(f'Error in math detection: {str(e)}')
            raise

    def _preprocess_image(self, image: np.ndarray) ->np.ndarray:
        """
        Enhanced preprocessing for math detection in both modern and historical documents.
        Includes specialized handling for faded mathematical symbols and historical notation.
        
        Args:
            image: Grayscale input image
            
        Returns:
            Preprocessed binary image optimized for math symbol detection
        """
        # Enhance contrast to bring out potential math symbols
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        # Apply bilateral filtering to preserve edges of math symbols while removing noise
        bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Apply adaptive thresholding with parameters tuned for math symbols
        # Uses a smaller block size for more precise handling of symbols
        binary = cv2.adaptiveThreshold(
            bilateral, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        
        # Apply morphological operations to connect broken parts of symbols
        # Close operation helps connect broken parts while preserving shape
        kernel_close = np.ones((2, 2), np.uint8)
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close)
        
        # Apply a small opening to remove tiny noise while preserving symbol structures
        kernel_open = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_open)
        
        # Additional sharpening to enhance edges of math symbols
        kernel_sharpen = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(cleaned, -1, kernel_sharpen)
        
        # Final noise removal with a more targeted approach
        denoised = cv2.fastNlMeansDenoising(sharpened, h=7)
        
        return denoised

    def _detect_math_regions(self, image: np.ndarray) ->List[Tuple[int, int,
        int, int]]:
        """Detect regions likely to contain mathematical content."""
        regions = []
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(cv2
            .bitwise_not(image), connectivity=8)
        for i in range(1, num_labels):
            x = stats[i, cv2.CC_STAT_LEFT]
            y = stats[i, cv2.CC_STAT_TOP]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]
            area = stats[i, cv2.CC_STAT_AREA]
            if self._is_valid_math_region(w, h, area):
                regions.append((x, y, w, h))
        return self._merge_regions(regions)

    def _is_valid_math_region(self, width: int, height: int, area: int) ->bool:
        """Check if region has characteristics of mathematical content."""
        aspect_ratio = width / height if height > 0 else float('inf')
        return (width >= 20 and height >= 15 and aspect_ratio <= 8.0 and 
            area >= 200)

    def _merge_regions(self, regions: List[Tuple[int, int, int, int]]) ->List[
        Tuple[int, int, int, int]]:
        """Merge overlapping regions."""
        if not regions:
            return []

        def overlaps(r1, r2):
            x1, y1, w1, h1 = r1
            x2, y2, w2, h2 = r2
            return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 +
                h2 < y1)
        merged = []
        regions = sorted(regions, key=lambda r: r[0])
        current = list(regions[0])
        for region in regions[1:]:
            if overlaps(current, region):
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

    def _process_region(self, image: np.ndarray, region: Tuple[int, int,
        int, int]) ->Optional[MathRegion]:
        """Process a detected math region."""
        x, y, w, h = region
        roi = image[y:y + h, x:x + w]
        config = ' '.join([f'-c {k}={v}' for k, v in self.math_config.items()])
        ocr_data = pytesseract.image_to_data(roi, config=config,
            output_type=pytesseract.Output.DICT)
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
        math_type = self._determine_math_type(w, h, content)
        return MathRegion(bbox=(x, y, w, h), content=content, confidence=
            avg_confidence, type=math_type, symbols=symbols)

    def _is_math_symbol(self, text: str) ->bool:
        """Check if text contains mathematical symbols."""
        import re
        for pattern in self.math_patterns.values():
            if re.search(pattern, text):
                return True
        return False

    def _determine_math_type(self, width: int, height: int, content: str
        ) ->str:
        """Determine type of mathematical content."""
        if width > 200 or '=' in content:
            return 'equation'
        elif height > 50:
            return 'display'
        else:
            return 'inline'

    def process_document(self, image: np.ndarray) ->Dict:
        """Process a document image and return math regions with metadata."""
        math_regions = self.detect_math(image)
        return {'total_regions': len(math_regions), 'regions': [{'type':
            region.type, 'content': region.content, 'confidence': region.
            confidence, 'location': region.bbox, 'symbols': region.symbols} for
            region in math_regions]}
