"""TIFF Transcript OCR Module.

OCRs single-page TIFF files and outputs individual TXT files per page,
organized into folders by collection and reference ID extracted from filenames.
"""

from .filename_parser import TiffFileInfo, parse_tiff_filename
from .tiff_ocr_processor import TiffOCRProcessor
from .batch_processor import TranscriptBatchProcessor

__all__ = [
    "TiffFileInfo",
    "parse_tiff_filename",
    "TiffOCRProcessor",
    "TranscriptBatchProcessor",
]
