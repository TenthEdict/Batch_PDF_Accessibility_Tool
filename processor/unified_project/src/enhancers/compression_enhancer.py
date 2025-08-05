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
        """Initialize the compression enhancer."""
        super().__init__("compression_enhancer", environment)
        
        # Academic web distribution settings
        self.target_dpi = 150          # Optimal for web viewing
        self.jpeg_quality = 60         # Aggressive for web distribution
        self.png_to_jpeg_threshold = 0.8  # Convert PNG to JPEG if compression ratio > 80%
        self.max_image_width = 2000    # Max width for academic figures
        self.max_image_height = 2000   # Max height for academic figures

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
        """Apply academic paper specific compression techniques."""
        try:
            # Open document with PyMuPDF for compression
            doc = fitz.open(input_path)
            
            # Compress each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                self._compress_page_images(doc, page, page_num)
            
            # Apply document-level optimizations
            self._optimize_document_structure(doc)
            
            # Save with maximum compression
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(
                output_path,
                garbage=4,           # Maximum garbage collection
                deflate=True,        # Enable deflate compression
                clean=True,          # Clean up document structure
                ascii=False,         # Use binary encoding
                linear=False,        # Don't linearize (web serving will handle)
                no_new_id=True,      # Don't generate new ID
                encryption=fitz.PDF_ENCRYPT_NONE  # No encryption
            )
            
            doc.close()
            return True
            
        except Exception as e:
            logger.error(f"Error in academic PDF compression: {e}")
            return False

    def _compress_page_images(self, doc: fitz.Document, page: fitz.Page, page_num: int) -> None:
        """Compress all images on a page for academic content."""
        image_list = page.get_images()
        
        if not image_list:
            return
            
        logger.info(f"Compressing {len(image_list)} images on page {page_num + 1}")
        
        for img_index, img in enumerate(image_list):
            try:
                # Get image data
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Process image with Pillow
                pil_image = Image.open(io.BytesIO(image_bytes))
                
                # Apply academic paper specific compression
                compressed_image = self._compress_academic_image(pil_image, image_ext)
                
                if compressed_image:
                    # Replace image in PDF
                    self._replace_image_in_pdf(doc, xref, compressed_image)
                    
            except Exception as e:
                logger.warning(f"Could not compress image {img_index} on page {page_num + 1}: {e}")

    def _compress_academic_image(self, pil_image: Image.Image, original_ext: str) -> bytes:
        """
        Apply academic paper specific image compression.
        
        Academic papers often contain:
        - Figures and charts (good for JPEG)
        - Diagrams (may need PNG)
        - Tables (good for high compression)
        - Photos (excellent for JPEG)
        """
        # Convert to RGB if necessary (for JPEG compatibility)
        if pil_image.mode in ('RGBA', 'LA', 'P'):
            # Check if image has transparency
            if pil_image.mode == 'RGBA' and self._has_transparency(pil_image):
                # Keep as PNG for transparency
                format_to_use = 'PNG'
                pil_image = pil_image.convert('RGBA')
            else:
                # Convert to RGB for JPEG
                format_to_use = 'JPEG'
                if pil_image.mode == 'RGBA':
                    # Create white background for transparent images
                    background = Image.new('RGB', pil_image.size, (255, 255, 255))
                    background.paste(pil_image, mask=pil_image.split()[-1])
                    pil_image = background
                else:
                    pil_image = pil_image.convert('RGB')
        else:
            # Default to JPEG for academic content
            format_to_use = 'JPEG'
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
        
        # Resize if too large (academic papers rarely need huge images)
        if pil_image.width > self.max_image_width or pil_image.height > self.max_image_height:
            pil_image.thumbnail((self.max_image_width, self.max_image_height), Image.Resampling.LANCZOS)
            logger.debug(f"Resized image to {pil_image.width}x{pil_image.height}")
        
        # Compress based on format
        output_buffer = io.BytesIO()
        
        if format_to_use == 'JPEG':
            pil_image.save(
                output_buffer, 
                format='JPEG', 
                quality=self.jpeg_quality,
                optimize=True,
                progressive=True  # Better for web loading
            )
        else:  # PNG
            pil_image.save(
                output_buffer,
                format='PNG',
                optimize=True,
                compress_level=9  # Maximum PNG compression
            )
        
        return output_buffer.getvalue()

    def _has_transparency(self, image: Image.Image) -> bool:
        """Check if RGBA image has actual transparency."""
        if image.mode != 'RGBA':
            return False
        
        # Check alpha channel
        alpha = image.split()[-1]
        return alpha.getextrema()[0] < 255

    def _replace_image_in_pdf(self, doc: fitz.Document, xref: int, image_bytes: bytes) -> None:
        """Replace an image in the PDF with compressed version."""
        try:
            # Create new image from compressed bytes
            new_image = fitz.open("png", image_bytes) if image_bytes[:4] == b'\x89PNG' else fitz.open("jpg", image_bytes)
            
            # Replace the image
            doc.update_stream(xref, image_bytes)
            new_image.close()
            
        except Exception as e:
            logger.warning(f"Could not replace image with xref {xref}: {e}")

    def _optimize_document_structure(self, doc: fitz.Document) -> None:
        """Apply document-level optimizations for academic papers."""
        try:
            # Remove unused resources
            doc.scrub()
            
            # Academic papers often have embedded fonts that can be optimized
            self._optimize_fonts(doc)
            
            # Clean metadata (keep essential, remove bloat)
            self._clean_metadata(doc)
            
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
            "compression.aggressive_web",
            "compression.image_optimization", 
            "compression.academic_specific",
            "compression.png_to_jpeg",
            "compression.font_optimization",
            "compression.structure_cleanup",
            "compression.metadata_cleaning"
        ]
