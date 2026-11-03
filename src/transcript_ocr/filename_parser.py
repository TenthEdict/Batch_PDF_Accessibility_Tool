"""Filename parser for TIFF transcript files.

Parses filenames with the convention:
    {collection}_{reference_id}_{page_number}.tif

Example:
    MSP00213_1f4d822f499c9eacb2f15403dd53e468_00001.tif
    ^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^
    collection     reference_id (hash)        page (5-digit)
"""

import re
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Union


@dataclass
class TiffFileInfo:
    """Parsed information from a TIFF filename."""

    collection: str
    reference_id: str
    page_number: int
    original_filename: str

    @property
    def transcript_key(self) -> tuple:
        """Key for grouping pages into transcripts."""
        return (self.collection, self.reference_id)


class FilenameParseError(ValueError):
    """Raised when a filename does not match the expected pattern."""

    pass


# Pattern: {collection}_{reference_id}_{page}.tif(f)
# - collection: alphanumeric (e.g., MSP00213)
# - reference_id: alphanumeric/hex hash (e.g., 1f4d822f499c9eacb2f15403dd53e468)
# - page: 5-digit zero-padded number (e.g., 00001)
FILENAME_PATTERN = re.compile(
    r"^(?P<collection>[A-Za-z0-9]+)_(?P<reference_id>[A-Za-z0-9]+)_(?P<page>\d{5})\.tiff?$",
    re.IGNORECASE,
)


def parse_tiff_filename(filename: Union[str, Path]) -> TiffFileInfo:
    """Parse a TIFF filename into its components.

    Args:
        filename: The filename (not full path) to parse. Can be a string or Path.

    Returns:
        TiffFileInfo with parsed collection, reference_id, page_number, and original filename.

    Raises:
        FilenameParseError: If the filename does not match the expected pattern.

    Examples:
        >>> info = parse_tiff_filename("MSP00213_1f4d822f499c9eacb2f15403dd53e468_00001.tif")
        >>> info.collection
        'MSP00213'
        >>> info.reference_id
        '1f4d822f499c9eacb2f15403dd53e468'
        >>> info.page_number
        1
    """
    if isinstance(filename, Path):
        filename = filename.name

    # Extract just the filename if a path was passed as string. PureWindowsPath
    # splits on both "/" and "\\", so Windows-style paths also work on Linux.
    if "/" in filename or "\\" in filename:
        filename = PureWindowsPath(filename).name

    match = FILENAME_PATTERN.match(filename)
    if not match:
        raise FilenameParseError(
            f"Filename '{filename}' does not match expected pattern: "
            f"{{collection}}_{{reference_id}}_{{page}}.tif(f)"
        )

    return TiffFileInfo(
        collection=match.group("collection"),
        reference_id=match.group("reference_id"),
        page_number=int(match.group("page")),
        original_filename=filename,
    )


def is_valid_tiff_filename(filename: Union[str, Path]) -> bool:
    """Check if a filename matches the expected TIFF naming pattern.

    Args:
        filename: The filename to check.

    Returns:
        True if the filename matches the pattern, False otherwise.
    """
    try:
        parse_tiff_filename(filename)
        return True
    except FilenameParseError:
        return False
