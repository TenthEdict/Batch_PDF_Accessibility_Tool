#!/usr/bin/env python3
"""
Simplified OCR enhancer without ML optimization.

This enhancer provides basic OCR functionality using pytesseract
with standard parameters. No machine learning, no pattern optimization,
just reliable OCR processing.
"""

import logging
import fitz  # PyMuPDF
from pathlib import Path
from typing import Union, Optional
from PIL import Image
import io

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

logger = logging.getLogger(__name__)


class SimpleOCREnhancer:
    """
    Simple OCR enhancer using pytesseract with standard parameters.

    Features:
    - Intelligent OCR detection (checks if PDF already has text)
    - Standard DPI (300) and language (eng)
    - Page-by-page processing
    - No ML optimization or pattern learning
    """

    def __init__(self, text_threshold: int = 100, dpi: int = 300, language: str = 'eng'):
        """
        Initialize the simple OCR enhancer.

        Args:
            text_threshold: Minimum average characters per page to skip OCR (default: 100)
            dpi: DPI for image conversion (default: 300)
            language: Tesseract language code (default: 'eng')
        """
        if not PYTESSERACT_AVAILABLE:
            raise ImportError(
                "pytesseract is required for SimpleOCREnhancer. "
                "Install it with: pip install pytesseract"
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
            return self._apply_ocr(input_path, output_path)

        except Exception as e:
            logger.error(f"Error in OCR enhancement: {e}")
            return False

    def _apply_ocr(self, input_path: Path, output_path: Path) -> bool:
        """
        Apply OCR to PDF using pytesseract.

        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF

        Returns:
            bool: True if successful
        """
        try:
            # Open source PDF
            source_doc = fitz.open(input_path)

            # Create new PDF for output
            output_doc = fitz.open()

            total_pages = len(source_doc)
            logger.info(f"Processing {total_pages} pages with OCR")

            for page_num in range(total_pages):
                # Get page
                page = source_doc[page_num]

                # Convert page to image
                mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
                pix = page.get_pixmap(matrix=mat)

                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))

                # Run OCR
                ocr_text = pytesseract.image_to_string(img, lang=self.language)

                # Create new page with OCR text
                new_page = output_doc.new_page(width=page.rect.width, height=page.rect.height)

                # Insert original page content
                new_page.show_pdf_page(new_page.rect, source_doc, page_num)

                # Add OCR text layer (invisible)
                if ocr_text.strip():
                    text_rect = new_page.rect
                    new_page.insert_textbox(
                        text_rect,
                        ocr_text,
                        fontsize=8,
                        color=(1, 1, 1),  # White (invisible)
                        overlay=False
                    )

                logger.debug(f"Processed page {page_num + 1}/{total_pages}")

            # Save output PDF
            output_doc.save(output_path)
            output_doc.close()
            source_doc.close()

            logger.info(f"OCR complete: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error applying OCR: {e}")
            return False

    def get_capabilities(self):
        """Get list of capabilities."""
        return [
            "ocr.basic_tesseract",
            "ocr.intelligent_detection",
            "ocr.text_analysis",
        ]
