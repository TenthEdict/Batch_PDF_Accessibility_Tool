#!/usr/bin/env python3
"""
Simplified OCR enhancer for Acrobat manual tagging workflow.

This enhancer creates INVISIBLE OCR text with marked content operators
that Acrobat can link to when manually creating tags. The marked content
provides "hooks" that allow Acrobat to associate invisible text with
structure elements during manual tagging.
"""

import logging
import fitz  # PyMuPDF
from pathlib import Path
from typing import Union, Optional

try:
    import ocrmypdf
    OCRMYPDF_AVAILABLE = True
except ImportError:
    OCRMYPDF_AVAILABLE = False

logger = logging.getLogger(__name__)


class SimpleOCREnhancer:
    """
    Simple OCR enhancer for Acrobat manual tagging workflow.

    Features:
    - Creates INVISIBLE OCR text (readable by screen readers, not visible to sighted users)
    - Generates marked content operators (BDC/EMC) that Acrobat uses as tagging "hooks"
    - Intelligent OCR detection (checks if PDF already has text)
    - Standard DPI (300) and language (eng)
    """

    def __init__(self, text_threshold: int = 100, dpi: int = 300, language: str = 'eng'):
        """
        Initialize the simple OCR enhancer.

        Args:
            text_threshold: Minimum average characters per page to skip OCR (default: 100)
            dpi: DPI for OCR processing (default: 300)
            language: Tesseract language code (default: 'eng')
        """
        if not OCRMYPDF_AVAILABLE:
            raise ImportError(
                "ocrmypdf is required for SimpleOCREnhancer. "
                "Install it with: pip install ocrmypdf"
            )

        self.text_threshold = text_threshold
        self.dpi = dpi
        self.language = language
        self.name = "simple_ocr_enhancer"

        logger.info(f"SimpleOCREnhancer initialized (DPI: {dpi}, Lang: {language}, Threshold: {text_threshold})")

    def needs_ocr(self, pdf_path: Union[str, Path]) -> bool:
        """
        Check if PDF needs OCR by analyzing text content.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            bool: True if OCR is needed (insufficient text), False otherwise
        """
        try:
            pdf_path = Path(pdf_path)
            doc = fitz.open(pdf_path)

            total_pages = len(doc)
            if total_pages == 0:
                doc.close()
                return True

            # Sample first 3 pages or all pages if fewer
            sample_pages = min(3, total_pages)
            total_chars = 0

            for page_num in range(sample_pages):
                page = doc[page_num]
                text = page.get_text().strip()
                total_chars += len(text)

            doc.close()

            avg_chars_per_page = total_chars / sample_pages
            needs_ocr = avg_chars_per_page < self.text_threshold

            logger.info(f"Text analysis: {avg_chars_per_page:.1f} avg chars/page - OCR needed: {needs_ocr}")
            return needs_ocr

        except Exception as e:
            logger.error(f"Error analyzing PDF text: {e}")
            # Default to needing OCR if analysis fails
            return True

    def enhance_file(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        force_ocr: bool = False,
        **kwargs
    ) -> bool:
        """
        Apply OCR to PDF file if needed.

        Args:
            input_path: Path to the input PDF
            output_path: Path where the enhanced PDF should be saved
            force_ocr: Force OCR even if text exists (default: False)
            **kwargs: Additional parameters (ignored for simplicity)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)

            if not input_path.exists():
                logger.error(f"Input file not found: {input_path}")
                return False

            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if OCR is needed
            if not force_ocr and not self.needs_ocr(input_path):
                logger.info("PDF has sufficient text - skipping OCR, copying to output")
                # Just copy the file if OCR not needed
                import shutil
                shutil.copy2(input_path, output_path)
                return True

            # Perform OCR
            logger.info(f"Starting OCR processing: {input_path}")
            return self._apply_ocr(input_path, output_path, force_ocr=force_ocr)

        except Exception as e:
            logger.error(f"Error in OCR enhancement: {e}")
            return False

    def _apply_ocr(self, input_path: Path, output_path: Path, force_ocr: bool = False) -> bool:
        """
        Apply OCR to PDF using ocrmypdf with proper text positioning.

        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF
            force_ocr: Force OCR even if text exists (currently always True to avoid Ghostscript bug)

        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Starting OCR processing with ocrmypdf: {input_path}")

            # WORKAROUND: Always use force_ocr to avoid Ghostscript 10.0.0 bug
            # Ghostscript 10.0.0-10.02.0 have regressions that corrupt PDFs when using skip_text
            # Using force_ocr avoids Ghostscript entirely by discarding and regenerating all text
            logger.info("Using force_ocr mode to avoid Ghostscript 10.0.0 bug")

            options = {
                "language": self.language,
                "force_ocr": True,              # Always force OCR to avoid Ghostscript
                "optimize": 0,                  # No compression (keep quality)
                "output_type": "pdf",           # PDF output
                "pdf_renderer": "hocr",         # hOCR: creates marked content for Acrobat tagging
                "progress_bar": False,          # Disable progress bar for cleaner logs
            }

            # Run ocrmypdf
            ocrmypdf.ocr(
                input_path,
                output_path,
                **options
            )

            logger.info(f"OCR complete: {output_path}")
            return True

        except ocrmypdf.exceptions.PriorOcrFoundError:
            # PDF already has OCR text, just copy it
            logger.info("PDF already has OCR text, copying to output")
            import shutil
            shutil.copy2(input_path, output_path)
            return True

        except ocrmypdf.exceptions.EncryptedPdfError:
            logger.error(f"Cannot process encrypted PDF: {input_path}")
            return False

        except Exception as e:
            logger.error(f"Error applying OCR: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False

    def get_capabilities(self):
        """Get list of capabilities."""
        return [
            "ocr.ocrmypdf",
            "ocr.automatic_positioning",
            "ocr.intelligent_detection",
            "ocr.text_analysis",
        ]
