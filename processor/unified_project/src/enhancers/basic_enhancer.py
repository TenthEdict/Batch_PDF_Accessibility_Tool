#!/usr/bin/env python3
"""
Basic PDF accessibility enhancer module.

This module extends the PDF enhancer to implement basic accessibility
features for PDF documents.
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

from .pdf_enhancer import PDFEnhancer

logger = logging.getLogger(__name__)


class BasicEnhancer(PDFEnhancer):
    """
    Basic PDF accessibility enhancement functionality.

    This class provides basic PDF accessibility enhancements:
    - Document title and author metadata
    - Document language
    - PDF/UA compliance markers
    - Viewer preferences to display document title
    """

    def __init__(self, environment: Optional[str] = None):
        """
        Initialize the basic enhancer.

        Args:
            environment: Optional environment name for configuration
        """
        super().__init__(environment)
        self.component_name = "basic_enhancer"

        # Reset configuration for this specific component
        from ..core.config import get_config_provider

        self.config = get_config_provider().get_config(self.component_name, environment)

    def enhance(self, document: pikepdf.Pdf, **kwargs) -> pikepdf.Pdf:
        """
        Enhance a PDF document with basic accessibility features.

        This implementation extends the PDF enhancer to add basic
        accessibility enhancements specific to this enhancer.

        Args:
            document: The PDF document to enhance
            **kwargs: Additional enhancer-specific parameters
                - title: Document title (default: None)
                - author: Document author (default: None)
                - language: Document language (default: 'en-US')
                - display_doc_title: Whether to display the document title
                  in the viewer (default: True)
                - extract_title_from_h1: Whether to extract the title
                  from H1 tags (default: True)
                - extract_title_from_filename: Whether to extract the title
                  from the filename if not provided (default: False)
                - filename: Original filename (for title extraction)

        Returns:
            pikepdf.Pdf: The enhanced PDF document
        """
        # Apply base PDF enhancements (including title extraction)
        document = super().enhance(document, **kwargs)

        # Add PDF/UA identifiers based on config
        add_pdfua_identifiers = self.config.get("add_pdfua_identifiers", False)
        if add_pdfua_identifiers:
            with document.open_metadata() as meta:
                # Add PDF/UA identifiers
                meta["pdfaid:part"] = "1"
                meta["pdfaid:conformance"] = "A"

            logger.info("Added PDF/UA identifiers")

        return document

    def enhance_file(
        self, input_path: Union[str, Path], output_path: Union[str, Path], **kwargs
    ) -> bool:
        """
        Enhance a PDF file with basic accessibility features.

        This implementation adds filename extraction for title generation.

        Args:
            input_path: Path to the input PDF document
            output_path: Path where the enhanced document should be saved
            **kwargs: Additional enhancer-specific parameters

        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        # Add filename to kwargs for title extraction
        input_path = Path(input_path)
        kwargs["filename"] = input_path.name

        return super().enhance_file(input_path, output_path, **kwargs)

    def get_capabilities(self) -> List[str]:
        """
        Get the list of enhancement capabilities provided by this enhancer.

        Returns:
            List[str]: List of capability identifiers
        """
        capabilities = super().get_capabilities()
        capabilities.extend(["metadata.pdfua"])
        return capabilities
