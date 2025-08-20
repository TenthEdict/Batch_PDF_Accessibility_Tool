#!/usr/bin/env python3
"""
Accessibility Data Extractor

This module extracts accessibility tag trees, compliance patterns, and semantic metadata
from WCAG/PDF-UA/ADA compliant PDF documents for training machine learning models.

Key Capabilities:
- PDF tag tree structure extraction and analysis
- WCAG success criteria mapping to structural patterns
- PDF/UA compliance metadata extraction
- Semantic role assignment pattern analysis
- Training data organization and serialization

Integration with existing Phase 2B infrastructure:
- Extends AdaptiveMLEnhancer feature extraction capabilities
- Integrates with FAISS vector database for accessibility pattern storage
- Leverages existing PyMuPDF and pikepdf infrastructure
"""

import logging
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import time
from collections import defaultdict, Counter

# PDF processing imports (existing infrastructure)
try:
    import fitz  # PyMuPDF
    import pikepdf
    PDF_DEPS_AVAILABLE = True
except ImportError as e:
    PDF_DEPS_AVAILABLE = False
    fitz = None
    pikepdf = None

# ML imports (existing Phase 2B infrastructure)
try:
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import StandardScaler
    ML_DEPS_AVAILABLE = True
except ImportError as e:
    ML_DEPS_AVAILABLE = False
    np = None
    pd = None

logger = logging.getLogger(__name__)


@dataclass
class AccessibilityTagNode:
    """Represents a single node in the PDF accessibility tag tree."""
    tag_type: str
    role: Optional[str]
    attributes: Dict[str, Any]
    text_content: Optional[str]
    children: List['AccessibilityTagNode']
    bounding_box: Optional[Tuple[float, float, float, float]]
    page_number: int
    level: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tag node to dictionary for serialization."""
        return {
            'tag_type': self.tag_type,
            'role': self.role,
            'attributes': self.attributes,
            'text_content': self.text_content,
            'children': [child.to_dict() for child in self.children],
            'bounding_box': self.bounding_box,
            'page_number': self.page_number,
            'level': self.level
        }


@dataclass
class CompliancePattern:
    """Represents an extracted accessibility compliance pattern."""
    pattern_id: str
    wcag_criteria: List[str]
    pdf_ua_requirements: List[str]
    ada_compliance_notes: List[str]
    tag_structure: Dict[str, Any]
    semantic_roles: List[str]
    content_type: str
    document_characteristics: Dict[str, float]
    confidence_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert compliance pattern to dictionary for serialization."""
        return asdict(self)


