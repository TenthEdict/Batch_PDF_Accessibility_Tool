"""
Caching module for ePubs Accessibility Enhancement.

This module provides local caching capabilities for OCR results,
ML analysis, and other processing intermediates to improve performance
and reduce redundant processing.
"""

from .cache_manager import CacheManager
from .cache_service import CacheService

__all__ = ['CacheManager', 'CacheService']