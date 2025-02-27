import logging
from typing import Dict, List, Tuple, Optional, Literal, Any
import numpy as np
from PIL import Image
import pytesseract
import cv2
from dataclasses import dataclass
from ..utils.retry import RetryHandler, OCRError, OCRTimeoutError
from ..utils.config import OCRConfig
OCRElementType = Literal['text', 'equation', 'reference', 'table', 'historical']


@dataclass
class OCRResult:
    """Data class to hold OCR result information."""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    page_num: int
    type: OCRElementType = 'text'


class OCRProcessor:
    """OCR processor with enhanced academic document processing capabilities."""

    def __init__(self, config: Optional[OCRConfig]=None, retry_handler:
        Optional[RetryHandler]=None, timeout: int=30) ->None:
        """
        Initialize OCR processor.
        
        Args:
            config: Optional OCRConfig object containing OCR configuration
            retry_handler: Optional retry handler for error recovery
            timeout: Maximum time in seconds for OCR processing
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.retry_handler = retry_handler
        self.timeout = timeout
        self.last_confidence = 0.0
        self.text_config = {'language': config.language if config else
            'eng', 'psm': config.psm if config else 3, 'oem': config.oem if
            config else 3, 'tessedit_char_whitelist': config.char_whitelist if
            config else
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:()[]{}"\'-'
            , 'preserve_interword_spaces': '1'}
        if config and config.additional_params:
            self.text_config.update(config.additional_params)
        # Default is standard processing, can be set to 'historical' for special handling
        self.document_mode = 'standard'

    def update_config(self, new_config: Dict[str, Any]) ->None:
        """Update OCR configuration with new settings."""
        self.text_config.update(new_config)
        if 'preprocessing' in new_config:
            self.preprocessing_config = new_config['preprocessing']
        if 'deskew' in new_config:
            self.enable_deskew = new_config['deskew']
        if 'document_mode' in new_config:
            self.document_mode = new_config['document_mode']
        self.logger.info(f'Updated OCR configuration: {new_config}')

    def preprocess_image(self, image: np.ndarray) ->np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
                
            # Special handling for historical documents
            if self.document_mode == 'historical':
                return self._preprocess_historical_document(gray)
            
            # Standard preprocessing for modern documents
            binary = cv2.adaptiveThreshold(gray, 255, cv2.
                ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            denoised = cv2.fastNlMeansDenoising(binary)
            angle = self._get_skew_angle(denoised)
            if abs(angle) > 0.5:
                denoised = self._rotate_image(denoised, angle)
            return denoised
        except Exception as e:
            error_msg = f'Image preprocessing failed: {str(e)}'
            self.logger.error(error_msg)
            raise OCRError(error_msg)
            
    def _preprocess_historical_document(self, image: np.ndarray) -> np.ndarray:
        """
        Specialized preprocessing for historical documents with faded text,
        stains, yellowed paper, and other age-related degradation.
        
        Args:
            image: Grayscale input image as numpy array
            
        Returns:
            Preprocessed image optimized for historical document OCR
        """
        self.logger.info("Applying historical document preprocessing pipeline")
        
        # 1. Enhance contrast to bring out faded text
        # Create a CLAHE object with higher clip limit for historical documents
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        # 2. Invert colors before thresholding for better text detection
        # This fixes issues with light text on dark backgrounds
        inverted = cv2.bitwise_not(enhanced)
        
        # 3. Apply Otsu thresholding 
        _, binary = cv2.threshold(
            inverted, 0, 255, 
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        # 4. Apply specialized historical document denoising
        # Higher strength denoising to handle age-related noise
        denoised = cv2.fastNlMeansDenoising(binary, h=10)
        
        # 5. Additional sharpening to improve character definition
        # Create a sharpening kernel optimized for faded historical text
        kernel = np.array([[-1, -1, -1], 
                           [-1, 9, -1], 
                           [-1, -1, -1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # 6. Correct skew - historical documents are often warped or skewed
        angle = self._get_skew_angle(sharpened)
        if abs(angle) > 0.5:
            processed = self._rotate_image(sharpened, angle)
        else:
            processed = sharpened
            
        # 7. Apply adaptive binarization optimized for historical fonts
        # Uses a smaller block size for more localized thresholding
        final = cv2.adaptiveThreshold(
            processed, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return final

    def process_image(self, image: np.ndarray, timeout: int=30) ->str:
        """
        Process image with OCR and return extracted text.
        
        Args:
            image: Input image as numpy array
            timeout: Maximum processing time in seconds
            
        Returns:
            Extracted text from the image
        """
        try:
            processed_image = self.preprocess_image(image)
            
            # Check if we need to use historical mode with special configuration
            if self.document_mode == 'historical':
                # Set historical config file as the base
                config = '--config historical.config'
                
                # Include specialized user dictionaries
                config += ' --user-words ./src/accessibility_checker/ocr/historical_words'
                config += ' --user-patterns ./src/accessibility_checker/ocr/historical_patterns.txt'
                
                # Add PSM and OEM settings
                config += f" --psm {self.text_config['psm']} --oem {self.text_config['oem']}"
                
                # Add custom parameters
                for k, v in self.text_config.items():
                    if k not in ['psm', 'oem', 'language'] and not isinstance(v, dict):
                        if isinstance(v, str):
                            # Properly quote string values
                            config += f' -c {k}="{v}"'
                        else:
                            config += f' -c {k}={v}'
            else:
                # Standard configuration for non-historical documents
                config_items = []
                for k, v in self.text_config.items():
                    if isinstance(v, str):
                        # Properly quote string values
                        config_items.append(f'-c {k}="{v}"')
                    else:
                        config_items.append(f'-c {k}={v}')
                
                config = ' '.join(config_items)
                config += (
                    f" --psm {self.text_config['psm']} --oem {self.text_config['oem']}"
                    )
            try:
                ocr_data = pytesseract.image_to_data(processed_image, lang=
                    self.text_config['language'], config=config,
                    output_type=pytesseract.Output.DICT)
            except pytesseract.TesseractError as e:
                self.logger.error(f'Tesseract OCR error: {e}')
                raise OCRError(f'Tesseract OCR error: {e}')
            except Exception as e:
                self.logger.error(f'Unexpected OCR processing failure: {e}')
                raise OCRError(f'Unexpected OCR processing failure: {e}')
            confidences = [float(conf) for conf in ocr_data['conf'] if conf !=
                '-1']
            self.last_confidence = np.mean(confidences) if confidences else 0.0
            text_results = []
            for i, text in enumerate(ocr_data['text']):
                if text.strip() and float(ocr_data['conf'][i]) > 0:
                    text_results.append(text)
            return ' '.join(text_results)
        except Exception as e:
            error_msg = f'OCR processing failed: {str(e)}'
            self.logger.error(error_msg)
            raise OCRError(error_msg)

    def process_page(self, image: np.ndarray, page_num: int) ->List[OCRResult]:
        """
        Process a page and return detailed OCR results.
        
        Args:
            image: Page image as numpy array
            page_num: Page number
            
        Returns:
            List of OCR results with position and confidence information
        """
        try:
            processed_image = self.preprocess_image(image)
            
            # Check if we need to use historical mode with special configuration
            if self.document_mode == 'historical':
                # Set historical config file as the base
                config = '--config historical.config'
                
                # Include specialized user dictionaries
                config += ' --user-words ./src/accessibility_checker/ocr/historical_words'
                config += ' --user-patterns ./src/accessibility_checker/ocr/historical_patterns.txt'
                
                # Add PSM and OEM settings
                config += f" --psm {self.text_config['psm']} --oem {self.text_config['oem']}"
                
                # Add custom parameters
                for k, v in self.text_config.items():
                    if k not in ['psm', 'oem', 'language'] and not isinstance(v, dict):
                        if isinstance(v, str):
                            # Properly quote string values
                            config += f' -c {k}="{v}"'
                        else:
                            config += f' -c {k}={v}'
                
                self.logger.info("Using historical document OCR configuration")
            else:
                # Standard configuration for non-historical documents
                config_items = []
                for k, v in self.text_config.items():
                    if isinstance(v, str):
                        # Properly quote string values
                        config_items.append(f'-c {k}="{v}"')
                    else:
                        config_items.append(f'-c {k}={v}')
                
                config = ' '.join(config_items)
                config += (
                    f" --psm {self.text_config['psm']} --oem {self.text_config['oem']}"
                    )
            ocr_data = pytesseract.image_to_data(processed_image, lang=self
                .text_config['language'], config=config, output_type=
                pytesseract.Output.DICT)
            results = []
            for i, text in enumerate(ocr_data['text']):
                if text.strip() and float(ocr_data['conf'][i]) > 0:
                    bbox = ocr_data['left'][i], ocr_data['top'][i], ocr_data[
                        'left'][i] + ocr_data['width'][i], ocr_data['top'][i
                        ] + ocr_data['height'][i]
                    results.append(OCRResult(text=text, confidence=float(
                        ocr_data['conf'][i]), bbox=bbox, page_num=page_num))
            confidences = [result.confidence for result in results]
            self.last_confidence = np.mean(confidences) if confidences else 0.0
            return results
        except Exception as e:
            error_msg = f'Page OCR processing failed: {str(e)}'
            self.logger.error(error_msg)
            raise OCRError(error_msg)

    def get_last_confidence(self) ->float:
        """Get the confidence score from the last OCR operation."""
        return self.last_confidence

    def _get_skew_angle(self, image: np.ndarray) ->float:
        """Calculate the skew angle of the image."""
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        return angle

    def _rotate_image(self, image: np.ndarray, angle: float) ->np.ndarray:
        """Rotate the image by the given angle."""
        h, w = image.shape
        center = w // 2, h // 2
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE)
        return rotated
            
    def detect_historical_font(self, image: np.ndarray) -> str:
        """
        Attempts to detect historical font types in the document.
        
        This analyzes character shapes and spacing patterns to detect:
        - Old style serif fonts (like Caslon, Garamond)
        - Blackletter/Gothic fonts
        - Decorative historical scripts
        
        Args:
            image: Preprocessed image as numpy array
            
        Returns:
            String identifying the likely historical font type
        """
        # Extract connected components (characters)
        _, labels, stats, centroids = cv2.connectedComponentsWithStats(
            cv2.bitwise_not(image), connectivity=8
        )
        
        if len(stats) <= 1:
            return "unknown"
            
        # Calculate character metrics
        heights = stats[1:, cv2.CC_STAT_HEIGHT]
        widths = stats[1:, cv2.CC_STAT_WIDTH]
        areas = stats[1:, cv2.CC_STAT_AREA]
        
        # Filter out noise and outliers
        valid_indices = np.where((heights > 5) & (widths > 3) & (areas < 2000))[0]
        if len(valid_indices) < 10:
            return "unknown"
            
        heights = heights[valid_indices]
        widths = widths[valid_indices]
        
        # Calculate aspect ratios
        aspect_ratios = widths / heights
        
        # Calculate metrics for classification
        mean_aspect = np.mean(aspect_ratios)
        std_aspect = np.std(aspect_ratios)
        height_variance = np.var(heights)
        width_variance = np.var(widths)
        
        # Classification logic based on font characteristics
        if mean_aspect < 0.65 and std_aspect > 0.25:
            return "blackletter"  # High, narrow characters with variation
        elif mean_aspect > 0.85 and height_variance < 100:
            return "modern_serif"  # More square characters, consistent height
        elif width_variance > 200 and std_aspect > 0.2:
            return "old_style_serif"  # Varied width, moderate aspect ratio
        elif mean_aspect < 0.75 and height_variance > 150:
            return "decorative_script"  # Tall characters with height variation
        else:
            return "standard_serif"  # Default historical font type
