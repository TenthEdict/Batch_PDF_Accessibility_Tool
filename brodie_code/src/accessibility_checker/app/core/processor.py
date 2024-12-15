from pathlib import Path
from typing import Dict, Any
from accessibility_checker.app.api.models import ProcessingResult
from accessibility_checker.core.document import AccessibilityDocumentProcessor
from accessibility_checker.utils.config import ConfigurationManager
from accessibility_checker.utils.retry import RetryHandler, RetryConfig
from accessibility_checker.ocr.processor import OCRProcessor

async def process_pdf_file(file_path: Path) -> ProcessingResult:
    """
    Process a single PDF file for accessibility.
    
    Args:
        file_path: Path to the PDF file
            
    Returns:
        ProcessingResult containing processing status and details
    """
    try:
        # Initialize configuration and components
        config_manager = ConfigurationManager("config.yaml")
        processing_config = config_manager.get_processing_config()
        
        retry_handler = RetryHandler(RetryConfig(
            max_attempts=processing_config.retry_count,
            base_delay=2.0,
            max_delay=30.0,
            jitter=True
        ))

        ocr_processor = OCRProcessor(
            config=processing_config.ocr_settings,
            retry_handler=retry_handler,
            timeout=processing_config.timeout
        )

        # Process document
        processor = AccessibilityDocumentProcessor(
            str(file_path),
            ocr_processor=ocr_processor,
            retry_handler=retry_handler
        )

        # Extract and analyze document structure
        processor.extract_text_with_positions()
        processor.detect_headings()
        processor.detect_tables()
        processor.analyze_reading_order()

        # Generate output paths
        output_dir = Path("output")
        processed_path = output_dir / "processed_pdfs" / f"{file_path.stem}_processed.pdf"
        report_path = output_dir / "reports" / f"{file_path.stem}_report.json"

        # Create output directories if they don't exist
        processed_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # Save processed PDF and report
        processor.doc.save(str(processed_path))
        processor.export_accessibility_report(str(report_path))

        # Count accessibility issues
        total_violations = sum(len(corrections) for corrections 
                             in processor.corrections.values())

        return ProcessingResult(
            filename=file_path.name,
            status="success",
            violations=total_violations,
            processed_path=str(processed_path),
            details={
                "report_path": str(report_path),
                "total_pages": len(processor.doc),
                "tables_detected": len(processor.tables),
                "headings_detected": sum(1 for elem in processor.text_elements 
                                      if elem.heading_level is not None)
            }
        )

    except Exception as e:
        return ProcessingResult(
            filename=file_path.name,
            status="failed",
            violations=0,
            details={"error": str(e)}
        )
