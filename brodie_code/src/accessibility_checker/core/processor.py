# src/accessibility_checker/core/processor.py

from pathlib import Path
from typing import Dict, Any
from ..api.models import ProcessingResult
from ..core.document import AccessibilityDocumentProcessor
from ..utils.config import ConfigurationManager
from ..utils.retry import RetryHandler, RetryConfig
from ..ocr.processor import OCRProcessor
from ..ocr.adaptive_config import AdaptiveOCRConfig

async def process_pdf_file(file_path: Path, config: Dict[str, Any] = None) -> ProcessingResult:
    """Process a single PDF file."""
    try:
        # Initialize configuration and components
        config_path = Path("/app/config.yaml")  # Use absolute container path
        config_manager = ConfigurationManager(str(config_path))
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

        # Initialize adaptive OCR configuration if provided
        adaptive_config = AdaptiveOCRConfig(config or {})
        
        # Process document
        processor = AccessibilityDocumentProcessor(
            str(file_path),
            ocr_processor=ocr_processor,
            retry_handler=retry_handler
        )

        processor.extract_text_with_positions()
        processor.detect_headings()
        processor.detect_tables()
        processor.analyze_reading_order()

        # Generate output paths using container paths
        output_dir = Path("/app/output")
        processed_path = output_dir / "processed_pdfs" / f"{file_path.stem}_processed.pdf"
        report_path = output_dir / "reports" / f"{file_path.stem}_report.json"

        # Ensure output directories exist
        processed_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # Save processed PDF and report
        processor.doc.save(str(processed_path))
        processor.export_accessibility_report(str(report_path))

        # Count violations
        violations = len(processor.corrections.get(0, []))

        return ProcessingResult(
            filename=file_path.name,
            status="success",
            violations=violations,
            processed_path=str(processed_path),
            details={
                "report_path": str(report_path)
            }
        )

    except Exception as e:
        return ProcessingResult(
            filename=file_path.name,
            status="failed",
            violations=0,
            details={"error": str(e)}
        )