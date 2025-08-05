from .ocr_enhancer import OCREnhancer
from .pdf_enhancer import PDFEnhancer
from .minimal_pdf_enhancer import MinimalPDFEnhancer
from .compression_enhancer import CompressionEnhancer
from .basic_enhancer import BasicEnhancer
from .enhancer_base import EnhancerBase

# Optional ML enhancer - only available if ML dependencies installed
try:
    from .ml_enhancer import MLEnhancer
    ML_ENHANCER_AVAILABLE = True
except ImportError:
    MLEnhancer = None
    ML_ENHANCER_AVAILABLE = False

# Optional Apple Silicon enhancer - only available on Apple Silicon with MLX
try:
    from .apple_optimized_enhancer import AppleOptimizedEnhancer
    APPLE_ENHANCER_AVAILABLE = True
except (ImportError, RuntimeError):
    AppleOptimizedEnhancer = None
    APPLE_ENHANCER_AVAILABLE = False
