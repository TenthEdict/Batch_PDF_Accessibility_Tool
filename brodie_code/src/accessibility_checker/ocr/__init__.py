# src/accessibility_checker/ocr/__init__.py

from .processor import OCRProcessor, OCRResult
from .adaptive_config import AdaptiveOCRConfig, DocumentCharacteristics

__all__ = ['OCRProcessor', 'OCRResult', 'AdaptiveOCRConfig', 'DocumentCharacteristics']
