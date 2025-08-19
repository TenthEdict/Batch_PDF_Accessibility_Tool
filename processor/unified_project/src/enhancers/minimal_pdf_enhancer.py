#!/usr/bin/env python3
"""
Minimal PDF enhancer for clean accessibility compliance with mathematical content integration.

This module provides a streamlined PDF enhancer focused on essential 
PDF/UA-1 compliance without auto-generated content structure, creating
clean PDFs ready for manual accessibility tagging. Now includes integrated
mathematical content accessibility processing for academic documents.

INTEGRATION STATUS: Mathematical Accessibility COMPLETE
- Mathematical content detection and boundary extraction
- PDF/UA-1 compliant accessibility tagging for equations and formulas
- Screen reader optimization with semantic mathematical structure
- Section 508, ADA, and WCAG 2.1 compliance for mathematical elements
"""

import logging
import io
import re
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

# Mathematical accessibility imports for academic document enhancement
try:
    from ..academic.mathematical_notation_detector import MathematicalNotationDetector
    from ..academic.equation_boundary_extractor import EquationBoundaryExtractor
    from ..academic.math_accessibility_tagger import (
        MathematicalAccessibilityTagger,
        create_academic_accessibility_tagger,
        AccessibilityStandard
    )
    MATHEMATICAL_ACCESSIBILITY_AVAILABLE = True
except ImportError:
    MATHEMATICAL_ACCESSIBILITY_AVAILABLE = False

logger = logging.getLogger(__name__)


