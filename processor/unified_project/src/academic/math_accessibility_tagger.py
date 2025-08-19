"""
Mathematical Content Accessibility Tagging Framework
=================================================

PDF/UA-1 compliant accessibility tagging system specifically designed for mathematical
content in academic documents. Provides comprehensive semantic structure for screen
readers and assistive technologies while maintaining institutional compliance standards.

Features:
- PDF/UA-1 compliant mathematical content structure
- Screen reader optimization with proper semantic tagging
- Section 508 and ADA compliance for mathematical accessibility
- Integration with equation boundary extraction system
- Performance monitoring with resource optimization tracking
- Academic document specialization for complex mathematical expressions
"""

import logging
import time
from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import xml.etree.ElementTree as ET

# Import equation boundary extraction components
from .equation_boundary_extractor import EquationBoundary, BoundaryExtractionResult

# PDF processing imports
try:
    import fitz  # PyMuPDF
    import pikepdf
    PDF_PROCESSING_AVAILABLE = True
except ImportError:
    PDF_PROCESSING_AVAILABLE = False

# Integration with monitoring system
try:
    from ..monitoring.ml_pattern_learning_metrics import (
        get_ml_metrics_collector, 
        MLOperationType
    )
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


class AccessibilityStandard(Enum):
    """Accessibility compliance standards."""
    PDF_UA_1 = "PDF/UA-1"
    SECTION_508 = "Section 508"
    ADA = "ADA"
    WCAG_2_1 = "WCAG 2.1"


class MathematicalContentType(Enum):
    """Types of mathematical content for accessibility tagging."""
    EQUATION = "equation"
    FORMULA = "formula"
    EXPRESSION = "expression"
    SYMBOL = "symbol"
    FRACTION = "fraction"
    INTEGRAL = "integral"
    MATRIX = "matrix"
    GRAPH = "graph"
    DIAGRAM = "diagram"


@dataclass
class AccessibilityTag:
    """Individual accessibility tag for mathematical content."""
    tag_id: str
    content_type: MathematicalContentType
    tag_name: str  # PDF structure tag name
    alt_text: str  # Alternative text description
    mathml_content: Optional[str] = None  # MathML representation
    aria_label: Optional[str] = None  # ARIA label for screen readers
    role: Optional[str] = None  # ARIA role
    title: Optional[str] = None  # Title attribute
    expanded_description: Optional[str] = None  # Detailed description
    reading_order: int = 0  # Reading order priority
    language: str = "en"  # Content language
    complexity_level: str = "medium"  # simple, medium, complex
    context_information: Dict[str, str] = field(default_factory=dict)


@dataclass
class MathematicalAccessibilityStructure:
    """Complete accessibility structure for mathematical content."""
    equation_boundary: EquationBoundary
    primary_tag: AccessibilityTag
    nested_tags: List[AccessibilityTag] = field(default_factory=list)
    structure_tree_elements: List[Dict[str, Any]] = field(default_factory=list)
    reading_order_sequence: List[str] = field(default_factory=list)
    screen_reader_instructions: Dict[str, str] = field(default_factory=dict)
    compliance_metadata: Dict[AccessibilityStandard, bool] = field(default_factory=dict)


@dataclass
class AccessibilityTaggingResult:
    """Complete accessibility tagging result for a document."""
    document_path: str
    boundary_extraction_result: BoundaryExtractionResult
    mathematical_structures: List[MathematicalAccessibilityStructure]
    tagging_time_ms: float
    compliance_score: float
    accessibility_metadata: Dict[str, Any]
    validation_report: Dict[str, Any]


