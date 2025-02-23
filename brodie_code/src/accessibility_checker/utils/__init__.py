# src/accessibility_checker/utils/__init__.py

"""
Utility modules for PDF accessibility checking.
Provides configuration, error handling, code analysis, and API client functionality.
"""

from .retry import (
    RetryHandler,
    RetryConfig,
    RetryableError,
    OCRError,
    OCRTimeoutError,
    ProcessingError,
    NetworkError
)

from .config import (
    OCRConfig,
    ProcessingConfig,
    ConfigurationManager
)

from .code_analyzer import (
    CodeAnalyzer,
    CodeAnalysisConfig,
    CodeIssue
)

from .anthropic_client import (
    AnthropicClient,
    AnthropicConfig,
    AnthropicAPIError,
    create_anthropic_client
)

__all__ = [
    # Retry handling
    'RetryHandler',
    'RetryConfig',
    'RetryableError',
    'OCRError',
    'OCRTimeoutError',
    'ProcessingError',
    'NetworkError',
    
    # Configuration
    'OCRConfig',
    'ProcessingConfig',
    'ConfigurationManager',
    
    # Code analysis
    'CodeAnalyzer',
    'CodeAnalysisConfig',
    'CodeIssue',
    
    # Anthropic integration
    'AnthropicClient',
    'AnthropicConfig',
    'AnthropicAPIError',
    'create_anthropic_client'
]

# Default retry settings
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BASE_DELAY = 1.0
DEFAULT_MAX_DELAY = 60.0
DEFAULT_EXPONENTIAL_BASE = 2.0

# Default timeout settings (in seconds)
DEFAULT_API_TIMEOUT = 30
DEFAULT_OCR_TIMEOUT = 300