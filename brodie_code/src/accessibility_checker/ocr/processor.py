import logging
from typing import Dict, List, Tuple, Optional, Literal
import numpy as np
from PIL import Image
import pytesseract
import cv2
from dataclasses import dataclass
from ..utils.retry import RetryHandler, OCRError, OCRTimeoutError
from ..utils.config import OCRConfig

OCRElementType = Literal['text', 'equation', 'reference', 'table']

@dataclass
class OCRResult:
    """Data class to hold OCR result information."""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    page_num: int
    type: OCRElementType = 'text'  # Default to 'text' if not specified

class OCRProcessor:
    """OCR processor with enhanced academic document processing capabilities."""
    
    def __init__(
            self, 
            config: Optional[OCRConfig] = None,
            retry_handler: Optional[RetryHandler] = None,
            timeout: int = 30
        ):
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
            
            # Default OCR configurations
            self.text_config = {
                'language': config.language if config else 'eng',
                'psm': config.psm if config else 3,
                'oem': config.oem if config else 3,
                'tessedit_char_whitelist': config.char_whitelist if config else 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:()[]{}"\'-',
                'preserve_interword_spaces': '1',
            }
            
            # Add any additional parameters from config
            if config and config.additional_params:
                self.text_config.update(config.additional_params)


    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(binary)
            
            # Correct skew if necessary
            angle = self._get_skew_angle(denoised)
            if abs(angle) > 0.5:
                denoised = self._rotate_image(denoised, angle)
            
            return denoised
            
        except Exception as e:
            error_msg = f"Image preprocessing failed: {str(e)}"
            self.logger.error(error_msg)
            raise OCRError(error_msg)

    def process_image(self, image: np.ndarray, timeout: int = 30) -> str:
        """
        Process image with OCR and return extracted text.
        
        Args:
            image: Input image as numpy array
            timeout: Maximum processing time in seconds
            
        Returns:
            Extracted text from the image
        """
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Create tesseract config string
            config = ' '.join([f'-c {k}={v}' for k, v in self.text_config.items()])
            config += f' --psm {self.text_config["psm"]} --oem {self.text_config["oem"]}'
            
            # Perform OCR
            ocr_data = pytesseract.image_to_data(
                processed_image,
                lang=self.text_config['language'],
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract confidence scores
            confidences = [float(conf) for conf in ocr_data['conf'] if conf != '-1']
            self.last_confidence = np.mean(confidences) if confidences else 0.0
            
            # Combine text results
            text_results = []
            for i, text in enumerate(ocr_data['text']):
                if text.strip() and float(ocr_data['conf'][i]) > 0:
                    text_results.append(text)
            
            return ' '.join(text_results)
            
        except Exception as e:
            error_msg = f"OCR processing failed: {str(e)}"
            self.logger.error(error_msg)
            raise OCRError(error_msg)

    def process_page(self, image: np.ndarray, page_num: int) -> List[OCRResult]:
        """
        Process a page and return detailed OCR results.
        
        Args:
            image: Page image as numpy array
            page_num: Page number
            
        Returns:
            List of OCR results with position and confidence information
        """
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Create tesseract config string
            config = ' '.join([f'-c {k}={v}' for k, v in self.text_config.items()])
            config += f' --psm {self.text_config["psm"]} --oem {self.text_config["oem"]}'
            
            # Perform OCR
            ocr_data = pytesseract.image_to_data(
                processed_image,
                lang=self.text_config['language'],
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            # Process results
            results = []
            for i, text in enumerate(ocr_data['text']):
                if text.strip() and float(ocr_data['conf'][i]) > 0:
                    bbox = (
                        ocr_data['left'][i],
                        ocr_data['top'][i],
                        ocr_data['left'][i] + ocr_data['width'][i],
                        ocr_data['top'][i] + ocr_data['height'][i]
                    )
                    
                    results.append(OCRResult(
                        text=text,
                        confidence=float(ocr_data['conf'][i]),
                        bbox=bbox,
                        page_num=page_num
                    ))
            
            # Update last confidence
            confidences = [result.confidence for result in results]
            self.last_confidence = np.mean(confidences) if confidences else 0.0
            
            return results
            
        except Exception as e:
            error_msg = f"Page OCR processing failed: {str(e)}"
            self.logger.error(error_msg)
            raise OCRError(error_msg)

    def get_last_confidence(self) -> float:
        """Get the confidence score from the last OCR operation."""
        return self.last_confidence

    def _get_skew_angle(self, image: np.ndarray) -> float:
        """Calculate the skew angle of the image."""
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        return angle

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
