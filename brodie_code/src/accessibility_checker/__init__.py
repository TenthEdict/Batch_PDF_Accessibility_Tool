# src/accessibility_checker/__init__.py

"""
PDF Accessibility Checker
========================

A comprehensive tool for analyzing and improving PDF accessibility,
with support for OCR, mathematical content recognition, and AI-enhanced processing.

Main Components:
- Document processing and accessibility checking
- OCR with adaptive configuration
- Batch processing capabilities
- AI-enhanced analysis using Claude
- Utility functions and configuration management
"""

from .core import (
    AccessibilityDocumentProcessor,
    BatchPDFProcessor,
    EnhancedAccessibilityChecker,
    AccessibilityViolation,
    AccessibilityLevel,
    ViolationType,
    AnthropicEnhancedProcessor,
    create_enhanced_processor
)

from .ocr import (
    OCRProcessor,
    AdaptiveOCRConfig,
    MathOCRProcessor
)

from .utils import (
    RetryHandler,
    ConfigurationManager,
    CodeAnalyzer,
    AnthropicClient
)

from .build import (
    BuildProcess
)

__version__ = '0.1.0'
__author__ = 'Your Organization'
__license__ = 'MIT'

__all__ = [
    # Core processing
    'AccessibilityDocumentProcessor',
    'BatchPDFProcessor',
    'EnhancedAccessibilityChecker',
    'AccessibilityViolation',
    'AccessibilityLevel',
    'ViolationType',
    'AnthropicEnhancedProcessor',
    'create_enhanced_processor',
    
    # OCR functionality
    'OCRProcessor',
    'AdaptiveOCRConfig',
    'MathOCRProcessor',
    
    # Utilities
    'RetryHandler',
    'ConfigurationManager',
    'CodeAnalyzer',
    'AnthropicClient',
    
    # Build process
    'BuildProcess'
]

# Package-level configuration
DEFAULT_CONFIG_PATH = 'config.yaml'
SUPPORTED_PDF_VERSIONS = ['1.4', '1.5', '1.6', '1.7', '2.0']
SUPPORTED_LANGUAGES = ['eng', 'fra', 'deu', 'spa', 'ita']

def get_version():
    """Return the package version."""
    return __version__

def check_dependencies():
    """Check if all required dependencies are installed."""
    import pkg_resources
    
    required = {
        'PyMuPDF': '>=1.22.5',
        'numpy': '>=1.23.0,<2.1.0',
        'pandas': '>=1.5.0',
        'pytesseract': '>=0.3.8',
        'opencv-python': '==4.8.0.76',
        'Pillow': '>=9.2.0',
        'pdf2image': '>=1.16.0',
        'anthropic': '>=0.18.0'
    }
    
    missing = []
    for package, version in required.items():
        try:
            pkg_resources.require(f"{package}{version}")
        except pkg_resources.DistributionNotFound:
            missing.append(package)
        except pkg_resources.VersionConflict:
            missing.append(f"{package}{version}")
    
    return missing

def initialize(config_path=DEFAULT_CONFIG_PATH):
    """Initialize the accessibility checker with configuration."""
    config_manager = ConfigurationManager(config_path)
    return config_manager.get_processing_config()