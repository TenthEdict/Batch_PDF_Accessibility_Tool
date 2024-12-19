import time
from functools import wraps
from typing import Type, Tuple, Callable, Optional, Dict, List
import logging
from datetime import datetime
import random
import numpy as np  # Add this import
from ..core.enhance import EnhancedAccessibilityChecker, AccessibilityViolation
import fitz 

class RetryableError(Exception):
    """Base class for errors that should trigger a retry."""
    pass

class OCRError(RetryableError):
    """Error during OCR processing."""
    pass

class OCRTimeoutError(RetryableError):
    """Error when OCR processing exceeds timeout."""
    pass

class ProcessingError(RetryableError):
    """Error during document processing."""
    pass

class NetworkError(RetryableError):
    """Error during network operations."""
    pass

class RetryConfig:
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

class RetryHandler:
    def __init__(self, config: RetryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter."""
        delay = min(
            self.config.base_delay * (self.config.exponential_base ** attempt),
            self.config.max_delay
        )
        
        if self.config.jitter:
            delay *= (0.5 + random.random())
            
        return delay

    def __call__(self, retryable_exceptions: Tuple[Type[Exception], ...] = (RetryableError,)):
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(self.config.max_attempts):
                    try:
                        return func(*args, **kwargs)
                    
                    except retryable_exceptions as e:
                        last_exception = e
                        
                        if attempt + 1 < self.config.max_attempts:
                            delay = self.calculate_delay(attempt)
                            
                            self.logger.warning(
                                f"Attempt {attempt + 1}/{self.config.max_attempts} "
                                f"failed: {str(e)}. Retrying in {delay:.2f} seconds..."
                            )
                            
                            self._log_retry_attempt(func.__name__, attempt + 1, str(e))
                            time.sleep(delay)
                        else:
                            self.logger.error(
                                f"All {self.config.max_attempts} attempts failed "
                                f"for {func.__name__}"
                            )
                            
                raise last_exception
            
            return wrapper
        return decorator

    def _log_retry_attempt(self, function_name: str, attempt: int, error: str):
        """Log detailed information about retry attempts."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'function': function_name,
            'attempt': attempt,
            'error': error
        }
        
        self.logger.debug(f"Retry log entry: {log_entry}")

# Example usage in the AccessibilityDocumentProcessor

class EnhancedAccessibilityDocumentProcessor:
    def __init__(self):
        self.retry_handler = RetryHandler(RetryConfig(
            max_attempts=3,
            base_delay=2.0,
            max_delay=30.0,
            jitter=True
        ))
        self.accessibility_checker = EnhancedAccessibilityChecker()

    @RetryHandler(RetryConfig())((OCRError, ProcessingError))
    def process_document(self, pdf_path: str) -> Dict:
        """Process document with retry capability."""
        try:
            doc = fitz.open(pdf_path)
            
            # Perform accessibility checks
            violations = self.accessibility_checker.check_document(doc)
            
            # Generate report
            report = self.accessibility_checker.generate_report()
            
            return {
                'status': 'success',
                'accessibility_report': report,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ProcessingError(f"Failed to process document: {str(e)}")

    @RetryHandler(RetryConfig(max_attempts=5, base_delay=1.0))((OCRError,))
    def perform_ocr(self, image: np.ndarray) -> str:
        """Perform OCR with retry capability."""
        try:
            result = self.ocr_processor.process_image(image)
            if not result.strip():
                raise OCRError("OCR produced empty result")
            return result
        except Exception as e:
            raise OCRError(f"OCR failed: {str(e)}")

    def check_document(self, doc: fitz.Document) -> List[AccessibilityViolation]:
        """Perform comprehensive accessibility check on the document."""
        self.violations = []
        
        # Check document-level properties
        self._check_document_properties(doc)
        
        # Add new comprehensive checks
        self.violations.extend(self.check_heading_structure(doc))
        self.violations.extend(self.check_color_contrast(doc))
        self.violations.extend(self.check_table_structure(doc))
        
        return self.violations

class WCAGTestRunner:
    """Base class for running WCAG compliance tests"""
    def __init__(self, doc: fitz.Document, accessibility_checker: EnhancedAccessibilityChecker):
        self.doc = doc
        self.checker = accessibility_checker
        self.violations = []

    @staticmethod
    def calculate_luminance(rgb: Tuple[float, float, float]) -> float:
        rgb_norm = [c/255 for c in rgb]
        rgb_adj = [c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4 for c in rgb_norm]
        return 0.2126 * rgb_adj[0] + 0.7152 * rgb_adj[1] + 0.0722 * rgb_adj[2]

    @staticmethod
    def calculate_contrast_ratio(fg: Tuple[float, float, float], bg: Tuple[float, float, float]) -> float:
        l1 = WCAGTestRunner.calculate_luminance(fg)
        l2 = WCAGTestRunner.calculate_luminance(bg)
        return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)

    def retry_with_backoff(self, func: Callable, *args, **kwargs):
        config = RetryConfig()
        for attempt in range(config.max_attempts):
            try:
                return func(*args, **kwargs)
            except RetryableError as e:
                if attempt == config.max_attempts - 1:
                    raise
                delay = min(
                    config.base_delay * (config.exponential_base ** attempt),
                    config.max_delay
                )
                if config.jitter:
                    delay *= random.uniform(0.5, 1.5)
                time.sleep(delay)
        return None

class HeadingAnalyzer(WCAGTestRunner):
    def analyze_headings(self) -> List[Dict]:
        heading_structure = []
        prev_level = 0
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            def analyze_block(block):
                if block["type"] == 0:  # text block
                    font_info = block.get("font", "")
                    font_size = block.get("font_size", 0)
                    text = block.get("text", "").strip()
                    
                    if not text:
                        return None
                        
                    level = self._determine_heading_level(font_size, font_info)
                    if level:
                        return {
                            "level": level,
                            "text": text,
                            "page": page_num + 1,
                            "bbox": block["bbox"]
                        }
                return None
            
            page_headings = filter(None, [analyze_block(b) for b in blocks])
            heading_structure.extend(page_headings)
            
        return heading_structure

    def _determine_heading_level(self, font_size: float, font_info: str) -> Optional[int]:
        # Font size thresholds for heading levels
        thresholds = {
            1: 20,
            2: 18,
            3: 16,
            4: 14,
            5: 12,
            6: 10
        }
        
        is_bold = "bold" in font_info.lower()
        
        for level, threshold in thresholds.items():
            if font_size >= threshold and (level == 1 or is_bold):
                return level
        
        return None

