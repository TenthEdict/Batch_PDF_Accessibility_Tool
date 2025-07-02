#!/usr/bin/env python3
"""
Enhancement service for business logic related to document enhancement.

This service encapsulates all business operations related to document
enhancement and provides a clean interface for enhancement operations.
"""

import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.service_container import ServiceContainer
from ..enhancers.ocr_enhancer import OCREnhancer
from ..enhancers.pdf_enhancer import PDFEnhancer
from ..enhancers.adobe_autotag_enhancer import AdobeAutotagEnhancer

logger = logging.getLogger(__name__)


class EnhancementService:
    """
    Service for coordinating document enhancement operations.
    """

    def __init__(self, container: Optional[ServiceContainer] = None):
        """
        Initialize the enhancement service.
        """
        self.container = container
        self.logger = logging.getLogger(__name__)
        self.ocr_enhancer = OCREnhancer()
        self.pdf_enhancer = PDFEnhancer()
        
        # Initialize Adobe AutoTag enhancer (with graceful fallback)
        try:
            self.adobe_autotag_enhancer = AdobeAutotagEnhancer()
            self.adobe_available = self.adobe_autotag_enhancer.is_available()
            if self.adobe_available:
                self.logger.info("Adobe PDF Services AutoTag enhancer initialized successfully")
            else:
                self.logger.info("Adobe PDF Services AutoTag enhancer initialized but not available (credentials missing)")
        except Exception as e:
            self.logger.warning(f"Adobe PDF Services AutoTag enhancer initialization failed: {e}")
            self.adobe_autotag_enhancer = None
            self.adobe_available = False

    def enhance_document(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        mode: str = "academic",
        use_adobe_autotag: Optional[bool] = None,
        generate_accessibility_report: bool = False,
        **kwargs,
    ) -> bool:
        """
        Enhance a document with OCR, Adobe AutoTag (when available), and accessibility features.
        
        Args:
            input_path: Path to the input document
            output_path: Path where the enhanced document should be saved
            mode: Processing mode (default: "academic")
            use_adobe_autotag: Whether to use Adobe AutoTag (default: auto-detect availability)
            generate_accessibility_report: Whether to generate accessibility report (Adobe only)
            **kwargs: Additional enhancement parameters
            
        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            self.logger.error(f"Input file not found: {input_path}")
            return False

        # Determine Adobe AutoTag usage
        if use_adobe_autotag is None:
            use_adobe_autotag = self.adobe_available
        elif use_adobe_autotag and not self.adobe_available:
            self.logger.warning("Adobe AutoTag requested but not available, falling back to local processing")
            use_adobe_autotag = False

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                ocr_output_path = temp_path / "ocr_enhanced.pdf"
                autotag_output_path = temp_path / "autotag_enhanced.pdf"

                # Step 1: OCR and Font Embedding
                self.logger.info("Step 1: Applying OCR and Font Embedding...")
                ocr_success = self.ocr_enhancer.enhance_file(
                    input_path, ocr_output_path
                )
                if not ocr_success:
                    self.logger.error("OCR enhancement failed.")
                    return False
                self.logger.info("OCR enhancement completed successfully.")

                # Step 2: Adobe AutoTag Enhancement (optional)
                current_input_path = ocr_output_path
                if use_adobe_autotag:
                    self.logger.info("Step 2: Applying Adobe PDF Services AutoTag...")
                    try:
                        # Prepare Adobe AutoTag parameters
                        autotag_kwargs = {
                            'generate_report': generate_accessibility_report,
                            'shift_headings': kwargs.get('shift_headings', False)
                        }
                        
                        # Add report saving if requested
                        if generate_accessibility_report:
                            report_path = output_path.parent / f"{output_path.stem}_accessibility_report.xlsx"
                            autotag_kwargs['save_report_to'] = str(report_path)
                        
                        autotag_success = self.adobe_autotag_enhancer.enhance_file(
                            ocr_output_path, autotag_output_path, **autotag_kwargs
                        )
                        
                        if autotag_success:
                            self.logger.info("Adobe AutoTag enhancement completed successfully.")
                            current_input_path = autotag_output_path
                        else:
                            self.logger.warning("Adobe AutoTag enhancement failed, continuing with local processing...")
                            
                    except Exception as e:
                        self.logger.warning(f"Adobe AutoTag enhancement error: {e}, falling back to local processing")

                # Step 3: Local PDF Metadata and Accessibility Enhancements
                step_name = "Step 3" if use_adobe_autotag else "Step 2"
                self.logger.info(f"{step_name}: Applying local PDF metadata and accessibility enhancements...")
                
                pdf_enhance_success = self.pdf_enhancer.enhance_file(
                    current_input_path, output_path, **kwargs
                )
                if not pdf_enhance_success:
                    self.logger.error("PDF metadata enhancement failed.")
                    return False
                self.logger.info("PDF metadata enhancement completed successfully.")

            enhancement_summary = []
            enhancement_summary.append("OCR and font embedding")
            if use_adobe_autotag and current_input_path == autotag_output_path:
                enhancement_summary.append("Adobe PDF Services AutoTag (AI-powered structure tagging)")
            enhancement_summary.append("Local PDF metadata and accessibility features")
            
            self.logger.info(f"Successfully enhanced document with: {', '.join(enhancement_summary)}")
            self.logger.info(f"Enhanced document saved to: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"An error occurred during the enhancement pipeline: {e}", exc_info=True)
            return False

    def get_available_enhancers(self) -> Dict[str, bool]:
        """
        Get the availability status of all enhancers.
        
        Returns:
            Dict[str, bool]: Dictionary mapping enhancer names to availability status
        """
        return {
            "ocr_enhancer": True,  # Always available if class loads
            "pdf_enhancer": True,  # Always available if class loads
            "adobe_autotag_enhancer": self.adobe_available
        }
    
    def get_enhancement_capabilities(self) -> Dict[str, List[str]]:
        """
        Get the capabilities of all available enhancers.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping enhancer names to their capabilities
        """
        capabilities = {
            "ocr_enhancer": self.ocr_enhancer.get_capabilities(),
            "pdf_enhancer": self.pdf_enhancer.get_capabilities()
        }
        
        if self.adobe_available:
            capabilities["adobe_autotag_enhancer"] = self.adobe_autotag_enhancer.get_capabilities()
        
        return capabilities
    
    def validate_adobe_services(self) -> Dict[str, Any]:
        """
        Validate Adobe PDF Services configuration and accessibility.
        
        Returns:
            Dict[str, Any]: Validation results with detailed status information
        """
        if not self.adobe_autotag_enhancer:
            return {
                "status": "unavailable",
                "message": "Adobe AutoTag enhancer not initialized",
                "details": {}
            }
        
        validation = self.adobe_autotag_enhancer.validate_environment()
        return {
            "status": validation["status"],
            "message": f"Adobe PDF Services status: {validation['status']}",
            "details": validation
        }
