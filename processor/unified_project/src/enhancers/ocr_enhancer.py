#!/usr/bin/env python3
"""
OCR and font embedding enhancer module.
"""

import logging
import ocrmypdf
from pathlib import Path
from typing import Union

from .enhancer_base import EnhancerBase

logger = logging.getLogger(__name__)


class OCREnhancer(EnhancerBase):
    """
    Enhancer for performing OCR and font embedding using ocrmypdf.
    """

    def __init__(self):
        super().__init__("ocr_enhancer")

    def enhance_file(
        self, input_path: Union[str, Path], output_path: Union[str, Path], **kwargs
    ) -> bool:
        """
        Apply OCR and font embedding to a PDF file.

        Args:
            input_path: Path to the input PDF document.
            output_path: Path where the enhanced document should be saved.
            **kwargs: Additional parameters for ocrmypdf.

        Returns:
            bool: True if enhancement was successful, False otherwise.
        """
        try:
            logger.info(f"Starting OCR and font embedding for {input_path}")
            
            # Default options optimized for smaller file sizes while avoiding Ghostscript 10.0.0 regression
            options = {
                "force_ocr": True,          # Always OCR all pages regardless of existing text
                "skip_text": False,         # Disable skip_text to avoid Ghostscript 10.0.0 regression
                "redo_ocr": False,          # Don't redo OCR on pages with existing text
                "deskew": False,            # Disable deskew to prevent image transcoding
                "clean": False,             # Disable clean to prevent image reprocessing  
                "optimize": 1,              # Enable basic PDF optimization
                "pdfa_image_compression": "jpeg",  # Use JPEG compression for images
                "jpeg_quality": 85,         # Good quality/size balance (default: 0 = lossless)
                "png_quality": 85,          # Compress PNG images
                "jbig2_lossy": True,        # Use lossy JBIG2 compression for better compression
                "use_threads": True,
                "output_type": "pdf",       # Use PDF output to avoid Ghostscript processing
                "pdf_renderer": "sandwich", # More compact than hocr renderer
                "tesseract_timeout": 600,   # 10 minutes
            }
            
            # Override with any user-provided kwargs
            options.update(kwargs)

            ocrmypdf.ocr(
                input_path,
                output_path,
                **options
            )
            
            logger.info(f"Successfully processed and saved to {output_path}")
            return True
        except ocrmypdf.exceptions.EncryptedPdfError:
            logger.error(f"Cannot process encrypted PDF: {input_path}")
            return False
        except ocrmypdf.exceptions.PriorOcrFoundError:
            logger.warning(f"PDF already has text. If OCR is still desired, consider using --force-ocr. File: {input_path}")
            # In this case, we can consider it a "success" as no action is needed.
            # Copy the file to the output path to continue the pipeline.
            import shutil
            shutil.copy(input_path, output_path)
            return True
        except Exception as e:
            logger.error(f"An unexpected error occurred during OCR: {e}")
            return False

    def enhance(self, document, **kwargs):
        """
        This enhancer operates on files directly, so this method is not used.
        """
        raise NotImplementedError("OCREnhancer operates on file paths directly via enhance_file.")

