"""
Historical document OCR processor.

This module provides specialized OCR processing for historical documents,
with enhanced preprocessing and recognition optimized for older texts.
"""

import logging
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import pytesseract
from PIL import Image

from ..processor import OCRProcessor, OCRResult, OCRElementType
from .analyzer import HistoricalDocumentAnalyzer, HistoricalCharacteristics

@dataclass
class HistoricalOCRConfig:
    """Configuration for historical OCR processing."""
    language: str = "eng"
    psm: int = 1  # Page segmentation mode - auto with OSD for historical docs by default
    oem: int = 2  # OCR Engine mode - LSTM + Legacy for historical by default
    char_whitelist: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:()[]{}\"'-—ſƺȝȣþðæœ"
    tessdata_path: Optional[str] = None
    deskew: bool = True
    era: str = "auto"  # "auto", "pre_1800", "19thC", "early_20thC"
    enhance_contrast: bool = True
    denoise: bool = True
    sharpen: bool = True
    user_patterns_file: Optional[str] = None
    user_words_file: Optional[str] = None
    additional_params: Dict[str, Any] = None

class HistoricalProcessor(OCRProcessor):
    """OCR processor with enhanced capabilities for historical documents."""
    
    def __init__(
            self, 
            config: Optional[HistoricalOCRConfig] = None,
            timeout: int = 60  # Historical docs often need more time
        ):
        """
        Initialize historical OCR processor.
        
        Args:
            config: Optional HistoricalOCRConfig with specialized settings
            timeout: Maximum time in seconds for OCR processing
        """
        super().__init__(None, None, timeout)  # Initialize base class
        
        self.logger = logging.getLogger(__name__)
        self.analyzer = HistoricalDocumentAnalyzer()
        
        # Use provided config or create default
        self.historical_config = config or HistoricalOCRConfig()
        
        # Set up Tesseract configuration
        self._configure_historical_ocr()
    
    def _configure_historical_ocr(self):
        """Configure OCR for historical document processing."""
        # Create base configuration
        self.text_config = {
            'language': self.historical_config.language,
            'psm': self.historical_config.psm,
            'oem': self.historical_config.oem,
            'tessedit_char_whitelist': self.historical_config.char_whitelist,
            'preserve_interword_spaces': '1',
            'textord_noise_rejwords': '1',
            'textord_noise_rejrows': '1',
            'tessdit_adaption_mode': '1',  # Special mode for degraded text
            'language_model_ngram_on': '1',
            'textord_heavy_nr': '1',
            'tessedit_enable_doc_dict': '1',
        }
        
        # Add user patterns file if specified
        if self.historical_config.user_patterns_file:
            self.text_config['user_patterns_suffix'] = self.historical_config.user_patterns_file
            
        # Add user words file if specified
        if self.historical_config.user_words_file:
            self.text_config['user_words_suffix'] = self.historical_config.user_words_file
        
        # Add any additional parameters from config
        if self.historical_config.additional_params:
            self.text_config.update(self.historical_config.additional_params)
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Enhanced preprocessing for historical documents.
        
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
            
            # Apply adaptive thresholding with adjusted parameters for historical docs
            binary = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                15,  # Larger block size for faded text
                4    # More aggressive threshold
            )
            
            # Special processing for historical documents
            enhanced = binary.copy()
            
            # Apply enhanced contrast if configured
            if self.historical_config.enhance_contrast:
                # Specialized CLAHE for historical documents - larger tile size
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(16, 16))
                enhanced = clahe.apply(gray)
                # Apply adaptive threshold again after contrast enhancement
                enhanced = cv2.adaptiveThreshold(
                    enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, 15, 4
                )
            
            # Apply stronger denoising for historical documents
            if self.historical_config.denoise:
                enhanced = cv2.fastNlMeansDenoising(enhanced, h=15)
            
            # Apply morphological operations to strengthen historical text
            kernel = np.ones((1, 1), np.uint8)
            enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
            
            # Apply sharpening if configured
            if self.historical_config.sharpen:
                kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
                enhanced = cv2.filter2D(enhanced, -1, kernel)
            
            # Correct skew if necessary and configured
            if self.historical_config.deskew:
                angle = self._get_skew_angle(enhanced)
                if abs(angle) > 0.5:
                    enhanced = self._rotate_image(enhanced, angle)
            
            return enhanced
            
        except Exception as e:
            error_msg = f"Historical image preprocessing failed: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
    
    def process_historical_document(self, image: Image.Image) -> List[OCRResult]:
        """
        Process a historical document image with optimized OCR.
        
        This method analyzes the document, determines its characteristics,
        and applies the appropriate OCR configuration before processing.
        
        Args:
            image: PIL Image of the document
            
        Returns:
            List of OCR results
        """
        # Analyze historical characteristics
        characteristics = self.analyzer.analyze_image(image)
        
        # Configure OCR based on detected era
        if self.historical_config.era == "auto":
            era = characteristics.estimated_age
        else:
            era = self.historical_config.era
            
        self.logger.info(f"Processing historical document (estimated era: {era})")
        
        # Adjust OCR configuration based on era
        self._configure_for_era(era)
        
        # Convert PIL Image to numpy array
        img_np = np.array(image)
        
        # Process the document
        ocr_results = self.process_page(img_np, 0)
        
        return ocr_results
    
    def _configure_for_era(self, era: str):
        """
        Configure OCR settings specifically for the detected historical era.
        
        Args:
            era: Historical era - "pre_1800", "19thC", "early_20thC", or "modern"
        """
        # Apply era-specific configurations
        if era == "pre_1800":
            # Very old documents need special handling
            self.text_config.update({
                'textord_min_linesize': '1.25',
                'textord_noise_sizelimit': '0.5',
                'textord_noise_normratio': '8',
                'tessdit_adaption_mode': '1',
                'thresholding_method': '1',
                'classify_bln_numeric_mode': '1',
            })
            
            # Use pre-1800 word list if available
            if not self.historical_config.user_words_file:
                self.text_config['user_words_suffix'] = 'historical_words/historical_pre1800.txt'
                
        elif era == "19thC":
            # 19th century documents
            self.text_config.update({
                'textord_noise_rejwords': '1',
                'textord_noise_rejrows': '1',
                'tessdit_adaption_mode': '1',
                'thresholding_method': '1',
            })
            
            # Use 19th century word list if available
            if not self.historical_config.user_words_file:
                self.text_config['user_words_suffix'] = 'historical_words/historical_19thC.txt'
                
        elif era == "early_20thC":
            # Early 20th century documents
            # Less aggressive settings
            self.text_config.update({
                'tessedit_enable_doc_dict': '1',
            })
            
            # Use early 20th century word list if available
            if not self.historical_config.user_words_file:
                self.text_config['user_words_suffix'] = 'historical_words/historical_early20thC.txt'
                
        # For all historical documents, we use the historical patterns file
        if not self.historical_config.user_patterns_file:
            self.text_config['user_patterns_suffix'] = 'historical_words/historical_patterns.txt'
            
        self.logger.debug(f"Configured OCR for historical era: {era}")
    
    def _get_skew_angle(self, image: np.ndarray) -> float:
        """Calculate the skew angle of the image."""
        # Historical documents often have more complex layouts
        # so we use a more robust skew detection
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