@dataclass 
class DocumentAccessibilityProfile:
    """Complete accessibility profile for a training document."""
    document_id: str
    file_path: str
    tag_tree: AccessibilityTagNode
    compliance_patterns: List[CompliancePattern]
    metadata: Dict[str, Any]
    wcag_level: str
    pdf_ua_version: str
    language: str
    page_count: int
    extraction_timestamp: float
    feature_vector: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document profile to dictionary for serialization."""
        return {
            'document_id': self.document_id,
            'file_path': self.file_path,
            'tag_tree': self.tag_tree.to_dict(),
            'compliance_patterns': [pattern.to_dict() for pattern in self.compliance_patterns],
            'metadata': self.metadata,
            'wcag_level': self.wcag_level,
            'pdf_ua_version': self.pdf_ua_version,
            'language': self.language,
            'page_count': self.page_count,
            'extraction_timestamp': self.extraction_timestamp,
            'feature_vector': self.feature_vector
        }


class AccessibilityDataExtractor:
    """
    Extract accessibility training data from compliant PDF documents.
    
    This extractor analyzes the tag tree structures, compliance metadata,
    and semantic patterns from WCAG/PDF-UA/ADA compliant documents to create
    training data for machine learning models.
    """
    
    def __init__(self, output_dir: Path, cache_extracted: bool = True):
        """
        Initialize the accessibility data extractor.
        
        Args:
            output_dir: Directory to store extracted patterns and data
            cache_extracted: Whether to cache extraction results for reprocessing
        """
        if not PDF_DEPS_AVAILABLE:
            raise ImportError("PDF dependencies not available. Install with: pip install PyMuPDF pikepdf")
        
        if not ML_DEPS_AVAILABLE:
            raise ImportError("ML dependencies not available. Install with: pip install scikit-learn pandas numpy")
            
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.patterns_dir = self.output_dir / "extracted_patterns"
        self.patterns_dir.mkdir(exist_ok=True)
        
        self.profiles_dir = self.output_dir / "document_profiles"
        self.profiles_dir.mkdir(exist_ok=True)
        
        self.cache_extracted = cache_extracted
        self.extraction_cache = {}
        
        # WCAG success criteria mapping
        self.wcag_criteria_map = self._initialize_wcag_mapping()
        
        # PDF/UA requirement patterns
        self.pdf_ua_patterns = self._initialize_pdf_ua_patterns()
        
        logger.info(f"AccessibilityDataExtractor initialized with output directory: {output_dir}")
    
    def _initialize_wcag_mapping(self) -> Dict[str, List[str]]:
        """Initialize mapping of tag structures to WCAG success criteria."""
        return {
            'heading_structure': ['1.3.1', '2.4.6', '2.4.10'],
            'list_structure': ['1.3.1'], 
            'table_structure': ['1.3.1', '1.3.2'],
            'image_alt_text': ['1.1.1'],
            'reading_order': ['1.3.2', '2.4.3'],
            'language_specification': ['3.1.1', '3.1.2'],
            'semantic_markup': ['1.3.1', '4.1.2'],
            'color_contrast': ['1.4.3', '1.4.11'],
            'form_labels': ['1.3.1', '3.3.2', '4.1.2']
        }
    
    def _initialize_pdf_ua_patterns(self) -> Dict[str, List[str]]:
        """Initialize PDF/UA compliance requirement patterns."""
        return {
            'document_structure': ['7.1 General', '7.2 Scoped content'],
            'semantic_structure': ['7.3 Metadata', '7.4 Logical structure'],
            'page_content': ['7.5 Page content', '7.6 Annotations'],
            'optional_content': ['7.7 Optional Content Groups'],
            'embedded_files': ['7.8 Embedded files'],
            'natural_language': ['7.9 Natural language specification']
        }
    
    def extract_document_profile(self, pdf_path: Path) -> Optional[DocumentAccessibilityProfile]:
        """
        Extract complete accessibility profile from a PDF document.
        
        Args:
            pdf_path: Path to the PDF document
            
        Returns:
            DocumentAccessibilityProfile or None if extraction fails
        """
        try:
            # Generate document ID
            document_id = self._generate_document_id(pdf_path)
            
            # Check cache if enabled
            if self.cache_extracted and document_id in self.extraction_cache:
                logger.info(f"Using cached extraction for {pdf_path.name}")
                return self.extraction_cache[document_id]
            
            logger.info(f"Extracting accessibility profile from: {pdf_path.name}")
            
            # Open PDF with both PyMuPDF and pikepdf for comprehensive analysis
            fitz_doc = fitz.open(str(pdf_path))
            pike_pdf = pikepdf.open(pdf_path)
            
            # Extract basic document metadata
            metadata = self._extract_basic_metadata(fitz_doc, pike_pdf)
            
            # Extract tag tree structure
            tag_tree = self._extract_tag_tree(fitz_doc, pike_pdf)
            
            # Analyze compliance patterns
            compliance_patterns = self._analyze_compliance_patterns(tag_tree, metadata)
            
            # Create document profile
            profile = DocumentAccessibilityProfile(
                document_id=document_id,
                file_path=str(pdf_path),
                tag_tree=tag_tree,
                compliance_patterns=compliance_patterns,
                metadata=metadata,
                wcag_level=metadata.get('wcag_level', 'Unknown'),
                pdf_ua_version=metadata.get('pdf_ua_version', 'Unknown'),
                language=metadata.get('language', 'en'),
                page_count=len(fitz_doc),
                extraction_timestamp=time.time()
            )
            
            # Generate feature vector for ML training
            profile.feature_vector = self._generate_feature_vector(profile)
            
            # Cache result if enabled
            if self.cache_extracted:
                self.extraction_cache[document_id] = profile
            
            # Close PDF documents
            fitz_doc.close()
            pike_pdf.close()
            
            logger.info(f"Successfully extracted accessibility profile for {pdf_path.name}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to extract accessibility profile from {pdf_path}: {str(e)}")
            return None
    
    def _generate_document_id(self, pdf_path: Path) -> str:
        """Generate unique document ID based on file path and content hash."""
        try:
            # Use file path and modification time for ID generation
            path_str = str(pdf_path.absolute())
            mtime = pdf_path.stat().st_mtime
            content_hash = hashlib.md5(f"{path_str}_{mtime}".encode()).hexdigest()
            return f"doc_{content_hash[:12]}"
        except Exception:
            # Fallback to simple path-based ID
            return f"doc_{hashlib.md5(str(pdf_path).encode()).hexdigest()[:12]}"
    
    def _extract_basic_metadata(self, fitz_doc, pike_pdf) -> Dict[str, Any]:
        """Extract basic document metadata and accessibility indicators."""
        metadata = {}
        
        try:
            # PyMuPDF metadata
            fitz_metadata = fitz_doc.metadata
            metadata.update({
                'title': fitz_metadata.get('title', ''),
                'author': fitz_metadata.get('author', ''),
                'subject': fitz_metadata.get('subject', ''),
                'creator': fitz_metadata.get('creator', ''),
                'producer': fitz_metadata.get('producer', ''),
                'creation_date': fitz_metadata.get('creationDate', ''),
                'modification_date': fitz_metadata.get('modDate', '')
            })
            
            # pikepdf metadata and PDF/UA indicators
            try:
                docinfo = pike_pdf.docinfo
                if docinfo:
                    metadata.update({
                        'pdf_version': str(pike_pdf.pdf_version),
                        'is_linearized': pike_pdf.is_linearized
                    })
                
                # Check for PDF/UA compliance indicators
                if pike_pdf.Root.get('/MarkInfo'):
                    mark_info = pike_pdf.Root.MarkInfo
                    metadata['marked'] = bool(mark_info.get('/Marked', False))
                    metadata['suspects'] = bool(mark_info.get('/Suspects', False))
                    
                # Check for accessibility metadata in XMP
                if pike_pdf.Root.get('/Metadata'):
                    metadata['has_xmp_metadata'] = True
                    # TODO: Parse XMP for WCAG/PDF-UA specific metadata
                else:
                    metadata['has_xmp_metadata'] = False
                    
                # Language specification
                if pike_pdf.Root.get('/Lang'):
                    metadata['language'] = str(pike_pdf.Root.Lang)
                else:
                    metadata['language'] = 'en'  # Default
                    
                # PDF/UA version detection (simplified)
                if metadata.get('marked', False):
                    metadata['pdf_ua_version'] = '1.0'  # Assume PDF/UA-1 if marked
                    metadata['wcag_level'] = 'AA'  # Assume WCAG 2.1 AA compliance
                else:
                    metadata['pdf_ua_version'] = 'None'
                    metadata['wcag_level'] = 'None'
                    
            except Exception as e:
                logger.warning(f"Error extracting pikepdf metadata: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error extracting basic metadata: {str(e)}")
            
        return metadata
    
    def _extract_tag_tree(self, fitz_doc, pike_pdf) -> AccessibilityTagNode:
        """Extract the complete PDF tag tree structure."""
        try:
            # Create root tag tree node
            root_node = AccessibilityTagNode(
                tag_type='Document',
                role='Document',
                attributes={},
                text_content=None,
                children=[],
                bounding_box=None,
                page_number=0,
                level=0
            )
            
            # Extract tag tree from PDF using pikepdf with better error handling
            import pikepdf
            
            try:
                # Check if StructTreeRoot exists
                if hasattr(pike_pdf.Root, 'StructTreeRoot') and pike_pdf.Root.StructTreeRoot is not None:
                    struct_tree_root = pike_pdf.Root.StructTreeRoot
                    logger.debug(f"Found StructTreeRoot of type: {type(struct_tree_root)}")
                    
                    # Parse structure tree if it has children
                    if self._is_pikepdf_dictionary(struct_tree_root):
                        children_obj = self._safe_pikepdf_get(struct_tree_root, '/K')
                        if children_obj is not None:
                            logger.debug(f"Found structure children of type: {type(children_obj)}")
                            
                            # Handle both single objects and arrays
                            if not isinstance(children_obj, list):
                                children = [children_obj]
                            else:
                                children = children_obj
                            
                            processed_children = 0
                            for child in children:
                                if self._is_pikepdf_dictionary(child):
                                    child_node = self._parse_structure_element(child, pike_pdf, 1)
                                    if child_node:
                                        root_node.children.append(child_node)
                                        processed_children += 1
                                else:
                                    logger.debug(f"Skipping non-dictionary structure child: {type(child)}")
                            
                            logger.debug(f"Processed {processed_children} structure tree children")
                        else:
                            logger.debug("StructTreeRoot has no /K children")
                    else:
                        logger.debug("StructTreeRoot is not accessible as dictionary")
                else:
                    logger.debug("No StructTreeRoot found in PDF")
                    
            except Exception as e:
                logger.warning(f"Error processing StructTreeRoot: {str(e)}")
            
            # If no structure tree found or processed, create basic structure from content
            if not root_node.children:
                logger.info("No valid structure tree found, creating basic structure from content")
                root_node = self._create_basic_structure_from_content(fitz_doc)
            else:
                logger.debug(f"Successfully extracted structure tree with {len(root_node.children)} top-level children")
            
            return root_node
            
        except Exception as e:
            logger.error(f"Error extracting tag tree: {str(e)}")
            # Return minimal structure as fallback
            return AccessibilityTagNode(
                tag_type='Document',
                role='Document', 
                attributes={},
                text_content=None,
                children=[],
                bounding_box=None,
                page_number=0,
                level=0
            )
    
    def _is_pikepdf_dictionary(self, obj):
        """Check if object is a pikepdf dictionary that can be accessed like a dict."""
        import pikepdf
        
        # Check for pikepdf Dictionary types
        if isinstance(obj, pikepdf.Dictionary):
            return True
        
        # Check for pikepdf Objects that might be dictionaries
        if isinstance(obj, pikepdf.Object):
            try:
                # Try to access it as a dictionary
                if hasattr(obj, 'get') or (hasattr(obj, '__getitem__') and hasattr(obj, '__contains__')):
                    return True
            except:
                pass
        
        # Check for regular dict
        if isinstance(obj, dict):
            return True
        
        return False
    
    def _safe_pikepdf_get(self, obj, key, default=None):
        """Safely get a value from a pikepdf object."""
        try:
            if key in obj:
                return obj[key]
            return default
        except:
            return default
    
    def _parse_structure_element(self, element, pike_pdf, level: int) -> Optional[AccessibilityTagNode]:
        """Parse a single structure element from the PDF tag tree."""
        try:
            # Check if element is valid
            if element is None:
                return None
            
            # Check if element can be accessed as a dictionary
            if not self._is_pikepdf_dictionary(element):
                logger.debug(f"Skipping non-dictionary element of type: {type(element)}")
                return None
            
            # Extract tag type and role with safer access
            tag_type = 'Unknown'
            try:
                s_value = self._safe_pikepdf_get(element, '/S')
                if s_value is not None:
                    tag_type = str(s_value)
            except Exception as e:
                logger.debug(f"Failed to extract tag type: {e}")
            
            role = tag_type  # Default role is tag type
            try:
                t_value = self._safe_pikepdf_get(element, '/T')
                if t_value is not None:
                    role = str(t_value)
            except Exception as e:
                logger.debug(f"Failed to extract role: {e}")
            
            # Extract attributes with safer access
            attributes = {}
            try:
                attr_dict = self._safe_pikepdf_get(element, '/A')
                if attr_dict is not None and self._is_pikepdf_dictionary(attr_dict):
                    # Parse common attributes safely
                    for attr_key, attr_name in [('/BBox', 'bbox'), ('/Layout', 'layout'), ('/Placement', 'placement')]:
                        try:
                            attr_value = self._safe_pikepdf_get(attr_dict, attr_key)
                            if attr_value is not None:
                                attributes[attr_name] = str(attr_value)
                        except Exception as e:
                            logger.debug(f"Failed to extract attribute {attr_name}: {e}")
            except Exception as e:
                logger.debug(f"Failed to process attributes: {e}")
            
            # Extract text content with safer access
            text_content = None
            try:
                actual_text = self._safe_pikepdf_get(element, '/ActualText')
                if actual_text is not None:
                    text_content = str(actual_text)
                else:
                    alt_text = self._safe_pikepdf_get(element, '/Alt')
                    if alt_text is not None:
                        text_content = str(alt_text)
            except Exception as e:
                logger.debug(f"Failed to extract text content: {e}")
            
            # Create tag node
            tag_node = AccessibilityTagNode(
                tag_type=tag_type,
                role=role,
                attributes=attributes,
                text_content=text_content,
                children=[],
                bounding_box=None,
                page_number=0,
                level=level
            )
            
            # Parse children recursively with safer access
            try:
                children_obj = self._safe_pikepdf_get(element, '/K')
                if children_obj is not None:
                    # Handle both single objects and arrays
                    if not isinstance(children_obj, list):
                        children = [children_obj]
                    else:
                        children = children_obj
                    
                    for child in children:
                        # Process child if it's a valid dictionary-like object
                        if self._is_pikepdf_dictionary(child):
                            child_node = self._parse_structure_element(child, pike_pdf, level + 1)
                            if child_node:
                                tag_node.children.append(child_node)
                        else:
                            logger.debug(f"Skipping non-dictionary child of type: {type(child)}")
            except Exception as e:
                logger.debug(f"Failed to process children: {e}")
            
            return tag_node
            
        except Exception as e:
            logger.warning(f"Error parsing structure element: {str(e)}")
            return None
    
    def _create_basic_structure_from_content(self, fitz_doc) -> AccessibilityTagNode:
        """Create basic accessibility structure from document content when no tag tree exists."""
        root_node = AccessibilityTagNode(
            tag_type='Document',
            role='Document',
            attributes={},
            text_content=None,
            children=[],
            bounding_box=None,
            page_number=0,
            level=0
        )
        
        try:
            for page_num in range(len(fitz_doc)):
                page = fitz_doc[page_num]
                
                # Create page structure
                page_node = AccessibilityTagNode(
                    tag_type='Part',
                    role='Page',
                    attributes={'page_number': page_num + 1},
                    text_content=None,
                    children=[],
                    bounding_box=(0, 0, page.rect.width, page.rect.height),
                    page_number=page_num + 1,
                    level=1
                )
                
                # Extract text blocks and create basic structure
                blocks = page.get_text("dict")["blocks"]
                for block in blocks:
                    if block.get("type") == 0:  # Text block
                        text_content = ""
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                text_content += span.get("text", "")
                        
                        if text_content.strip():
                            text_node = AccessibilityTagNode(
                                tag_type='P',
                                role='Paragraph',
                                attributes={},
                                text_content=text_content.strip(),
                                children=[],
                                bounding_box=tuple(block.get("bbox", (0, 0, 0, 0))),
                                page_number=page_num + 1,
                                level=2
                            )
                            page_node.children.append(text_node)
                
                root_node.children.append(page_node)
                
        except Exception as e:
            logger.error(f"Error creating basic structure: {str(e)}")
        
        return root_node
    
    def _analyze_compliance_patterns(self, tag_tree: AccessibilityTagNode, metadata: Dict[str, Any]) -> List[CompliancePattern]:
        """Analyze tag tree structure to identify accessibility compliance patterns."""
        patterns = []
        
        try:
            # Pattern 1: Heading Structure Analysis
            heading_pattern = self._analyze_heading_structure(tag_tree)
            if heading_pattern:
                patterns.append(heading_pattern)
            
            # Pattern 2: List Structure Analysis  
            list_pattern = self._analyze_list_structure(tag_tree)
            if list_pattern:
                patterns.append(list_pattern)
            
            # Pattern 3: Table Structure Analysis
            table_pattern = self._analyze_table_structure(tag_tree)
            if table_pattern:
                patterns.append(table_pattern)
            
            # Pattern 4: Image Alt Text Analysis
            image_pattern = self._analyze_image_accessibility(tag_tree)
            if image_pattern:
                patterns.append(image_pattern)
            
            # Pattern 5: Reading Order Analysis
            reading_order_pattern = self._analyze_reading_order(tag_tree)
            if reading_order_pattern:
                patterns.append(reading_order_pattern)
            
            # Pattern 6: Language Specification Analysis
            language_pattern = self._analyze_language_specification(metadata, tag_tree)
            if language_pattern:
                patterns.append(language_pattern)
            
            logger.info(f"Identified {len(patterns)} compliance patterns")
            
        except Exception as e:
            logger.error(f"Error analyzing compliance patterns: {str(e)}")
        
        return patterns
    
    def _analyze_heading_structure(self, tag_tree: AccessibilityTagNode) -> Optional[CompliancePattern]:
        """Analyze heading structure for WCAG compliance."""
        try:
            headings = self._find_tags_by_type(tag_tree, ['H', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6'])
            
            if not headings:
                return None
            
            # Analyze heading hierarchy
            heading_levels = []
            for heading in headings:
                if heading.tag_type.startswith('H'):
                    if heading.tag_type == 'H':
                        # Generic H tag, check attributes for level
                        level = heading.attributes.get('level', 1)
                    else:
                        # Specific heading level (H1, H2, etc.)
                        level = int(heading.tag_type[1:]) if heading.tag_type[1:].isdigit() else 1
                    heading_levels.append(level)
            
            # Calculate compliance characteristics
            has_h1 = 1 in heading_levels
            proper_hierarchy = self._check_heading_hierarchy(heading_levels)
            heading_count = len(headings)
            
            return CompliancePattern(
                pattern_id=f"heading_structure_{hash(str(heading_levels)) % 10000}",
                wcag_criteria=self.wcag_criteria_map['heading_structure'],
                pdf_ua_requirements=['7.4 Logical structure'],
                ada_compliance_notes=['Proper heading hierarchy supports screen reader navigation'],
                tag_structure={'heading_levels': heading_levels, 'heading_count': heading_count},
                semantic_roles=['heading'],
                content_type='structured_document',
                document_characteristics={
                    'has_h1': float(has_h1),
                    'proper_hierarchy': float(proper_hierarchy),
                    'heading_density': heading_count / max(self._count_all_nodes(tag_tree), 1)
                },
                confidence_score=0.9 if has_h1 and proper_hierarchy else 0.6
            )
            
        except Exception as e:
            logger.warning(f"Error analyzing heading structure: {str(e)}")
            return None
    
    def _analyze_list_structure(self, tag_tree: AccessibilityTagNode) -> Optional[CompliancePattern]:
        """Analyze list structure for accessibility compliance."""
        try:
            lists = self._find_tags_by_type(tag_tree, ['L', 'UL', 'OL'])
            list_items = self._find_tags_by_type(tag_tree, ['LI'])
            
            if not lists:
                return None
            
            # Analyze list characteristics
            list_count = len(lists)
            item_count = len(list_items)
            nested_lists = sum(1 for lst in lists if self._has_nested_lists(lst))
            
            return CompliancePattern(
                pattern_id=f"list_structure_{hash(str([lst.tag_type for lst in lists])) % 10000}",
                wcag_criteria=self.wcag_criteria_map['list_structure'],
                pdf_ua_requirements=['7.4 Logical structure'],
                ada_compliance_notes=['Proper list markup supports assistive technology navigation'],
                tag_structure={'list_types': [lst.tag_type for lst in lists], 'item_count': item_count},
                semantic_roles=['list', 'listitem'],
                content_type='structured_content',
                document_characteristics={
                    'list_count': float(list_count),
                    'avg_items_per_list': item_count / max(list_count, 1),
                    'has_nested_lists': float(nested_lists > 0)
                },
                confidence_score=0.8
            )
            
        except Exception as e:
            logger.warning(f"Error analyzing list structure: {str(e)}")
            return None
    
    def _analyze_table_structure(self, tag_tree: AccessibilityTagNode) -> Optional[CompliancePattern]:
        """Analyze table structure for accessibility compliance."""
        try:
            tables = self._find_tags_by_type(tag_tree, ['Table'])
            headers = self._find_tags_by_type(tag_tree, ['TH'])
            cells = self._find_tags_by_type(tag_tree, ['TD'])
            
            if not tables:
                return None
            
            # Analyze table characteristics
            table_count = len(tables)
            has_headers = len(headers) > 0
            header_ratio = len(headers) / max(len(headers) + len(cells), 1)
            
            return CompliancePattern(
                pattern_id=f"table_structure_{hash(str(table_count)) % 10000}",
                wcag_criteria=self.wcag_criteria_map['table_structure'],
                pdf_ua_requirements=['7.5 Page content'],
                ada_compliance_notes=['Table headers and structure support data comprehension'],
                tag_structure={'table_count': table_count, 'has_headers': has_headers},
                semantic_roles=['table', 'rowheader', 'columnheader'],
                content_type='tabular_data',
                document_characteristics={
                    'table_count': float(table_count),
                    'has_headers': float(has_headers),
                    'header_ratio': header_ratio
                },
                confidence_score=0.9 if has_headers else 0.5
            )
            
        except Exception as e:
            logger.warning(f"Error analyzing table structure: {str(e)}")
            return None
    
    def _analyze_image_accessibility(self, tag_tree: AccessibilityTagNode) -> Optional[CompliancePattern]:
        """Analyze image accessibility features."""
        try:
            images = self._find_tags_by_type(tag_tree, ['Figure', 'Image'])
            
            if not images:
                return None
            
            # Check for alt text and accessibility features
            images_with_alt = 0
            total_images = len(images)
            
            for image in images:
                if (image.text_content or 
                    image.attributes.get('alt') or 
                    image.attributes.get('ActualText')):
                    images_with_alt += 1
            
            alt_text_ratio = images_with_alt / max(total_images, 1)
            
            return CompliancePattern(
                pattern_id=f"image_accessibility_{hash(str(total_images)) % 10000}",
                wcag_criteria=self.wcag_criteria_map['image_alt_text'],
                pdf_ua_requirements=['7.5 Page content'],
                ada_compliance_notes=['Alternative text enables screen reader access to images'],
                tag_structure={'image_count': total_images, 'alt_text_coverage': alt_text_ratio},
                semantic_roles=['img'],
                content_type='visual_content',
                document_characteristics={
                    'image_count': float(total_images),
                    'alt_text_ratio': alt_text_ratio,
                    'has_images': float(total_images > 0)
                },
                confidence_score=alt_text_ratio
            )
            
        except Exception as e:
            logger.warning(f"Error analyzing image accessibility: {str(e)}")
            return None
    
    def _analyze_reading_order(self, tag_tree: AccessibilityTagNode) -> Optional[CompliancePattern]:
        """Analyze logical reading order for accessibility."""
        try:
            # Simple reading order analysis based on tag sequence
            all_content_tags = self._get_content_tags_in_order(tag_tree)
            
            if len(all_content_tags) < 2:
                return None
            
            # Check for proper reading order indicators
            has_logical_sequence = self._check_logical_reading_sequence(all_content_tags)
            content_count = len(all_content_tags)
            
            return CompliancePattern(
                pattern_id=f"reading_order_{hash(str(content_count)) % 10000}",
                wcag_criteria=self.wcag_criteria_map['reading_order'],
                pdf_ua_requirements=['7.4 Logical structure', '7.5 Page content'],
                ada_compliance_notes=['Logical reading order supports sequential content consumption'],
                tag_structure={'content_sequence': [tag.tag_type for tag in all_content_tags[:10]]},  # First 10 for sample
                semantic_roles=['document'],
                content_type='sequential_content',
                document_characteristics={
                    'content_count': float(content_count),
                    'has_logical_sequence': float(has_logical_sequence)
                },
                confidence_score=0.8 if has_logical_sequence else 0.4
            )
            
        except Exception as e:
            logger.warning(f"Error analyzing reading order: {str(e)}")
            return None
    
    def _analyze_language_specification(self, metadata: Dict[str, Any], tag_tree: AccessibilityTagNode) -> Optional[CompliancePattern]:
        """Analyze language specification for accessibility."""
        try:
            # Check document-level language specification
            doc_language = metadata.get('language', '')
            has_doc_language = bool(doc_language and doc_language != 'en')
            
            # Check for language changes within content (simplified)
            language_changes = self._find_language_changes(tag_tree)
            
            return CompliancePattern(
                pattern_id=f"language_spec_{hash(doc_language) % 10000}",
                wcag_criteria=self.wcag_criteria_map['language_specification'],
                pdf_ua_requirements=['7.9 Natural language specification'],
                ada_compliance_notes=['Language specification supports proper pronunciation by screen readers'],
                tag_structure={'document_language': doc_language, 'language_changes': len(language_changes)},
                semantic_roles=['document'],
                content_type='multilingual_content' if language_changes else 'monolingual_content',
                document_characteristics={
                    'has_doc_language': float(has_doc_language),
                    'language_changes': float(len(language_changes))
                },
                confidence_score=0.9 if has_doc_language else 0.6
            )
            
        except Exception as e:
            logger.warning(f"Error analyzing language specification: {str(e)}")
            return None
    
    # Utility methods for tag tree analysis
    
    def _find_tags_by_type(self, node: AccessibilityTagNode, tag_types: List[str]) -> List[AccessibilityTagNode]:
        """Recursively find all nodes with specified tag types."""
        found_tags = []
        
        if node.tag_type in tag_types:
            found_tags.append(node)
        
        for child in node.children:
            found_tags.extend(self._find_tags_by_type(child, tag_types))
        
        return found_tags
    
    def _count_all_nodes(self, node: AccessibilityTagNode) -> int:
        """Count total number of nodes in tag tree."""
        count = 1  # Count current node
        for child in node.children:
            count += self._count_all_nodes(child)
        return count
    
    def _check_heading_hierarchy(self, heading_levels: List[int]) -> bool:
        """Check if heading levels follow proper hierarchy (no skipped levels)."""
        if not heading_levels:
            return False
        
        sorted_levels = sorted(set(heading_levels))
        expected_sequence = list(range(1, len(sorted_levels) + 1))
        
        return sorted_levels == expected_sequence
    
    def _has_nested_lists(self, list_node: AccessibilityTagNode) -> bool:
        """Check if a list contains nested lists."""
        for child in list_node.children:
            if child.tag_type in ['L', 'UL', 'OL']:
                return True
            if self._has_nested_lists(child):
                return True
        return False
    
    def _get_content_tags_in_order(self, node: AccessibilityTagNode) -> List[AccessibilityTagNode]:
        """Get all content tags in document order."""
        content_tags = []
        
        # Content tag types that contribute to reading order
        content_types = ['P', 'H', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'L', 'LI', 'Table', 'Figure']
        
        if node.tag_type in content_types:
            content_tags.append(node)
        
        for child in node.children:
            content_tags.extend(self._get_content_tags_in_order(child))
        
        return content_tags
    
    def _check_logical_reading_sequence(self, content_tags: List[AccessibilityTagNode]) -> bool:
        """Check if content follows logical reading sequence."""
        if len(content_tags) < 2:
            return True
        
        # Simple check: headings should generally come before content
        # More sophisticated analysis would check page layout and positioning
        heading_types = ['H', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6']
        
        last_heading_index = -1
        for i, tag in enumerate(content_tags):
            if tag.tag_type in heading_types:
                last_heading_index = i
            elif tag.tag_type == 'P' and last_heading_index >= 0:
                # Content should come after headings
                if i <= last_heading_index:
                    return False
        
        return True
    
    def _find_language_changes(self, node: AccessibilityTagNode) -> List[str]:
        """Find language specification changes within document."""
        language_changes = []
        
        # Check for language attributes (simplified)
        if 'lang' in node.attributes or 'language' in node.attributes:
            lang = node.attributes.get('lang') or node.attributes.get('language')
            if lang and lang not in language_changes:
                language_changes.append(str(lang))
        
        for child in node.children:
            language_changes.extend(self._find_language_changes(child))
        
        return list(set(language_changes))  # Remove duplicates
    
    def _generate_feature_vector(self, profile: DocumentAccessibilityProfile) -> List[float]:
        """Generate feature vector for machine learning training."""
        features = []
        
        try:
            # Document-level features
            features.extend([
                float(profile.page_count),
                float(len(profile.compliance_patterns)),
                float(profile.metadata.get('marked', False)),
                float(profile.metadata.get('has_xmp_metadata', False))
            ])
            
            # Tag tree structure features
            total_nodes = self._count_all_nodes(profile.tag_tree)
            max_depth = self._calculate_max_depth(profile.tag_tree)
            
            features.extend([
                float(total_nodes),
                float(max_depth),
                float(total_nodes / max(profile.page_count, 1))  # Node density per page
            ])
            
            # Compliance pattern features
            pattern_types = defaultdict(int)
            avg_confidence = 0.0
            
            for pattern in profile.compliance_patterns:
                pattern_types[pattern.content_type] += 1
                avg_confidence += pattern.confidence_score
            
            if profile.compliance_patterns:
                avg_confidence /= len(profile.compliance_patterns)
            
            features.extend([
                float(pattern_types.get('structured_document', 0)),
                float(pattern_types.get('structured_content', 0)),
                float(pattern_types.get('tabular_data', 0)),
                float(pattern_types.get('visual_content', 0)),
                float(avg_confidence)
            ])
            
            # Pad to standard feature vector size (matching Phase 2B: 32 + 96 accessibility = 128)
            while len(features) < 128:
                features.append(0.0)
            
            # Truncate if too long
            features = features[:128]
            
        except Exception as e:
            logger.error(f"Error generating feature vector: {str(e)}")
            # Return zero vector if feature extraction fails
            features = [0.0] * 128
        
        return features
    
    def _calculate_max_depth(self, node: AccessibilityTagNode, current_depth: int = 0) -> int:
        """Calculate maximum depth of tag tree."""
        max_depth = current_depth
        
        for child in node.children:
            child_depth = self._calculate_max_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def save_document_profile(self, profile: DocumentAccessibilityProfile) -> bool:
        """Save document profile to disk for training data persistence."""
        try:
            profile_file = self.profiles_dir / f"{profile.document_id}.json"
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved document profile: {profile_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save document profile {profile.document_id}: {str(e)}")
            return False
    
    def batch_extract_profiles(self, pdf_directory: Path, 
                             max_files: Optional[int] = None,
                             file_pattern: str = "*.pdf") -> List[DocumentAccessibilityProfile]:
        """
        Extract accessibility profiles from a batch of PDF files.
        
        Args:
            pdf_directory: Directory containing PDF files
            max_files: Maximum number of files to process (None for all)
            file_pattern: File pattern to match (default: *.pdf)
            
        Returns:
            List of successfully extracted document profiles
        """
        pdf_files = list(pdf_directory.glob(file_pattern))
        
        if max_files:
            pdf_files = pdf_files[:max_files]
        
        logger.info(f"Starting batch extraction of {len(pdf_files)} PDF files")
        
        profiles = []
        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"Processing file {i}/{len(pdf_files)}: {pdf_file.name}")
            
            profile = self.extract_document_profile(pdf_file)
            if profile:
                profiles.append(profile)
                
                # Save individual profile
                self.save_document_profile(profile)
            else:
                logger.warning(f"Failed to extract profile from {pdf_file.name}")
        
        logger.info(f"Successfully extracted {len(profiles)} accessibility profiles")
        
        # Save batch summary
        self._save_batch_summary(profiles, pdf_directory)
        
        return profiles
    
    def _save_batch_summary(self, profiles: List[DocumentAccessibilityProfile], source_dir: Path):
        """Save batch extraction summary for training analysis."""
        try:
            summary = {
                'extraction_timestamp': time.time(),
                'source_directory': str(source_dir),
                'total_processed': len(profiles),
                'summary_statistics': {
                    'avg_page_count': np.mean([p.page_count for p in profiles]) if profiles else 0,
                    'avg_patterns_per_doc': np.mean([len(p.compliance_patterns) for p in profiles]) if profiles else 0,
                    'wcag_levels': {level: sum(1 for p in profiles if p.wcag_level == level) 
                                  for level in set(p.wcag_level for p in profiles)},
                    'content_types': {}
                }
            }
            
            # Analyze content type distribution
            content_type_counts = defaultdict(int)
            for profile in profiles:
                for pattern in profile.compliance_patterns:
                    content_type_counts[pattern.content_type] += 1
            
            summary['summary_statistics']['content_types'] = dict(content_type_counts)
            
            summary_file = self.output_dir / "batch_extraction_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Saved batch summary: {summary_file}")
            
        except Exception as e:
            logger.error(f"Failed to save batch summary: {str(e)}")

    def aggregate_patterns_from_profiles(self) -> Dict[str, Any]:
        """
        Analyze all document profiles to extract common accessibility patterns.
        
        Returns:
            Dictionary containing aggregated patterns for ML training
        """
        logger.info("Starting pattern aggregation from document profiles")
        
        # Load all document profiles
        profile_files = list(self.profiles_dir.glob("doc_*.json"))
        if not profile_files:
            logger.warning("No document profiles found for pattern aggregation")
            return {}
        
        profiles = []
        for profile_file in profile_files:
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.loads(f.read())
                    profiles.append(profile_data)
            except Exception as e:
                logger.warning(f"Failed to load profile {profile_file.name}: {str(e)}")
        
        logger.info(f"Loaded {len(profiles)} document profiles for analysis")
        
        # Aggregate patterns
        aggregated_patterns = self._extract_common_patterns(profiles)
        
        # Save aggregated patterns
        self._save_aggregated_patterns(aggregated_patterns)
        
        logger.info(f"Pattern aggregation complete. Extracted {len(aggregated_patterns)} pattern types")
        return aggregated_patterns
    
    def _extract_common_patterns(self, profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common accessibility patterns from document profiles."""
        from collections import defaultdict, Counter
        
        # Initialize pattern collectors
        wcag_patterns = defaultdict(list)
        pdf_ua_patterns = defaultdict(list)
        content_type_patterns = defaultdict(list)
        feature_patterns = []
        compliance_distribution = Counter()
        
        for profile in profiles:
            # Collect WCAG patterns
            for pattern in profile.get('compliance_patterns', []):
                wcag_criteria = pattern.get('wcag_criteria', [])
                content_type = pattern.get('content_type', 'unknown')
                
                for criterion in wcag_criteria:
                    wcag_patterns[criterion].append({
                        'content_type': content_type,
                        'confidence_score': pattern.get('confidence_score', 0.0),
                        'semantic_roles': pattern.get('semantic_roles', []),
                        'document_characteristics': pattern.get('document_characteristics', {})
                    })
            
            # Collect PDF/UA patterns
            pdf_ua_version = profile.get('pdf_ua_version', 'unknown')
            wcag_level = profile.get('wcag_level', 'unknown')
            compliance_key = f"PDF/UA-{pdf_ua_version}_WCAG-{wcag_level}"
            compliance_distribution[compliance_key] += 1
            
            # Collect feature vectors
            feature_vector = profile.get('feature_vector', [])
            if feature_vector:
                feature_patterns.append(feature_vector)
            
            # Collect content type patterns
            for pattern in profile.get('compliance_patterns', []):
                content_type = pattern.get('content_type', 'unknown')
                content_type_patterns[content_type].append(pattern)
        
        # Create aggregated patterns
        aggregated = {
            'pattern_summary': {
                'total_documents': len(profiles),
                'extraction_timestamp': time.time(),
                'pattern_types_found': len(wcag_patterns)
            },
            'wcag_compliance_patterns': dict(wcag_patterns),
            'compliance_distribution': dict(compliance_distribution),
            'content_type_analysis': self._analyze_content_types(content_type_patterns),
            'feature_vector_statistics': self._analyze_feature_vectors(feature_patterns),
            'common_accessibility_structures': self._extract_common_structures(profiles)
        }
        
        return aggregated
    
    def _analyze_content_types(self, content_type_patterns: Dict[str, List]) -> Dict[str, Any]:
        """Analyze patterns by content type."""
        analysis = {}
        
        for content_type, patterns in content_type_patterns.items():
            confidence_scores = [p.get('confidence_score', 0.0) for p in patterns]
            semantic_roles = []
            for p in patterns:
                semantic_roles.extend(p.get('semantic_roles', []))
            
            analysis[content_type] = {
                'count': len(patterns),
                'avg_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0,
                'common_semantic_roles': list(set(semantic_roles))
            }
        
        return analysis
    
    def _analyze_feature_vectors(self, feature_vectors: List[List[float]]) -> Dict[str, Any]:
        """Analyze feature vector statistics for ML training."""
        if not feature_vectors:
            return {}
        
        # Convert to numpy array for analysis
        import numpy as np
        features_array = np.array(feature_vectors)
        
        return {
            'dimension_count': features_array.shape[1],
            'sample_count': features_array.shape[0],
            'feature_means': features_array.mean(axis=0).tolist(),
            'feature_stds': features_array.std(axis=0).tolist(),
            'feature_mins': features_array.min(axis=0).tolist(),
            'feature_maxs': features_array.max(axis=0).tolist()
        }
    
    def _extract_common_structures(self, profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common document structure patterns."""
        from collections import Counter
        
        tag_structure_patterns = Counter()
        language_patterns = Counter()
        page_count_distribution = []
        
        for profile in profiles:
            # Analyze tag structures
            tag_tree = profile.get('tag_tree', {})
            if tag_tree:
                self._analyze_tag_tree_recursive(tag_tree, tag_structure_patterns)
            
            # Language patterns
            language = profile.get('language', 'unknown')
            language_patterns[language] += 1
            
            # Page count distribution
            page_count = profile.get('page_count', 0)
            page_count_distribution.append(page_count)
        
        return {
            'common_tag_structures': dict(tag_structure_patterns.most_common(20)),
            'language_distribution': dict(language_patterns),
            'page_count_stats': {
                'mean': sum(page_count_distribution) / len(page_count_distribution) if page_count_distribution else 0,
                'min': min(page_count_distribution) if page_count_distribution else 0,
                'max': max(page_count_distribution) if page_count_distribution else 0
            }
        }
    
    def _analyze_tag_tree_recursive(self, tag_node: Dict[str, Any], counter: Counter):
        """Recursively analyze tag tree structure."""
        tag_type = tag_node.get('tag_type', 'Unknown')
        role = tag_node.get('role', 'Unknown')
        
        # Count tag type and role combinations
        counter[f"{tag_type}:{role}"] += 1
        
        # Recurse into children
        children = tag_node.get('children', [])
        for child in children:
            self._analyze_tag_tree_recursive(child, counter)
    
    def _save_aggregated_patterns(self, patterns: Dict[str, Any]):
        """Save aggregated patterns to files for ML training."""
        try:
            # Save main aggregated patterns file
            main_file = self.patterns_dir / "aggregated_patterns.json"
            with open(main_file, 'w', encoding='utf-8') as f:
                json.dump(patterns, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved main patterns file: {main_file}")
            
            # Save individual pattern type files for focused training
            pattern_types = {
                'wcag_compliance': patterns.get('wcag_compliance_patterns', {}),
                'content_type_analysis': patterns.get('content_type_analysis', {}),
                'feature_statistics': patterns.get('feature_vector_statistics', {}),
                'structure_patterns': patterns.get('common_accessibility_structures', {})
            }
            
            for pattern_type, pattern_data in pattern_types.items():
                if pattern_data:
                    type_file = self.patterns_dir / f"{pattern_type}_patterns.json"
                    with open(type_file, 'w', encoding='utf-8') as f:
                        json.dump(pattern_data, f, indent=2, ensure_ascii=False)
                    logger.info(f"Saved {pattern_type} patterns: {type_file}")
            
            # Save training-ready datasets
            self._create_training_datasets(patterns)
            
        except Exception as e:
            logger.error(f"Failed to save aggregated patterns: {str(e)}")
    
    def _create_training_datasets(self, patterns: Dict[str, Any]):
        """Create ML-ready training datasets."""
        try:
            # Create WCAG compliance training data
            wcag_training = []
            for criterion, examples in patterns.get('wcag_compliance_patterns', {}).items():
                for example in examples:
                    wcag_training.append({
                        'wcag_criterion': criterion,
                        'content_type': example.get('content_type'),
                        'confidence_score': example.get('confidence_score'),
                        'semantic_roles': example.get('semantic_roles', []),
                        'characteristics': example.get('document_characteristics', {})
                    })
            
            if wcag_training:
                wcag_file = self.patterns_dir / "wcag_training_data.json"
                with open(wcag_file, 'w', encoding='utf-8') as f:
                    json.dump(wcag_training, f, indent=2, ensure_ascii=False)
                logger.info(f"Created WCAG training dataset: {wcag_file}")
            
            # Create feature vector training data
            feature_stats = patterns.get('feature_vector_statistics', {})
            if feature_stats:
                feature_file = self.patterns_dir / "feature_vector_stats.json"
                with open(feature_file, 'w', encoding='utf-8') as f:
                    json.dump(feature_stats, f, indent=2, ensure_ascii=False)
                logger.info(f"Created feature vector statistics: {feature_file}")
            
        except Exception as e:
            logger.error(f"Failed to create training datasets: {str(e)}")


def main():
    """Example usage of AccessibilityDataExtractor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract accessibility training data from PDF documents")
    parser.add_argument("input_dir", type=Path, help="Directory containing compliant PDF files")
    parser.add_argument("output_dir", type=Path, help="Directory to store extracted training data")
    parser.add_argument("--max-files", type=int, help="Maximum number of files to process")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize extractor
    extractor = AccessibilityDataExtractor(args.output_dir)
    
    # Extract profiles
    profiles = extractor.batch_extract_profiles(
        args.input_dir, 
        max_files=args.max_files
    )
    
    print(f"Successfully extracted {len(profiles)} accessibility profiles")
    print(f"Training data saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
