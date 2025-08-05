#!/usr/bin/env python3
"""
PDF accessibility enhancer module.

This module provides PDF-specific implementation of the Enhancer interface
for adding accessibility features to PDF documents.
"""

import logging
import io
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import pikepdf
    from pikepdf import Pdf, Name, String, Dictionary, Array
except ImportError:
    raise ImportError(
        "pikepdf is required for PDF enhancement. "
        "Install it with: pip install pikepdf"
    )

from .enhancer_base import EnhancerBase

logger = logging.getLogger(__name__)


class PDFEnhancer(EnhancerBase):
    """
    PDF-specific implementation of the Enhancer interface.

    This class provides common functionality for enhancing PDF documents
    and serves as a base class for more specialized PDF enhancers.
    """

    def __init__(self, environment: Optional[str] = None):
        """
        Initialize the PDF enhancer.

        Args:
            environment: Optional environment name for configuration
        """
        super().__init__("pdf_enhancer", environment)

    def _load_document(self, input_path: Path) -> pikepdf.Pdf:
        """
        Load a PDF document from a file.

        Args:
            input_path: Path to the input PDF document

        Returns:
            pikepdf.Pdf: The loaded PDF document
        """
        return pikepdf.open(input_path)

    def _save_document(self, document: pikepdf.Pdf, output_path: Path) -> None:
        """
        Save a PDF document to a file.

        Args:
            document: The PDF document to save
            output_path: Path where the document should be saved
        """
        document.save(output_path)

    def enhance_file(
        self, input_path: Union[str, Path], output_path: Union[str, Path], **kwargs
    ) -> bool:
        """
        Enhance a PDF file with accessibility features.

        This implementation adds filename extraction for title generation.

        Args:
            input_path: Path to the input PDF document
            output_path: Path where the enhanced document should be saved
            **kwargs: Additional enhancer-specific parameters

        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        # Add filename to kwargs for title extraction
        input_path = Path(input_path)
        kwargs["filename"] = input_path.name

        try:
            document = self._load_document(input_path)
            document = self.enhance(document, **kwargs)

            # Create output directory if needed
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            self._save_document(document, output_path)
            return True
        except Exception as e:
            logger.error(f"Error enhancing PDF file: {e}")
            return False

    def enhance(self, document: pikepdf.Pdf, **kwargs) -> pikepdf.Pdf:
        """
        Enhance a PDF document with accessibility features.

        This implementation applies common PDF accessibility enhancements
        that are applicable to all PDF documents.

        Args:
            document: The PDF document to enhance
            **kwargs: Additional enhancer-specific parameters
                - title: Document title (default: None)
                - author: Document author (default: None)
                - language: Document language (default: 'en-US')
                - display_doc_title: Whether to display the document title
                  in the viewer (default: True)
                - extract_title_from_h1: Whether to extract title from H1 tag (default: True)
                - extract_title_from_filename: Whether to extract title from filename (default: False)
                - filename: Original filename (for title extraction)

        Returns:
            pikepdf.Pdf: The enhanced PDF document
        """
        # Extract parameters
        title = kwargs.get("title")
        author = kwargs.get("author")
        language = kwargs.get("language", "en-US")
        display_doc_title = kwargs.get("display_doc_title", True)
        extract_title_from_h1 = kwargs.get("extract_title_from_h1", True)
        extract_title_from_filename = kwargs.get("extract_title_from_filename", False)

        # Try to extract title using advanced spatial filtering algorithm
        if not title:
            # Prepare path for advanced extraction
            source_path = kwargs.get("source_path") or kwargs.get("input_path") or kwargs.get("filename")
            
            if source_path:
                # Try advanced content-based extraction first
                advanced_title = self._extract_document_title_advanced(document, Path(source_path))
                if advanced_title:
                    title = advanced_title
                    logger.info(f"Extracted title using advanced algorithm: {title}")
                elif extract_title_from_h1:
                    # Fallback to H1 extraction
                    title_from_h1 = self.extract_title_from_h1_tag(document)
                    if title_from_h1:
                        title = title_from_h1
                        logger.info(f"Extracted title from H1 tag: {title}")
                    elif extract_title_from_filename and kwargs.get("filename"):
                        # Final fallback to filename
                        filename = Path(kwargs["filename"]).stem
                        title = filename.replace("_", " ").title()
                        logger.info(f"Extracted title from filename: {title}")
                elif extract_title_from_filename and kwargs.get("filename"):
                    # Direct filename extraction if H1 disabled
                    filename = Path(kwargs["filename"]).stem
                    title = filename.replace("_", " ").title()
                    logger.info(f"Extracted title from filename: {title}")
            elif extract_title_from_h1:
                # No source path, try H1 extraction
                title_from_h1 = self.extract_title_from_h1_tag(document)
                if title_from_h1:
                    title = title_from_h1
                    logger.info(f"Extracted title from H1 tag: {title}")
                elif extract_title_from_filename and kwargs.get("filename"):
                    # Fallback to filename
                    filename = Path(kwargs["filename"]).stem
                    title = filename.replace("_", " ").title()
                    logger.info(f"Extracted title from filename: {title}")
            elif extract_title_from_filename and kwargs.get("filename"):
                # Only filename extraction
                filename = Path(kwargs["filename"]).stem
                title = filename.replace("_", " ").title()
                logger.info(f"Extracted title from filename: {title}")

        # Update document metadata
        with document.open_metadata(set_pikepdf_as_editor=False) as meta:
            if title:
                meta["dc:title"] = title

            if author:
                meta["dc:creator"] = author

            # Set document language
            meta["dc:language"] = language

        # Set viewer preferences to display document title
        if display_doc_title:
            if Name.ViewerPreferences not in document.Root:
                document.Root.ViewerPreferences = Dictionary()

            document.Root.ViewerPreferences[Name.DisplayDocTitle] = True

        # Log applied enhancements
        enhancements = ["Updated document metadata"]
        if title:
            enhancements.append(f"Added title: {title}")
        if author:
            enhancements.append(f"Added author: {author}")
        enhancements.append(f"Set language to {language}")
        if display_doc_title:
            enhancements.append("Set display document title preference")

        # Add PDF/UA identifier
        self._add_pdfua_identifier(document)
        enhancements.append("Added PDF/UA-1 identifier")

        logger.info("Applied enhancements:")
        for enhancement in enhancements:
            logger.info(f"- {enhancement}")

        return document

    def _add_pdfua_identifier(self, document: pikepdf.Pdf):
        """
        Add PDF/UA-1 identifier to the document.
        """
        # Ensure the document is marked as tagged
        if Name.MarkInfo not in document.Root:
            document.Root.MarkInfo = Dictionary()
        document.Root.MarkInfo[Name.Marked] = True

        # Create PDF/UA-1 output intent
        output_intent = Dictionary(
            S=Name.GTS_PDFUA1,
            OutputConditionIdentifier=String("PDF/UA-1"),
            Info=String("PDF for Universal Accessibility"),
        )

        if Name.OutputIntents not in document.Root:
            document.Root.OutputIntents = Array()

        # Avoid adding duplicate identifiers
        found = False
        for intent in document.Root.OutputIntents:
            if intent.get(Name.S) == Name.GTS_PDFUA1:
                found = True
                break
        
        if not found:
            document.Root.OutputIntents.append(output_intent)
            logger.info("Added PDF/UA-1 identifier.")

    def extract_title_from_h1_tag(self, document: pikepdf.Pdf) -> Optional[str]:
        """
        Extract the document title from the first H1 tag in the document.

        This method analyzes the document structure to find the first heading (H1)
        and uses its text as the document title.

        Args:
            document: The PDF document to analyze

        Returns:
            str or None: The extracted title or None if no H1 tag is found
        """
        try:
            # Import needed modules
            try:
                import fitz  # PyMuPDF
            except ImportError:
                logger.warning(
                    "PyMuPDF (fitz) is required for H1 extraction. Falling back to filename."
                )
                return None

            # Extract first page for title analysis
            if len(document.pages) == 0:
                return None

            # Save document to a temporary buffer
            buffer = io.BytesIO()
            document.save(buffer)
            buffer.seek(0)

            # Open with PyMuPDF for text extraction and analysis
            with fitz.open(stream=buffer, filetype="pdf") as doc:
                if not doc.page_count:
                    return None

                # Get the first page
                page = doc[0]
                page_height = page.rect.height

                # Define spatial exclusion zones to avoid journal headers
                header_zone_limit = page_height * 0.15  # Top 15%
                footer_zone_limit = page_height * 0.85  # Bottom 15%

                # Extract text blocks with their attributes
                blocks = page.get_text("dict")["blocks"]

                # Find potential headings based on font size and position
                headings = []
                max_font_size = 0

                # First pass: determine the maximum font size used in the document
                for block in blocks:
                    if block.get("type") == 0:  # Text block
                        # Check if block is in valid zone (not header/footer)
                        block_y = block.get("bbox", [0, 0, 0, 0])[1]
                        if header_zone_limit <= block_y <= footer_zone_limit:
                            for line in block.get("lines", []):
                                for span in line.get("spans", []):
                                    max_font_size = max(max_font_size, span.get("size", 0))

                # Second pass: identify the actual headings
                # Typically, headings use larger fonts and are positioned near the top
                threshold_size = (
                    max_font_size * 0.85
                )  # Headings are usually at least 85% of the max font size

                # Sort blocks by vertical position (top to bottom)
                blocks_by_position = sorted(
                    blocks, key=lambda b: b.get("bbox", [0, 0, 0, 0])[1]
                )

                # First: Collect all potential heading spans
                potential_heading_spans = []

                for block in blocks_by_position:
                    if block.get("type") == 0:  # Text block
                        # Apply spatial filtering - skip header and footer zones
                        block_y = block.get("bbox", [0, 0, 0, 0])[1]
                        if not (header_zone_limit <= block_y <= footer_zone_limit):
                            continue
                            
                        for line in block.get("lines", []):
                            line_spans = []
                            line_y = line.get("bbox", [0, 0, 0, 0])[
                                1
                            ]  # y-position (top)

                            for span in line.get("spans", []):
                                size = span.get("size", 0)
                                text = span.get("text", "").strip()

                                # Check if this is likely a heading span
                                if (
                                    size >= threshold_size
                                    and text
                                    and len(text) > 3
                                    and not text.endswith(".")
                                ):  # Headings rarely end with periods
                                    line_spans.append(
                                        {
                                            "text": text,
                                            "size": size,
                                            "y": line_y,
                                            "x": span.get("bbox", [0, 0, 0, 0])[
                                                0
                                            ],  # x-position (left)
                                        }
                                    )

                            # Add all spans from this line
                            if line_spans:
                                potential_heading_spans.append(line_spans)

                # Second: Reconstruct full headings from spans
                line_headings = []
                for line_spans in potential_heading_spans:
                    if not line_spans:
                        continue

                    # Sort spans within line by x-position
                    sorted_spans = sorted(line_spans, key=lambda s: s.get("x", 0))

                    # Combine all spans in the line to form a complete heading
                    combined_text = " ".join([s.get("text", "") for s in sorted_spans])

                    # Use size and y-position from the first span
                    line_headings.append(
                        {
                            "text": combined_text,
                            "size": sorted_spans[0].get("size", 0),
                            "y": sorted_spans[0].get("y", 0),
                        }
                    )

                # Third: Handle multi-line titles by combining consecutive headings with similar font size
                # Sort headings by vertical position
                line_headings.sort(key=lambda h: h.get("y", 0))

                # Merge consecutive headings that are likely part of the same title
                i = 0
                while i < len(line_headings):
                    current = line_headings[i]
                    title_parts = [current["text"]]

                    # Look ahead for consecutive headings that could be part of the same title
                    j = i + 1
                    while j < len(line_headings):
                        next_heading = line_headings[j]

                        # Check if the next heading is close in vertical position and similar in font size
                        y_diff = next_heading["y"] - current["y"]
                        size_ratio = min(current["size"], next_heading["size"]) / max(
                            current["size"], next_heading["size"]
                        )

                        # Conditions for merging: close vertically (less than 3x line height) and similar font size (within 15%)
                        if y_diff < current["size"] * 3 and size_ratio > 0.85:
                            title_parts.append(next_heading["text"])
                            j += 1
                        else:
                            break

                    # Create the multi-line title
                    if len(title_parts) > 1:
                        headings.append(
                            {
                                "text": " ".join(title_parts),
                                "size": current["size"],
                                "y": current["y"],
                            }
                        )
                        i = j  # Skip all the merged headings
                    else:
                        headings.append(current)
                        i += 1

                # Get the first heading that's not special text like "Abstract" or "Introduction"
                # Also filter out journal patterns
                import re
                non_heading_terms = [
                    "abstract",
                    "introduction", 
                    "summary",
                    "contents",
                    "table of contents",
                ]
                
                journal_patterns = [
                    r'\bjournal\s+of\b',
                    r'\bproceedings\s+of\b',
                    r'\btransactions\s+on\b',
                    r'\bieee\s+',
                    r'\bacm\s+',
                    r'\breview\s+of\b',
                    r'\bvol\.?\s*\d+',
                ]
                
                journal_regex = re.compile('|'.join(journal_patterns), re.IGNORECASE)

                for heading in headings:
                    text = heading["text"].lower()
                    # Skip if contains non-heading terms or journal patterns
                    if (all(term not in text for term in non_heading_terms) and
                        not journal_regex.search(heading["text"])):
                        return heading["text"].strip()

                # If no suitable heading found, return the first heading as fallback
                if headings:
                    return headings[0]["text"].strip()

            return None

        except Exception as e:
            logger.warning(f"Error extracting title from H1 tag: {str(e)}")
            return None
    
    def _extract_document_title_advanced(self, document: pikepdf.Pdf, input_path: Path) -> Optional[str]:
        """
        Extract document title using advanced spatial filtering algorithm.
        
        Implements O(n log n) complexity with spatial zone filtering,
        journal pattern recognition, and Gaussian position weighting.
        
        Args:
            document: The PDF document to extract title from
            input_path: Path to the original PDF file
            
        Returns:
            Optional[str]: The extracted title, or None if not found
        """
        import re
        import math
        
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.warning("PyMuPDF required for advanced title extraction")
            return None
            
        try:
            # Open document with PyMuPDF for text analysis
            temp_doc = fitz.open(str(input_path))
            
            if len(temp_doc) == 0:
                temp_doc.close()
                return None
            
            first_page = temp_doc[0]
            page_height = first_page.rect.height
            
            # Define spatial exclusion zones (15% header, 15% footer)
            header_zone_limit = page_height * 0.15
            footer_zone_limit = page_height * 0.85
            
            # Journal name patterns for detection
            journal_patterns = [
                r'\bjournal\s+of\b',
                r'\bproceedings\s+of\b',
                r'\btransactions\s+on\b',
                r'\bieee\s+',
                r'\bacm\s+',
                r'\breview\s+of\b',
                r'\bannals\s+of\b',
                r'\binternational\s+(journal|conference)\b',
                r'\bsymposium\s+on\b',
                r'\bworkshop\s+on\b',
                r'\bvol\.?\s*\d+',
                r'\bissn\b',
                r'\bdoi\b',
                r'©\s*\d{4}',
            ]
            
            # Compile patterns for efficiency
            journal_regex = re.compile('|'.join(journal_patterns), re.IGNORECASE)
            
            # Get text blocks with formatting information
            blocks = first_page.get_text("dict")
            
            title_candidates = []
            
            # Look for text blocks that could be titles
            for block in blocks.get("blocks", []):
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    bbox = line.get("bbox", [0, 0, 0, 0])
                    y_position = bbox[1]
                    
                    # Skip text in header/footer zones
                    if y_position < header_zone_limit or y_position > footer_zone_limit:
                        continue
                    
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        font_size = span.get("size", 0)
                        font_flags = span.get("flags", 0)
                        
                        # Enhanced filtering for potential title text
                        if (text and 
                            len(text) > 10 and
                            len(text) < 300 and
                            font_size > 12 and
                            not text.lower().startswith(('abstract', 'keywords', 'introduction', 
                                                       'figure', 'table', 'contents', 'acknowledgment')) and
                            not any(char.isdigit() for char in text[:3]) and
                            not text.startswith(('http', 'www.', 'doi:')) and
                            text.count(' ') >= 2):
                            
                            # Check if text matches journal patterns
                            is_journal = bool(journal_regex.search(text))
                            
                            # Calculate position score with Gaussian weighting
                            gaussian_center = page_height * 0.3
                            gaussian_sigma = page_height * 0.15
                            position_score = math.exp(-((y_position - gaussian_center) ** 2) / (2 * gaussian_sigma ** 2))
                            
                            # Text quality score
                            text_quality = self._calculate_text_quality_score(text, font_flags)
                            
                            # Font size normalized score
                            font_score = min(font_size / 24.0, 1.0)
                            
                            # Composite scoring function
                            composite_score = (
                                0.4 * font_score + 
                                0.35 * position_score + 
                                0.25 * text_quality - 
                                0.5 * (1.0 if is_journal else 0.0)
                            )
                            
                            title_candidates.append({
                                'text': text,
                                'font_size': font_size,
                                'font_flags': font_flags,
                                'y_position': y_position,
                                'is_journal': is_journal,
                                'composite_score': composite_score,
                                'position_score': position_score,
                                'quality_score': text_quality
                            })
            
            temp_doc.close()
            
            if not title_candidates:
                return None
            
            # Sort by composite score (descending)
            title_candidates.sort(key=lambda x: x['composite_score'], reverse=True)
            
            # Multi-line title detection
            best_candidate = title_candidates[0]
            complete_title = best_candidate['text']
            
            # Check for continuation lines
            proximity_threshold = 30
            for candidate in title_candidates[1:]:
                if (not candidate['is_journal'] and
                    abs(candidate['y_position'] - best_candidate['y_position']) < proximity_threshold and
                    candidate['font_size'] >= best_candidate['font_size'] * 0.9):
                    complete_title += " " + candidate['text']
            
            # Clean up the title
            complete_title = ' '.join(complete_title.split())
            complete_title = complete_title.strip('.,;:')
            complete_title = re.sub(r'\s*\*+\s*', ' ', complete_title)  # Remove asterisks
            complete_title = re.sub(r'\s+', ' ', complete_title).strip()  # Final cleanup
            
            logger.info(f"Enhanced H1 extraction: {complete_title}")
            return complete_title

        except Exception as e:
            logger.warning(f"Error extracting title from H1 tag: {str(e)}")
            return None

    def enhance_pdf_accessibility(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        title: Optional[str] = None,
        author: Optional[str] = None,
        language: str = "en-US",
    ) -> bool:
        """
        Enhance PDF accessibility features.

        This is a convenience method for CLI interfaces.

        Args:
            input_path: Path to the input PDF document
            output_path: Path where the enhanced document should be saved
            title: Document title (default: None, will extract from H1 or filename)
            author: Document author (default: None)
            language: Document language (default: 'en-US')

        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        kwargs = {
            "title": title,
            "author": author,
            "language": language,
            "extract_title_from_h1": True,
            "extract_title_from_filename": True,
        }

        return self.enhance_file(input_path, output_path, **kwargs)

    def get_capabilities(self) -> List[str]:
        """
        Get the list of enhancement capabilities provided by this enhancer.

        Returns:
            List[str]: List of capability identifiers
        """
        return [
            "metadata.title",
            "metadata.author",
            "metadata.language",
            "viewer.display_title",
            "metadata.title_from_h1",
        ]
    
    def _calculate_text_quality_score(self, text: str, font_flags: int) -> float:
        """
        Calculate text quality score based on academic title characteristics.
        
        Args:
            text: The text to analyze
            font_flags: Font formatting flags
            
        Returns:
            float: Quality score between 0.0 and 1.0
        """
        score = 0.0
        
        # Length scoring
        text_length = len(text)
        if 50 <= text_length <= 150:
            score += 0.3
        elif 30 <= text_length < 50 or 150 < text_length <= 200:
            score += 0.2
        elif 20 <= text_length < 30 or 200 < text_length <= 250:
            score += 0.1
        
        # Capitalization patterns
        words = text.split()
        if len(words) > 0:
            title_case_words = sum(1 for word in words if word[0].isupper() if word)
            title_case_ratio = title_case_words / len(words)
            if title_case_ratio > 0.7:
                score += 0.2
            elif text[0].isupper():
                score += 0.15
        
        # Academic keywords boost
        academic_keywords = ['analysis', 'study', 'investigation', 'approach', 'method',
                           'system', 'framework', 'model', 'evaluation', 'assessment',
                           'comparative', 'novel', 'efficient', 'optimal', 'enhanced']
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in academic_keywords):
            score += 0.15
        
        # Punctuation patterns
        if ':' in text:
            score += 0.1
        
        # Font style bonus
        if font_flags & 2**4:
            score += 0.15
        
        # Penalize all caps
        if text.isupper() and len(text) > 20:
            score -= 0.2
        
        return max(0.0, min(1.0, score))

    def enhance_pdf_accessibility(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        title: Optional[str] = None,
        author: Optional[str] = None,
        language: str = "en-US",
    ) -> bool:
        """
        Enhance PDF accessibility features.

        This is a convenience method for CLI interfaces.

        Args:
            input_path: Path to the input PDF document
            output_path: Path where the enhanced document should be saved
            title: Document title (default: None, will extract from H1 or filename)
            author: Document author (default: None)
            language: Document language (default: 'en-US')

        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        kwargs = {
            "title": title,
            "author": author,
            "language": language,
            "extract_title_from_h1": True,
            "extract_title_from_filename": True,
        }

        return self.enhance_file(input_path, output_path, **kwargs)

    def get_capabilities(self) -> List[str]:
        """
        Get the list of enhancement capabilities provided by this enhancer.

        Returns:
            List[str]: List of capability identifiers
        """
        return [
            "metadata.title",
            "metadata.author",
            "metadata.language",
            "viewer.display_title",
            "metadata.title_from_h1",
        ]
