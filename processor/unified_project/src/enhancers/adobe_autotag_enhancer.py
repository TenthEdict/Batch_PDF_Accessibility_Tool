#!/usr/bin/env python3
"""
Adobe PDF Services AutoTag enhancer module.

This module provides cloud-based PDF accessibility enhancement using
Adobe's PDF Services SDK for advanced document structure tagging.
"""

import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
    from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
    from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
    from adobe.pdfservices.operation.io.stream_asset import StreamAsset
    from adobe.pdfservices.operation.pdf_services import PDFServices
    from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
    from adobe.pdfservices.operation.pdfjobs.jobs.autotag_pdf_job import AutotagPDFJob
    from adobe.pdfservices.operation.pdfjobs.params.autotag_pdf.autotag_pdf_params import AutotagPDFParams
    from adobe.pdfservices.operation.pdfjobs.result.autotag_pdf_result import AutotagPDFResult
    ADOBE_SDK_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Adobe PDF Services SDK not available: {e}")
    ADOBE_SDK_AVAILABLE = False

from .enhancer_base import EnhancerBase

logger = logging.getLogger(__name__)


class AdobeAutotagEnhancer(EnhancerBase):
    """
    Adobe PDF Services AutoTag implementation of the Enhancer interface.
    
    This class provides cloud-based PDF accessibility enhancement using Adobe's
    advanced AI-powered document structure recognition and tagging capabilities.
    """

    def __init__(self, environment: Optional[str] = None):
        """
        Initialize the Adobe AutoTag enhancer.
        
        Args:
            environment: Optional environment name for configuration
        """
        super().__init__("adobe_autotag", environment)
        
        # Validate Adobe SDK availability
        if not ADOBE_SDK_AVAILABLE:
            logger.error("Adobe PDF Services SDK is not available. Please install with: pip install pdfservices-sdk")
            raise ImportError("Adobe PDF Services SDK is required for AdobeAutotagEnhancer")
        
        # Initialize credentials
        self._credentials = None
        self._pdf_services = None
        self._initialize_credentials()

    def _initialize_credentials(self):
        """
        Initialize Adobe PDF Services credentials from environment variables.
        """
        client_id = os.getenv('PDF_SERVICES_CLIENT_ID')
        client_secret = os.getenv('PDF_SERVICES_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.warning(
                "Adobe PDF Services credentials not found in environment variables. "
                "Set PDF_SERVICES_CLIENT_ID and PDF_SERVICES_CLIENT_SECRET to enable cloud processing."
            )
            return
        
        try:
            self._credentials = ServicePrincipalCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            self._pdf_services = PDFServices(credentials=self._credentials)
            logger.info("Adobe PDF Services credentials initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Adobe PDF Services credentials: {e}")

    def _load_document(self, input_path: Path) -> bytes:
        """
        Load a PDF document from a file as bytes for cloud processing.
        
        Args:
            input_path: Path to the input PDF document
            
        Returns:
            bytes: The PDF document content as bytes
        """
        with open(input_path, 'rb') as file:
            return file.read()

    def _save_document(self, document_stream: bytes, output_path: Path) -> None:
        """
        Save a PDF document stream to a file.
        
        Args:
            document_stream: The PDF document content as bytes
            output_path: Path where the document should be saved
        """
        with open(output_path, 'wb') as file:
            file.write(document_stream)

    def enhance(self, document: bytes, **kwargs) -> bytes:
        """
        Enhance a PDF document using Adobe PDF Services AutoTag.
        
        This method sends the document to Adobe's cloud service for AI-powered
        accessibility enhancement and structure tagging.
        
        Args:
            document: The PDF document content as bytes
            **kwargs: Additional parameters:
                - generate_report: Whether to generate accessibility report (default: False)
                - shift_headings: Whether to shift heading levels (default: False)
                - return_report_path: If True and generate_report=True, returns tuple (pdf_bytes, report_path)
                
        Returns:
            bytes: The enhanced PDF document as bytes, or tuple if return_report_path=True
        """
        if not self._pdf_services:
            raise RuntimeError(
                "Adobe PDF Services not initialized. Please check credentials and try again."
            )
        
        # Extract parameters
        generate_report = kwargs.get('generate_report', False)
        shift_headings = kwargs.get('shift_headings', False)
        return_report_path = kwargs.get('return_report_path', False)
        
        try:
            logger.info("Starting Adobe PDF Services AutoTag processing...")
            
            # Upload document to Adobe cloud
            input_asset = self._pdf_services.upload(
                input_stream=document,
                mime_type=PDFServicesMediaType.PDF
            )
            logger.info("Document uploaded to Adobe PDF Services")
            
            # Create AutoTag parameters
            autotag_params = AutotagPDFParams(
                generate_report=generate_report,
                shift_headings=shift_headings
            )
            
            # Create and submit AutoTag job
            autotag_job = AutotagPDFJob(
                input_asset=input_asset,
                autotag_pdf_params=autotag_params
            )
            
            logger.info("Submitting AutoTag job to Adobe PDF Services...")
            location = self._pdf_services.submit(autotag_job)
            
            # Wait for job completion and get results
            logger.info("Waiting for Adobe PDF Services processing to complete...")
            pdf_services_response = self._pdf_services.get_job_result(location, AutotagPDFResult)
            
            # Download enhanced PDF
            result_asset: CloudAsset = pdf_services_response.get_result().get_tagged_pdf()
            stream_asset: StreamAsset = self._pdf_services.get_content(result_asset)
            enhanced_pdf_bytes = stream_asset.get_input_stream()
            
            logger.info("Adobe PDF Services AutoTag processing completed successfully")
            
            # Handle report generation if requested
            if generate_report:
                try:
                    result_asset_report: CloudAsset = pdf_services_response.get_result().get_report()
                    stream_asset_report: StreamAsset = self._pdf_services.get_content(result_asset_report)
                    
                    # Save report to temporary file if returning path
                    if return_report_path:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        report_path = Path(tempfile.gettempdir()) / f"adobe_autotag_report_{timestamp}.xlsx"
                        with open(report_path, 'wb') as report_file:
                            report_file.write(stream_asset_report.get_input_stream())
                        logger.info(f"Accessibility report saved to: {report_path}")
                        return (enhanced_pdf_bytes, report_path)
                    
                    logger.info("Accessibility report generated (not saved)")
                except Exception as e:
                    logger.warning(f"Failed to retrieve accessibility report: {e}")
            
            return enhanced_pdf_bytes
            
        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            logger.error(f"Adobe PDF Services error: {e}")
            raise RuntimeError(f"Adobe PDF Services processing failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Adobe AutoTag processing: {e}")
            raise

    def enhance_file(
        self, 
        input_path: Union[str, Path], 
        output_path: Union[str, Path], 
        **kwargs
    ) -> bool:
        """
        Enhance a PDF file using Adobe PDF Services AutoTag.
        
        Args:
            input_path: Path to the input PDF document
            output_path: Path where the enhanced document should be saved
            **kwargs: Additional parameters:
                - generate_report: Whether to generate accessibility report (default: False)
                - shift_headings: Whether to shift heading levels (default: False)
                - save_report_to: Optional path to save accessibility report
                
        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            return False
        
        if not self._pdf_services:
            logger.error("Adobe PDF Services not available - credentials not initialized")
            return False
        
        try:
            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Enhancing PDF with Adobe AutoTag: {input_path}")
            logger.info(f"Output will be saved to: {output_path}")
            
            # Load document
            document_bytes = self._load_document(input_path)
            
            # Handle report generation
            generate_report = kwargs.get('generate_report', False)
            save_report_to = kwargs.get('save_report_to')
            
            if generate_report and save_report_to:
                kwargs['return_report_path'] = True
                result = self.enhance(document_bytes, **kwargs)
                if isinstance(result, tuple):
                    enhanced_bytes, report_path = result
                    # Move report to specified location
                    save_report_path = Path(save_report_to)
                    save_report_path.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.move(str(report_path), str(save_report_path))
                    logger.info(f"Accessibility report saved to: {save_report_path}")
                else:
                    enhanced_bytes = result
            else:
                enhanced_bytes = self.enhance(document_bytes, **kwargs)
            
            # Save enhanced document
            self._save_document(enhanced_bytes, output_path)
            
            logger.info(f"Successfully enhanced PDF with Adobe AutoTag: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error enhancing PDF with Adobe AutoTag: {e}")
            return False

    def is_available(self) -> bool:
        """
        Check if Adobe PDF Services is available and properly configured.
        
        Returns:
            bool: True if Adobe services are available, False otherwise
        """
        return ADOBE_SDK_AVAILABLE and self._pdf_services is not None

    def get_capabilities(self) -> List[str]:
        """
        Get the list of enhancement capabilities provided by this enhancer.
        
        Returns:
            List[str]: List of capability identifiers
        """
        if not self.is_available():
            return []
        
        return [
            "autotag.structure_tagging",
            "autotag.heading_detection",
            "autotag.table_recognition", 
            "autotag.figure_identification",
            "autotag.reading_order",
            "autotag.accessibility_report",
            "cloud.ai_powered",
            "cloud.adobe_services"
        ]

    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate the current environment for Adobe PDF Services usage.
        
        Returns:
            Dict[str, Any]: Validation results with status and details
        """
        validation = {
            "status": "unknown",
            "sdk_available": ADOBE_SDK_AVAILABLE,
            "credentials_configured": False,
            "service_accessible": False,
            "details": [],
            "recommendations": []
        }
        
        # Check SDK availability
        if not ADOBE_SDK_AVAILABLE:
            validation["details"].append("Adobe PDF Services SDK not installed")
            validation["recommendations"].append("Install with: pip install pdfservices-sdk")
            validation["status"] = "error"
            return validation
        
        # Check credentials
        client_id = os.getenv('PDF_SERVICES_CLIENT_ID')
        client_secret = os.getenv('PDF_SERVICES_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            validation["details"].append("Adobe PDF Services credentials not configured")
            validation["recommendations"].append("Set PDF_SERVICES_CLIENT_ID and PDF_SERVICES_CLIENT_SECRET environment variables")
            validation["status"] = "error"
            return validation
        
        validation["credentials_configured"] = True
        validation["details"].append("Adobe PDF Services credentials found")
        
        # Check service accessibility
        if self._pdf_services:
            validation["service_accessible"] = True
            validation["details"].append("Adobe PDF Services initialized successfully")
            validation["status"] = "ready"
        else:
            validation["details"].append("Adobe PDF Services initialization failed")
            validation["recommendations"].append("Check credentials validity and network connectivity")
            validation["status"] = "error"
        
        return validation
