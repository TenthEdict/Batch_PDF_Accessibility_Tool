from .core.document import AccessibilityDocumentProcessor
from .core.batch import BatchPDFProcessor
from .core.enhance import EnhancedAccessibilityChecker
from .ocr.processor import OCRProcessor
from .utils.retry import RetryHandler, RetryConfig, OCRError, ProcessingError, OCRTimeoutError
from .utils.config import OCRConfig
from .ocr.adaptive_config import AdaptiveOCRConfig

__version__ = "0.1.0"

__all__ = [
    'AccessibilityDocumentProcessor',
    'BatchPDFProcessor',
    'EnhancedAccessibilityChecker',
    'OCRProcessor',
    'RetryHandler',
    'RetryConfig',
    'OCRError',
    'ProcessingError',
    'OCRTimeoutError',
    'OCRConfig',
    'AdaptiveOCRConfig'
]