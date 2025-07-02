"""
Academic paper structure analyzer.

This module analyzes the structure of academic papers and detects
sections, headings, figures, tables, and other elements.
"""

import logging
from typing import Dict, List, Any, Optional
import re


class AcademicStructureAnalyzer:
    """
    Analyzes the structure of academic papers for better accessibility tagging.

    Specialized for modern academic papers with flexible structure detection
    that doesn't rely on specific heading names.
    """

    def __init__(self):
        """Initialize the academic structure analyzer."""
        self.logger = logging.getLogger(__name__)

    def detect_sections(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect standard academic paper sections.

        Uses a flexible approach that looks for common section patterns
        but doesn't rely on specific names, allowing for variations
        across different academic disciplines and journals.

        Args:
            text: Full text of the academic paper

        Returns:
            Dictionary with sections, headings, and other structural elements
        """
        result = {"sections": [], "headings": [], "paragraphs": []}

        # Split text into lines for analysis
        lines = text.split("\n")
        current_section = None

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Detect if this line is likely a heading
            if self._is_likely_heading(line, lines, i):
                heading = {
                    "text": line,
                    "level": self._estimate_heading_level(line, lines, i),
                    "line_index": i,
                }
                result["headings"].append(heading)

                # Classify section type if possible
                section_type = self._classify_section_type(line)
                if section_type:
                    # Close previous section if exists
                    if current_section and "end_line" not in current_section:
                        current_section["end_line"] = i - 1

                    # Create new section
                    current_section = {
                        "type": section_type,
                        "heading": line,
                        "start_line": i,
                    }
                    result["sections"].append(current_section)

            # Detect paragraphs
            elif self._is_paragraph_start(line, lines, i):
                paragraph = {"start_line": i, "text": line}

                # Find paragraph end
                end_idx = i
                while (
                    end_idx + 1 < len(lines)
                    and lines[end_idx + 1].strip()
                    and not self._is_likely_heading(
                        lines[end_idx + 1], lines, end_idx + 1
                    )
                ):
                    paragraph["text"] += " " + lines[end_idx + 1].strip()
                    end_idx += 1

                paragraph["end_line"] = end_idx
                result["paragraphs"].append(paragraph)

        # Close the final section
        if current_section and "end_line" not in current_section:
            current_section["end_line"] = len(lines) - 1

        return result

    def detect_citations(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect citations in various formats (APA, MLA, Chicago, etc.).

        Identifies common citation patterns in academic papers:
        - Author-year: (Smith, 2020)
        - Numeric: [1] or [1-3]
        - Superscript: ¹²³

        Args:
            text: Text to analyze for citations

        Returns:
            List of citation locations and text
        """
        citations = []

        # Common citation patterns
        citation_patterns = [
            (
                r"\((?:[A-Za-z\-]+(?:\s+and\s+|\s*,\s*)){0,2}[A-Za-z\-]+(?:,?\s+et\s+al\.?)?,\s+\d{4}(?:[a-z])?(?:;\s+(?:[^)]+))?\)",
                "author_year",
            ),  # (Smith, 2020) or (Smith and Jones, 2020)
            (
                r"\[(\d+(?:[-–]\d+)?(?:,\s*\d+)*)\]",
                "numeric",
            ),  # [1] or [1-3] or [1,2,3]
            (
                r"\((\d+(?:[-–]\d+)?(?:,\s*\d+)*)\)",
                "numeric_paren",
            ),  # (1) or (1-3) or (1,2,3)
            (
                r"(?<!\w)(?:\d+,){2,}\d+(?!\w)",
                "superscript",
            ),  # 1,2,3 (without parentheses, potential superscript)
        ]

        # Check text for citation patterns
        lines = text.split("\n")
        for i, line in enumerate(lines):
            for pattern, citation_type in citation_patterns:
                for match in re.finditer(pattern, line):
                    citation = {
                        "text": match.group(0),
                        "type": citation_type,
                        "line_index": i,
                        "char_start": match.start(),
                        "char_end": match.end(),
                    }
                    citations.append(citation)

        return citations

    def detect_figures_and_tables(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect figures and tables with captions.

        Identifies figure and table references in academic text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with lists of figures and tables
        """
        result = {"figures": [], "tables": []}

        # Figure and table caption patterns
        figure_patterns = [
            r"(?i)(?:^|\n|\s)(fig(?:ure)?\.?\s*\d+[a-z]?)",  # Fig. 1, Figure 2a
            r"(?i)(?:^|\n|\s)(figure\s*\d+[a-z]?:)",  # Figure 1:
        ]

        table_patterns = [
            r"(?i)(?:^|\n|\s)(table\s*\d+[a-z]?)",  # Table 1, Table 2a
            r"(?i)(?:^|\n|\s)(table\s*\d+[a-z]?:)",  # Table 1:
        ]

        # Check for figure captions
        lines = text.split("\n")
        for i, line in enumerate(lines):
            # Check for figures
            for pattern in figure_patterns:
                for match in re.finditer(pattern, line):
                    caption_text = self._extract_caption(lines, i, match.end())
                    figure = {
                        "ref": match.group(1),
                        "line_index": i,
                        "caption": caption_text,
                    }
                    result["figures"].append(figure)

            # Check for tables
            for pattern in table_patterns:
                for match in re.finditer(pattern, line):
                    caption_text = self._extract_caption(lines, i, match.end())
                    table = {
                        "ref": match.group(1),
                        "line_index": i,
                        "caption": caption_text,
                    }
                    result["tables"].append(table)

        return result

    def _extract_caption(self, lines: List[str], line_idx: int, start_pos: int) -> str:
        """Extract the caption text from a figure or table reference."""
        # Start with the remainder of the current line
        caption = lines[line_idx][start_pos:].strip()

        # If caption continues to next line, include it
        next_idx = line_idx + 1
        while (
            next_idx < len(lines)
            and lines[next_idx].strip()
            and not self._is_likely_heading(lines[next_idx], lines, next_idx)
        ):
            # Stop if we encounter another figure or table reference
            if re.search(r"(?i)fig(?:ure)?\.?\s*\d+|table\s*\d+", lines[next_idx]):
                break
            caption += " " + lines[next_idx].strip()
            next_idx += 1

            # Don't extract too many lines (captions are usually short)
            if next_idx - line_idx > 2:
                break

        return caption

    def _is_likely_heading(self, line: str, lines: List[str], index: int) -> bool:
        """
        Determine if a line is likely a heading based on multiple signals.

        Uses characteristics beyond just text content to identify headings:
        - Line formatting (all caps, title case)
        - Surrounding whitespace
        - Numbering patterns
        - Length compared to other lines

        Args:
            line: Current line text
            lines: All lines in the document
            index: Current line index

        Returns:
            Boolean indicating if the line is likely a heading
        """
        # Skip empty lines
        if not line.strip():
            return False

        # Common academic numbering patterns
        heading_patterns = [
            r"^\d+\.\s+\w+",  # "1. Introduction"
            r"^\d+\.\d+\.\s+\w+",  # "1.1. Methods"
            r"^[A-Z][a-z]+\s+\d+\.\s+\w+",  # "Section 1. Introduction"
            r"^[IVXLCDM]+\.\s+\w+",  # "IV. Results"
            r"^[A-Z]\.(?:\s+|\s*-)\w+",  # "A. Methods" or "A-Methods"
        ]

        # Check against patterns
        for pattern in heading_patterns:
            if re.match(pattern, line):
                return True

        # Surrounding whitespace indicates heading
        whitespace_surrounded = (index == 0 or not lines[index - 1].strip()) and (
            index == len(lines) - 1 or not lines[index + 1].strip()
        )

        # Short line length compared to document average
        non_empty_lines = [l for l in lines if l.strip()]
        if non_empty_lines:
            avg_line_length = sum(len(l) for l in non_empty_lines) / len(
                non_empty_lines
            )
            is_short_line = len(line) < avg_line_length * 0.7
        else:
            is_short_line = False

        # All caps or title case are often headings
        is_all_caps = line.isupper()
        is_title_case = line.istitle() or (
            line.split()[0].istitle() if line.split() else False
        )

        # Check if the line is likely a heading based on combined signals
        heading_score = sum(
            [
                whitespace_surrounded,
                is_short_line,
                is_all_caps or is_title_case,
                bool(
                    re.match(r"^[A-Za-z\s\d\.\-]+$", line)
                ),  # Headings rarely contain special chars
            ]
        )

        return heading_score >= 2

    def _estimate_heading_level(self, line: str, lines: List[str], index: int) -> int:
        """
        Estimate the heading level based on text characteristics.

        Uses common academic numbering patterns and formatting to estimate
        the heading level/hierarchy.

        Args:
            line: Current line text
            lines: All lines in the document
            index: Current line index

        Returns:
            Estimated heading level (1-6)
        """
        # Level 1 patterns (main headings)
        if (
            line.isupper()
            or re.match(r"^\d+\.\s+[A-Z]", line)
            or re.match(r"^[IVXLCDM]+\.\s+", line)
        ):
            return 1

        # Level 2 patterns (sub-headings)
        if re.match(r"^\d+\.\d+\.\s+", line) or re.match(r"^[A-Z]\.(?:\s+|\s*-)", line):
            return 2

        # Level 3 patterns (sub-sub-headings)
        if re.match(r"^\d+\.\d+\.\d+\.\s+", line):
            return 3

        # Default to level 2 if uncertain
        return 2

    def _classify_section_type(self, heading: str) -> Optional[str]:
        """
        Classify section type based on heading text.

        Uses fuzzy matching to identify common academic paper sections
        regardless of exact wording.

        Args:
            heading: Heading text

        Returns:
            Section type or None if unrecognized
        """
        heading_lower = heading.lower()

        # Remove numbering and common prefixes for better matching
        clean_heading = re.sub(r"^[\d\.IVXLCDM]+\s+", "", heading_lower)
        clean_heading = re.sub(r"^section\s+[\d\.]+\s+", "", clean_heading)

        # Common section patterns with flexible matching
        section_patterns = {
            "abstract": [r"abstract", r"summary"],
            "introduction": [r"introduction", r"background", r"overview"],
            "literature_review": [
                r"literature",
                r"related work",
                r"state of the art",
                r"previous research",
            ],
            "methods": [
                r"method",
                r"methodology",
                r"materials",
                r"experimental",
                r"procedure",
                r"design",
            ],
            "results": [r"result", r"findings", r"observation"],
            "discussion": [r"discussion", r"interpretation", r"implications"],
            "conclusion": [r"conclusion", r"concluding", r"summary", r"final remarks"],
            "references": [
                r"reference",
                r"bibliography",
                r"works cited",
                r"literature cited",
            ],
            "acknowledgments": [r"acknowledgment", r"acknowledgement"],
            "appendix": [r"appendix", r"supplementary", r"supporting information"],
        }

        # Check each section type's patterns
        for section_type, patterns in section_patterns.items():
            for pattern in patterns:
                if re.search(pattern, clean_heading):
                    return section_type

        return None

    def _is_paragraph_start(self, line: str, lines: List[str], index: int) -> bool:
        """
        Determine if a line is the start of a paragraph.

        Args:
            line: Current line text
            lines: All lines in the document
            index: Current line index

        Returns:
            Boolean indicating if the line starts a paragraph
        """
        # Skip empty lines
        if not line.strip():
            return False

        # Skip lines that are likely headings
        if self._is_likely_heading(line, lines, index):
            return False

        # Check if previous line is empty (paragraph break)
        if index > 0 and not lines[index - 1].strip():
            return True

        # First line in document
        if index == 0:
            return True

        # Indentation often indicates paragraph start
        if line.startswith("    ") and not lines[index - 1].startswith("    "):
            return True

        return False
