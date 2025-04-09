#!/usr/bin/env python3
"""
Accessibility validation rules module.

This module provides a rule-based approach to accessibility validation,
with composable rules and rule sets for different accessibility standards.
"""

import abc
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pikepdf

logger = logging.getLogger(__name__)


class ValidationRule(abc.ABC):
    """
    Abstract base class for accessibility validation rules.
    
    Rules are individual validation checks that can be composed into
    rule sets for comprehensive validation.
    """
    
    def __init__(self, name: str, description: str, weight: float = 1.0):
        """
        Initialize a validation rule.
        
        Args:
            name: Rule name
            description: Rule description
            weight: Rule weight for score calculation (default: 1.0)
        """
        self.name = name
        self.description = description
        self.weight = weight
    
    @abc.abstractmethod
    def validate(self, document: Any) -> Dict[str, Any]:
        """
        Validate a document against this rule.
        
        Args:
            document: The document to validate
            
        Returns:
            Dict[str, Any]: Validation result with the following keys:
                - passed: Whether the rule passed
                - score: Rule score (0-100)
                - message: Optional message about the validation
                - details: Optional details about the validation
        """
        pass


class PDFValidationRule(ValidationRule):
    """
    Base class for PDF-specific validation rules.
    
    This class provides common functionality for PDF validation rules.
    """
    
    def validate_pdf_file(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a PDF file against this rule.
        
        Args:
            pdf_path: Path to the PDF file to validate
            
        Returns:
            Dict[str, Any]: Validation result
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return {
                'passed': False,
                'score': 0,
                'message': f"File not found: {pdf_path}",
                'details': {}
            }
        
        try:
            with pikepdf.open(pdf_path) as pdf:
                return self.validate(pdf)
        except Exception as e:
            logger.error(f"Error validating PDF: {e}")
            return {
                'passed': False,
                'score': 0,
                'message': f"Error validating PDF: {e}",
                'details': {}
            }


class HasTitleRule(PDFValidationRule):
    """Rule that checks if a PDF document has a title."""
    
    def __init__(self, weight: float = 1.0):
        """
        Initialize the rule.
        
        Args:
            weight: Rule weight for score calculation (default: 1.0)
        """
        super().__init__(
            name="has_title",
            description="Checks if the document has a title",
            weight=weight
        )
    
    def validate(self, document: pikepdf.Pdf) -> Dict[str, Any]:
        """
        Validate a PDF document against this rule.
        
        Args:
            document: The PDF document to validate
            
        Returns:
            Dict[str, Any]: Validation result
        """
        with document.open_metadata() as meta:
            has_title = 'dc:title' in meta and meta['dc:title'].strip()
            
            if has_title:
                return {
                    'passed': True,
                    'score': 100,
                    'message': "Document has a title",
                    'details': {
                        'title': meta['dc:title']
                    }
                }
            else:
                return {
                    'passed': False,
                    'score': 0,
                    'message': "Document does not have a title",
                    'details': {}
                }


class HasLanguageRule(PDFValidationRule):
    """Rule that checks if a PDF document has a language specified."""
    
    def __init__(self, weight: float = 1.0):
        """
        Initialize the rule.
        
        Args:
            weight: Rule weight for score calculation (default: 1.0)
        """
        super().__init__(
            name="has_language",
            description="Checks if the document has a language specified",
            weight=weight
        )
    
    def validate(self, document: pikepdf.Pdf) -> Dict[str, Any]:
        """
        Validate a PDF document against this rule.
        
        Args:
            document: The PDF document to validate
            
        Returns:
            Dict[str, Any]: Validation result
        """
        with document.open_metadata() as meta:
            has_language = 'dc:language' in meta and meta['dc:language'].strip()
            
            if has_language:
                return {
                    'passed': True,
                    'score': 100,
                    'message': "Document has a language specified",
                    'details': {
                        'language': meta['dc:language']
                    }
                }
            else:
                return {
                    'passed': False,
                    'score': 0,
                    'message': "Document does not have a language specified",
                    'details': {}
                }


class DisplaysDocumentTitleRule(PDFValidationRule):
    """Rule that checks if a PDF document is set to display its title."""
    
    def __init__(self, weight: float = 0.5):
        """
        Initialize the rule.
        
        Args:
            weight: Rule weight for score calculation (default: 0.5)
        """
        super().__init__(
            name="displays_document_title",
            description="Checks if the document is set to display its title",
            weight=weight
        )
    
    def validate(self, document: pikepdf.Pdf) -> Dict[str, Any]:
        """
        Validate a PDF document against this rule.
        
        Args:
            document: The PDF document to validate
            
        Returns:
            Dict[str, Any]: Validation result
        """
        has_viewer_prefs = pikepdf.Name.ViewerPreferences in document.Root
        
        if has_viewer_prefs:
            display_title = (
                pikepdf.Name.DisplayDocTitle in document.Root.ViewerPreferences and
                document.Root.ViewerPreferences[pikepdf.Name.DisplayDocTitle]
            )
            
            if display_title:
                return {
                    'passed': True,
                    'score': 100,
                    'message': "Document is set to display its title",
                    'details': {}
                }
        
        return {
            'passed': False,
            'score': 0,
            'message': "Document is not set to display its title",
            'details': {}
        }


class IsTaggedRule(PDFValidationRule):
    """Rule that checks if a PDF document is tagged."""
    
    def __init__(self, weight: float = 2.0):
        """
        Initialize the rule.
        
        Args:
            weight: Rule weight for score calculation (default: 2.0)
        """
        super().__init__(
            name="is_tagged",
            description="Checks if the document is tagged",
            weight=weight
        )
    
    def validate(self, document: pikepdf.Pdf) -> Dict[str, Any]:
        """
        Validate a PDF document against this rule.
        
        Args:
            document: The PDF document to validate
            
        Returns:
            Dict[str, Any]: Validation result
        """
        is_tagged = (
            pikepdf.Name.MarkInfo in document.Root and
            pikepdf.Name.Marked in document.Root.MarkInfo and
            document.Root.MarkInfo[pikepdf.Name.Marked]
        )
        
        if is_tagged:
            return {
                'passed': True,
                'score': 100,
                'message': "Document is tagged",
                'details': {}
            }
        else:
            return {
                'passed': False,
                'score': 0,
                'message': "Document is not tagged",
                'details': {}
            }


class HasStructureTreeRule(PDFValidationRule):
    """Rule that checks if a PDF document has a structure tree."""
    
    def __init__(self, weight: float = 1.5):
        """
        Initialize the rule.
        
        Args:
            weight: Rule weight for score calculation (default: 1.5)
        """
        super().__init__(
            name="has_structure_tree",
            description="Checks if the document has a structure tree",
            weight=weight
        )
    
    def validate(self, document: pikepdf.Pdf) -> Dict[str, Any]:
        """
        Validate a PDF document against this rule.
        
        Args:
            document: The PDF document to validate
            
        Returns:
            Dict[str, Any]: Validation result
        """
        has_structure_tree = pikepdf.Name.StructTreeRoot in document.Root
        
        if has_structure_tree:
            return {
                'passed': True,
                'score': 100,
                'message': "Document has a structure tree",
                'details': {}
            }
        else:
            return {
                'passed': False,
                'score': 0,
                'message': "Document does not have a structure tree",
                'details': {}
            }


class HasPDFUAIdentifiersRule(PDFValidationRule):
    """Rule that checks if a PDF document has PDF/UA identifiers."""
    
    def __init__(self, weight: float = 1.0):
        """
        Initialize the rule.
        
        Args:
            weight: Rule weight for score calculation (default: 1.0)
        """
        super().__init__(
            name="has_pdfua_identifiers",
            description="Checks if the document has PDF/UA identifiers",
            weight=weight
        )
    
    def validate(self, document: pikepdf.Pdf) -> Dict[str, Any]:
        """
        Validate a PDF document against this rule.
        
        Args:
            document: The PDF document to validate
            
        Returns:
            Dict[str, Any]: Validation result
        """
        with document.open_metadata() as meta:
            has_part = 'pdfaid:part' in meta and meta['pdfaid:part'] == '1'
            has_conformance = 'pdfaid:conformance' in meta and meta['pdfaid:conformance'] == 'A'
            
            if has_part and has_conformance:
                return {
                    'passed': True,
                    'score': 100,
                    'message': "Document has PDF/UA identifiers",
                    'details': {
                        'part': meta.get('pdfaid:part', ''),
                        'conformance': meta.get('pdfaid:conformance', '')
                    }
                }
            elif has_part or has_conformance:
                return {
                    'passed': False,
                    'score': 50,
                    'message': "Document has incomplete PDF/UA identifiers",
                    'details': {
                        'part': meta.get('pdfaid:part', ''),
                        'conformance': meta.get('pdfaid:conformance', '')
                    }
                }
            else:
                return {
                    'passed': False,
                    'score': 0,
                    'message': "Document does not have PDF/UA identifiers",
                    'details': {}
                }


class ValidationRuleSet:
    """
    Collection of validation rules with weight calculation.
    
    Rule sets group related rules together for comprehensive validation
    against specific accessibility standards.
    """
    
    def __init__(self, name: str, description: str, rules: Optional[List[ValidationRule]] = None):
        """
        Initialize a validation rule set.
        
        Args:
            name: Rule set name
            description: Rule set description
            rules: List of validation rules (default: None)
        """
        self.name = name
        self.description = description
        self.rules = rules or []
    
    def add_rule(self, rule: ValidationRule) -> None:
        """
        Add a rule to the rule set.
        
        Args:
            rule: Validation rule to add
        """
        self.rules.append(rule)
    
    def validate(self, document: Any) -> Dict[str, Any]:
        """
        Validate a document against all rules in the rule set.
        
        Args:
            document: The document to validate
            
        Returns:
            Dict[str, Any]: Validation results for all rules and overall score
        """
        results = {}
        total_weight = 0
        weighted_score = 0
        
        for rule in self.rules:
            rule_result = rule.validate(document)
            results[rule.name] = rule_result
            
            total_weight += rule.weight
            weighted_score += rule_result['score'] * rule.weight
        
        if total_weight > 0:
            overall_score = int(weighted_score / total_weight)
        else:
            overall_score = 0
        
        return {
            'ruleset_name': self.name,
            'ruleset_description': self.description,
            'overall_score': overall_score,
            'passes': overall_score >= 80,
            'rule_results': results
        }
    
    def validate_pdf_file(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a PDF file against all rules in the rule set.
        
        Args:
            pdf_path: Path to the PDF file to validate
            
        Returns:
            Dict[str, Any]: Validation results for all rules and overall score
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return {
                'ruleset_name': self.name,
                'ruleset_description': self.description,
                'overall_score': 0,
                'passes': False,
                'error': f"File not found: {pdf_path}",
                'rule_results': {}
            }
        
        try:
            with pikepdf.open(pdf_path) as pdf:
                result = self.validate(pdf)
                result['filename'] = pdf_path.name
                result['path'] = str(pdf_path)
                result['filesize_bytes'] = pdf_path.stat().st_size
                result['page_count'] = len(pdf.pages)
                return result
        except Exception as e:
            logger.error(f"Error validating PDF: {e}")
            return {
                'ruleset_name': self.name,
                'ruleset_description': self.description,
                'overall_score': 0,
                'passes': False,
                'error': f"Error validating PDF: {e}",
                'rule_results': {},
                'filename': pdf_path.name,
                'path': str(pdf_path)
            }


# Create standard rule sets

def create_basic_pdf_ruleset() -> ValidationRuleSet:
    """
    Create a basic PDF accessibility validation rule set.
    
    This rule set includes checks for basic accessibility features
    such as title, language, and display title preference.
    
    Returns:
        ValidationRuleSet: Basic PDF accessibility validation rule set
    """
    ruleset = ValidationRuleSet(
        name="basic_pdf_accessibility",
        description="Basic PDF accessibility validation rules"
    )
    
    ruleset.add_rule(HasTitleRule(weight=1.0))
    ruleset.add_rule(HasLanguageRule(weight=1.0))
    ruleset.add_rule(DisplaysDocumentTitleRule(weight=0.5))
    
    return ruleset


def create_structure_pdf_ruleset() -> ValidationRuleSet:
    """
    Create a PDF structure validation rule set.
    
    This rule set includes checks for document structure features
    such as tagging and structure trees.
    
    Returns:
        ValidationRuleSet: PDF structure validation rule set
    """
    ruleset = ValidationRuleSet(
        name="pdf_structure",
        description="PDF structure validation rules"
    )
    
    ruleset.add_rule(IsTaggedRule(weight=2.0))
    ruleset.add_rule(HasStructureTreeRule(weight=1.5))
    
    return ruleset


def create_pdfua_ruleset() -> ValidationRuleSet:
    """
    Create a PDF/UA compliance validation rule set.
    
    This rule set includes checks for PDF/UA compliance features
    including all basic and structure rules plus PDF/UA identifiers.
    
    Returns:
        ValidationRuleSet: PDF/UA compliance validation rule set
    """
    ruleset = ValidationRuleSet(
        name="pdfua_compliance",
        description="PDF/UA compliance validation rules"
    )
    
    # Add basic rules
    ruleset.add_rule(HasTitleRule(weight=1.0))
    ruleset.add_rule(HasLanguageRule(weight=1.0))
    ruleset.add_rule(DisplaysDocumentTitleRule(weight=0.5))
    
    # Add structure rules
    ruleset.add_rule(IsTaggedRule(weight=2.0))
    ruleset.add_rule(HasStructureTreeRule(weight=1.5))
    
    # Add PDF/UA specific rules
    ruleset.add_rule(HasPDFUAIdentifiersRule(weight=1.0))
    
    return ruleset