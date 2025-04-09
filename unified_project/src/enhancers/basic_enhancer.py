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
                - extract_title_from_filename: Whether to extract the title
                  from the filename if not provided (default: True)
                - filename: Original filename (for title extraction)
            
        Returns:
            pikepdf.Pdf: The enhanced PDF document
        """
        # Extract title from H1 tag if available, otherwise fallback to filename
        extract_title_from_h1 = kwargs.get('extract_title_from_h1', True)
        extract_title_from_filename = kwargs.get('extract_title_from_filename', False)  # Default to False to prioritize H1

        if extract_title_from_h1 and not kwargs.get('title'):
            # Try to extract title from H1 tag in the document
            title_from_h1 = self._extract_title_from_h1_tag(document)
            if title_from_h1:
                kwargs['title'] = title_from_h1
                logger.info(f"Extracted title from H1 tag: {kwargs['title']}")
            elif extract_title_from_filename and kwargs.get('filename'):
                # Fallback to filename if no H1 tag found
                filename = Path(kwargs['filename']).stem
                kwargs['title'] = filename.replace('_', ' ').title()
                logger.info(f"Extracted title from filename: {kwargs['title']}")
        elif extract_title_from_filename and not kwargs.get('title') and kwargs.get('filename'):
            # Extract title from filename
            filename = Path(kwargs['filename']).stem
            kwargs['title'] = filename.replace('_', ' ').title()
            logger.info(f"Extracted title from filename: {kwargs['title']}")
        
        # Apply base PDF enhancements
        document = super().enhance(document, **kwargs)
        
        # Add PDF/UA identifiers based on config
        add_pdfua_identifiers = self.config.get('add_pdfua_identifiers', False)
        if add_pdfua_identifiers:
            with document.open_metadata() as meta:
                # Add PDF/UA identifiers
                meta['pdfaid:part'] = '1'
                meta['pdfaid:conformance'] = 'A'
            
            logger.info("Added PDF/UA identifiers")
        
        return document
    
    def enhance_file(self, 
                    input_path: Union[str, Path], 
                    output_path: Union[str, Path], 
                    **kwargs) -> bool:
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
        kwargs['filename'] = input_path.name
        
        return super().enhance_file(input_path, output_path, **kwargs)
    
    def _extract_title_from_h1_tag(self, document: pikepdf.Pdf) -> Optional[str]:
        """
        Extract the document title from the first H1 tag in the document.
        
        This method analyzes the document structure to find the first heading (H1)
        and uses its text as the document title.
        
        Args:
            document: The PDF document to analyze
            
        Returns:
            str or None: The extracted title or None if no H1 tag is found
        """
        try:
            import sys
            import re
            import io
            
            # Import needed modules
            try:
                import fitz  # PyMuPDF
            except ImportError:
                logger.warning("PyMuPDF (fitz) is required for H1 extraction. Falling back to filename.")
                return None
                
            # Extract first page for title analysis
            if len(document.pages) == 0:
                return None
                
            # Save document to a temporary buffer
            buffer = io.BytesIO()
            document.save(buffer)
            buffer.seek(0)
            
            # Open with PyMuPDF for text extraction and analysis
            with fitz.open(stream=buffer, filetype="pdf") as doc:
                if not doc.page_count:
                    return None
                    
                # Get the first page
                page = doc[0]
                
                # Extract text blocks with their attributes
                blocks = page.get_text("dict")["blocks"]
                
                # Find potential headings based on font size and position
                headings = []
                max_font_size = 0
                
                # First pass: determine the maximum font size used in the document
                for block in blocks:
                    if block.get("type") == 0:  # Text block
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                max_font_size = max(max_font_size, span.get("size", 0))
                
                # Second pass: identify the actual headings
                # Typically, headings use larger fonts and are positioned near the top
                threshold_size = max_font_size * 0.85  # Headings are usually at least 85% of the max font size
                
                # Sort blocks by vertical position (top to bottom)
                blocks_by_position = sorted(blocks, key=lambda b: b.get("bbox", [0, 0, 0, 0])[1])
                
                # First: Collect all potential heading spans
                potential_heading_spans = []
                
                for block in blocks_by_position:
                    if block.get("type") == 0:  # Text block
                        for line in block.get("lines", []):
                            line_spans = []
                            line_y = line.get("bbox", [0, 0, 0, 0])[1]  # y-position (top)
                            
                            for span in line.get("spans", []):
                                size = span.get("size", 0)
                                text = span.get("text", "").strip()
                                
                                # Check if this is likely a heading span
                                if (size >= threshold_size and 
                                    text and 
                                    len(text) > 3 and 
                                    not text.endswith(".")):  # Headings rarely end with periods
                                    
                                    line_spans.append({
                                        "text": text,
                                        "size": size,
                                        "y": line_y,
                                        "x": span.get("bbox", [0, 0, 0, 0])[0]  # x-position (left)
                                    })
                            
                            # Add all spans from this line
                            if line_spans:
                                potential_heading_spans.append(line_spans)
                
                # Second: Reconstruct full headings from spans
                line_headings = []
                for line_spans in potential_heading_spans:
                    if not line_spans:
                        continue
                        
                    # Sort spans within line by x-position
                    sorted_spans = sorted(line_spans, key=lambda s: s.get("x", 0))
                    
                    # Combine all spans in the line to form a complete heading
                    combined_text = " ".join([s.get("text", "") for s in sorted_spans])
                    
                    # Use size and y-position from the first span
                    line_headings.append({
                        "text": combined_text,
                        "size": sorted_spans[0].get("size", 0),
                        "y": sorted_spans[0].get("y", 0)
                    })
                
                # Third: Handle multi-line titles by combining consecutive headings with similar font size
                # Sort headings by vertical position
                line_headings.sort(key=lambda h: h.get("y", 0))
                
                # Merge consecutive headings that are likely part of the same title
                i = 0
                while i < len(line_headings):
                    current = line_headings[i]
                    title_parts = [current["text"]]
                    
                    # Look ahead for consecutive headings that could be part of the same title
                    j = i + 1
                    while j < len(line_headings):
                        next_heading = line_headings[j]
                        
                        # Check if the next heading is close in vertical position and similar in font size
                        y_diff = next_heading["y"] - current["y"]
                        size_ratio = min(current["size"], next_heading["size"]) / max(current["size"], next_heading["size"])
                        
                        # Conditions for merging: close vertically (less than 3x line height) and similar font size (within 15%)
                        if y_diff < current["size"] * 3 and size_ratio > 0.85:
                            title_parts.append(next_heading["text"])
                            j += 1
                        else:
                            break
                    
                    # Create the multi-line title
                    if len(title_parts) > 1:
                        headings.append({
                            "text": " ".join(title_parts),
                            "size": current["size"],
                            "y": current["y"]
                        })
                        i = j  # Skip all the merged headings
                    else:
                        headings.append(current)
                        i += 1
                
                # Get the first heading that's not special text like "Abstract" or "Introduction"
                non_heading_terms = ["abstract", "introduction", "summary", "contents", "table of contents"]
                
                for heading in headings:
                    text = heading["text"].lower()
                    if all(term not in text for term in non_heading_terms):
                        return heading["text"].strip()
                        
                # If no suitable heading found, return the first heading as fallback
                if headings:
                    return headings[0]["text"].strip()
                    
            return None
                
        except Exception as e:
            logger.warning(f"Error extracting title from H1 tag: {str(e)}")
            return None
            
    def get_capabilities(self) -> List[str]:
        """
        Get the list of enhancement capabilities provided by this enhancer.
        
        Returns:
            List[str]: List of capability identifiers
        """
        capabilities = super().get_capabilities()
        capabilities.extend([
            'metadata.pdfua',
            'metadata.title_from_filename',
            'metadata.title_from_h1'
        ])
        return capabilities