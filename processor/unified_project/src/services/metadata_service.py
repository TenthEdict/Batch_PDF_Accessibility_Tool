#!/usr/bin/env python3
"""
Metadata service for business logic related to document metadata.

This service encapsulates all business operations related to document
metadata extraction, manipulation, and management.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.interfaces import MetadataEditor
from ..core.service_container import ServiceContainer

logger = logging.getLogger(__name__)


class MetadataService:
    """
    Service for coordinating document metadata operations.
    
    This service provides business logic for extracting, updating,
    and managing document metadata for accessibility enhancement.
    """
    
    def __init__(self, container: Optional[ServiceContainer] = None):
        """
        Initialize the metadata service.
        
        Args:
            container: Optional service container for dependency injection
        """
        self.container = container
        self.logger = logging.getLogger(__name__)
        
        # Metadata field definitions and validation rules
        self._metadata_fields = {
            'title': {
                'required': True,
                'type': str,
                'description': 'Document title',
                'max_length': 200
            },
            'author': {
                'required': False,
                'type': str,
                'description': 'Document author(s)',
                'max_length': 100
            },
            'language': {
                'required': True,
                'type': str,
                'description': 'Document language code (e.g., en-US)',
                'pattern': r'^[a-z]{2}(-[A-Z]{2})?$'
            },
            'subject': {
                'required': False,
                'type': str,
                'description': 'Document subject/topic',
                'max_length': 150
            },
            'keywords': {
                'required': False,
                'type': list,
                'description': 'Document keywords/tags',
                'max_items': 10
            },
            'creator': {
                'required': False,
                'type': str,
                'description': 'Software/tool that created the document',
                'max_length': 100
            },
            'producer': {
                'required': False,
                'type': str,
                'description': 'Software/tool that produced the final document',
                'max_length': 100
            },
            'creation_date': {
                'required': False,
                'type': str,
                'description': 'Document creation date (ISO format)',
                'pattern': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*$'
            },
            'modification_date': {
                'required': False,
                'type': str,
                'description': 'Document modification date (ISO format)',
                'pattern': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*$'
            }
        }
        
        # Common language codes
        self._language_codes = {
            'en': 'English',
            'en-US': 'English (United States)',
            'en-GB': 'English (United Kingdom)',
            'es': 'Spanish',
            'es-ES': 'Spanish (Spain)',
            'es-MX': 'Spanish (Mexico)',
            'fr': 'French',
            'fr-FR': 'French (France)',
            'fr-CA': 'French (Canada)',
            'de': 'German',
            'de-DE': 'German (Germany)',
            'it': 'Italian',
            'pt': 'Portuguese',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'ru': 'Russian'
        }
    
    def extract_metadata(self, document_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract metadata from a document.
        
        Args:
            document_path: Path to the document
            
        Returns:
            Dictionary containing extracted metadata
        """
        document_path = Path(document_path)
        
        result = {
            'file_path': str(document_path),
            'file_size': None,
            'metadata': {},
            'extracted_fields': [],
            'missing_fields': [],
            'errors': []
        }
        
        if not document_path.exists():
            result['errors'].append(f"Document not found: {document_path}")
            return result
        
        try:
            # Basic file information
            result['file_size'] = document_path.stat().st_size
            
            # Get metadata editor for this document type
            editor = self._get_metadata_editor(document_path)
            if not editor:
                result['errors'].append(f"No metadata editor available for {document_path.suffix}")
                return result
            
            # Extract metadata using the editor
            raw_metadata = editor.get_metadata(document_path)
            
            # Process and normalize metadata
            result['metadata'] = self._normalize_metadata(raw_metadata)
            
            # Check which fields were extracted
            for field in self._metadata_fields:
                if field in result['metadata'] and result['metadata'][field]:
                    result['extracted_fields'].append(field)
                else:
                    result['missing_fields'].append(field)
            
            self.logger.info(f"Extracted metadata from {document_path}: {len(result['extracted_fields'])} fields")
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata from {document_path}: {e}")
            result['errors'].append(f"Metadata extraction error: {e}")
        
        return result
    
    def update_metadata(self, 
                       document_path: Union[str, Path],
                       metadata: Dict[str, Any],
                       save_path: Optional[Union[str, Path]] = None) -> bool:
        """
        Update document metadata.
        
        Args:
            document_path: Path to the document to update
            metadata: Dictionary of metadata fields to update
            save_path: Optional path to save updated document
            
        Returns:
            True if update was successful, False otherwise
        """
        document_path = Path(document_path)
        
        try:
            # Validate metadata
            validation_result = self.validate_metadata(metadata)
            if not validation_result['valid']:
                self.logger.error(f"Invalid metadata: {validation_result['errors']}")
                return False
            
            # Get metadata editor
            editor = self._get_metadata_editor(document_path)
            if not editor:
                self.logger.error(f"No metadata editor available for {document_path.suffix}")
                return False
            
            # Normalize metadata before updating
            normalized_metadata = self._normalize_metadata(metadata)
            
            # Update metadata
            success = editor.update_metadata(document_path, normalized_metadata, save_path)
            
            if success:
                target_path = save_path or document_path
                self.logger.info(f"Successfully updated metadata for {target_path}")
            else:
                self.logger.error(f"Failed to update metadata for {document_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error updating metadata for {document_path}: {e}")
            return False
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate metadata against field definitions.
        
        Args:
            metadata: Metadata dictionary to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_required': []
        }
        
        # Check required fields
        for field, field_def in self._metadata_fields.items():
            if field_def.get('required', False):
                if field not in metadata or not metadata[field]:
                    result['missing_required'].append(field)
                    result['valid'] = False
        
        # Validate individual fields
        for field, value in metadata.items():
            if field not in self._metadata_fields:
                result['warnings'].append(f"Unknown metadata field: {field}")
                continue
            
            field_def = self._metadata_fields[field]
            
            # Type validation
            expected_type = field_def.get('type', str)
            if value is not None and not isinstance(value, expected_type):
                result['errors'].append(f"Field '{field}' should be {expected_type.__name__}, got {type(value).__name__}")
                result['valid'] = False
                continue
            
            # String length validation
            if isinstance(value, str) and 'max_length' in field_def:
                if len(value) > field_def['max_length']:
                    result['errors'].append(f"Field '{field}' exceeds maximum length of {field_def['max_length']}")
                    result['valid'] = False
            
            # List length validation
            if isinstance(value, list) and 'max_items' in field_def:
                if len(value) > field_def['max_items']:
                    result['errors'].append(f"Field '{field}' exceeds maximum of {field_def['max_items']} items")
                    result['valid'] = False
            
            # Pattern validation
            if isinstance(value, str) and 'pattern' in field_def:
                import re
                if not re.match(field_def['pattern'], value):
                    result['errors'].append(f"Field '{field}' does not match required pattern")
                    result['valid'] = False
        
        # Special validation for language codes
        if 'language' in metadata:
            lang = metadata['language']
            if lang and lang not in self._language_codes:
                result['warnings'].append(f"Language code '{lang}' not in common language list")
        
        return result
    
    def suggest_metadata(self, document_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Suggest metadata values based on document content and filename.
        
        Args:
            document_path: Path to the document
            
        Returns:
            Dictionary with suggested metadata values
        """
        document_path = Path(document_path)
        
        suggestions = {
            'title': None,
            'author': None,
            'language': 'en-US',  # Default
            'keywords': [],
            'creator': 'ePubs Accessibility Enhancement Project'
        }
        
        try:
            # Extract title from filename
            filename = document_path.stem
            # Clean up filename for title
            title_from_filename = filename.replace('_', ' ').replace('-', ' ')
            title_from_filename = ' '.join(word.capitalize() for word in title_from_filename.split())
            suggestions['title'] = title_from_filename
            
            # Try to extract metadata to get better suggestions
            current_metadata = self.extract_metadata(document_path)
            if not current_metadata.get('errors'):
                metadata = current_metadata.get('metadata', {})
                
                # Use existing metadata if available and non-empty
                for field in ['title', 'author', 'language', 'subject']:
                    if metadata.get(field):
                        suggestions[field] = metadata[field]
            
            # Generate keywords from title
            if suggestions['title']:
                # Simple keyword extraction from title
                words = suggestions['title'].lower().split()
                keywords = [word for word in words if len(word) > 3]
                suggestions['keywords'] = keywords[:5]  # Limit to 5 keywords
            
            self.logger.info(f"Generated metadata suggestions for {document_path}")
            
        except Exception as e:
            self.logger.warning(f"Error generating metadata suggestions for {document_path}: {e}")
        
        return suggestions
    
    def get_metadata_template(self, document_type: str = 'academic') -> Dict[str, Any]:
        """
        Get a metadata template for a specific document type.
        
        Args:
            document_type: Type of document (academic, general, web)
            
        Returns:
            Dictionary with template metadata
        """
        templates = {
            'academic': {
                'title': '',
                'author': '',
                'subject': '',
                'keywords': [],
                'language': 'en-US',
                'creator': 'Academic Publishing System',
                'producer': 'ePubs Accessibility Enhancement Project'
            },
            'general': {
                'title': '',
                'author': '',
                'language': 'en-US',
                'creator': 'ePubs Accessibility Enhancement Project'
            },
            'web': {
                'title': '',
                'author': '',
                'subject': '',
                'language': 'en-US',
                'keywords': [],
                'creator': 'Web Content Management System',
                'producer': 'ePubs Accessibility Enhancement Project'
            }
        }
        
        return templates.get(document_type, templates['general']).copy()
    
    def get_field_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata field definitions.
        
        Returns:
            Dictionary of field definitions
        """
        return self._metadata_fields.copy()
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get supported language codes and names.
        
        Returns:
            Dictionary mapping language codes to names
        """
        return self._language_codes.copy()
    
    def compare_metadata(self, 
                        metadata1: Dict[str, Any], 
                        metadata2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two metadata dictionaries.
        
        Args:
            metadata1: First metadata dictionary
            metadata2: Second metadata dictionary
            
        Returns:
            Dictionary with comparison results
        """
        result = {
            'identical': True,
            'differences': {},
            'missing_in_first': [],
            'missing_in_second': [],
            'field_differences': []
        }
        
        all_fields = set(metadata1.keys()) | set(metadata2.keys())
        
        for field in all_fields:
            value1 = metadata1.get(field)
            value2 = metadata2.get(field)
            
            if field not in metadata1:
                result['missing_in_first'].append(field)
                result['identical'] = False
            elif field not in metadata2:
                result['missing_in_second'].append(field)
                result['identical'] = False
            elif value1 != value2:
                result['differences'][field] = {
                    'first': value1,
                    'second': value2
                }
                result['field_differences'].append(field)
                result['identical'] = False
        
        return result
    
    def _get_metadata_editor(self, document_path: Path) -> Optional[MetadataEditor]:
        """
        Get appropriate metadata editor for document type.
        
        Args:
            document_path: Path to the document
            
        Returns:
            MetadataEditor instance or None
        """
        # Try to get editor from service container
        if self.container and self.container.has('metadata_editor'):
            return self.container.get('metadata_editor')
        
        # Fallback: create basic editor based on file type
        extension = document_path.suffix.lower()
        
        if extension == '.pdf':
            # Try to import and create PDF metadata editor
            try:
                from ..metadata.metadata_editor import MetadataEditorImpl
                return MetadataEditorImpl()
            except ImportError:
                self.logger.warning("PDF metadata editor not available")
                return None
        
        # Add more editor types as needed
        return None
    
    def _normalize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize metadata values to standard formats.
        
        Args:
            metadata: Raw metadata dictionary
            
        Returns:
            Normalized metadata dictionary
        """
        normalized = {}
        
        for field, value in metadata.items():
            if value is None or value == '':
                continue
            
            # Convert to string and strip whitespace for text fields
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    continue
            
            # Special handling for specific fields
            if field == 'keywords':
                if isinstance(value, str):
                    # Split string keywords
                    normalized[field] = [kw.strip() for kw in value.split(',') if kw.strip()]
                elif isinstance(value, list):
                    normalized[field] = [str(kw).strip() for kw in value if str(kw).strip()]
            elif field == 'language':
                # Normalize language code
                if isinstance(value, str):
                    lang = value.lower().replace('_', '-')
                    # Common normalizations
                    if lang == 'en':
                        lang = 'en-US'
                    elif lang == 'es':
                        lang = 'es-ES'
                    elif lang == 'fr':
                        lang = 'fr-FR'
                    normalized[field] = lang
            else:
                normalized[field] = value
        
        return normalized