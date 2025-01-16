# core/processor.py
from pathlib import Path
from typing import Dict, Any
from ..api.models import ProcessingResult
from accessibility_checker.core.document import AccessibilityDocumentProcessor
from accessibility_checker.utils.config import ConfigurationManager
from accessibility_checker.utils.retry import RetryHandler, RetryConfig
from accessibility_checker.ocr.processor import OCRProcessor
from accessibility_checker.ocr.math_processor import MathOCRProcessor  # New import

async def process_pdf_file(file_path: Path) -> ProcessingResult:
    """Process a single PDF file."""
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

        # Initialize OCR processor with math OCR support
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

        # Extract and analyze document content
        processor.extract_text_with_positions()
        processor.detect_headings()
        processor.detect_tables()
        processor.analyze_reading_order()

        # Generate output paths
        output_dir = Path("output")
        processed_path = output_dir / "processed_pdfs" / f"{file_path.stem}_processed.pdf"
        report_path = output_dir / "reports" / f"{file_path.stem}_report.json"
        math_report_path = output_dir / "reports" / f"{file_path.stem}_math_report.json"

        # Create output directories
        processed_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # Save processed PDF and reports
        processor.doc.save(str(processed_path))
        processor.export_accessibility_report(str(report_path))

        # Get math processing results if available
        math_results = {}
        if hasattr(processor, 'math_regions') and processor.math_regions:
            math_results = {
                "math_regions": len(processor.math_regions),
                "details": processor.math_regions
            }

        # Count violations
        violations = len(processor.corrections.get(0, []))

        return ProcessingResult(
            filename=file_path.name,
            status="success",
            violations=violations,
            processed_path=str(processed_path),
            details={
                "report_path": str(report_path),
                "math_detection": math_results
            }
        )

    except Exception as e:
        return ProcessingResult(
            filename=file_path.name,
            status="failed",
            violations=0,
            details={"error": str(e)}
        )
