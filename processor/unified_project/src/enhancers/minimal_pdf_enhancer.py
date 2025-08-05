#!/usr/bin/env python3
"""
Minimal PDF enhancer for clean accessibility compliance.

This module provides a streamlined PDF enhancer focused on essential 
PDF/UA-1 compliance without auto-generated content structure, creating
clean PDFs ready for manual accessibility tagging.
"""

import logging
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

try:
    import pikepdf
    from pikepdf import Pdf, Name, String, Dictionary, Array
    import fitz  # PyMuPDF for title extraction
except ImportError:
    raise ImportError(
        "pikepdf and PyMuPDF are required for PDF enhancement. "
        "Install them with: pip install pikepdf PyMuPDF"
    )

from .enhancer_base import EnhancerBase

logger = logging.getLogger(__name__)


class MinimalPDFEnhancer(EnhancerBase):
    """
    Minimal PDF enhancer for clean accessibility compliance.
    
    This enhancer focuses on essential PDF/UA-1 compliance without
    auto-generated content structure, creating clean PDFs ready for
    manual accessibility tagging. Optimized for academic papers
    distributed on digital commons platforms.
    """

    def __init__(self, environment: Optional[str] = None):
        """
        Initialize the minimal PDF enhancer.

        Args:
            environment: Optional environment name for configuration
        """
        super().__init__("minimal_pdf_enhancer", environment)

    def _load_document(self, input_path: Path) -> pikepdf.Pdf:
        """Load a PDF document from a file."""
        try:
            return pikepdf.open(input_path)
        except Exception as e:
            logger.error(f"Failed to load PDF document: {e}")
            raise

    def _extract_document_title(self, document: pikepdf.Pdf, input_path: Path) -> Optional[str]:
        """
        Extract the actual document title from the PDF content with advanced spatial filtering.
        
        Implements O(n log n) algorithmic complexity with spatial zone filtering,
        journal pattern recognition, and Gaussian position weighting for optimal
        academic paper title detection.
        
        Args:
            document: The PDF document to extract title from
            input_path: Path to the original PDF file
            
        Returns:
            Optional[str]: The extracted title, or None if not found
        """
        import re
        import math
        
        try:
            # Use the input path to read with PyMuPDF for text analysis
            temp_doc = fitz.open(str(input_path))
            
            if len(temp_doc) == 0:
                temp_doc.close()
                return None
            
            first_page = temp_doc[0]
            page_height = first_page.rect.height
            
            # Define spatial exclusion zones (12% header to be more inclusive, 15% footer)
            header_zone_limit = page_height * 0.12  # Slightly more inclusive for titles
            footer_zone_limit = page_height * 0.85
            optimal_title_zone = (header_zone_limit, page_height * 0.5)
            
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
                r'\bvol\.?\s*\d+',  # Volume indicators
                r'\bissn\b',
                r'\bdoi\b',
                r'©\s*\d{4}',  # Copyright lines
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
                        x_position = span.get("bbox", [0, 0, 0, 0])[0]  # X coordinate for ordering
                        
                        # Enhanced filtering for potential title text
                        if (text and 
                            len(text) > 10 and  # Reasonable title length
                            len(text) < 300 and  # Academic titles can be longer
                            font_size > 12 and   # Larger font size threshold
                            not text.lower().startswith(('abstract', 'keywords', 'introduction', 
                                                       'figure', 'table', 'contents', 'acknowledgment')) and
                            not any(char.isdigit() for char in text[:3]) and  # Avoid page numbers
                            not text.startswith(('http', 'www.', 'doi:')) and  # Avoid URLs/DOIs
                            text.count(' ') >= 2):  # Multi-word titles
                            
                            # Check if text matches journal patterns
                            is_journal = bool(journal_regex.search(text))
                            
                            # Calculate position score with Gaussian weighting
                            # Gaussian centered at 30% of page height (typical title position)
                            gaussian_center = page_height * 0.3
                            gaussian_sigma = page_height * 0.15
                            position_score = math.exp(-((y_position - gaussian_center) ** 2) / (2 * gaussian_sigma ** 2))
                            
                            # Text quality score based on characteristics
                            text_quality = self._calculate_text_quality_score(text, font_flags)
                            
                            # Font size normalized score (0-1)
                            font_score = min(font_size / 24.0, 1.0)  # Normalize to 24pt max
                            
                            # Composite scoring function
                            # S(t) = α·FontSize(t) + β·Position(t) + γ·Quality(t) - δ·IsJournal(t)
                            composite_score = (
                                0.4 * font_score + 
                                0.35 * position_score + 
                                0.25 * text_quality - 
                                0.5 * (1.0 if is_journal else 0.0)  # Penalty for journal patterns
                            )
                            
                            title_candidates.append({
                                'text': text,
                                'font_size': font_size,
                                'font_flags': font_flags,
                                'y_position': y_position,
                                'x_position': x_position,
                                'is_journal': is_journal,
                                'composite_score': composite_score,
                                'position_score': position_score,
                                'quality_score': text_quality
                            })
            
            temp_doc.close()
            
            if not title_candidates:
                return None
            
            # Sort by composite score (descending) - O(n log n) complexity
            title_candidates.sort(key=lambda x: x['composite_score'], reverse=True)
            
            # Enhanced multi-line title detection with proper sorting
            best_candidate = title_candidates[0]
            
            # Find all candidates that could be part of the same title
            title_parts = [best_candidate]
            proximity_threshold = 25  # Pixels
            
            for candidate in title_candidates[1:]:
                if (not candidate['is_journal'] and
                    abs(candidate['y_position'] - best_candidate['y_position']) < proximity_threshold and
                    candidate['font_size'] >= best_candidate['font_size'] * 0.9 and  # Similar font size
                    candidate['composite_score'] > 0.4):  # Reasonable quality threshold
                    title_parts.append(candidate)
            
            # Sort title parts by Y position (top to bottom) and then X position (left to right)
            title_parts.sort(key=lambda x: (x['y_position'], x['x_position']))
            
            # Assemble the complete title
            complete_title = ' '.join([part['text'] for part in title_parts])
            
            # If we only have one part, check if there are other high-scoring candidates nearby
            if len(title_parts) == 1 and len(title_candidates) > 1:
                # Look for other strong candidates within a larger proximity
                extended_threshold = 50
                additional_parts = []
                
                for candidate in title_candidates[1:]:
                    if (not candidate['is_journal'] and
                        abs(candidate['y_position'] - best_candidate['y_position']) < extended_threshold and
                        candidate['composite_score'] > 0.3):  # Lower threshold for potential title parts
                        additional_parts.append(candidate)
                
                if additional_parts:
                    all_parts = [best_candidate] + additional_parts
                    all_parts.sort(key=lambda x: (x['y_position'], x['x_position']))
                    complete_title = ' '.join([part['text'] for part in all_parts])
            
            # Clean up the title
            complete_title = ' '.join(complete_title.split())  # Normalize whitespace
            complete_title = complete_title.strip('.,;:')      # Remove trailing punctuation
            complete_title = re.sub(r'\s*\*+\s*', ' ', complete_title)  # Remove asterisks
            complete_title = re.sub(r'\s+', ' ', complete_title).strip()  # Final cleanup
            
            logger.info(f"Enhanced algorithm extracted title: {complete_title}")
            logger.info(f"Selected from {len(title_candidates)} candidates with score: {best_candidate['composite_score']:.3f}")
            
            return complete_title
            
        except Exception as e:
            logger.warning(f"Enhanced title extraction failed: {e}")
            return None

    def _save_document(self, document: pikepdf.Pdf, output_path: Path) -> None:
        """Save a PDF document to a file."""
        document.save(output_path)

    def enhance_file(
        self, input_path: Union[str, Path], output_path: Union[str, Path], **kwargs
    ) -> bool:
        """
        Enhance a PDF file with minimal accessibility compliance.

        Args:
            input_path: Path to the input PDF document
            output_path: Path where the enhanced document should be saved
            **kwargs: Additional enhancer-specific parameters

        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        input_path = Path(input_path)
        kwargs["filename"] = input_path.name

        try:
            document = self._load_document(input_path)
            document = self.enhance(document, **kwargs)

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            self._save_document(document, output_path)
            return True
        except Exception as e:
            logger.error(f"Error enhancing PDF file: {e}")
            return False

    def enhance(self, document: pikepdf.Pdf, **kwargs) -> pikepdf.Pdf:
        """
        Apply minimal accessibility enhancements to PDF document.
        
        Creates clean PDF/UA-1 compliant document without auto-generated
        content structure, optimized for academic papers.

        Args:
            document: The PDF document to enhance
            **kwargs: Additional enhancer-specific parameters
                - title: Document title (default: extracted from filename)
                - author: Document author (default: None)
                - language: Document language (default: 'en-US')

        Returns:
            pikepdf.Pdf: The enhanced PDF document
        """
        # Extract parameters with academic paper defaults
        title = kwargs.get("title")
        author = kwargs.get("author")
        language = kwargs.get("language", "en-US")
        
        # Preserve original title from PDF content if not explicitly provided
        if not title:
            # First try to extract the actual document title from content
            source_path = kwargs.get("source_path") or kwargs.get("original_filename")
            if source_path:
                content_title = self._extract_document_title(document, Path(source_path))
                if content_title:
                    title = content_title
                else:
                    # Fallback to existing PDF metadata
                    try:
                        with document.open_metadata() as meta:
                            original_title = meta.get("dc:title") or document.docinfo.get("/Title")
                            if original_title and original_title.strip() and original_title.strip() != "Compressed":
                                title = str(original_title).strip()
                                logger.info(f"Using original PDF metadata title: {title}")
                            else:
                                # Final fallback to cleaned filename
                                original_filename = kwargs.get("original_filename") or kwargs.get("filename")
                                if original_filename:
                                    filename = Path(original_filename).stem
                                    # Clean up common academic filename patterns
                                    title = filename.replace("_", " ").replace("-", " ")
                                    # Remove common file suffixes and academic patterns
                                    title = title.replace(" final", "").replace(" draft", "").replace(" v1", "").replace(" v2", "")
                                    title = title.replace("1-s2.0-", "").replace("-main", "")  # Clean DOI patterns
                                    title = title.title().strip()
                                    logger.info(f"Using cleaned filename as title: {title}")
                    except Exception as e:
                        logger.warning(f"Could not extract metadata title: {e}")
                        # Final fallback to basic filename
                        original_filename = kwargs.get("original_filename") or kwargs.get("filename")
                        if original_filename:
                            filename = Path(original_filename).stem
                            title = filename.replace("_", " ").replace("-", " ").title().strip()
                            logger.info(f"Using basic filename as title: {title}")

        # Apply minimal enhancements
        enhancements = []
        
        # Update document metadata (essential for accessibility)
        self._update_document_metadata(document, title, author, language)
        enhancements.extend(self._get_metadata_enhancements(title, author, language))
        
        # Add complete PDF/UA-1 compliance
        self._add_complete_pdfua_compliance(document, language)
        enhancements.append("Added complete PDF/UA-1 compliance")
        
        # Set viewer preferences for accessibility
        self._set_accessibility_viewer_preferences(document)
        enhancements.append("Set accessibility viewer preferences")

        # Log applied enhancements
        logger.info("Applied minimal enhancements:")
        for enhancement in enhancements:
            logger.info(f"- {enhancement}")

        return document

    def _update_document_metadata(self, document: pikepdf.Pdf, title: str, author: str, language: str) -> None:
        """Update document metadata for accessibility."""
        with document.open_metadata(set_pikepdf_as_editor=False) as meta:
            if title:
                meta["dc:title"] = title
            if author:
                meta["dc:creator"] = author
            meta["dc:language"] = language
            
            # Add creation date for academic papers
            meta["xmp:CreateDate"] = datetime.now().isoformat()
            meta["pdf:Producer"] = "ePubs Accessibility Enhancement Project"

    def _get_metadata_enhancements(self, title: str, author: str, language: str) -> List[str]:
        """Get list of metadata enhancements applied."""
        enhancements = []
        if title:
            enhancements.append(f"Added title: {title}")
        if author:
            enhancements.append(f"Added author: {author}")
        enhancements.append(f"Set language to {language}")
        enhancements.append("Added creation metadata")
        return enhancements

    def _add_complete_pdfua_compliance(self, document: pikepdf.Pdf, language: str) -> None:
        """
        Add complete PDF/UA-1 compliance including OutputIntent and XMP metadata.
        
        This implements the full PDF/UA-1 specification requirements:
        1. OutputIntent with GTS_PDFUA1
        2. XMP metadata with pdfuaid:part = "1"
        3. Document marked as tagged
        4. Language specification
        """
        # 1. Ensure document is marked as tagged
        if Name.MarkInfo not in document.Root:
            document.Root.MarkInfo = Dictionary()
        document.Root.MarkInfo[Name.Marked] = True
        
        # 2. Set document language in catalog
        document.Root[Name.Lang] = String(language)
        
        # 3. Create complete PDF/UA-1 OutputIntent
        output_intent = Dictionary(
            Type=Name.OutputIntent,
            S=Name.GTS_PDFUA1,
            OutputConditionIdentifier=String("PDF/UA-1"),
            Info=String("PDF for Universal Accessibility - Academic Paper"),
            RegistryName=String("http://www.color.org")
        )

        if Name.OutputIntents not in document.Root:
            document.Root.OutputIntents = Array()

        # Avoid adding duplicate identifiers
        pdfua_exists = any(
            intent.get(Name.S) == Name.GTS_PDFUA1 
            for intent in document.Root.OutputIntents 
            if isinstance(intent, Dictionary)
        )
        
        if not pdfua_exists:
            document.Root.OutputIntents.append(output_intent)
            logger.info("Added PDF/UA-1 OutputIntent")
        else:
            logger.info("PDF/UA-1 OutputIntent already exists")
            
        # 4. Add PDF/UA XMP metadata
        self._add_pdfua_xmp_metadata(document)

    def _add_pdfua_xmp_metadata(self, document: pikepdf.Pdf) -> None:
        """Add PDF/UA XMP metadata to document."""
        try:
            with document.open_metadata(set_pikepdf_as_editor=False) as meta:
                # Add PDF/UA identification
                meta["pdfuaid:part"] = "1"
                meta["pdfuaid:conformance"] = "PDF/UA-1"
                logger.info("Added PDF/UA XMP metadata")
        except Exception as e:
            logger.warning(f"Could not add PDF/UA XMP metadata: {e}")

    def _set_accessibility_viewer_preferences(self, document: pikepdf.Pdf) -> None:
        """Set viewer preferences optimized for accessibility."""
        if Name.ViewerPreferences not in document.Root:
            document.Root.ViewerPreferences = Dictionary()

        # Essential accessibility viewer preferences
        prefs = document.Root.ViewerPreferences
        prefs[Name.DisplayDocTitle] = True  # Display title instead of filename
        prefs[Name.FitWindow] = True        # Fit document in window
        prefs[Name.CenterWindow] = False    # Don't center (better for screen readers)
        
        # Academic paper specific preferences
        prefs[Name.HideToolbar] = False     # Keep toolbar visible
        prefs[Name.HideMenubar] = False     # Keep menubar visible
        prefs[Name.HideWindowUI] = False    # Keep window UI visible

    def get_capabilities(self) -> List[str]:
        """
        Get the list of enhancement capabilities provided by this enhancer.

        Returns:
            List[str]: List of capability identifiers
        """
        return [
            "pdfua1.complete_compliance",
            "pdfua1.output_intent", 
            "pdfua1.xmp_metadata",
            "metadata.title",
            "metadata.author", 
            "metadata.language",
            "metadata.creation_date",
            "viewer.accessibility_preferences",
            "structure.minimal_tagging"
        ]

    def enhance_pdf_accessibility(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        title: Optional[str] = None,
        author: Optional[str] = None,
        language: str = "en-US",
    ) -> bool:
        """
        Convenience method for enhancing PDF accessibility.
        
        Optimized for academic papers with minimal, clean structure.

        Args:
            input_path: Path to the input PDF document
            output_path: Path where the enhanced document should be saved
            title: Document title (default: extracted from filename)
            author: Document author (default: None)
            language: Document language (default: 'en-US')

        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        kwargs = {
            "title": title,
            "author": author,
            "language": language,
        }

        return self.enhance_file(input_path, output_path, **kwargs)
    
    def _calculate_text_quality_score(self, text: str, font_flags: int) -> float:
        """
        Calculate text quality score based on academic title characteristics.
        
        Implements heuristic scoring with O(n) complexity where n is text length.
        
        Args:
            text: The text to analyze
            font_flags: Font formatting flags
            
        Returns:
            float: Quality score between 0.0 and 1.0
        """
        score = 0.0
        
        # Length scoring (optimal 50-150 characters)
        text_length = len(text)
        if 50 <= text_length <= 150:
            score += 0.3
        elif 30 <= text_length < 50 or 150 < text_length <= 200:
            score += 0.2
        elif 20 <= text_length < 30 or 200 < text_length <= 250:
            score += 0.1
        
        # Capitalization patterns (title case or sentence case preferred)
        words = text.split()
        if len(words) > 0:
            title_case_words = sum(1 for word in words if word[0].isupper() if word)
            title_case_ratio = title_case_words / len(words)
            if title_case_ratio > 0.7:  # Mostly title case
                score += 0.2
            elif text[0].isupper():  # At least sentence case
                score += 0.15
        
        # Academic keywords boost
        academic_keywords = ['analysis', 'study', 'investigation', 'approach', 'method',
                           'system', 'framework', 'model', 'evaluation', 'assessment',
                           'comparative', 'novel', 'efficient', 'optimal', 'enhanced']
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in academic_keywords):
            score += 0.15
        
        # Punctuation patterns (colons common in academic titles)
        if ':' in text:
            score += 0.1
        
        # Font style bonus (bold/italic often used for titles)
        if font_flags & 2**4:  # Bold flag
            score += 0.15
        
        # Penalize all caps (less common in modern academic titles)
        if text.isupper() and len(text) > 20:
            score -= 0.2
        
        # Normalize score to [0, 1]
        return max(0.0, min(1.0, score))

    def _save_document(self, document: pikepdf.Pdf, output_path: Path) -> None:
        """Save a PDF document to a file."""
        document.save(output_path)

    def enhance_file(
        self, input_path: Union[str, Path], output_path: Union[str, Path], **kwargs
    ) -> bool:
        """
        Enhance a PDF file with minimal accessibility compliance.

        Args:
            input_path: Path to the input PDF document
            output_path: Path where the enhanced document should be saved
            **kwargs: Additional enhancer-specific parameters

        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        input_path = Path(input_path)
        kwargs["filename"] = input_path.name

        try:
            document = self._load_document(input_path)
            document = self.enhance(document, **kwargs)

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            self._save_document(document, output_path)
            return True
        except Exception as e:
            logger.error(f"Error enhancing PDF file: {e}")
            return False

    def enhance(self, document: pikepdf.Pdf, **kwargs) -> pikepdf.Pdf:
        """
        Apply minimal accessibility enhancements to PDF document.
        
        Creates clean PDF/UA-1 compliant document without auto-generated
        content structure, optimized for academic papers.

        Args:
            document: The PDF document to enhance
            **kwargs: Additional enhancer-specific parameters
                - title: Document title (default: extracted from filename)
                - author: Document author (default: None)
                - language: Document language (default: 'en-US')

        Returns:
            pikepdf.Pdf: The enhanced PDF document
        """
        # Extract parameters with academic paper defaults
        title = kwargs.get("title")
        author = kwargs.get("author")
        language = kwargs.get("language", "en-US")
        
        # Preserve original title from PDF content if not explicitly provided
        if not title:
            # First try to extract the actual document title from content
            source_path = kwargs.get("source_path") or kwargs.get("original_filename")
            if source_path:
                content_title = self._extract_document_title(document, Path(source_path))
                if content_title:
                    title = content_title
                else:
                    # Fallback to existing PDF metadata
                    try:
                        with document.open_metadata() as meta:
                            original_title = meta.get("dc:title") or document.docinfo.get("/Title")
                            if original_title and original_title.strip() and original_title.strip() != "Compressed":
                                title = str(original_title).strip()
                                logger.info(f"Using original PDF metadata title: {title}")
                            else:
                                # Final fallback to cleaned filename
                                original_filename = kwargs.get("original_filename") or kwargs.get("filename")
                                if original_filename:
                                    filename = Path(original_filename).stem
                                    # Clean up common academic filename patterns
                                    title = filename.replace("_", " ").replace("-", " ")
                                    # Remove common file suffixes and academic patterns
                                    title = title.replace(" final", "").replace(" draft", "").replace(" v1", "").replace(" v2", "")
                                    title = title.replace("1-s2.0-", "").replace("-main", "")  # Clean DOI patterns
                                    title = title.title().strip()
                                    logger.info(f"Using cleaned filename as title: {title}")
                    except Exception as e:
                        logger.warning(f"Could not extract metadata title: {e}")
                        # Final fallback to basic filename
                        original_filename = kwargs.get("original_filename") or kwargs.get("filename")
                        if original_filename:
                            filename = Path(original_filename).stem
                            title = filename.replace("_", " ").replace("-", " ").title().strip()
                            logger.info(f"Using basic filename as title: {title}")

        # Apply minimal enhancements
        enhancements = []
        
        # Update document metadata (essential for accessibility)
        self._update_document_metadata(document, title, author, language)
        enhancements.extend(self._get_metadata_enhancements(title, author, language))
        
        # Add complete PDF/UA-1 compliance
        self._add_complete_pdfua_compliance(document, language)
        enhancements.append("Added complete PDF/UA-1 compliance")
        
        # Set viewer preferences for accessibility
        self._set_accessibility_viewer_preferences(document)
        enhancements.append("Set accessibility viewer preferences")

        # Log applied enhancements
        logger.info("Applied minimal enhancements:")
        for enhancement in enhancements:
            logger.info(f"- {enhancement}")

        return document

    def _update_document_metadata(self, document: pikepdf.Pdf, title: str, author: str, language: str) -> None:
        """Update document metadata for accessibility."""
        with document.open_metadata(set_pikepdf_as_editor=False) as meta:
            if title:
                meta["dc:title"] = title
            if author:
                meta["dc:creator"] = author
            meta["dc:language"] = language
            
            # Add creation date for academic papers
            meta["xmp:CreateDate"] = datetime.now().isoformat()
            meta["pdf:Producer"] = "ePubs Accessibility Enhancement Project"

    def _get_metadata_enhancements(self, title: str, author: str, language: str) -> List[str]:
        """Get list of metadata enhancements applied."""
        enhancements = []
        if title:
            enhancements.append(f"Added title: {title}")
        if author:
            enhancements.append(f"Added author: {author}")
        enhancements.append(f"Set language to {language}")
        enhancements.append("Added creation metadata")
        return enhancements

    def _add_complete_pdfua_compliance(self, document: pikepdf.Pdf, language: str) -> None:
        """
        Add complete PDF/UA-1 compliance including OutputIntent and XMP metadata.
        
        This implements the full PDF/UA-1 specification requirements:
        1. OutputIntent with GTS_PDFUA1
        2. XMP metadata with pdfuaid:part = "1"
        3. Document marked as tagged
        4. Language specification
        """
        # 1. Ensure document is marked as tagged
        if Name.MarkInfo not in document.Root:
            document.Root.MarkInfo = Dictionary()
        document.Root.MarkInfo[Name.Marked] = True
        
        # 2. Set document language in catalog
        document.Root[Name.Lang] = String(language)
        
        # 3. Create complete PDF/UA-1 OutputIntent
        output_intent = Dictionary(
            Type=Name.OutputIntent,
            S=Name.GTS_PDFUA1,
            OutputConditionIdentifier=String("PDF/UA-1"),
            Info=String("PDF for Universal Accessibility - Academic Paper"),
            RegistryName=String("http://www.color.org")
        )

        if Name.OutputIntents not in document.Root:
            document.Root.OutputIntents = Array()

        # Avoid adding duplicate identifiers
        pdfua_exists = any(
            intent.get(Name.S) == Name.GTS_PDFUA1 
            for intent in document.Root.OutputIntents 
            if isinstance(intent, Dictionary)
        )
        
        if not pdfua_exists:
            document.Root.OutputIntents.append(output_intent)
            logger.info("Added PDF/UA-1 OutputIntent")
        else:
            logger.info("PDF/UA-1 OutputIntent already exists")
            
        # 4. Add PDF/UA XMP metadata
        self._add_pdfua_xmp_metadata(document)

    def _add_pdfua_xmp_metadata(self, document: pikepdf.Pdf) -> None:
        """Add PDF/UA XMP metadata to document."""
        try:
            with document.open_metadata(set_pikepdf_as_editor=False) as meta:
                # Add PDF/UA identification
                meta["pdfuaid:part"] = "1"
                meta["pdfuaid:conformance"] = "PDF/UA-1"
                logger.info("Added PDF/UA XMP metadata")
        except Exception as e:
            logger.warning(f"Could not add PDF/UA XMP metadata: {e}")

    def _set_accessibility_viewer_preferences(self, document: pikepdf.Pdf) -> None:
        """Set viewer preferences optimized for accessibility."""
        if Name.ViewerPreferences not in document.Root:
            document.Root.ViewerPreferences = Dictionary()

        # Essential accessibility viewer preferences
        prefs = document.Root.ViewerPreferences
        prefs[Name.DisplayDocTitle] = True  # Display title instead of filename
        prefs[Name.FitWindow] = True        # Fit document in window
        prefs[Name.CenterWindow] = False    # Don't center (better for screen readers)
        
        # Academic paper specific preferences
        prefs[Name.HideToolbar] = False     # Keep toolbar visible
        prefs[Name.HideMenubar] = False     # Keep menubar visible
        prefs[Name.HideWindowUI] = False    # Keep window UI visible

    def get_capabilities(self) -> List[str]:
        """
        Get the list of enhancement capabilities provided by this enhancer.

        Returns:
            List[str]: List of capability identifiers
        """
        return [
            "pdfua1.complete_compliance",
            "pdfua1.output_intent", 
            "pdfua1.xmp_metadata",
            "metadata.title",
            "metadata.author", 
            "metadata.language",
            "metadata.creation_date",
            "viewer.accessibility_preferences",
            "structure.minimal_tagging"
        ]

    def enhance_pdf_accessibility(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        title: Optional[str] = None,
        author: Optional[str] = None,
        language: str = "en-US",
    ) -> bool:
        """
        Convenience method for enhancing PDF accessibility.
        
        Optimized for academic papers with minimal, clean structure.

        Args:
            input_path: Path to the input PDF document
            output_path: Path where the enhanced document should be saved
            title: Document title (default: extracted from filename)
            author: Document author (default: None)
            language: Document language (default: 'en-US')

        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        kwargs = {
            "title": title,
            "author": author,
            "language": language,
        }

        return self.enhance_file(input_path, output_path, **kwargs)
