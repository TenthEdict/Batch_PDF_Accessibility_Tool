#!/usr/bin/env python3
"""
Simplified OCR enhancer for Acrobat manual tagging workflow.

This enhancer creates INVISIBLE OCR text layer that Acrobat can use
when manually creating tags. The sandwich renderer places invisible
searchable text behind visible content while preserving accurate page
boundaries and text positioning.
"""

import logging
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional, Tuple, Union

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
    - Sandwich renderer: places text behind content with accurate positioning
    - Intelligent OCR detection (checks if PDF already has text)
    - Explicit DPI handling (default: 300) for proper page boundaries
    - Standard language (eng) with configurable options
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
        """Apply OCR if needed. Returns True on success (see enhance_file_with_status)."""
        success, _ = self.enhance_file_with_status(
            input_path, output_path, force_ocr=force_ocr, **kwargs
        )
        return success

    def enhance_file_with_status(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        force_ocr: bool = False,
        **kwargs
    ) -> Tuple[bool, bool]:
        """
        Apply OCR to PDF file if needed, reporting whether OCR actually ran.

        Returning the status (rather than storing it on self) keeps this safe
        when one enhancer is shared across batch worker threads.

        Args:
            input_path: Path to the input PDF
            output_path: Path where the enhanced PDF should be saved
            force_ocr: Force OCR even if text exists (default: False)
            **kwargs: Additional parameters (ignored for simplicity)

        Returns:
            (success, ocr_performed): ocr_performed is False when the input
            was copied through unchanged (enough text already present).
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)

            if not input_path.exists():
                logger.error(f"Input file not found: {input_path}")
                return False, False

            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if OCR is needed
            if not force_ocr and not self.needs_ocr(input_path):
                logger.info("PDF has sufficient text - skipping OCR, copying to output")
                # Just copy the file if OCR not needed
                import shutil
                shutil.copy2(input_path, output_path)
                return True, False

            # Perform OCR
            logger.info(f"Starting OCR processing: {input_path}")
            return self._apply_ocr(input_path, output_path, force_ocr=force_ocr)

        except Exception as e:
            logger.error(f"Error in OCR enhancement: {e}")
            return False, False

    def _apply_ocr(
        self, input_path: Path, output_path: Path, force_ocr: bool = False
    ) -> Tuple[bool, bool]:
        """
        Apply OCR to PDF using ocrmypdf with proper text positioning.

        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF
            force_ocr: Force OCR even if text exists

        Returns:
            (success, ocr_performed)
        """
        try:
            logger.info(f"Starting OCR processing with ocrmypdf: {input_path}")

            # CRITICAL FIX: Normalize MediaBox to handle non-standard PDFs
            # Some PDFs have MediaBox with negative origins (e.g., [0, -40, 456, 672])
            # This causes OCR text positioning to shift when using force_ocr
            # Solution: Normalize to [0, 0, width, height] before OCR
            original_input = input_path
            temp_normalized = None

            if force_ocr:
                logger.info("Normalizing PDF page boxes before force_ocr to preserve text positioning")
                normalized_path = self._normalize_page_boxes(input_path)
                if normalized_path != input_path:
                    temp_normalized = normalized_path
                input_path = normalized_path

            # For misaligned text: use redo_ocr instead of force_ocr
            # redo_ocr preserves page geometry while regenerating text layer
            use_redo = force_ocr  # User's --force-ocr flag triggers redo_ocr

            options = {
                "language": self.language,
                "redo_ocr": use_redo,           # Preserve geometry while re-OCRing
                "force_ocr": False,             # Don't use force (loses geometry)
                "skip_text": not use_redo,      # Skip if not redoing OCR
                "optimize": 0,                  # No compression (keep quality)
                "output_type": "pdf",           # PDF output
                "pdf_renderer": "sandwich",     # Invisible text behind visible content
                "progress_bar": False,          # Disable progress bar for cleaner logs
                "image_dpi": self.dpi,          # Explicit DPI for proper page dimensions
                "rotate_pages": True,           # Handle rotated pages correctly
                "remove_vectors": False,        # Preserve page geometry and vectors
            }

            # Run ocrmypdf
            ocrmypdf.ocr(
                input_path,
                output_path,
                **options
            )

            # Clean up temporary normalized file
            if temp_normalized:
                import os
                try:
                    os.unlink(temp_normalized)
                    logger.debug(f"Cleaned up temporary normalized file: {temp_normalized}")
                except:
                    pass

            logger.info(f"OCR complete: {output_path}")
            return True, True

        except ocrmypdf.exceptions.PriorOcrFoundError:
            # PDF already has OCR text, just copy it
            logger.info("PDF already has OCR text, copying to output")
            import shutil
            shutil.copy2(input_path, output_path)
            return True, False

        except ocrmypdf.exceptions.EncryptedPdfError:
            logger.error(f"Cannot process encrypted PDF: {input_path}")
            return False, False

        except Exception as e:
            logger.error(f"Error applying OCR: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False, False

    def _normalize_page_boxes(self, input_path: Path) -> Path:
        """
        Normalize PDF page boxes to handle non-standard coordinates.

        Some PDFs have MediaBox with negative origins (e.g., [0, -40, 456, 672])
        which causes OCR text positioning issues. This method normalizes all
        page boxes to start at [0, 0, width, height].

        Args:
            input_path: Path to input PDF

        Returns:
            Path: Path to normalized PDF (temporary file)
        """
        try:
            import pikepdf
            import tempfile

            # Create temporary file for normalized PDF
            temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf', prefix='normalized_')
            import os
            os.close(temp_fd)

            logger.debug(f"Normalizing page boxes: {input_path}")

            with pikepdf.open(input_path) as pdf:
                pages_normalized = 0

                for page_num, page in enumerate(pdf.pages):
                    # Get MediaBox
                    if '/MediaBox' not in page:
                        continue

                    media_box = page.MediaBox
                    x0, y0, x1, y1 = float(media_box[0]), float(media_box[1]), float(media_box[2]), float(media_box[3])

                    # Check if normalization is needed
                    if x0 != 0 or y0 != 0:
                        width = x1 - x0
                        height = y1 - y0

                        logger.debug(f"Page {page_num}: MediaBox [{x0}, {y0}, {x1}, {y1}] → [0, 0, {width}, {height}]")

                        # Step 1: Shift content to match normalized coordinate system
                        # In PDF coordinates (bottom-left origin, Y increases upward):
                        # - Original content at Y position needs to shift by -y0
                        # - This preserves visual position when MediaBox origin changes
                        transformation = f"1 0 0 1 {-x0} {-y0} cm\n".encode('latin-1')

                        if '/Contents' in page:
                            old_contents = page.Contents
                            if isinstance(old_contents, pikepdf.Array):
                                # Multiple streams - prepend to first
                                first_stream = old_contents[0]
                                old_data = first_stream.read_bytes()
                                first_stream.write(transformation + old_data)
                            else:
                                # Single stream
                                old_data = old_contents.read_bytes()
                                old_contents.write(transformation + old_data)

                        # Step 2: Normalize MediaBox
                        page.MediaBox = pikepdf.Array([0, 0, width, height])

                        # Step 3: Normalize other boxes
                        for box_name in ['/CropBox', '/TrimBox', '/BleedBox', '/ArtBox']:
                            if box_name in page:
                                box = page[box_name]
                                bx0, by0, bx1, by1 = float(box[0]), float(box[1]), float(box[2]), float(box[3])
                                page[box_name] = pikepdf.Array([
                                    bx0 - x0,
                                    by0 - y0,
                                    bx1 - x0,
                                    by1 - y0
                                ])

                        pages_normalized += 1

                # Save normalized PDF
                pdf.save(temp_path)

            if pages_normalized > 0:
                logger.info(f"Normalized {pages_normalized} pages with non-standard page boxes")
                return Path(temp_path)
            else:
                # No normalization needed, return original
                os.unlink(temp_path)
                return input_path

        except Exception as e:
            logger.warning(f"Could not normalize page boxes: {e} - using original PDF")
            return input_path

    def get_capabilities(self):
        """Get list of capabilities."""
        return [
            "ocr.ocrmypdf",
            "ocr.sandwich_renderer",
            "ocr.explicit_dpi",
            "ocr.intelligent_detection",
            "ocr.text_analysis",
            "ocr.page_box_normalization",
        ]
