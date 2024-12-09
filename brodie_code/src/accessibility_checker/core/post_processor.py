from typing import Dict, Optional
import os
from pikepdf import Pdf, Name, String, Dictionary
from libxmp import XMPFiles, XMPMeta, consts

# Import existing error types and handlers
from .retry_mechanism import RetryHandler, RetryConfig, ProcessingError
from .config_manager import ConfigurationManager

class PDFPostProcessor:
    def __init__(self, config: dict, retry_handler: RetryHandler):
        self.config = config
        self.retry_handler = retry_handler
        self.xmp_path = config.get('xmp_metadata_path')
        
    @RetryHandler(RetryConfig()).__call__((ProcessingError,))
    def process_pdf(self, input_path: str, output_path: str) -> bool:
        """
        Post-process a PDF file to ensure accessibility compliance.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path to save processed PDF file
            
        Returns:
            bool: True if processing was successful
            
        Raises:
            ProcessingError: If post-processing fails
        """
        try:
            # Load the XMP metadata
            with open(self.xmp_path, "rb") as xmp_file:
                xmp_data = xmp_file.read()
            
            xmp_meta = XMPMeta(xmp_str=xmp_data.decode('utf-8'))
            
            # Open and process PDF
            with Pdf.open(input_path) as pdf:
                # Preserve existing title
                if '/Title' in pdf.docinfo:
                    xmp_meta.set_property(
                        consts.XMP_NS_DC, 
                        'title', 
                        str(pdf.docinfo['/Title'])
                    )
                
                # Set language
                pdf.Root[Name('/Lang')] = String('en-US')
                
                # Mark as tagged PDF
                pdf.Root[Name('/MarkInfo')] = Dictionary()
                pdf.Root.MarkInfo[Name('/Marked')] = True
                
                # Set tab order by structure
                for page in pdf.pages:
                    page[Name('/Tabs')] = Name('/S')
                
                # Update XMP metadata
                if Name('/Metadata') in pdf.Root:
                    del pdf.Root[Name('/Metadata')]
                    
                pdf.Root[Name('/Metadata')] = pdf.make_stream(
                    xmp_meta.serialize_to_str().encode('utf-8')
                )
                
                # Save processed PDF
                pdf.save(output_path)
                
            return True
            
        except Exception as e:
            raise ProcessingError(f"PDF post-processing failed: {str(e)}")

class EnhancedAccessibilityDocumentProcessor:
    def __init__(self, config_path: str):
        # Initialize configuration
        self.config_manager = ConfigurationManager(config_path)
        self.config = self.config_manager.get_processing_config()
        
        # Initialize components
        self.retry_handler = RetryHandler(RetryConfig(
            max_attempts=self.config.retry_count,
            base_delay=2.0,
            max_delay=30.0,
            jitter=True
        ))
        
        self.accessibility_checker = EnhancedAccessibilityChecker()
        self.post_processor = PDFPostProcessor(
            config={
                'xmp_metadata_path': os.path.join(
                    os.path.dirname(config_path), 
                    'pdfUA-ID.xmp'
                )
            },
            retry_handler=self.retry_handler
        )
    
    def process_document(self, input_path: str, output_path: str) -> Dict:
        """
        Process document with full accessibility workflow.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path to save processed PDF file
            
        Returns:
            Dict: Processing result including accessibility report and post-processing status
            
        Raises:
            ProcessingError: If processing fails
        """
        # Existing accessibility checks
        result = super().process_document(input_path)
        
        # Add post-processing step
        if result['status'] == 'success':
            post_process_success = self.post_processor.process_pdf(
                input_path=input_path,
                output_path=output_path
            )
            
            result['post_processed'] = post_process_success
            
        return result