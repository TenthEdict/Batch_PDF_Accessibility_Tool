#!/usr/bin/env python3
"""
OCR processor with enhanced academic document processing capabilities.
"""

import logging
import numpy as np
import cv2
import pytesseract
from PIL import Image
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Literal, Any

# Define OCR element types
OCRElementType = Literal['text', 'equation', 'reference', 'table', 'historical']


@dataclass
class OCRResult:
    """Data class to hold OCR result information."""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    page_num: int
    type: OCRElementType = 'text'


class OCRConfig:
    """Configuration for OCR processing."""
    
    def __init__(self, 
                 language='eng', 
                 psm=3, 
                 oem=1, 
                 char_whitelist=None,
                 additional_params=None):
        """
        Initialize OCR configuration.
        
        Args:
            language: OCR language (default: 'eng')
            psm: Page segmentation mode (default: 3)
            oem: OCR engine mode (default: 1)
            char_whitelist: Character whitelist (default: None)
            additional_params: Additional parameters (default: None)
        """
        self.language = language
        self.psm = psm
        self.oem = oem
        self.char_whitelist = char_whitelist or 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:()[]{}"\'-'
        self.additional_params = additional_params or {}


class RetryHandler:
    """Handler for retrying OCR operations on failure."""
    
    def __init__(self, max_retries=3, timeout=30):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            timeout: Maximum time in seconds for OCR processing (default: 30)
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)


class OCRError(Exception):
    """Exception raised for OCR processing errors."""
    pass


