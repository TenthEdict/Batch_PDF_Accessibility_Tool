#!/usr/bin/env python3
"""
Core interfaces for the ePubs Accessibility Project.

This module defines the abstract base classes that establish the contract
between different components of the system. Following the principles of
clean architecture, these interfaces enable loose coupling and facilitate
unit testing through dependency injection.
"""

import abc
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class DocumentProcessor(abc.ABC):
    """
    Abstract base class for document processors.

    Document processors are responsible for transforming input documents
    into more accessible versions through a series of operations.
    """

    @abc.abstractmethod
    def process(
        self, input_path: Union[str, Path], output_path: Union[str, Path], **kwargs
    ) -> bool:
        """
        Process a document to enhance its accessibility.

        Args:
            input_path: Path to the input document
            output_path: Path where the processed document should be saved
            **kwargs: Additional processor-specific parameters

        Returns:
            bool: True if processing was successful, False otherwise
        """
        pass


class Enhancer(abc.ABC):
    """
    Abstract base class for document enhancers.

    Enhancers apply specific accessibility improvements to documents,
    such as adding metadata, structure, or tags.
    """

    @abc.abstractmethod
    def enhance(self, document: Any, **kwargs) -> Any:
        """
        Enhance a document with accessibility features.

        Args:
            document: The document to enhance
            **kwargs: Additional enhancer-specific parameters

        Returns:
            Any: The enhanced document
        """
        pass

    @abc.abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get the list of enhancement capabilities provided by this enhancer.

        Returns:
            List[str]: List of capability identifiers
        """
        pass


class Validator(abc.ABC):
    """
    Abstract base class for accessibility validators.

    Validators assess documents against accessibility standards and
    provide feedback on compliance issues.
    """

    @abc.abstractmethod
    def validate(self, document_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a document against accessibility standards.

        Args:
            document_path: Path to the document to validate

        Returns:
            Dict[str, Any]: Validation results with scores and issues
        """
        pass

    @abc.abstractmethod
    def generate_report(
        self,
        results: Dict[str, Any],
        output_path: Union[str, Path],
        format: str = "json",
    ) -> bool:
        """
        Generate a report from validation results.

        Args:
            results: Validation results to include in the report
            output_path: Path where the report should be saved
            format: Report format (e.g., 'json', 'csv', 'html')

        Returns:
            bool: True if report generation was successful, False otherwise
        """
        pass


class OCRProcessor(abc.ABC):
    """
    Abstract base class for OCR processors.

    OCR processors extract text from images or image-based PDFs to
    make them more accessible.
    """

    @abc.abstractmethod
    def process_document(
        self, input_path: Union[str, Path], output_path: Union[str, Path], **kwargs
    ) -> bool:
        """
        Process a document with OCR.

        Args:
            input_path: Path to the input document
            output_path: Path where the OCR'd document should be saved
            **kwargs: Additional OCR-specific parameters

        Returns:
            bool: True if OCR processing was successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def supports_document_type(self, document_path: Union[str, Path]) -> bool:
        """
        Check if this processor supports the given document type.

        Args:
            document_path: Path to the document to check

        Returns:
            bool: True if the document type is supported, False otherwise
        """
        pass


class MetadataEditor(abc.ABC):
    """
    Abstract base class for document metadata editors.

    Metadata editors modify document metadata to improve accessibility
    and compliance with standards.
    """

    @abc.abstractmethod
    def update_metadata(
        self,
        document_path: Union[str, Path],
        metadata: Dict[str, Any],
        save_path: Optional[Union[str, Path]] = None,
    ) -> bool:
        """
        Update document metadata.

        Args:
            document_path: Path to the document to update
            metadata: Dictionary of metadata fields to update
            save_path: Path where the updated document should be saved
                       (if None, the original document will be modified)

        Returns:
            bool: True if metadata update was successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_metadata(self, document_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get document metadata.

        Args:
            document_path: Path to the document

        Returns:
            Dict[str, Any]: Document metadata
        """
        pass


class ConfigurationProvider(abc.ABC):
    """
    Abstract base class for configuration providers.

    Configuration providers supply component-specific settings and
    enable environment-specific configuration.
    """

    @abc.abstractmethod
    def get_config(
        self, component: str, environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get configuration for a specific component.

        Args:
            component: Component identifier
            environment: Optional environment name

        Returns:
            Dict[str, Any]: Configuration settings
        """
        pass

    @abc.abstractmethod
    def set_config(
        self,
        component: str,
        settings: Dict[str, Any],
        environment: Optional[str] = None,
    ) -> bool:
        """
        Set configuration for a specific component.

        Args:
            component: Component identifier
            settings: Configuration settings to set
            environment: Optional environment name

        Returns:
            bool: True if configuration was set successfully, False otherwise
        """
        pass
