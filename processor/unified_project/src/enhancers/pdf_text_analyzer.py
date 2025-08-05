#!/usr/bin/env python3
"""
PDF text content analyzer for intelligent OCR detection.
"""

import logging
import fitz  # PyMuPDF
from pathlib import Path
from typing import Union, Dict, Any

logger = logging.getLogger(__name__)


class PDFTextAnalyzer:
    """
    Analyzer for determining if a PDF needs OCR based on existing text content.
    """

    def __init__(self, text_threshold: int = 100, sample_pages: int = 3):
        """
        Initialize the PDF text analyzer.

        Args:
            text_threshold: Minimum average characters per page to skip OCR
            sample_pages: Number of pages to analyze for text content
        """
        self.text_threshold = text_threshold
        self.sample_pages = sample_pages

    def analyze_text_content(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Analyze PDF text content to determine if OCR is needed.

        Args:
            pdf_path: Path to the PDF file to analyze

        Returns:
            Dict containing analysis results:
            - needs_ocr: bool indicating if OCR is needed
            - total_chars: total characters found in sampled pages
            - avg_chars_per_page: average characters per page
            - pages_analyzed: number of pages analyzed
            - total_pages: total pages in document
            - analysis_ratio: ratio of pages analyzed to total pages
        """
        try:
            logger.info(f"Analyzing text content in PDF: {pdf_path}")
            
            # Open PDF for read-only analysis
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            if total_pages == 0:
                logger.warning(f"PDF has no pages: {pdf_path}")
                doc.close()
                return self._create_analysis_result(True, 0, 0, 0, total_pages, "No pages found")

            # Determine how many pages to analyze
            pages_to_analyze = min(self.sample_pages, total_pages)
            total_chars = 0

            # Analyze text content in sample pages
            for page_num in range(pages_to_analyze):
                try:
                    page = doc[page_num]
                    text = page.get_text().strip()
                    page_chars = len(text)
                    total_chars += page_chars
                    
                    logger.debug(f"Page {page_num + 1}: {page_chars} characters")
                    
                except Exception as e:
                    logger.warning(f"Error reading page {page_num + 1}: {e}")
                    continue

            doc.close()

            # Calculate average characters per page
            avg_chars_per_page = total_chars / pages_to_analyze if pages_to_analyze > 0 else 0
            analysis_ratio = pages_to_analyze / total_pages

            # Determine if OCR is needed
            needs_ocr = avg_chars_per_page < self.text_threshold

            logger.info(f"Text analysis complete: {avg_chars_per_page:.1f} avg chars/page, "
                       f"OCR needed: {needs_ocr}")

            return self._create_analysis_result(
                needs_ocr=needs_ocr,
                total_chars=total_chars,
                avg_chars_per_page=avg_chars_per_page,
                pages_analyzed=pages_to_analyze,
                total_pages=total_pages,
                reason=f"Average {avg_chars_per_page:.1f} chars/page vs threshold {self.text_threshold}"
            )

        except Exception as e:
            logger.error(f"Error analyzing PDF text content: {e}")
            # Default to needing OCR if analysis fails
            return self._create_analysis_result(True, 0, 0, 0, 0, f"Analysis error: {e}")

    def _create_analysis_result(self, needs_ocr: bool, total_chars: int, 
                               avg_chars_per_page: float, pages_analyzed: int, 
                               total_pages: int, reason: str) -> Dict[str, Any]:
        """Create standardized analysis result dictionary."""
        return {
            "needs_ocr": needs_ocr,
            "total_chars": total_chars,
            "avg_chars_per_page": avg_chars_per_page,
            "pages_analyzed": pages_analyzed,
            "total_pages": total_pages,
            "analysis_ratio": pages_analyzed / total_pages if total_pages > 0 else 0,
            "text_threshold": self.text_threshold,
            "reason": reason
        }

    def quick_text_check(self, pdf_path: Union[str, Path]) -> bool:
        """
        Quick check to determine if PDF needs OCR.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            bool: True if OCR is needed, False if PDF has sufficient text
        """
        analysis = self.analyze_text_content(pdf_path)
        return analysis["needs_ocr"]

    def configure_thresholds(self, text_threshold: int = None, sample_pages: int = None):
        """
        Update analyzer configuration.

        Args:
            text_threshold: New minimum characters per page threshold
            sample_pages: New number of pages to sample
        """
        if text_threshold is not None:
            self.text_threshold = text_threshold
            logger.info(f"Updated text threshold to {text_threshold} chars/page")
        
        if sample_pages is not None:
            self.sample_pages = sample_pages
            logger.info(f"Updated sample pages to {sample_pages}")
