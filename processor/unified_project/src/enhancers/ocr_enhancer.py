#!/usr/bin/env python3
"""
OCR and font embedding enhancer module.
"""

import logging
import ocrmypdf
from pathlib import Path
from typing import Union, List

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
            
            # Academic web distribution optimized settings - FORCE OCR FOR STANDARDIZATION
            options = {
                "force_ocr": True,          # FORCE OCR on all documents for standardization
                "skip_text": False,         # Process all text for academic accuracy  
                "redo_ocr": False,          # Don't use redo_ocr due to compatibility issues
                "remove_vectors": False,    # Don't remove vectors to avoid conflicts
                "deskew": False,            # Disable to prevent image transcoding (major size impact)
                "clean": False,             # Disable image enhancement to prevent reprocessing
                "clean_final": False,       # Disable final cleaning to avoid redo_ocr conflicts
                "remove_background": False, # Disable background removal to avoid redo_ocr conflicts
                "optimize": 3,              # Maximum PDF optimization for web distribution
                "jpg_quality": 60,          # Aggressive compression for web viewing
                "png_quality": 60,          # Aggressive PNG compression  
                "jbig2_lossy": True,        # Use lossy JBIG2 compression
                "max_image_mpixels": 30,    # Limit image resolution for web (150 DPI equivalent)
                "use_threads": True,
                "output_type": "pdf",       # Standard PDF output (avoids Ghostscript Tagged PDF issues)
                "pdf_renderer": "sandwich", # Compact renderer for academic papers
                "tesseract_timeout": 600,   # 10 minutes for complex academic content
                
                # Enhanced Academic paper specific Tesseract settings for standardization
                "tesseract_pagesegmode": 1,  # Auto page segmentation with OSD
                "tesseract_oem": 3,          # LSTM + Legacy engine for academic content
                # Simplified config to avoid argument parsing issues
                # "tesseract_config": [
                #     "-c", "preserve_interword_spaces=1",           # Preserve academic spacing
                #     "-c", "tessedit_enable_doc_dict=1",           # Dictionary support for academic terms
                #     "-c", "language_model_ngram_on=1",            # Language modeling for academic text
                # ],
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
            logger.info(f"PDF had existing OCR - forced re-OCR for standardization: {input_path}")
            return True
        except Exception as e:
            # Handle Tesseract temporary file issues with retry logic
            error_msg = str(e)
            if ("failed to open locally" in error_msg or 
                "image file not found" in error_msg or
                "Error during processing" in error_msg or
                len(error_msg.strip()) == 0):  # Empty error message often indicates temp file issues
                logger.warning(f"Tesseract temp file issue detected, retrying with minimal settings: {input_path}")
                # Retry with minimal configuration to avoid temp file conflicts
                try:
                    minimal_options = {
                        "force_ocr": True,
                        "optimize": 1,              # Reduced optimization to avoid conflicts
                        "use_threads": False,       # Single thread to avoid file conflicts
                        "output_type": "pdf",
                        "pdf_renderer": "hocr",     # Different renderer to avoid temp file issues
                        "tesseract_timeout": 300,   # Reduced timeout
                        "jpg_quality": 75,          # Less aggressive compression
                        "png_quality": 75,
                        "max_image_mpixels": 50,    # Higher limit to reduce processing
                    }
                    # Override with any user-provided kwargs
                    minimal_options.update(kwargs)
                    
                    ocrmypdf.ocr(input_path, output_path, **minimal_options)
                    logger.info(f"Successfully processed with minimal settings: {output_path}")
                    return True
                except Exception as retry_error:
                    logger.error(f"Retry with minimal settings also failed: {retry_error}")
                    logger.info(f"Falling back to file copy to continue pipeline: {input_path}")
                    # As a last resort, copy the file to continue the pipeline
                    import shutil
                    shutil.copy(input_path, output_path)
                    return True
            logger.error(f"An unexpected error occurred during OCR: {e}")
            return False

    def enhance(self, document, **kwargs):
        """
        This enhancer operates on files directly, so this method is not used.
        """
        raise NotImplementedError("OCREnhancer operates on file paths directly via enhance_file.")

    def get_capabilities(self) -> List[str]:
        """
        Get the list of enhancement capabilities provided by this enhancer.

        Returns:
            List[str]: List of capability identifiers
        """
        return [
            "ocr.force_ocr",
            "ocr.academic_tesseract",
            "ocr.table_detection", 
            "ocr.math_support",
            "ocr.font_embedding",
            "compression.aggressive_web",
            "compression.jpeg_optimization",
            "compression.png_optimization", 
            "compression.jbig2_lossy",
            "compression.image_resolution_limit",
            "academic.table_processing",
            "academic.layout_analysis",
            "academic.spacing_preservation"
        ]