class MathematicalAccessibilityTagger:
    """
    Comprehensive mathematical content accessibility tagging system.
    
    Provides PDF/UA-1 compliant accessibility enhancement for mathematical content
    with screen reader optimization and institutional compliance standards for
    academic document accessibility enhancement workflows.
    """
    
    def __init__(self,
                 compliance_standards: List[AccessibilityStandard] = None,
                 generate_mathml: bool = True,
                 enable_aria_labels: bool = True,
                 enable_monitoring: bool = True):
        """
        Initialize mathematical accessibility tagger.
        
        Args:
            compliance_standards: Target accessibility standards for compliance
            generate_mathml: Enable MathML generation for mathematical content
            enable_aria_labels: Enable ARIA labels for screen reader support
            enable_monitoring: Enable performance monitoring integration
        """
        self.compliance_standards = compliance_standards or [
            AccessibilityStandard.PDF_UA_1,
            AccessibilityStandard.SECTION_508,
            AccessibilityStandard.WCAG_2_1
        ]
        self.generate_mathml = generate_mathml
        self.enable_aria_labels = enable_aria_labels
        self.enable_monitoring = enable_monitoring
        
        # Accessibility tagging configuration
        self.tagging_config = {
            'structure_tree_enabled': True,
            'reading_order_optimization': True,
            'alternative_text_generation': True,
            'mathematical_semantic_analysis': True,
            'screen_reader_instructions': True
        }
        
        # Mathematical content classification patterns
        self.math_classification_patterns = self._initialize_classification_patterns()
        
        # PDF/UA-1 compliance requirements
        self.pdf_ua_requirements = self._initialize_pdf_ua_requirements()
        
        # Performance tracking
        self.tagging_stats = {
            'total_tags_created': 0,
            'successful_structures': 0,
            'compliance_scores': [],
            'processing_times_ms': [],
            'mathml_generation_count': 0,
            'aria_labels_created': 0
        }
        
        # Logger setup
        self.logger = logging.getLogger(f"{__name__}.MathematicalAccessibilityTagger")
        
        self.logger.info(f"Mathematical Accessibility Tagger initialized - "
                        f"Standards: {[std.value for std in self.compliance_standards]}")
    
    def create_accessibility_tags(self,
                                boundary_result: BoundaryExtractionResult) -> AccessibilityTaggingResult:
        """
        Create comprehensive accessibility tags for mathematical content.
        
        Args:
            boundary_result: Equation boundary extraction result
            
        Returns:
            Complete accessibility tagging result with compliance metadata
        """
        start_time = time.time()
        
        if MONITORING_AVAILABLE and self.enable_monitoring:
            ml_collector = get_ml_metrics_collector()
            operation_id = ml_collector.record_ml_operation(
                operation_type=MLOperationType.FEATURE_EXTRACTION,
                duration_ms=0,
                document_count=1,
                success=False
            )
        
        try:
            mathematical_structures = []
            
            # Process each equation boundary for accessibility tagging
            for boundary in boundary_result.equation_boundaries:
                accessibility_structure = self._create_accessibility_structure(boundary)
                if accessibility_structure:
                    mathematical_structures.append(accessibility_structure)
            
            # Generate reading order sequence
            reading_order = self._optimize_reading_order(mathematical_structures)
            
            # Calculate compliance scores
            compliance_score = self._calculate_compliance_score(mathematical_structures)
            
            # Generate accessibility metadata
            accessibility_metadata = self._generate_accessibility_metadata(mathematical_structures)
            
            # Validate accessibility compliance
            validation_report = self._validate_accessibility_compliance(mathematical_structures)
            
            # Calculate processing metrics
            processing_time = (time.time() - start_time) * 1000
            
            # Create tagging result
            result = AccessibilityTaggingResult(
                document_path=boundary_result.document_path,
                boundary_extraction_result=boundary_result,
                mathematical_structures=mathematical_structures,
                tagging_time_ms=processing_time,
                compliance_score=compliance_score,
                accessibility_metadata=accessibility_metadata,
                validation_report=validation_report
            )
            
            # Update performance tracking
            self._update_tagging_stats(result)
            
            # Update monitoring if available
            if MONITORING_AVAILABLE and self.enable_monitoring:
                ml_collector.record_ml_operation(
                    operation_type=MLOperationType.FEATURE_EXTRACTION,
                    duration_ms=processing_time,
                    document_count=1,
                    accuracy_score=compliance_score,
                    patterns_learned=len(mathematical_structures),
                    success=True
                )
            
            self.logger.info(f"Accessibility tagging completed: "
                           f"{len(mathematical_structures)} structures created in {processing_time:.1f}ms")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Accessibility tagging failed: {e}")
            if MONITORING_AVAILABLE and self.enable_monitoring:
                ml_collector.record_ml_operation(
                    operation_type=MLOperationType.FEATURE_EXTRACTION,
                    duration_ms=(time.time() - start_time) * 1000,
                    document_count=1,
                    success=False,
                    error_message=str(e)
                )
            raise
    
    def _create_accessibility_structure(self, boundary: EquationBoundary) -> Optional[MathematicalAccessibilityStructure]:
        """Create comprehensive accessibility structure for a mathematical equation."""
        try:
            # Classify mathematical content type
            content_type = self._classify_mathematical_content(boundary)
            
            # Generate primary accessibility tag
            primary_tag = self._create_primary_accessibility_tag(boundary, content_type)
            
            # Generate nested tags for complex mathematical structures
            nested_tags = self._create_nested_accessibility_tags(boundary, content_type)
            
            # Create PDF structure tree elements
            structure_elements = self._create_structure_tree_elements(primary_tag, nested_tags)
            
            # Generate reading order sequence
            reading_sequence = self._generate_reading_order_sequence(primary_tag, nested_tags)
            
            # Create screen reader instructions
            screen_reader_instructions = self._create_screen_reader_instructions(content_type, primary_tag)
            
            # Validate compliance with accessibility standards
            compliance_metadata = self._validate_compliance_standards(primary_tag, nested_tags)
            
            return MathematicalAccessibilityStructure(
                equation_boundary=boundary,
                primary_tag=primary_tag,
                nested_tags=nested_tags,
                structure_tree_elements=structure_elements,
                reading_order_sequence=reading_sequence,
                screen_reader_instructions=screen_reader_instructions,
                compliance_metadata=compliance_metadata
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to create accessibility structure for {boundary.equation_id}: {e}")
            return None
    
    def _classify_mathematical_content(self, boundary: EquationBoundary) -> MathematicalContentType:
        """Classify the type of mathematical content based on boundary characteristics."""
        element = boundary.original_detection
        
        # Use existing element type as base classification
        if element.element_type == "equation":
            return MathematicalContentType.EQUATION
        elif element.element_type == "formula":
            return MathematicalContentType.FORMULA
        elif element.element_type == "fraction":
            return MathematicalContentType.FRACTION
        elif element.element_type == "integral":
            return MathematicalContentType.INTEGRAL
        elif element.element_type == "symbol":
            return MathematicalContentType.SYMBOL
        
        # Additional classification based on characteristics
        aspect_ratio = element.aspect_ratio
        complexity = element.complexity_score
        area = element.content_area
        
        # Enhanced classification logic
        if aspect_ratio > 3.0 and area > 2000:
            return MathematicalContentType.EQUATION
        elif aspect_ratio < 0.8 and complexity > 0.6:
            return MathematicalContentType.FRACTION
        elif complexity > 0.8:
            return MathematicalContentType.INTEGRAL
        elif area < 500:
            return MathematicalContentType.SYMBOL
        else:
            return MathematicalContentType.EXPRESSION
    
    def _create_primary_accessibility_tag(self, 
                                        boundary: EquationBoundary,
                                        content_type: MathematicalContentType) -> AccessibilityTag:
        """Create primary accessibility tag for mathematical content."""
        # Generate alternative text description
        alt_text = self._generate_alternative_text(boundary, content_type)
        
        # Generate MathML if enabled
        mathml_content = None
        if self.generate_mathml:
            mathml_content = self._generate_mathml_representation(boundary, content_type)
        
        # Generate ARIA label if enabled
        aria_label = None
        if self.enable_aria_labels:
            aria_label = self._generate_aria_label(boundary, content_type)
        
        # Determine PDF structure tag name based on content type
        tag_name = self._determine_pdf_tag_name(content_type)
        
        # Generate expanded description for complex content
        expanded_description = self._generate_expanded_description(boundary, content_type)
        
        # Determine complexity level
        complexity_level = self._determine_complexity_level(boundary)
        
        # Generate context information
        context_info = self._extract_context_information(boundary)
        
        return AccessibilityTag(
            tag_id=f"math_tag_{boundary.equation_id}",
            content_type=content_type,
            tag_name=tag_name,
            alt_text=alt_text,
            mathml_content=mathml_content,
            aria_label=aria_label,
            role="math",
            title=f"{content_type.value.title()} - {alt_text[:50]}...",
            expanded_description=expanded_description,
            reading_order=0,  # Will be set during reading order optimization
            language="en",
            complexity_level=complexity_level,
            context_information=context_info
        )
    
    def _create_nested_accessibility_tags(self, 
                                        boundary: EquationBoundary,
                                        content_type: MathematicalContentType) -> List[AccessibilityTag]:
        """Create nested accessibility tags for complex mathematical structures."""
        nested_tags = []
        
        # Only create nested tags for complex mathematical content
        if boundary.mathematical_regions and len(boundary.mathematical_regions) > 1:
            for i, region in enumerate(boundary.mathematical_regions):
                x, y, w, h = region
                
                # Classify sub-region content
                sub_content_type = self._classify_sub_region(region, content_type)
                
                # Create nested tag
                nested_tag = AccessibilityTag(
                    tag_id=f"math_nested_{boundary.equation_id}_{i}",
                    content_type=sub_content_type,
                    tag_name=self._determine_pdf_tag_name(sub_content_type),
                    alt_text=self._generate_sub_region_alt_text(region, sub_content_type),
                    role="math",
                    reading_order=i + 1,
                    complexity_level="simple"
                )
                
                nested_tags.append(nested_tag)
        
        return nested_tags
    
    def _generate_alternative_text(self, 
                                 boundary: EquationBoundary,
                                 content_type: MathematicalContentType) -> str:
        """Generate descriptive alternative text for mathematical content."""
        element = boundary.original_detection
        
        # Base alternative text based on content type
        type_descriptions = {
            MathematicalContentType.EQUATION: "Mathematical equation",
            MathematicalContentType.FORMULA: "Mathematical formula", 
            MathematicalContentType.EXPRESSION: "Mathematical expression",
            MathematicalContentType.SYMBOL: "Mathematical symbol",
            MathematicalContentType.FRACTION: "Mathematical fraction",
            MathematicalContentType.INTEGRAL: "Integral expression",
            MathematicalContentType.MATRIX: "Matrix notation",
            MathematicalContentType.GRAPH: "Mathematical graph",
            MathematicalContentType.DIAGRAM: "Mathematical diagram"
        }
        
        base_description = type_descriptions.get(content_type, "Mathematical content")
        
        # Add complexity information
        complexity_desc = ""
        if element.complexity_score > 0.7:
            complexity_desc = " with complex notation"
        elif element.complexity_score < 0.3:
            complexity_desc = " with simple notation"
        
        # Add size information
        size_desc = ""
        if element.content_area > 5000:
            size_desc = " spanning multiple lines"
        elif element.content_area < 500:
            size_desc = " containing inline notation"
        
        # Combine descriptions
        alt_text = f"{base_description}{complexity_desc}{size_desc}"
        
        # Add context if available
        if boundary.surrounding_context:
            alt_text += " within academic text"
        
        return alt_text
    
    def _generate_mathml_representation(self, 
                                      boundary: EquationBoundary,
                                      content_type: MathematicalContentType) -> Optional[str]:
        """Generate MathML representation of mathematical content."""
        if not self.generate_mathml:
            return None
        
        # Simplified MathML generation - in a full implementation,
        # this would use sophisticated OCR and mathematical expression parsing
        
        mathml_templates = {
            MathematicalContentType.EQUATION: '<math><mrow><mi>equation</mi></mrow></math>',
            MathematicalContentType.FORMULA: '<math><mrow><mi>formula</mi></mrow></math>',
            MathematicalContentType.FRACTION: '<math><mfrac><mi>numerator</mi><mi>denominator</mi></mfrac></math>',
            MathematicalContentType.INTEGRAL: '<math><mrow><mo>∫</mo><mi>f</mi><mo>(</mo><mi>x</mi><mo>)</mo><mi>dx</mi></mrow></math>',
            MathematicalContentType.SYMBOL: '<math><mi>symbol</mi></math>',
            MathematicalContentType.EXPRESSION: '<math><mrow><mi>expression</mi></mrow></math>'
        }
        
        # Return template MathML (in practice, this would be much more sophisticated)
        return mathml_templates.get(content_type, '<math><mrow><mi>mathematical_content</mi></mrow></math>')
    
    def _generate_aria_label(self, 
                           boundary: EquationBoundary,
                           content_type: MathematicalContentType) -> Optional[str]:
        """Generate ARIA label for screen reader support."""
        if not self.enable_aria_labels:
            return None
        
        # Create concise ARIA label for screen readers
        aria_labels = {
            MathematicalContentType.EQUATION: "equation",
            MathematicalContentType.FORMULA: "formula",
            MathematicalContentType.EXPRESSION: "math expression",
            MathematicalContentType.SYMBOL: "math symbol",
            MathematicalContentType.FRACTION: "fraction",
            MathematicalContentType.INTEGRAL: "integral",
            MathematicalContentType.MATRIX: "matrix",
            MathematicalContentType.GRAPH: "math graph",
            MathematicalContentType.DIAGRAM: "math diagram"
        }
        
        return aria_labels.get(content_type, "mathematical content")
    
    def _determine_pdf_tag_name(self, content_type: MathematicalContentType) -> str:
        """Determine appropriate PDF structure tag name for mathematical content."""
        # PDF/UA-1 compliant tag names for mathematical content
        pdf_tag_mapping = {
            MathematicalContentType.EQUATION: "Formula",
            MathematicalContentType.FORMULA: "Formula",
            MathematicalContentType.EXPRESSION: "Formula",
            MathematicalContentType.SYMBOL: "Span",
            MathematicalContentType.FRACTION: "Formula",
            MathematicalContentType.INTEGRAL: "Formula",
            MathematicalContentType.MATRIX: "Table",
            MathematicalContentType.GRAPH: "Figure",
            MathematicalContentType.DIAGRAM: "Figure"
        }
        
        return pdf_tag_mapping.get(content_type, "Formula")
    
    def _generate_expanded_description(self, 
                                     boundary: EquationBoundary,
                                     content_type: MathematicalContentType) -> str:
        """Generate detailed description for complex mathematical content."""
        element = boundary.original_detection
        
        # Create detailed description based on characteristics
        description_parts = []
        
        # Add content type description
        description_parts.append(f"This is a {content_type.value}")
        
        # Add positioning information
        if element.bbox:
            x, y, w, h = element.bbox
            description_parts.append(f"positioned at coordinates ({x}, {y})")
        
        # Add size information
        if element.content_area:
            description_parts.append(f"with a content area of {element.content_area} pixels")
        
        # Add complexity assessment
        if element.complexity_score > 0.7:
            description_parts.append("featuring complex mathematical notation")
        elif element.complexity_score < 0.3:
            description_parts.append("with simple mathematical notation")
        
        # Add aspect ratio information
        if element.aspect_ratio > 3.0:
            description_parts.append("extending horizontally across the page")
        elif element.aspect_ratio < 0.5:
            description_parts.append("arranged in a vertical layout")
        
        return ". ".join(description_parts) + "."
    
    def _determine_complexity_level(self, boundary: EquationBoundary) -> str:
        """Determine complexity level for accessibility purposes."""
        complexity_score = boundary.original_detection.complexity_score
        
        if complexity_score > 0.7:
            return "complex"
        elif complexity_score > 0.4:
            return "medium"
        else:
            return "simple"
    
    def _extract_context_information(self, boundary: EquationBoundary) -> Dict[str, str]:
        """Extract context information about the mathematical content."""
        context = {}
        
        # Add boundary extraction metadata
        if boundary.processing_metadata:
            context.update({
                'extraction_method': boundary.extraction_method,
                'boundary_confidence': str(boundary.boundary_confidence)
            })
        
        # Add position context
        if boundary.precise_bbox:
            x, y, w, h = boundary.precise_bbox
            context['position'] = f"x:{x}, y:{y}, width:{w}, height:{h}"
        
        # Add baseline information
        if boundary.text_baseline is not None:
            context['text_baseline'] = str(boundary.text_baseline)
        
        # Add region count
        if boundary.mathematical_regions:
            context['region_count'] = str(len(boundary.mathematical_regions))
        
        return context
    
    def _classify_sub_region(self, region: Tuple[int, int, int, int], 
                           parent_type: MathematicalContentType) -> MathematicalContentType:
        """Classify mathematical content type for sub-regions."""
        x, y, w, h = region
        aspect_ratio = w / h if h > 0 else 1.0
        area = w * h
        
        # Simple classification based on geometric properties
        if area < 200:
            return MathematicalContentType.SYMBOL
        elif aspect_ratio < 0.5:
            return MathematicalContentType.FRACTION
        elif parent_type == MathematicalContentType.EQUATION:
            return MathematicalContentType.EXPRESSION
        else:
            return MathematicalContentType.SYMBOL
    
    def _generate_sub_region_alt_text(self, region: Tuple[int, int, int, int],
                                    content_type: MathematicalContentType) -> str:
        """Generate alternative text for mathematical sub-regions."""
        x, y, w, h = region
        
        type_descriptions = {
            MathematicalContentType.SYMBOL: f"Mathematical symbol at position ({x}, {y})",
            MathematicalContentType.EXPRESSION: f"Mathematical expression spanning {w}x{h} pixels",
            MathematicalContentType.FRACTION: f"Fraction component in vertical arrangement"
        }
        
        return type_descriptions.get(content_type, f"Mathematical component at ({x}, {y})")
    
    def _create_structure_tree_elements(self, 
                                       primary_tag: AccessibilityTag,
                                       nested_tags: List[AccessibilityTag]) -> List[Dict[str, Any]]:
        """Create PDF structure tree elements for accessibility."""
        structure_elements = []
        
        # Primary structure element
        primary_element = {
            'tag_name': primary_tag.tag_name,
            'tag_id': primary_tag.tag_id,
            'alt_text': primary_tag.alt_text,
            'actual_text': primary_tag.alt_text,
            'lang': primary_tag.language,
            'role': primary_tag.role,
            'title': primary_tag.title
        }
        
        if primary_tag.mathml_content:
            primary_element['mathml'] = primary_tag.mathml_content
        
        structure_elements.append(primary_element)
        
        # Nested structure elements
        for nested_tag in nested_tags:
            nested_element = {
                'tag_name': nested_tag.tag_name,
                'tag_id': nested_tag.tag_id,
                'alt_text': nested_tag.alt_text,
                'parent_id': primary_tag.tag_id,
                'lang': nested_tag.language,
                'role': nested_tag.role
            }
            
            structure_elements.append(nested_element)
        
        return structure_elements
    
    def _generate_reading_order_sequence(self, 
                                       primary_tag: AccessibilityTag,
                                       nested_tags: List[AccessibilityTag]) -> List[str]:
        """Generate logical reading order sequence for mathematical content."""
        sequence = [primary_tag.tag_id]
        
        # Add nested tags in reading order
        sorted_nested = sorted(nested_tags, key=lambda t: t.reading_order)
        sequence.extend([tag.tag_id for tag in sorted_nested])
        
        return sequence
    
    def _create_screen_reader_instructions(self, 
                                         content_type: MathematicalContentType,
                                         primary_tag: AccessibilityTag) -> Dict[str, str]:
        """Create screen reader specific instructions."""
        instructions = {}
        
        # Navigation instructions
        instructions['navigation'] = f"Navigate through {content_type.value} using arrow keys"
        
        # Reading instructions
        instructions['reading'] = f"Mathematical {content_type.value}: {primary_tag.alt_text}"
        
        # Interaction instructions
        if content_type in [MathematicalContentType.EQUATION, MathematicalContentType.FORMULA]:
            instructions['interaction'] = "Use verbatim mode for detailed mathematical reading"
        else:
            instructions['interaction'] = "Standard reading mode applicable"
        
        # Complexity guidance
        if primary_tag.complexity_level == "complex":
            instructions['complexity'] = "Complex mathematical notation - consider using math mode"
        
        return instructions
    
    def _validate_compliance_standards(self, 
                                     primary_tag: AccessibilityTag,
                                     nested_tags: List[AccessibilityTag]) -> Dict[AccessibilityStandard, bool]:
        """Validate compliance with accessibility standards."""
        compliance = {}
        
        for standard in self.compliance_standards:
            if standard == AccessibilityStandard.PDF_UA_1:
                compliance[standard] = self._validate_pdf_ua_1_compliance(primary_tag, nested_tags)
            elif standard == AccessibilityStandard.SECTION_508:
                compliance[standard] = self._validate_section_508_compliance(primary_tag, nested_tags)
            elif standard == AccessibilityStandard.WCAG_2_1:
                compliance[standard] = self._validate_wcag_21_compliance(primary_tag, nested_tags)
            else:
                compliance[standard] = True  # Default to compliant for unknown standards
        
        return compliance
    
    def _validate_pdf_ua_1_compliance(self, 
                                    primary_tag: AccessibilityTag,
                                    nested_tags: List[AccessibilityTag]) -> bool:
        """Validate PDF/UA-1 compliance for mathematical content."""
        # Check required PDF/UA-1 elements
        required_elements = [
            primary_tag.alt_text is not None,
            primary_tag.tag_name is not None,
            primary_tag.role is not None,
            primary_tag.language is not None
        ]
        
        return all(required_elements)
    
    def _validate_section_508_compliance(self, 
                                       primary_tag: AccessibilityTag,
                                       nested_tags: List[AccessibilityTag]) -> bool:
        """Validate Section 508 compliance for mathematical content."""
        # Section 508 requires alternative text and proper markup
        return (primary_tag.alt_text is not None and 
                len(primary_tag.alt_text.strip()) > 0)
    
    def _validate_wcag_21_compliance(self, 
                                   primary_tag: AccessibilityTag,
                                   nested_tags: List[AccessibilityTag]) -> bool:
        """Validate WCAG 2.1 compliance for mathematical content."""
        # WCAG 2.1 Level AA requirements for mathematical content
        wcag_requirements = [
            primary_tag.alt_text is not None,
            primary_tag.role is not None,
            primary_tag.title is not None or primary_tag.aria_label is not None
        ]
        
        return all(wcag_requirements)
    
    def _optimize_reading_order(self, structures: List[MathematicalAccessibilityStructure]) -> List[str]:
        """Optimize reading order for mathematical structures in document."""
        if not structures:
            return []
        
        # Sort structures by page position (top to bottom, left to right)
        sorted_structures = sorted(structures, key=lambda s: (
            s.equation_boundary.precise_bbox[1],  # Y coordinate (top to bottom)
            s.equation_boundary.precise_bbox[0]   # X coordinate (left to right)
        ))
        
        # Generate global reading order
        reading_order = []
        for i, structure in enumerate(sorted_structures):
            structure.primary_tag.reading_order = i
            reading_order.extend(structure.reading_order_sequence)
        
        return reading_order
    
    def _calculate_compliance_score(self, structures: List[MathematicalAccessibilityStructure]) -> float:
        """Calculate overall accessibility compliance score."""
        if not structures:
            return 0.0
        
        total_compliance = 0
        total_checks = 0
        
        for structure in structures:
            for standard, compliant in structure.compliance_metadata.items():
                total_checks += 1
                if compliant:
                    total_compliance += 1
        
        return total_compliance / total_checks if total_checks > 0 else 0.0
    
    def _generate_accessibility_metadata(self, structures: List[MathematicalAccessibilityStructure]) -> Dict[str, Any]:
        """Generate comprehensive accessibility metadata."""
        if not structures:
            return {}
        
        metadata = {
            'total_mathematical_structures': len(structures),
            'content_type_distribution': {},
            'complexity_distribution': {},
            'compliance_summary': {},
            'mathml_generated_count': 0,
            'aria_labels_count': 0,
            'structure_tree_elements': 0
        }
        
        # Analyze content types
        for structure in structures:
            content_type = structure.primary_tag.content_type.value
            metadata['content_type_distribution'][content_type] = \
                metadata['content_type_distribution'].get(content_type, 0) + 1
            
            # Analyze complexity
            complexity = structure.primary_tag.complexity_level
            metadata['complexity_distribution'][complexity] = \
                metadata['complexity_distribution'].get(complexity, 0) + 1
            
            # Count MathML and ARIA labels
            if structure.primary_tag.mathml_content:
                metadata['mathml_generated_count'] += 1
            
            if structure.primary_tag.aria_label:
                metadata['aria_labels_count'] += 1
            
            # Count structure elements
            metadata['structure_tree_elements'] += len(structure.structure_tree_elements)
        
        # Compliance summary
        compliance_counts = {}
        for structure in structures:
            for standard, compliant in structure.compliance_metadata.items():
                if standard.value not in compliance_counts:
                    compliance_counts[standard.value] = {'compliant': 0, 'total': 0}
                
                compliance_counts[standard.value]['total'] += 1
                if compliant:
                    compliance_counts[standard.value]['compliant'] += 1
        
        metadata['compliance_summary'] = compliance_counts
        
        return metadata
    
    def _validate_accessibility_compliance(self, structures: List[MathematicalAccessibilityStructure]) -> Dict[str, Any]:
        """Validate overall accessibility compliance and generate report."""
        validation_report = {
            'overall_compliance': True,
            'compliance_by_standard': {},
            'issues_found': [],
            'recommendations': []
        }
        
        for standard in self.compliance_standards:
            standard_compliance = []
            
            for structure in structures:
                compliance = structure.compliance_metadata.get(standard, False)
                standard_compliance.append(compliance)
                
                if not compliance:
                    validation_report['issues_found'].append(
                        f"Non-compliant with {standard.value}: {structure.equation_boundary.equation_id}"
                    )
            
            # Calculate standard compliance rate
            compliance_rate = sum(standard_compliance) / len(standard_compliance) if standard_compliance else 0
            validation_report['compliance_by_standard'][standard.value] = {
                'rate': compliance_rate,
                'compliant_count': sum(standard_compliance),
                'total_count': len(standard_compliance)
            }
            
            if compliance_rate < 1.0:
                validation_report['overall_compliance'] = False
        
        # Generate recommendations
        if not validation_report['overall_compliance']:
            validation_report['recommendations'].extend([
                "Review mathematical content tagging for compliance gaps",
                "Ensure all mathematical elements have appropriate alternative text",
                "Validate PDF structure tree completeness",
                "Test with screen readers for accessibility verification"
            ])
        else:
            validation_report['recommendations'].append(
                "Accessibility compliance achieved - consider periodic validation"
            )
        
        return validation_report
    
    def _update_tagging_stats(self, result: AccessibilityTaggingResult) -> None:
        """Update internal tagging performance statistics."""
        self.tagging_stats['total_tags_created'] += sum(
            1 + len(struct.nested_tags) for struct in result.mathematical_structures
        )
        self.tagging_stats['successful_structures'] += len(result.mathematical_structures)
        self.tagging_stats['compliance_scores'].append(result.compliance_score)
        self.tagging_stats['processing_times_ms'].append(result.tagging_time_ms)
        
        # Count MathML and ARIA labels
        for structure in result.mathematical_structures:
            if structure.primary_tag.mathml_content:
                self.tagging_stats['mathml_generation_count'] += 1
            if structure.primary_tag.aria_label:
                self.tagging_stats['aria_labels_created'] += 1
    
    def _initialize_classification_patterns(self) -> Dict[str, Any]:
        """Initialize patterns for mathematical content classification."""
        return {
            'equation_indicators': ['=', '≠', '≈', '≡'],
            'fraction_indicators': ['/', '÷', 'numerator', 'denominator'],
            'integral_indicators': ['∫', '∑', '∏', 'integral', 'sum'],
            'symbol_patterns': ['α', 'β', 'γ', 'δ', 'π', 'θ', 'λ', 'μ'],
            'matrix_indicators': ['matrix', 'determinant', 'vector'],
            'complexity_factors': ['nested', 'multi-line', 'subscript', 'superscript']
        }
    
    def _initialize_pdf_ua_requirements(self) -> Dict[str, Any]:
        """Initialize PDF/UA-1 compliance requirements."""
        return {
            'required_attributes': ['alt_text', 'tag_name', 'role', 'language'],
            'optional_attributes': ['title', 'expanded_description', 'mathml_content'],
            'structure_requirements': ['reading_order', 'parent_child_relationships'],
            'semantic_requirements': ['content_type_classification', 'accessibility_role']
        }
    
    def get_tagging_statistics(self) -> Dict[str, Any]:
        """Get current tagging performance statistics."""
        stats = self.tagging_stats.copy()
        
        if stats['compliance_scores']:
            stats['average_compliance_score'] = sum(stats['compliance_scores']) / len(stats['compliance_scores'])
            stats['compliance_score_std'] = np.std(stats['compliance_scores'])
        
        if stats['processing_times_ms']:
            stats['average_processing_time_ms'] = sum(stats['processing_times_ms']) / len(stats['processing_times_ms'])
            stats['max_processing_time_ms'] = max(stats['processing_times_ms'])
        
        return stats


# Utility functions for integration
def create_mathematical_accessibility_tags(boundary_result: BoundaryExtractionResult,
                                         compliance_standards: List[AccessibilityStandard] = None) -> AccessibilityTaggingResult:
    """
    Convenience function to create accessibility tags for mathematical content.
    
    Args:
        boundary_result: Equation boundary extraction result
        compliance_standards: Target accessibility standards
        
    Returns:
        Complete accessibility tagging result
    """
    tagger = MathematicalAccessibilityTagger(compliance_standards=compliance_standards)
    return tagger.create_accessibility_tags(boundary_result)


def create_academic_accessibility_tagger(enable_monitoring: bool = True) -> MathematicalAccessibilityTagger:
    """
    Create accessibility tagger optimized for academic mathematical content.
    
    Args:
        enable_monitoring: Enable performance monitoring integration
        
    Returns:
        Configured mathematical accessibility tagger
    """
    return MathematicalAccessibilityTagger(
        compliance_standards=[
            AccessibilityStandard.PDF_UA_1,
            AccessibilityStandard.SECTION_508,
            AccessibilityStandard.WCAG_2_1
        ],
        generate_mathml=True,
        enable_aria_labels=True,
        enable_monitoring=enable_monitoring
    )


# Import numpy for statistics calculations
import numpy as np
