#!/usr/bin/env python3
"""
Compression enhancer for academic papers optimized for web distribution.

This module provides aggressive PDF and image compression specifically
optimized for academic papers distributed on digital commons platforms.
Focuses on maximum file size reduction for web viewing.
"""

import io
import logging
import tempfile
from pathlib import Path
from typing import Union, Dict, List, Tuple, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    raise ImportError(
        "PyMuPDF (fitz) is required for compression. "
        "Install it with: pip install PyMuPDF"
    )

try:
    from PIL import Image, ImageOps
except ImportError:
    raise ImportError(
        "Pillow is required for image processing. "
        "Install it with: pip install Pillow"
    )

from .enhancer_base import EnhancerBase

logger = logging.getLogger(__name__)


class CompressionEnhancer(EnhancerBase):
    """
    Compression enhancer for academic papers optimized for web distribution.
    
    Applies aggressive compression techniques specifically designed for
    academic papers that will be viewed on web platforms, not printed.
    """

    def __init__(self, environment: Optional[str] = None):
        """Initialize the compression enhancer with figure-preserving settings."""
        super().__init__("compression_enhancer", environment)
        
        # Academic figure preservation settings - balanced compression
        self.target_dpi = 150          # Optimal for web viewing
        self.jpeg_quality = 85         # Higher quality for academic figures
        self.png_quality = 90          # High quality for diagrams and charts
        self.png_to_jpeg_threshold = 0.5  # More conservative conversion threshold
        self.max_image_width = 3000    # Higher limit for detailed academic figures
        self.max_image_height = 3000   # Higher limit for detailed academic figures
        self.min_compression_size = 50000  # Don't compress images smaller than 50KB

    def enhance_file(
        self, input_path: Union[str, Path], output_path: Union[str, Path], **kwargs
    ) -> bool:
        """
        Apply aggressive compression to PDF file for web distribution.

        Args:
            input_path: Path to the input PDF document
            output_path: Path where the compressed document should be saved
            **kwargs: Additional compression parameters

        Returns:
            bool: True if compression was successful, False otherwise
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            return False

        try:
            logger.info(f"Starting aggressive compression for academic paper: {input_path}")
            
            # Get original file size
            original_size = input_path.stat().st_size
            
            # Apply compression
            success = self._compress_pdf_academic(input_path, output_path)
            
            if success and output_path.exists():
                # Calculate compression ratio
                compressed_size = output_path.stat().st_size
                compression_ratio = (original_size - compressed_size) / original_size * 100
                
                logger.info(f"Compression completed successfully")
                logger.info(f"Original size: {original_size / 1024 / 1024:.2f} MB")
                logger.info(f"Compressed size: {compressed_size / 1024 / 1024:.2f} MB")
                logger.info(f"Size reduction: {compression_ratio:.1f}%")
                
                return True
            else:
                logger.error("Compression failed")
                return False
                
        except Exception as e:
            logger.error(f"Error during compression: {e}")
            return False

    def _compress_pdf_academic(self, input_path: Path, output_path: Path) -> bool:
        """Apply academic paper specific compression techniques with Adobe Acrobat compatibility."""
        try:
            # Open document with PyMuPDF for compression
            doc = fitz.open(input_path)
            
            # Apply document-level optimizations without modifying image structures
            self._optimize_document_structure(doc)
            
            # Save with conservative compression that maintains Adobe compatibility
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(
                output_path,
                garbage=2,           # Moderate garbage collection (safer than aggressive)
                deflate=True,        # Enable deflate compression
                clean=False,         # Don't clean structure (maintains Adobe compatibility)
                ascii=False,         # Use binary encoding for better compression
                linear=False,        # Don't linearize
                no_new_id=True,      # Don't generate new ID
                encryption=fitz.PDF_ENCRYPT_NONE  # No encryption
            )
            
            doc.close()
            return True
            
        except Exception as e:
            logger.error(f"Error in academic PDF compression: {e}")
            return False

    def _log_image_analysis(self, doc: fitz.Document) -> None:
        """Log image analysis for academic papers without modifying them."""
        total_images = 0
        total_size = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            images = page.get_images()
            
            if images:
                logger.info(f"Page {page_num + 1}: {len(images)} images found")
                total_images += len(images)
                
                for img_index, img in enumerate(images):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_size = len(base_image["image"])
                        total_size += image_size
                        
                        logger.debug(f"  Image {img_index}: {base_image['width']}x{base_image['height']}, "
                                   f"{base_image['ext']}, {image_size:,} bytes")
                        
                    except Exception as e:
                        logger.warning(f"Could not analyze image {img_index} on page {page_num + 1}: {e}")
        
        if total_images > 0:
            logger.info(f"Document analysis: {total_images} images, {total_size / 1024:.1f} KB total")
            logger.info(f"Images preserved without modification for Adobe Acrobat compatibility")

    def _optimize_document_structure(self, doc: fitz.Document) -> None:
        """Apply document-level optimizations for academic papers with Adobe compatibility."""
        try:
            # Log image analysis without modifying images
            self._log_image_analysis(doc)
            
            # Conservative document optimization that maintains structure
            # Remove unused resources without breaking image references
            doc.scrub()
            
            # Academic papers often have embedded fonts that can be optimized
            self._optimize_fonts(doc)
            
            # Clean metadata (keep essential, remove bloat)
            self._clean_metadata(doc)
            
            logger.info("Applied Adobe-compatible document optimization")
            
        except Exception as e:
            logger.warning(f"Could not optimize document structure: {e}")

    def _optimize_fonts(self, doc: fitz.Document) -> None:
        """Optimize fonts for academic papers."""
        try:
            # Get font information
            font_list = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                font_list.extend(page.get_fonts())
            
            logger.info(f"Document contains {len(set(font_list))} unique fonts")
            
            # Note: Font subsetting is handled by PyMuPDF automatically
            # when saving with garbage collection
            
        except Exception as e:
            logger.warning(f"Could not optimize fonts: {e}")

    def _clean_metadata(self, doc: fitz.Document) -> None:
        """Clean document metadata, keeping essential information."""
        try:
            metadata = doc.metadata
            
            # Keep essential metadata, remove bloat
            essential_keys = {'title', 'author', 'subject', 'creator', 'producer', 'creationDate', 'modDate'}
            
            # Remove non-essential metadata
            for key in list(metadata.keys()):
                if key not in essential_keys:
                    metadata[key] = ""
            
            doc.set_metadata(metadata)
            
        except Exception as e:
            logger.warning(f"Could not clean metadata: {e}")

    def enhance(self, document, **kwargs):
        """This enhancer operates on files directly."""
        raise NotImplementedError("CompressionEnhancer operates on file paths directly via enhance_file.")

    def get_capabilities(self) -> List[str]:
        """Get compression capabilities."""
        return [
            "compression.adobe_compatible",
            "compression.structure_preservation", 
            "compression.academic_optimized",
            "compression.safe_processing",
            "compression.image_analysis",
            "compression.font_optimization",
            "compression.metadata_cleaning",
            "compression.stream_compression"
        ]
