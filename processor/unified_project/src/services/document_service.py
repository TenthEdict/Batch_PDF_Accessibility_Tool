#!/usr/bin/env python3
"""
Document service for business logic related to document processing.

This service encapsulates all business operations related to document
processing and coordinates between different components.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from ..core.interfaces import DocumentProcessor, OCRProcessor, Validator
from ..core.service_container import ServiceContainer
from .enhancement_service import EnhancementService
from .validation_service import ValidationService
from .metadata_service import MetadataService

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of document processing operation."""

    success: bool
    output_path: Optional[Path] = None
    validation_results: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


@dataclass
class ProcessingRequest:
    """Request for document processing."""

    input_path: Path
    output_path: Path
    mode: str = "accessibility"  # accessibility, academic, basic
    extract_title_from_h1: bool = True
    extract_title_from_filename: bool = True
    add_pdfua_identifiers: bool = False
    display_doc_title: bool = True
    title: Optional[str] = None
    author: Optional[str] = None
    language: str = "en-US"
    validate_output: bool = True
    generate_report: bool = False
    report_format: str = "json"


class DocumentService:
    """
    Service for coordinating document processing operations.

    This service provides high-level business operations for document
    processing, orchestrating between enhancement, validation, and
    metadata services.
    """

    def __init__(self, container: Optional[ServiceContainer] = None):
        """
        Initialize the document service.

        Args:
            container: Optional service container for dependency injection
        """
        self.container = container
        self.logger = logging.getLogger(__name__)

        # Initialize sub-services
        self.enhancement_service = EnhancementService(container)
        self.validation_service = ValidationService(container)
        self.metadata_service = MetadataService(container)

    def process_document(self, request: ProcessingRequest) -> ProcessingResult:
        """
        Process a document according to the processing request.

        Args:
            request: Document processing request

        Returns:
            ProcessingResult with success status and details
        """
        result = ProcessingResult(success=False)

        try:
            # Validate input
            if not self._validate_request(request, result):
                return result

            # Process document with enhancements
            enhancement_success = self.enhancement_service.enhance_document(
                input_path=request.input_path,
                output_path=request.output_path,
                mode=request.mode,
                title=request.title,
                author=request.author,
                language=request.language,
                extract_title_from_h1=request.extract_title_from_h1,
                extract_title_from_filename=request.extract_title_from_filename,
                add_pdfua_identifiers=request.add_pdfua_identifiers,
                display_doc_title=request.display_doc_title,
            )

            if not enhancement_success:
                result.errors.append("Document enhancement failed")
                return result

            result.output_path = request.output_path

            # Extract metadata from processed document
            try:
                result.metadata = self.metadata_service.extract_metadata(
                    request.output_path
                )
            except Exception as e:
                self.logger.warning(f"Failed to extract metadata: {e}")
                result.errors.append(f"Metadata extraction failed: {e}")

            # Validate output if requested
            if request.validate_output:
                try:
                    validation_results = self.validation_service.validate_document(
                        request.output_path
                    )
                    result.validation_results = validation_results

                    # Generate validation report if requested
                    if request.generate_report:
                        report_path = request.output_path.with_suffix(
                            f".validation.{request.report_format}"
                        )
                        self.validation_service.generate_report(
                            validation_results, report_path, request.report_format
                        )

                except Exception as e:
                    self.logger.warning(f"Validation failed: {e}")
                    result.errors.append(f"Validation failed: {e}")

            result.success = True
            self.logger.info(f"Successfully processed document: {request.output_path}")

        except Exception as e:
            self.logger.error(f"Error processing document {request.input_path}: {e}")
            result.errors.append(f"Processing error: {e}")

        return result

    def process_batch(
        self,
        input_directory: Path,
        output_directory: Path,
        mode: str = "accessibility",
        file_patterns: Optional[List[str]] = None,
        **kwargs,
    ) -> List[ProcessingResult]:
        """
        Process multiple documents in batch.

        Args:
            input_directory: Directory containing input documents
            output_directory: Directory for output documents
            mode: Processing mode
            file_patterns: File patterns to match (default: ['*.pdf'])
            **kwargs: Additional processing parameters

        Returns:
            List of processing results
        """
        if file_patterns is None:
            file_patterns = ["*.pdf"]

        results = []

        # Ensure output directory exists
        output_directory.mkdir(parents=True, exist_ok=True)

        # Find input files
        input_files = []
        for pattern in file_patterns:
            input_files.extend(input_directory.glob(pattern))

        self.logger.info(f"Found {len(input_files)} files to process")

        for input_file in input_files:
            output_file = output_directory / input_file.name

            request = ProcessingRequest(
                input_path=input_file, output_path=output_file, mode=mode, **kwargs
            )

            result = self.process_document(request)
            results.append(result)

            if result.success:
                self.logger.info(f"✓ Processed: {input_file.name}")
            else:
                self.logger.error(
                    f"✗ Failed: {input_file.name} - {'; '.join(result.errors)}"
                )

        return results

    def get_document_info(self, document_path: Path) -> Dict[str, Any]:
        """
        Get comprehensive information about a document.

        Args:
            document_path: Path to the document

        Returns:
            Dictionary with document information
        """
        info = {
            "path": str(document_path),
            "exists": document_path.exists(),
            "size": None,
            "metadata": None,
            "validation": None,
        }

        if not document_path.exists():
            return info

        # Basic file info
        info["size"] = document_path.stat().st_size

        # Metadata
        try:
            info["metadata"] = self.metadata_service.extract_metadata(document_path)
        except Exception as e:
            self.logger.warning(f"Failed to extract metadata from {document_path}: {e}")

        # Validation (if it's a processed document)
        try:
            info["validation"] = self.validation_service.validate_document(
                document_path
            )
        except Exception as e:
            self.logger.warning(f"Failed to validate {document_path}: {e}")

        return info

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported document formats.

        Returns:
            List of supported file extensions
        """
        # This could be dynamic based on registered processors
        return [".pdf", ".docx", ".txt"]

    def _validate_request(
        self, request: ProcessingRequest, result: ProcessingResult
    ) -> bool:
        """
        Validate a processing request.

        Args:
            request: Processing request to validate
            result: Result object to populate with errors

        Returns:
            True if request is valid, False otherwise
        """
        # Check input file exists
        if not request.input_path.exists():
            result.errors.append(f"Input file not found: {request.input_path}")
            return False

        # Check input file is readable
        if not request.input_path.is_file():
            result.errors.append(f"Input path is not a file: {request.input_path}")
            return False

        # Check output directory exists or can be created
        try:
            request.output_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            result.errors.append(f"Cannot create output directory: {e}")
            return False

        # Check supported format
        supported_formats = self.get_supported_formats()
        if request.input_path.suffix.lower() not in supported_formats:
            result.errors.append(
                f"Unsupported format {request.input_path.suffix}. "
                f"Supported: {', '.join(supported_formats)}"
            )
            return False

        return True
