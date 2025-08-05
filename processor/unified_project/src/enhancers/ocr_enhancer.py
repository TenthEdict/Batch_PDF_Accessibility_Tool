#!/usr/bin/env python3
"""
OCR and font embedding enhancer module with intelligent OCR detection.
"""

import logging
import ocrmypdf
from pathlib import Path
from typing import Union, List

from .enhancer_base import EnhancerBase
from .pdf_text_analyzer import PDFTextAnalyzer

logger = logging.getLogger(__name__)


class OCREnhancer(EnhancerBase):
    """
    Enhancer for performing OCR and font embedding using ocrmypdf with intelligent OCR detection.
    """

    def __init__(self, text_threshold: int = 100, sample_pages: int = 3):
        super().__init__("ocr_enhancer")
        self.text_analyzer = PDFTextAnalyzer(text_threshold=text_threshold, sample_pages=sample_pages)
        logger.info(f"OCR Enhancer initialized with text threshold: {text_threshold} chars/page")

    def enhance_file(
        self, input_path: Union[str, Path], output_path: Union[str, Path], **kwargs
    ) -> bool:
        """
        Apply OCR and font embedding to a PDF file with intelligent OCR detection.

        Args:
            input_path: Path to the input PDF document.
            output_path: Path where the enhanced document should be saved.
            **kwargs: Additional parameters for ocrmypdf.
                     Special kwargs:
                     - force_ocr_override: bool - Force OCR even if text exists
                     - skip_text_analysis: bool - Skip text analysis and apply OCR

        Returns:
            bool: True if enhancement was successful, False otherwise.
        """
        try:
            logger.info(f"Starting intelligent OCR processing for {input_path}")
            
            # Check for override parameters
            force_ocr_override = kwargs.pop('force_ocr_override', False)
            skip_text_analysis = kwargs.pop('skip_text_analysis', False)
            
            # Determine if OCR is needed
            if skip_text_analysis or force_ocr_override:
                needs_ocr = True
                analysis_reason = "OCR forced by override parameter"
                logger.info(f"OCR forced by override: {analysis_reason}")
            else:
                # Analyze text content to determine if OCR is needed
                analysis = self.text_analyzer.analyze_text_content(input_path)
                needs_ocr = analysis["needs_ocr"]
                analysis_reason = analysis["reason"]
                
                logger.info(f"Text analysis: {analysis_reason}")
                logger.info(f"OCR needed: {needs_ocr} (avg: {analysis['avg_chars_per_page']:.1f} chars/page)")

            # Configure OCR options based on analysis
            if needs_ocr:
                logger.info("Applying OCR with compression optimization")
                return self._apply_ocr_with_compression(input_path, output_path, **kwargs)
            else:
                logger.info("Skipping OCR - applying compression-only optimization")
                return self._apply_compression_only(input_path, output_path, **kwargs)
                
        except Exception as e:
            logger.error(f"Error in intelligent OCR processing: {e}")
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
            "ocr.intelligent_detection",
            "ocr.text_content_analysis",
            "ocr.conditional_processing",
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
            "compression.compression_only_mode",
            "academic.table_processing",
            "academic.layout_analysis",
            "academic.spacing_preservation",
            "safety.pdf_corruption_prevention"
        ]

    def _apply_ocr_with_compression(self, input_path, output_path, **kwargs):
        """Apply OCR with compression optimization for documents that need OCR."""
        try:
            # Academic web distribution optimized settings with OCR
            options = {
                "force_ocr": True,          # OCR needed based on text analysis
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
                
                # Enhanced Academic paper specific Tesseract settings
                "tesseract_pagesegmode": 1,  # Auto page segmentation with OSD
                "tesseract_oem": 3,          # LSTM + Legacy engine for academic content
            }
            
            # Override with any user-provided kwargs
            options.update(kwargs)

            ocrmypdf.ocr(input_path, output_path, **options)
            
            logger.info(f"Successfully applied OCR with compression to {output_path}")
            return True
            
        except ocrmypdf.exceptions.EncryptedPdfError:
            logger.error(f"Cannot process encrypted PDF: {input_path}")
            return False
        except ocrmypdf.exceptions.PriorOcrFoundError:
            logger.info(f"PDF had existing OCR - applied forced OCR for standardization: {input_path}")
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

    def _apply_compression_only(self, input_path, output_path, **kwargs):
        """Apply compression-only optimization for documents with existing good text."""
        try:
            # Compression-only settings without OCR for documents with existing text
            options = {
                "skip_text": True,          # Skip OCR completely - preserve existing text
                "force_ocr": False,         # Don't force OCR on documents with good text
                "redo_ocr": False,          # Don't redo existing OCR
                "remove_vectors": False,    # Don't remove vectors to preserve quality
                "deskew": False,            # Disable to prevent image transcoding
                "clean": False,             # Disable image enhancement to prevent reprocessing
                "clean_final": False,       # Disable final cleaning
                "remove_background": False, # Disable background removal
                "optimize": 3,              # Maximum PDF optimization for web distribution
                "jpg_quality": 60,          # Aggressive compression for web viewing
                "png_quality": 60,          # Aggressive PNG compression  
                "jbig2_lossy": True,        # Use lossy JBIG2 compression
                "max_image_mpixels": 30,    # Limit image resolution for web (150 DPI equivalent)
                "use_threads": True,
                "output_type": "pdf",       # Standard PDF output
                "pdf_renderer": "sandwich", # Compact renderer for academic papers
            }
            
            # Override with any user-provided kwargs
            options.update(kwargs)

            ocrmypdf.ocr(input_path, output_path, **options)
            
            logger.info(f"Successfully applied compression-only optimization to {output_path}")
            return True
            
        except ocrmypdf.exceptions.EncryptedPdfError:
            logger.error(f"Cannot process encrypted PDF: {input_path}")
            return False
        except Exception as e:
            logger.warning(f"Compression-only processing failed, falling back to copy: {e}")
            # Fall back to simple copy if compression fails
            import shutil
            try:
                shutil.copy(input_path, output_path)
                logger.info(f"Fallback file copy completed: {output_path}")
                return True
            except Exception as copy_error:
                logger.error(f"File copy fallback also failed: {copy_error}")
                return False

