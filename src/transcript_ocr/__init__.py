"""TIFF Transcript OCR Module.

OCRs single-page TIFF files and combines them into structured transcript
TXT files, grouped by collection and reference ID extracted from filenames.
"""

from .filename_parser import TiffFileInfo, parse_tiff_filename
from .tiff_ocr_processor import TiffOCRProcessor
from .transcript_assembler import TranscriptAssembler
from .batch_processor import TranscriptBatchProcessor

__all__ = [
    "TiffFileInfo",
    "parse_tiff_filename",
    "TiffOCRProcessor",
    "TranscriptAssembler",
    "TranscriptBatchProcessor",
]
