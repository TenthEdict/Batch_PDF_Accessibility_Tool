# src/accessibility_checker/build/__init__.py

"""
Build process module for PDF accessibility checking.
Handles document processing workflow and build automation.
"""

from .process import BuildProcess, main

__all__ = [
    'BuildProcess',
    'main',
]