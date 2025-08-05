"""
Utility modules for ePubs Accessibility Enhancement.

This package contains utility functions and classes for platform detection,
performance optimization, and other common functionality.
"""

from .platform_detection import (
    is_apple_silicon,
    get_apple_chip,
    get_platform_info,
    get_optimization_recommendations
)

__all__ = [
    'is_apple_silicon',
    'get_apple_chip', 
    'get_platform_info',
    'get_optimization_recommendations'
]