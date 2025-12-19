"""Transcript assembler for combining OCR'd pages.

Combines multiple pages of OCR'd text into a single structured transcript file.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class PageData:
    """Data for a single page in a transcript."""

    page_number: int
    filename: str
    text: str
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Whether OCR succeeded for this page."""
        return self.error is None


class TranscriptAssembler:
    """Assembles multiple pages into a structured transcript."""

    SEPARATOR = "=" * 80
    PAGE_SEPARATOR = "-" * 3

    def assemble(
        self,
        collection: str,
        reference_id: str,
        pages: List[PageData],
    ) -> str:
        """Assemble pages into a structured transcript.

        Args:
            collection: Collection identifier (e.g., 'MSP00213').
            reference_id: Reference ID within the collection.
            pages: List of PageData objects, will be sorted by page_number.

        Returns:
            Formatted transcript string.
        """
        # Sort pages by page number
        sorted_pages = sorted(pages, key=lambda p: p.page_number)
        total_pages = len(sorted_pages)
        successful_pages = sum(1 for p in sorted_pages if p.success)
        timestamp = datetime.now().isoformat(timespec="seconds")

        lines = []

        # Header
        lines.append(self.SEPARATOR)
        lines.append("TRANSCRIPT")
        lines.append(f"Collection:    {collection}")
        lines.append(f"Reference ID:  {reference_id}")
        lines.append(f"Generated:     {timestamp}")
        lines.append(f"Total Pages:   {total_pages}")
        if successful_pages < total_pages:
            lines.append(f"OCR Errors:    {total_pages - successful_pages}")
        lines.append(self.SEPARATOR)
        lines.append("")

        # Pages
        for page in sorted_pages:
            page_header = (
                f"{self.PAGE_SEPARATOR} Page {page.page_number} of {total_pages}: "
                f"{page.filename} {self.PAGE_SEPARATOR}"
            )
            lines.append(page_header)
            lines.append("")

            if page.success:
                lines.append(page.text)
            else:
                lines.append(f"[OCR ERROR: {page.error}]")

            lines.append("")

        # Footer
        lines.append(self.SEPARATOR)
        lines.append("END OF TRANSCRIPT")
        lines.append(self.SEPARATOR)

        return "\n".join(lines)