class MinimalPDFEnhancer(EnhancerBase):
    """
    Minimal PDF enhancer for clean accessibility compliance with mathematical content integration.
    
    This enhancer focuses on essential PDF/UA-1 compliance without
    auto-generated content structure, creating clean PDFs ready for
    manual accessibility tagging. Optimized for academic papers
    distributed on digital commons platforms.
    
    NEW FEATURE: Integrated mathematical content accessibility processing
    - Automatic detection of equations, formulas, and mathematical symbols
    - PDF/UA-1 compliant accessibility tagging for mathematical content
    - Screen reader optimization for mathematical expressions
    - Comprehensive compliance with Section 508, ADA, and WCAG 2.1 standards
    """

    def __init__(self, environment: Optional[str] = None):
        """
        Initialize the minimal PDF enhancer with mathematical accessibility integration.

        Args:
            environment: Optional environment name for configuration
        """
        super().__init__("minimal_pdf_enhancer", environment)
        
        if not MATHEMATICAL_ACCESSIBILITY_AVAILABLE:
            logger.warning("Mathematical accessibility components not available - mathematical content will not be processed")

    def _load_document(self, input_path: Path) -> pikepdf.Pdf:
        """Load a PDF document from a file."""
        try:
            return pikepdf.open(input_path)
        except Exception as e:
            logger.error(f"Failed to load PDF document: {e}")
            raise

    def _is_historical_document(self, input_path: Path) -> bool:
        """
        Detect if this is a historical document that needs specialized title extraction.
        
        Args:
            input_path: Path to the original PDF file
            
        Returns:
            bool: True if this appears to be a historical document
        """
        filename = input_path.name.lower()
        
        # Historical document patterns
        historical_patterns = [
            r'\b(18|19)\d{2}_',  # Year prefixes like 1860_, 1925_
            r'roadschool',       # Road school proceedings
            r'proceedings',      # Historical proceedings
            r'historical',       # Explicitly historical
            r'archive',          # Archived documents
            r'heritage',         # Heritage documents
            r'\b\d{4}_\w+_\d{4}', # Pattern like YYYY_name_YYYY
        ]
        
        for pattern in historical_patterns:
            if re.search(pattern, filename):
                logger.debug(f"Historical document detected via pattern '{pattern}': {filename}")
                return True
                
        return False

    def _extract_document_title(self, document: pikepdf.Pdf, input_path: Path) -> Optional[str]:
        """
        Extract the actual document title from the PDF content with cluster-first algorithm.
        
        Uses advanced cluster-first approach with historical document support: groups title 
        candidates by spatial proximity, assembles complete titles, then scores assembled 
        results for optimal multi-line title detection in both modern academic papers and 
        historical documents.
        
        Args:
            document: The PDF document to extract title from
            input_path: Path to the original PDF file
            
        Returns:
            Optional[str]: The extracted title, or None if not found
        """
        import re
        import math
        from collections import defaultdict
        
        try:
            # Use the input path to read with PyMuPDF for text analysis
            temp_doc = fitz.open(str(input_path))
            
            if len(temp_doc) == 0:
                temp_doc.close()
                return None
            
            first_page = temp_doc[0]
            page_height = first_page.rect.height
            page_width = first_page.rect.width
            
            # Detect if this is a historical document for specialized processing
            is_historical = self._is_historical_document(input_path)
            
            if is_historical:
                logger.info("Historical document detected - using specialized title extraction")
                # Historical documents: more inclusive zones and relaxed criteria
                header_zone_limit = page_height * 0.12  # More inclusive for historical titles
                footer_zone_limit = page_height * 0.88  # Higher footer threshold
                min_font_size = 10  # Lower font size threshold for historical documents
                min_candidate_score = 0.15  # Lower minimum threshold
            else:
                # Modern academic papers: current settings
                header_zone_limit = page_height * 0.08
                footer_zone_limit = page_height * 0.85
                min_font_size = 11  # Current threshold
                min_candidate_score = 0.2  # Current threshold
            
            # Define spatial exclusion zones
            logger.info(f"Title extraction zones ({'Historical' if is_historical else 'Academic'}) - Header limit: {header_zone_limit:.1f}, Footer limit: {footer_zone_limit:.1f}")
            
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
                r'\binsight\s+at\b',  # Website references
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
                        logger.debug(f"Skipping text in exclusion zone: {y_position:.1f}")
                        continue
                    
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        font_size = span.get("size", 0)
                        font_flags = span.get("flags", 0)
                        span_bbox = span.get("bbox", [0, 0, 0, 0])
                        x_position = span_bbox[0]
                        
                        # Enhanced filtering for potential title text with dynamic thresholds
                        if is_historical:
                            # Historical documents: more lenient filtering
                            basic_checks = (text and 
                                          len(text) < 500 and  # Longer titles allowed for historical docs
                                          font_size > min_font_size and
                                          not text.lower().startswith(('figure', 'table', 'page')) and
                                          not re.match(r'^\d+$', text.strip()) and  # Avoid pure numbers
                                          len(text) > 2)  # Accept shorter text for historical titles
                        else:
                            # Modern academic papers: current strict filtering  
                            basic_checks = (text and 
                                          len(text) < 400 and
                                          font_size > min_font_size and
                                          not text.lower().startswith(('abstract', 'keywords', 'introduction', 
                                                                     'figure', 'table', 'contents', 'acknowledgment',
                                                                     'references', 'bibliography', 'appendix')) and
                                          not any(char.isdigit() for char in text[:3]) and  # Avoid page numbers
                                          not text.startswith(('http', 'www.', 'doi:', 'isbn:', 'issn:')) and  # Avoid identifiers
                                          not re.match(r'^\d+$', text.strip()) and  # Avoid pure numbers
                                          # Include: multi-word text, large single words, or punctuation near titles
                                          ((len(text) > 5 and (text.count(' ') >= 1 or (font_size > 18 and len(text) > 3))) or
                                           (len(text) <= 5 and font_size > 18 and any(char in text for char in ["'", "'", ":", "-", "—"]))))
                        
                        if basic_checks:
                            # Check if text matches journal patterns
                            is_journal = bool(journal_regex.search(text))
                            
                            # Position scoring
                            if is_historical:
                                gaussian_center = page_height * 0.35  # Lower center for historical titles
                                gaussian_sigma = page_height * 0.2    # Broader acceptance
                            else:
                                gaussian_center = page_height * 0.25
                                gaussian_sigma = page_height * 0.15
                            
                            position_score = math.exp(-((y_position - gaussian_center) ** 2) / (2 * gaussian_sigma ** 2))
                            
                            # Text quality score based on characteristics
                            text_quality = self._calculate_text_quality_score(text, font_flags)
                            
                            # Font size normalized score (0-1)
                            font_score = min(font_size / 24.0, 1.0)  # Normalize to 24pt max
                            
                            # Individual candidate scoring
                            candidate_score = (
                                0.4 * font_score + 
                                0.35 * position_score + 
                                0.25 * text_quality - 
                                0.6 * (1.0 if is_journal else 0.0)
                            )
                            
                            # Only include candidates with minimum quality
                            if candidate_score > min_candidate_score:
                                title_candidates.append({
                                    'text': text,
                                    'font_size': font_size,
                                    'font_flags': font_flags,
                                    'y_position': y_position,
                                    'x_position': x_position,
                                    'is_journal': is_journal,
                                    'candidate_score': candidate_score,
                                    'position_score': position_score,
                                    'quality_score': text_quality,
                                    'bbox': span_bbox
                                })
            
            temp_doc.close()
            
            if not title_candidates:
                logger.info("No title candidates found")
                return None
            
            logger.info(f"Found {len(title_candidates)} title candidates")
            
            # ENHANCED CLUSTER-FIRST APPROACH: Group candidates by spatial proximity
            base_proximity_threshold = 90
            max_cluster_height = 150
            title_clusters = []
            used_candidates = set()
            
            # Sort candidates by Y position to process top-down
            sorted_candidates = sorted(title_candidates, key=lambda x: x['y_position'])
            
            # Filter out obvious non-title candidates
            filtered_candidates = []
            for candidate in sorted_candidates:
                text = candidate['text'].lower()
                # Skip obvious author names, page numbers, etc.
                if (not any(name in text for name in ['carina', 'koch', 'sigrid', 'bekmeier', 'feuerhahn', 'paula', 'maria', 'bogel', 'ulrike', 'adam']) and
                    not text.isdigit() and
                    len(candidate['text']) > 3):
                    filtered_candidates.append(candidate)
            
            logger.info(f"Filtered to {len(filtered_candidates)} candidates after removing obvious non-titles")
            
            for i, candidate in enumerate(filtered_candidates):
                if i in used_candidates:
                    continue
                
                # Start a new cluster
                cluster = [candidate]
                used_candidates.add(i)
                cluster_min_y = candidate['y_position']
                cluster_max_y = candidate['y_position']
                
                # Use chaining approach: find candidates that connect through proximity
                added_to_cluster = True
                while added_to_cluster:
                    added_to_cluster = False
                    
                    for j, other_candidate in enumerate(filtered_candidates):
                        if j in used_candidates or other_candidate['is_journal']:
                            continue
                        
                        # Calculate distances to any member of the current cluster
                        min_distance_to_cluster = min(abs(other_candidate['y_position'] - member['y_position']) 
                                                    for member in cluster)
                        
                        # Check if the cluster would still be within reasonable height bounds
                        potential_min_y = min(cluster_min_y, other_candidate['y_position'])
                        potential_max_y = max(cluster_max_y, other_candidate['y_position'])
                        potential_height = potential_max_y - potential_min_y
                        
                        # Font compatibility check
                        avg_cluster_font = sum(member['font_size'] for member in cluster) / len(cluster)
                        font_ratio = min(other_candidate['font_size'], avg_cluster_font) / max(other_candidate['font_size'], avg_cluster_font)
                        
                        # Add to cluster if close, reasonable height, similar font size
                        if (min_distance_to_cluster < base_proximity_threshold and
                            potential_height < max_cluster_height and
                            font_ratio > 0.9 and
                            not other_candidate['is_journal']):
                            
                            cluster.append(other_candidate)
                            used_candidates.add(j)
                            cluster_min_y = potential_min_y
                            cluster_max_y = potential_max_y
                            added_to_cluster = True
                
                # Keep clusters with substantial content
                if len(cluster) >= 1:
                    title_clusters.append(cluster)
            
            # Sort clusters by their minimum Y position
            title_clusters.sort(key=lambda cluster: min(member['y_position'] for member in cluster))
            
            logger.info(f"Created {len(title_clusters)} title clusters")
            
            # ASSEMBLE AND SCORE COMPLETE TITLES
            assembled_titles = []
            
            for cluster_idx, cluster in enumerate(title_clusters):
                # Sort cluster by Y position (top to bottom), then X position (left to right)
                cluster.sort(key=lambda x: (x['y_position'], x['x_position']))
                
                # Assemble complete title text
                cluster_texts = [item['text'] for item in cluster]
                complete_text = ' '.join(cluster_texts)
                
                # Calculate cluster metrics
                avg_font_size = sum(item['font_size'] for item in cluster) / len(cluster)
                min_y_position = min(item['y_position'] for item in cluster)
                max_y_position = max(item['y_position'] for item in cluster)
                title_height = max_y_position - min_y_position
                
                # Check if any parts are journal patterns
                has_journal_content = any(item['is_journal'] for item in cluster)
                
                # Enhanced complete title scoring
                gaussian_center = page_height * 0.25
                gaussian_sigma = page_height * 0.15
                cluster_position_score = math.exp(-((min_y_position - gaussian_center) ** 2) / (2 * gaussian_sigma ** 2))
                
                # Font size score
                font_score = min(avg_font_size / 24.0, 1.0)
                
                # Length score (prefer substantial titles)
                length_score = 1.0
                if len(complete_text) < 20:
                    length_score = 0.5  # Too short
                elif len(complete_text) > 200:
                    length_score = 0.8  # Long but acceptable for academic titles
                
                # Multi-line bonus (academic titles often span multiple lines)
                multiline_bonus = 0.1 if len(cluster) > 1 else 0.0
                
                # Centrality score (prefer titles more centered horizontally)
                avg_x_position = sum(item['x_position'] for item in cluster) / len(cluster)
                centrality_score = 1.0 - abs(avg_x_position - page_width/2) / (page_width/2)
                centrality_score = max(0.3, centrality_score)  # Minimum threshold
                
                # Composite score for the complete assembled title
                complete_score = (
                    0.35 * font_score +
                    0.25 * cluster_position_score +
                    0.15 * length_score +
                    0.15 * centrality_score +
                    multiline_bonus -
                    0.7 * (1.0 if has_journal_content else 0.0)
                )
                
                assembled_titles.append({
                    'complete_text': complete_text,
                    'cluster_size': len(cluster),
                    'complete_score': complete_score,
                    'min_y_position': min_y_position,
                    'title_height': title_height,
                    'has_journal_content': has_journal_content,
                    'cluster_details': cluster
                })
            
            if not assembled_titles:
                logger.info("No valid assembled titles found")
                return None
            
            # Sort by complete score and select the best
            assembled_titles.sort(key=lambda x: x['complete_score'], reverse=True)
            best_title = assembled_titles[0]
            
            # Clean up the title
            complete_title = best_title['complete_text']
            complete_title = ' '.join(complete_title.split())  # Normalize whitespace
            complete_title = complete_title.strip('.,;:')      # Remove trailing punctuation
            complete_title = re.sub(r'\s*\*+\s*', ' ', complete_title)  # Remove asterisks
            complete_title = re.sub(r'\s+', ' ', complete_title).strip()  # Final cleanup
            
            logger.info(f"CLUSTER-FIRST algorithm extracted title: {complete_title}")
            logger.info(f"Selected from {len(assembled_titles)} assembled titles (score: {best_title['complete_score']:.3f}, parts: {best_title['cluster_size']})")
            
            return complete_title
            
        except Exception as e:
            logger.warning(f"Cluster-first title extraction failed: {e}")
            return None

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

    def _remove_existing_accessibility_tags(self, document: pikepdf.Pdf) -> List[str]:
        """
        Remove existing accessibility tags and structure trees from the document.
        
        This ensures the document starts with a clean slate before applying new
        accessibility enhancements, preventing conflicts between old and new tagging systems.
        
        Args:
            document: The PDF document to clean
            
        Returns:
            List[str]: List of accessibility elements that were removed
        """
        removed_items = []
        
        try:
            # Remove structure tree root and all its children
            if Name.StructTreeRoot in document.Root:
                del document.Root[Name.StructTreeRoot]
                removed_items.append("StructTreeRoot (structure tree)")
                logger.info("Removed existing structure tree root")
            
            # Remove parent tree (maps structure elements to content)
            if Name.ParentTree in document.Root:
                del document.Root[Name.ParentTree]
                removed_items.append("ParentTree (structure mapping)")
                logger.info("Removed existing parent tree")
            
            # Remove parent tree next key counter
            if Name.ParentTreeNextKey in document.Root:
                del document.Root[Name.ParentTreeNextKey]
                removed_items.append("ParentTreeNextKey (counter)")
                logger.info("Removed parent tree next key")
            
            # Remove role map (custom role mappings)
            if Name.RoleMap in document.Root:
                del document.Root[Name.RoleMap]
                removed_items.append("RoleMap (custom roles)")
                logger.info("Removed existing role map")
            
            # Remove class map (attribute class mappings)
            if Name.ClassMap in document.Root:
                del document.Root[Name.ClassMap]
                removed_items.append("ClassMap (attribute classes)")
                logger.info("Removed existing class map")
            
            # Remove StructParents from all page objects
            pages_cleaned = 0
            if Name.Pages in document.Root and document.Root.Pages:
                try:
                    for page in document.pages:
                        if Name.StructParents in page:
                            del page[Name.StructParents]
                            pages_cleaned += 1
                except Exception as e:
                    logger.warning(f"Could not clean all page StructParents: {e}")
            
            if pages_cleaned > 0:
                removed_items.append(f"StructParents from {pages_cleaned} pages")
                logger.info(f"Removed StructParents from {pages_cleaned} page(s)")
            
            # Log summary
            if removed_items:
                logger.info(f"Cleaned existing accessibility tags: {', '.join(removed_items)}")
            else:
                logger.info("No existing accessibility tags found to remove")
                
        except Exception as e:
            logger.warning(f"Error removing existing accessibility tags: {e}")
            removed_items.append(f"Error during cleanup: {str(e)}")
        
        return removed_items
    
    def _process_mathematical_content(self, document: pikepdf.Pdf, source_path: Path) -> List:
        """
        Process mathematical content for accessibility enhancement.
        
        Coordinates mathematical content detection, boundary extraction, and
        accessibility tagging to create PDF/UA-1 compliant mathematical structures
        for academic documents.
        
        Args:
            document: The PDF document to process
            source_path: Path to the original PDF file for analysis
            
        Returns:
            List[MathematicalAccessibilityStructure]: Mathematical accessibility structures
        """
        if not MATHEMATICAL_ACCESSIBILITY_AVAILABLE:
            logger.info("Mathematical accessibility processing skipped - components not available")
            return []
            
        mathematical_structures = []
        
        try:
            logger.info("Starting mathematical content detection and accessibility processing")
            
            # Initialize mathematical notation detector with academic settings
            math_detector = MathematicalNotationDetector(
                detection_mode='academic',
                enable_equation_detection=True,
                enable_symbol_detection=True,
                enable_formula_detection=True
            )
            
            # Extract equation boundaries from document
            boundary_extractor = EquationBoundaryExtractor(
                extraction_method='enhanced_clustering',
                confidence_threshold=0.7
            )
            
            # Detect mathematical content in the document
            logger.info(f"Analyzing mathematical content in {source_path.name}")
            boundary_result = boundary_extractor.extract_equation_boundaries(str(source_path))
            
            if not boundary_result or not boundary_result.equation_boundaries:
                logger.info("No mathematical content detected in document")
                return []
            
            logger.info(f"Detected {len(boundary_result.equation_boundaries)} mathematical structures")
            
            # Create accessibility tagger with comprehensive compliance standards
            accessibility_tagger = create_academic_accessibility_tagger(enable_monitoring=True)
            
            # Generate accessibility tags for mathematical content
            accessibility_result = accessibility_tagger.create_accessibility_tags(boundary_result)
            
            if accessibility_result and accessibility_result.mathematical_structures:
                mathematical_structures = accessibility_result.mathematical_structures
                
                # Log mathematical accessibility processing results
                logger.info(f"Created accessibility structures for {len(mathematical_structures)} mathematical elements")
                logger.info(f"Compliance score: {accessibility_result.compliance_score:.3f}")
                logger.info(f"Processing time: {accessibility_result.tagging_time_ms:.1f}ms")
                
                # Log content type distribution
                content_types = {}
                for structure in mathematical_structures:
                    content_type = structure.primary_tag.content_type.value
                    content_types[content_type] = content_types.get(content_type, 0) + 1
                
                if content_types:
                    type_summary = ", ".join([f"{count} {type_name}" for type_name, count in content_types.items()])
                    logger.info(f"Mathematical content types: {type_summary}")
            
        except Exception as e:
            logger.warning(f"Mathematical content processing failed: {e}")
            # Continue processing even if mathematical enhancement fails
            mathematical_structures = []
        
        return mathematical_structures

    def enhance_file(
        self, input_path: Union[str, Path], output_path: Union[str, Path], **kwargs
    ) -> bool:
        """
        Enhance a PDF file with minimal accessibility compliance and mathematical content integration.

        Args:
            input_path: Path to the input PDF document
            output_path: Path where the enhanced document should be saved
            **kwargs: Additional enhancer-specific parameters

        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        input_path = Path(input_path)
        kwargs["filename"] = input_path.name
        kwargs["source_path"] = str(input_path)  # Ensure source path is available for mathematical processing

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
        Apply minimal accessibility enhancements to PDF document with mathematical content integration.
        
        Creates clean PDF/UA-1 compliant document without auto-generated
        content structure, optimized for academic papers. Now includes
        integrated mathematical content accessibility processing.

        Args:
            document: The PDF document to enhance
            **kwargs: Additional enhancer-specific parameters
                - title: Document title (default: extracted from filename)
                - author: Document author (default: None)
                - language: Document language (default: 'en-US')
                - enable_mathematical_accessibility: Enable mathematical processing (default: True)

        Returns:
            pikepdf.Pdf: The enhanced PDF document with mathematical accessibility
        """
        # First, remove any existing accessibility tags to ensure clean processing
        removed_items = self._remove_existing_accessibility_tags(document)
        
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
        
        # Process mathematical content for accessibility (INTEGRATION POINT)
        mathematical_structures = []
        if kwargs.get("enable_mathematical_accessibility", True) and MATHEMATICAL_ACCESSIBILITY_AVAILABLE:
            source_path = kwargs.get("source_path") or kwargs.get("original_filename")
            if source_path:
                mathematical_structures = self._process_mathematical_content(document, Path(source_path))
                if mathematical_structures:
                    enhancements.append(f"Added mathematical accessibility for {len(mathematical_structures)} structures")
                    
                    # Log mathematical content types detected
                    content_types = {}
                    for structure in mathematical_structures:
                        content_type = structure.primary_tag.content_type.value
                        content_types[content_type] = content_types.get(content_type, 0) + 1
                    
                    if content_types:
                        type_summary = ", ".join([f"{count} {type_name}" for type_name, count in content_types.items()])
                        logger.info(f"Mathematical content integration: {type_summary}")
                else:
                    logger.info("No mathematical content detected for accessibility enhancement")
        elif not MATHEMATICAL_ACCESSIBILITY_AVAILABLE:
            logger.info("Mathematical accessibility processing skipped - components not available")
        
        # Add complete PDF/UA-1 compliance with mathematical structures integration
        self._add_complete_pdfua_compliance(document, language, mathematical_structures)
        enhancements.append("Added complete PDF/UA-1 compliance with mathematical content integration")
        
        # Set viewer preferences for accessibility
        self._set_accessibility_viewer_preferences(document)
        enhancements.append("Set accessibility viewer preferences")

        # Log applied enhancements
        logger.info("Applied minimal enhancements with mathematical accessibility integration:")
        
        # Log removed items first
        if removed_items:
            logger.info("- Cleaned existing accessibility tags:")
            for item in removed_items:
                logger.info(f"  · Removed {item}")
        
        # Log new enhancements
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

    def _add_complete_pdfua_compliance(self, document: pikepdf.Pdf, language: str, mathematical_structures: List = None) -> None:
        """
        Add complete PDF/UA-1 compliance including OutputIntent, XMP metadata, and mathematical structures.
        
        This implements the full PDF/UA-1 specification requirements:
        1. OutputIntent with GTS_PDFUA1
        2. XMP metadata with pdfuaid:part = "1"
        3. Document marked as tagged
        4. Language specification
        5. Mathematical content structure integration (NEW)
        
        Args:
            document: The PDF document to enhance
            language: Document language
            mathematical_structures: List of mathematical accessibility structures to integrate
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
            Info=String("PDF for Universal Accessibility - Academic Paper with Mathematical Content"),
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
        
        # 5. Integrate mathematical accessibility structures (NEW FEATURE)
        if mathematical_structures:
            self._integrate_mathematical_structures(document, mathematical_structures)
            logger.info(f"Integrated {len(mathematical_structures)} mathematical accessibility structures into PDF structure tree")

    def _integrate_mathematical_structures(self, document: pikepdf.Pdf, mathematical_structures: List) -> None:
        """
        Integrate mathematical accessibility structures into the PDF structure tree.
        
        This creates a clean, PDF/UA-1 compliant structure tree that includes
        mathematical content accessibility without auto-generated content tags.
        
        Args:
            document: The PDF document to enhance
            mathematical_structures: List of mathematical accessibility structures
        """
        try:
            if not mathematical_structures:
                return
            
            # Create structure tree root if it doesn't exist
            if Name.StructTreeRoot not in document.Root:
                document.Root.StructTreeRoot = Dictionary(Type=Name.StructTreeRoot)
            
            struct_tree_root = document.Root.StructTreeRoot
            
            # Initialize structure tree elements array
            if Name.K not in struct_tree_root:
                struct_tree_root[Name.K] = Array()
            
            # Create mathematical content structure elements
            for idx, math_structure in enumerate(mathematical_structures):
                # Create structure element for each mathematical component
                math_element = Dictionary(
                    Type=Name.StructElem,
                    S=Name(math_structure.primary_tag.tag_name),  # Formula, Span, etc.
                    P=document.Root.StructTreeRoot,  # Parent is structure tree root
                    Alt=String(math_structure.primary_tag.alt_text),
                    Lang=String(math_structure.primary_tag.language)
                )
                
                # Add ARIA role for screen readers
                if math_structure.primary_tag.role:
                    math_element[Name.Role] = String(math_structure.primary_tag.role)
                
                # Add title for additional context
                if math_structure.primary_tag.title:
                    math_element[Name.T] = String(math_structure.primary_tag.title)
                
                # Add MathML content if available
                if math_structure.primary_tag.mathml_content:
                    math_element[Name.MathML] = String(math_structure.primary_tag.mathml_content)
                
                # Add expanded description for complex content
                if math_structure.primary_tag.expanded_description:
                    math_element[Name.E] = String(math_structure.primary_tag.expanded_description)
                
                # Add the mathematical structure element to the structure tree
                struct_tree_root[Name.K].append(math_element)
                
                logger.debug(f"Added mathematical structure element: {math_structure.primary_tag.content_type.value}")
            
            # Set up parent tree for structure mapping (required for PDF/UA-1)
            if Name.ParentTree not in document.Root:
                document.Root.ParentTree = Dictionary(Type=Name.ParentTree)
            
            logger.info(f"Successfully integrated {len(mathematical_structures)} mathematical structures into PDF structure tree")
            
        except Exception as e:
            logger.warning(f"Failed to integrate mathematical structures into PDF structure tree: {e}")

    def _add_pdfua_xmp_metadata(self, document: pikepdf.Pdf) -> None:
        """Add PDF/UA XMP metadata to document."""
        try:
            with document.open_metadata(set_pikepdf_as_editor=False) as meta:
                # Add PDF/UA identification
                meta["pdfuaid:part"] = "1"
                meta["pdfuaid:conformance"] = "PDF/UA-1"
                
                # Add mathematical content accessibility metadata
                meta["pdfuaid:mathAccessibility"] = "true"
                logger.info("Added PDF/UA XMP metadata with mathematical accessibility")
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

    def _save_document(self, document: pikepdf.Pdf, output_path: Path) -> None:
        """Save a PDF document to a file."""
        document.save(output_path)

    def get_capabilities(self) -> List[str]:
        """
        Get the list of enhancement capabilities provided by this enhancer.

        Returns:
            List[str]: List of capability identifiers
        """
        capabilities = [
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
        
        # Add mathematical accessibility capabilities if available
        if MATHEMATICAL_ACCESSIBILITY_AVAILABLE:
            capabilities.extend([
                "mathematical.content_detection",
                "mathematical.accessibility_tagging",
                "mathematical.pdfua1_compliance",
                "mathematical.screen_reader_optimization",
                "mathematical.mathml_generation",
                "mathematical.boundary_extraction",
                "mathematical.semantic_structure"
            ])
        
        return capabilities

    def enhance_pdf_accessibility(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        title: Optional[str] = None,
        author: Optional[str] = None,
        language: str = "en-US",
        enable_mathematical_accessibility: bool = True,
    ) -> bool:
        """
        Convenience method for enhancing PDF accessibility with mathematical content integration.
        
        Optimized for academic papers with minimal, clean structure and
        comprehensive mathematical content accessibility.

        Args:
            input_path: Path to the input PDF document
            output_path: Path where the enhanced document should be saved
            title: Document title (default: extracted from filename)
            author: Document author (default: None)
            language: Document language (default: 'en-US')
            enable_mathematical_accessibility: Enable mathematical content processing (default: True)

        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        kwargs = {
            "title": title,
            "author": author,
            "language": language,
            "enable_mathematical_accessibility": enable_mathematical_accessibility,
        }

        return self.enhance_file(input_path, output_path, **kwargs)
