"""TIFF OCR processor using pytesseract.

Handles OCR extraction from single-page TIFF files.
"""

import logging
import warnings
from pathlib import Path
from typing import Optional, Union

import pytesseract
from PIL import Image

# Suppress noisy PIL warnings about TIFF metadata tags (e.g., IPTC tag 33723)
warnings.filterwarnings("ignore", message="Metadata Warning, tag .* had too many entries")

logger = logging.getLogger(__name__)


class OCRError(Exception):
    """Raised when OCR processing fails."""

    pass


class TiffOCRProcessor:
    """Processes TIFF files to extract text via OCR."""

    def __init__(
        self,
        language: str = "eng",
        dpi: int = 300,
        psm: int = 3,
        oem: int = 3,
    ):
        """Initialize the OCR processor.

        Args:
            language: Tesseract language code (default: 'eng').
            dpi: DPI hint for Tesseract (default: 300).
            psm: Page segmentation mode (default: 3 = fully automatic).
            oem: OCR Engine mode (default: 3 = default based on available).
        """
        self.language = language
        self.dpi = dpi
        self.psm = psm
        self.oem = oem

    def process_tiff(self, tiff_path: Union[str, Path]) -> str:
        """Extract text from a TIFF file using OCR.

        Args:
            tiff_path: Path to the TIFF file.

        Returns:
            Extracted text as a string.

        Raises:
            OCRError: If the file cannot be read or OCR fails.
        """
        tiff_path = Path(tiff_path)

        if not tiff_path.exists():
            raise OCRError(f"TIFF file not found: {tiff_path}")

        try:
            image = Image.open(tiff_path)
        except Exception as e:
            raise OCRError(f"Failed to open TIFF file {tiff_path}: {e}")

        try:
            # Build Tesseract config string
            config = f"--psm {self.psm} --oem {self.oem} --dpi {self.dpi}"

            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=config,
            )

            return text.strip()

        except pytesseract.TesseractError as e:
            raise OCRError(f"Tesseract OCR failed for {tiff_path}: {e}")
        except Exception as e:
            raise OCRError(f"Unexpected error during OCR of {tiff_path}: {e}")
        finally:
            image.close()

    def process_tiff_safe(
        self, tiff_path: Union[str, Path]
    ) -> tuple[Optional[str], Optional[str]]:
        """Extract text from a TIFF file, returning None on error.

        Args:
            tiff_path: Path to the TIFF file.

        Returns:
            Tuple of (text, error_message). One will always be None.
        """
        try:
            text = self.process_tiff(tiff_path)
            return text, None
        except OCRError as e:
            logger.error(str(e))
            return None, str(e)
