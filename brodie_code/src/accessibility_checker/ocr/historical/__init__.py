"""
Historical document processing module.

This module provides specialized OCR processing for historical documents.
"""

from .processor import HistoricalProcessor
from .analyzer import HistoricalDocumentAnalyzer
from .resources import setup_historical_resources

__all__ = ['HistoricalProcessor', 'HistoricalDocumentAnalyzer', 'setup_historical_resources']