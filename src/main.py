from pathlib import Path
import argparse
import yaml
import logging
from datetime import datetime
import sys

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent))

from processor.batch import BatchPDFProcessor
from processor.accessibility import AccessibilityDocumentProcessor
from processor.enhance import EnhancedAccessibilityChecker
from processor.retry import RetryHandler, RetryConfig, ProcessingError, OCRError, OCRTimeoutError
from processor.ocr import OCRProcessor
from processor.config import ConfigurationManager

def setup_logging(log_dir: Path) -> None:
    """Set up logging configuration."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"accessibility_checker_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='PDF Accessibility Checker')
    
    parser.add_argument(
        '--input-dir',
        type=str,
        required=True,
        help='Directory containing PDF files to process'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        required=True,
        help='Directory for output files and reports'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        help='Number of worker processes (overrides config file)'
    )
    
    parser.add_argument(
        '--ocr-timeout',
        type=int,
        default=30,
        help='Timeout in seconds for OCR processing'
    )
    
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Create output directory structure
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up logging
    log_dir = output_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    setup_logging(log_dir)
    
    try:
        # Load configuration
        logging.info(f"Loading configuration from {args.config}")
        config_manager = ConfigurationManager(args.config)
        processing_config = config_manager.get_processing_config()
        
        # Override max_workers if specified in command line arguments
        if args.workers:
            processing_config.max_workers = args.workers
        
        # Initialize processors with retry capability
        retry_handler = RetryHandler(RetryConfig(
            max_attempts=processing_config.retry_count,
            base_delay=2.0,
            max_delay=30.0,
            jitter=True
        ))
        
        # Initialize OCR processor with retry and timeout
        ocr_processor = OCRProcessor(
            config=processing_config.ocr_settings,
            retry_handler=retry_handler,
            timeout=30
        )
        
        # Initialize batch processor with OCR capability
        processor = BatchPDFProcessor(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            max_workers=processing_config.max_workers,
            ocr_processor=ocr_processor,
            retry_handler=retry_handler
        )
        
        # Process files
        logging.info("Starting batch processing")
        summary_df = processor.process_directory()
        
        # Print processing summary
        success_count = sum(summary_df['status'] == 'success')
        failed_count = sum(summary_df['status'] == 'failed')
        ocr_count = sum(summary_df.get('ocr_applied', False))
        
        print("\nProcessing Summary:")
        print(f"Total files processed: {len(summary_df)}")
        print(f"Successfully processed: {success_count}")
        print(f"Failed: {failed_count}")
        print(f"OCR applied: {ocr_count}")
        print(f"\nOutput files located in: {args.output_dir}")
        
        logging.info("Processing completed successfully")
        
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()