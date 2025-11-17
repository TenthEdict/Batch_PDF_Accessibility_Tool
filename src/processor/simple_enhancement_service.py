#!/usr/bin/env python3
"""
Simplified enhancement service for basic PDF processing.

This service orchestrates a simple two-step pipeline:
1. OCR enhancement (if needed)
2. PDF/UA-1 compliance enhancement

No ML features, no caching, no complex orchestration.
"""

import logging
import tempfile
from pathlib import Path
from typing import Union, Optional

from src.processor.simple_ocr_enhancer import SimpleOCREnhancer
from src.processor.simple_pdfua_enhancer import SimplePDFUAEnhancer

logger = logging.getLogger(__name__)


class SimpleEnhancementService:
    """
    Simple orchestration service for PDF enhancement.

    Pipeline:
    1. OCR Enhancement (if PDF needs OCR)
    2. PDF/UA-1 Enhancement (orphan tags + metadata)

    Features:
    - Sequential processing (no parallelization complexity)
    - Automatic OCR detection
    - Clean temporary file handling
    - Basic error recovery
    """

    def __init__(
        self,
        text_threshold: int = 100,
        dpi: int = 300,
        language: str = 'eng'
    ):
        """
        Initialize the simple enhancement service.

        Args:
            text_threshold: Minimum chars/page to skip OCR (default: 100)
            dpi: DPI for OCR image conversion (default: 300)
            language: OCR language code (default: 'eng')
        """
        self.ocr_enhancer = SimpleOCREnhancer(
            text_threshold=text_threshold,
            dpi=dpi,
            language=language
        )
        self.pdfua_enhancer = SimplePDFUAEnhancer()

        logger.info("SimpleEnhancementService initialized")

    def enhance_document(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        title: Optional[str] = None,
        author: Optional[str] = None,
        language: str = "en-US",
        skip_ocr: bool = False,
        force_ocr: bool = False,
        **kwargs
    ) -> bool:
        """
        Enhance a PDF document through the complete pipeline.

        Args:
            input_path: Path to input PDF
            output_path: Path where enhanced PDF should be saved
            title: Document title (default: extracted from filename)
            author: Document author (default: None)
            language: Document language (default: "en-US")
            skip_ocr: Skip OCR step entirely (default: False)
            force_ocr: Force OCR even if text exists (default: False)
            **kwargs: Additional parameters (ignored)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)

            if not input_path.exists():
                logger.error(f"Input file not found: {input_path}")
                return False

            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"Starting enhancement pipeline for: {input_path}")
            logger.info(f"Output will be saved to: {output_path}")

            # Step 0: Normalize MediaBox to fix coordinate system issues
            # This fixes PDFs with non-standard origins (e.g., MediaBox [0, -40, 456, 672])
            normalized_input = self.ocr_enhancer._normalize_page_boxes(input_path)
            temp_normalized = normalized_input if normalized_input != input_path else None

            # Step 1: OCR Enhancement (if needed)
            if skip_ocr:
                logger.info("Skipping OCR step (skip_ocr=True)")
                ocr_output = normalized_input
            else:
                # Use temporary file for OCR output
                with tempfile.NamedTemporaryFile(
                    suffix='.pdf',
                    delete=False,
                    dir=output_path.parent
                ) as tmp_file:
                    ocr_output = Path(tmp_file.name)

                logger.info("Step 1/2: OCR Enhancement")
                ocr_success = self.ocr_enhancer.enhance_file(
                    normalized_input,
                    ocr_output,
                    force_ocr=force_ocr
                )

                if not ocr_success:
                    logger.error("OCR enhancement failed")
                    # Clean up temp files
                    if ocr_output.exists():
                        ocr_output.unlink()
                    if temp_normalized and Path(temp_normalized).exists():
                        Path(temp_normalized).unlink()
                    return False

            # Step 2: PDF/UA Enhancement
            logger.info("Step 2/2: PDF/UA-1 Enhancement")
            # Pass ocr_performed flag to help PDF/UA enhancer make smart decisions
            ocr_performed = not skip_ocr
            pdfua_success = self.pdfua_enhancer.enhance_file(
                ocr_output,
                output_path,
                title=title,
                author=author,
                language=language,
                ocr_performed=ocr_performed
            )

            # Clean up temporary OCR file if it was created
            if not skip_ocr and ocr_output != normalized_input:
                if ocr_output.exists():
                    ocr_output.unlink()
                    logger.debug(f"Cleaned up temporary OCR file: {ocr_output}")

            # Clean up normalized file if it was created
            if temp_normalized and Path(temp_normalized).exists():
                Path(temp_normalized).unlink()
                logger.debug(f"Cleaned up normalized file: {temp_normalized}")

            if not pdfua_success:
                logger.error("PDF/UA enhancement failed")
                return False

            logger.info(f"Enhancement complete: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error in enhancement pipeline: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_document(self, *args, **kwargs) -> bool:
        """
        Alias for enhance_document for compatibility.

        Returns:
            bool: True if successful
        """
        return self.enhance_document(*args, **kwargs)
