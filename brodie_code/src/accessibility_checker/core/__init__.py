# src/accessibility_checker/core/__init__.py

"""
Core processing module for PDF accessibility checking.
Provides document processing, accessibility enhancement, and batch processing capabilities.
"""

from .document import (
    AccessibilityDocumentProcessor,
    TextElement,
    TableCell,
    TableStructure,
    BatchPDFProcessor
)

from .enhance import (
    EnhancedAccessibilityChecker,
    AccessibilityViolation,
    AccessibilityLevel,
    ViolationType
)

from .anthropic_processor import (
    AnthropicEnhancedProcessor,
    create_enhanced_processor
)

from .processor import (
    process_pdf_file,
    ProcessingResult
)

__all__ = [
    # Document processing
    'AccessibilityDocumentProcessor',
    'TextElement',
    'TableCell',
    'TableStructure',
    'BatchPDFProcessor',
    
    # Accessibility enhancement
    'EnhancedAccessibilityChecker',
    'AccessibilityViolation',
    'AccessibilityLevel',
    'ViolationType',
    
    # Anthropic integration
    'AnthropicEnhancedProcessor',
    'create_enhanced_processor',
    
    # Processing utilities
    'process_pdf_file',
    'ProcessingResult'
]

# Core module version
__version__ = '0.1.0'

# Default batch processing settings
DEFAULT_BATCH_SIZE = 10
DEFAULT_MAX_WORKERS = 4