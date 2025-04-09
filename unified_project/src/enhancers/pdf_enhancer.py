#!/usr/bin/env python3
"""
PDF accessibility enhancer module.

This module provides PDF-specific implementation of the Enhancer interface
for adding accessibility features to PDF documents.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import pikepdf
    from pikepdf import Pdf, Name, String, Dictionary, Array
except ImportError:
    raise ImportError(
        "pikepdf is required for PDF enhancement. "
        "Install it with: pip install pikepdf"
    )

from .enhancer_base import EnhancerBase

logger = logging.getLogger(__name__)


class PDFEnhancer(EnhancerBase):
    """
    PDF-specific implementation of the Enhancer interface.
    
    This class provides common functionality for enhancing PDF documents
    and serves as a base class for more specialized PDF enhancers.
    """
    
    def __init__(self, environment: Optional[str] = None):
        """
        Initialize the PDF enhancer.
        
        Args:
            environment: Optional environment name for configuration
        """
        super().__init__("pdf_enhancer", environment)
    
    def _load_document(self, input_path: Path) -> pikepdf.Pdf:
        """
        Load a PDF document from a file.
        
        Args:
            input_path: Path to the input PDF document
            
        Returns:
            pikepdf.Pdf: The loaded PDF document
        """
        return pikepdf.open(input_path)
    
    def _save_document(self, document: pikepdf.Pdf, output_path: Path) -> None:
        """
        Save a PDF document to a file.
        
        Args:
            document: The PDF document to save
            output_path: Path where the document should be saved
        """
        document.save(output_path)
    
    def enhance(self, document: pikepdf.Pdf, **kwargs) -> pikepdf.Pdf:
        """
        Enhance a PDF document with accessibility features.
        
        This implementation applies common PDF accessibility enhancements
        that are applicable to all PDF documents.
        
        Args:
            document: The PDF document to enhance
            **kwargs: Additional enhancer-specific parameters
                - title: Document title (default: None)
                - author: Document author (default: None)
                - language: Document language (default: 'en-US')
                - display_doc_title: Whether to display the document title
                  in the viewer (default: True)
            
        Returns:
            pikepdf.Pdf: The enhanced PDF document
        """
        # Extract parameters
        title = kwargs.get('title')
        author = kwargs.get('author')
        language = kwargs.get('language', 'en-US')
        display_doc_title = kwargs.get('display_doc_title', True)
        
        # Update document metadata
        with document.open_metadata(set_pikepdf_as_editor=False) as meta:
            if title:
                meta['dc:title'] = title
            
            if author:
                meta['dc:creator'] = author
            
            # Set document language
            meta['dc:language'] = language
        
        # Set viewer preferences to display document title
        if display_doc_title:
            if Name.ViewerPreferences not in document.Root:
                document.Root.ViewerPreferences = Dictionary()
            
            document.Root.ViewerPreferences[Name.DisplayDocTitle] = True
        
        # Log applied enhancements
        enhancements = ['Updated document metadata']
        if title:
            enhancements.append(f'Added title: {title}')
        if author:
            enhancements.append(f'Added author: {author}')
        enhancements.append(f'Set language to {language}')
        if display_doc_title:
            enhancements.append('Set display document title preference')
        
        logger.info("Applied enhancements:")
        for enhancement in enhancements:
            logger.info(f"- {enhancement}")
        
        return document
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of enhancement capabilities provided by this enhancer.
        
        Returns:
            List[str]: List of capability identifiers
        """
        return [
            'metadata.title',
            'metadata.author',
            'metadata.language',
            'viewer.display_title'
        ]