class OCRTimeoutError(OCRError):
    """Exception raised for OCR timeout errors."""
    pass


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
        self.config = config or OCRConfig()
        self.retry_handler = retry_handler or RetryHandler()
        self.timeout = timeout
        self.last_confidence = 0.0
        self.text_config = {
            'language': self.config.language,
            'psm': self.config.psm,
            'oem': self.config.oem,
            'tessedit_char_whitelist': self.config.char_whitelist,
            'preserve_interword_spaces': '1',
            'tessedit_do_invert': '0',
            'textord_min_linesize': '1.25'
        }
        if self.config.additional_params:
            self.text_config.update(self.config.additional_params)
        # Default is standard processing, can be set to 'historical' for special handling
        self.document_mode = 'standard'  # Forcing standard mode for better compatibility

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
            
            # Enhanced preprocessing for modern documents
            # Apply more aggressive denoising to filter out non-text elements like decorations on cover pages
            
            # 1. Apply bilateral filtering to preserve edges while removing noise
            bilateral = cv2.bilateralFilter(gray, 11, 75, 75)  # Increased kernel size
            
            # 2. Apply adaptive thresholding with optimized parameters for JBIG2 compressed documents
            binary = cv2.adaptiveThreshold(bilateral, 255, cv2.
                ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 13, 1)  # Modified parameters
                
            # 3. Apply stronger denoising for JBIG2 compressed documents
            denoised = cv2.fastNlMeansDenoising(binary, h=15)  # Increased h parameter for stronger denoising
            
            # 4. Apply morphological operations to remove small noise
            kernel = np.ones((2, 2), np.uint8)
            denoised = cv2.morphologyEx(denoised, cv2.MORPH_OPEN, kernel)
            
            # 5. Apply deskewing if needed
            angle = self._get_skew_angle(denoised)
            if abs(angle) > 0.5:
                denoised = self._rotate_image(denoised, angle)
                
            self.logger.info("Applied enhanced modern document preprocessing")
            return denoised
        except Exception as e:
            error_msg = f'Image preprocessing failed: {str(e)}'
            self.logger.error(error_msg)
            raise OCRError(error_msg)
            
    def _preprocess_historical_document(self, image: np.ndarray) -> np.ndarray:
        """
        Enhanced preprocessing for historical documents with faded text,
        stains, yellowed paper, and other age-related degradation.
        
        Args:
            image: Grayscale input image as numpy array
            
        Returns:
            Preprocessed image optimized for historical document OCR
        """
        self.logger.info("Applying enhanced historical document preprocessing pipeline")
        
        # 1. Apply background normalization to address yellowed paper
        bg_norm = self._normalize_background(image)
        
        # 2. Enhance contrast to bring out faded text with higher clip limit
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(16, 16))
        enhanced = clahe.apply(bg_norm)
        
        # 3. Apply bilateral filtering to preserve edges while removing noise
        # This preserves text edges better than standard denoising
        bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # 4. Apply adaptive thresholding with optimized parameters for historical documents
        # Smaller block size (7) for more precise local thresholding
        # Negative C value (-2) increases sensitivity to faint text
        binary = cv2.adaptiveThreshold(
            bilateral, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 7, -2
        )
        
        # 5. Apply morphological operations to enhance character connectivity
        # Define kernel for morphological operations
        kernel = np.ones((1, 1), np.uint8)
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 6. Apply specialized historical document denoising
        denoised = cv2.fastNlMeansDenoising(morph, h=10)
        
        # 7. Apply sharpening to enhance character definition
        kernel = np.array([[-1, -1, -1], 
                          [-1, 9, -1], 
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # 8. Correct skew - historical documents are often warped or skewed
        angle = self._get_skew_angle(sharpened)
        if abs(angle) > 0.5:
            deskewed = self._rotate_image(sharpened, angle)
        else:
            deskewed = sharpened
            
        # 9. Final enhancement - apply targeted contrast enhancement
        # This enhances faint characters without amplifying noise
        final = self._enhance_faint_text(deskewed)
        
        return final
        
    def _normalize_background(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize document background to address yellowing and staining.
        
        Args:
            image: Grayscale input image
            
        Returns:
            Image with normalized background
        """
        # Create a heavily blurred version to estimate background
        blur_kernel_size = max(21, min(image.shape) // 30)
        if blur_kernel_size % 2 == 0:
            blur_kernel_size += 1  # Ensure odd kernel size
            
        background = cv2.GaussianBlur(image, (blur_kernel_size, blur_kernel_size), 0)
        
        # Subtract background to normalize
        normalized = cv2.subtract(255, cv2.subtract(255, image, background))
        
        return normalized
        
    def _enhance_faint_text(self, image: np.ndarray) -> np.ndarray:
        """
        Apply targeted enhancement to bring out faint text.
        
        Args:
            image: Binary image with text
            
        Returns:
            Enhanced image with improved visibility of faint text
        """
        # Calculate local variance to identify areas with faint text
        # Higher variance = clearer text, lower variance = potential faint text
        mean, stddev = cv2.meanStdDev(image)
        
        # Apply targeted enhancement based on local statistics
        enhanced = cv2.convertScaleAbs(image, alpha=1.2, beta=10)
        
        # Use morphological operations to strengthen faint characters
        kernel = np.ones((1, 1), np.uint8)
        enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
        
        return enhanced

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
                config += ' --user-words ./src/ocr/historical_words'
                config += ' --user-patterns ./src/ocr/historical_patterns.txt'
                
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
            # Lower confidence threshold for JBIG2 compressed documents
            # This helps capture more text in scanned documents with minimal text layers
            min_confidence = 15.0  # Lowered from 30% to 15% to capture more text from JBIG2 compressed images
            text_results = []
            for i, text in enumerate(ocr_data['text']):
                if text.strip() and float(ocr_data['conf'][i]) > min_confidence:
                    text_results.append(text)
            self.logger.info(f"OCR extracted {len(text_results)} text elements with confidence > {min_confidence}%")
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
                config += ' --user-words ./src/ocr/historical_words'
                config += ' --user-patterns ./src/ocr/historical_patterns.txt'
                
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
            # Use a higher confidence threshold to filter out noise
            min_confidence = 30.0  # Require at least 30% confidence (adjust as needed)
            results = []
            for i, text in enumerate(ocr_data['text']):
                if text.strip() and float(ocr_data['conf'][i]) > min_confidence:
                    bbox = ocr_data['left'][i], ocr_data['top'][i], ocr_data[
                        'left'][i] + ocr_data['width'][i], ocr_data['top'][i
                        ] + ocr_data['height'][i]
                    results.append(OCRResult(text=text, confidence=float(
                        ocr_data['conf'][i]), bbox=bbox, page_num=page_num))
            self.logger.info(f"Page {page_num}: OCR extracted {len(results)} text elements with confidence > {min_confidence}%")
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