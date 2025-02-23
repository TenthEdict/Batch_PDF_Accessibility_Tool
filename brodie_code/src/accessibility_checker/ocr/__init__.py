# src/accessibility_checker/ocr/__init__.py

"""
OCR (Optical Character Recognition) module for PDF accessibility checking.
Provides OCR processing, configuration, and adaptive text recognition capabilities.
"""

from .processor import (
    OCRProcessor,
    OCRResult,
    OCRElementType
)

from .adaptive_config import (
    AdaptiveOCRConfig,
    DocumentCharacteristics
)

from .math_processor import (
    MathOCRProcessor,
    MathRegion
)

__all__ = [
    # Main OCR processor
    'OCRProcessor',
    'OCRResult',
    'OCRElementType',
    
    # Adaptive configuration
    'AdaptiveOCRConfig',
    'DocumentCharacteristics',
    
    # Math OCR processing
    'MathOCRProcessor',
    'MathRegion'
]

# Version of the OCR module
__version__ = '0.1.0'

# Default OCR settings
DEFAULT_LANGUAGE = 'eng'
DEFAULT_PSM = 3  # Fully automatic page segmentation
DEFAULT_OEM = 3  # Default, based on what is available