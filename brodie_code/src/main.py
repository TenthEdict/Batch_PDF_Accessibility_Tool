import os
import shutil
from pathlib import Path
import logging
from datetime import datetime
import yaml
from accessibility_checker.ocr.processor import OCRProcessor
from accessibility_checker.utils.config import OCRConfig
from accessibility_checker.utils.retry import RetryHandler, RetryConfig
from accessibility_checker.core.batch import BatchPDFProcessor

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def clean_directory(directory: Path) -> None:
    """Clean all files in a directory without removing the directory itself."""
    if directory.exists():
        for item in directory.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        logging.info(f"Cleaned directory: {directory}")
    else:
        logging.info(f"Directory does not exist, will be created: {directory}")

def clean_output_directories(output_dir: Path) -> None:
    """Clean all output directories before processing."""
    # Define directories to clean
    directories = [
        output_dir / "corrections",
        output_dir / "logs",
        output_dir / "ocr_results",
        output_dir / "processed_pdfs",
        output_dir / "reports"
    ]
    
    # Clean each directory
    for directory in directories:
        clean_directory(directory)
        directory.mkdir(parents=True, exist_ok=True)

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

def create_ocr_config(config: dict) -> OCRConfig:
    """Create OCRConfig from config dictionary."""
    ocr_settings = config.get('ocr', {})
    return OCRConfig(
        language=ocr_settings.get('language', 'eng'),
        psm=ocr_settings.get('psm', 3),
        oem=ocr_settings.get('oem', 3),
        char_whitelist=ocr_settings.get('char_whitelist', ''),
        additional_params=ocr_settings.get('additional_params', {})
    )

def main():
    # Get the project root (2 levels up from main.py)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    
    # Create paths relative to project root
    input_dir = project_root / "input"
    output_dir = project_root / "output"
    config_path = project_root / "config.yaml"
    log_dir = output_dir / "logs"
    
    # Clean up previous run outputs
    print("Cleaning up previous run outputs...")
    clean_output_directories(output_dir)
    
    # Create necessary directories
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up logging
    setup_logging(log_dir)
    
    logging.info(f"Starting processing with:")
    logging.info(f"Project root: {project_root}")
    logging.info(f"Input directory: {input_dir}")
    logging.info(f"Output directory: {output_dir}")
    
    try:
        # Load configuration
        config = load_config(config_path)
        logging.info("Configuration loaded successfully")
        
        # Create OCR configuration
        ocr_config = create_ocr_config(config)
        logging.info("OCR configuration created")
        
        # Initialize retry handler
        retry_handler = RetryHandler(RetryConfig(
            max_attempts=config.get('retry_count', 3),
            base_delay=2.0,
            max_delay=30.0,
            jitter=True
        ))
        logging.info("Retry handler initialized")
        
        # Initialize OCR processor with config
        ocr_processor = OCRProcessor(
            config=ocr_config,
            retry_handler=retry_handler,
            timeout=config.get('timeout', 300)
        )
        logging.info("OCR processor initialized with configuration")
        
        # Initialize batch processor
        processor = BatchPDFProcessor(
            str(input_dir),
            str(output_dir),
            max_workers=config.get('max_workers', 4),
            ocr_processor=ocr_processor,
            retry_handler=retry_handler
        )
        logging.info("Batch processor initialized")
        
        # Process files
        logging.info("Starting batch processing")
        summary_df = processor.process_directory()
        
        print("\nProcessing Summary:")
        print(f"Total files processed: {len(summary_df)}")
        
        if not summary_df.empty:
            success_count = sum(summary_df['status'] == 'success')
            failed_count = sum(summary_df['status'] == 'failed')
            print(f"Successfully processed: {success_count}")
            print(f"Failed: {failed_count}")
            
            print("\nProcessed files:")
            for idx, row in summary_df.iterrows():
                print(f"  - {idx}: {row['status']}")
                if row['errors']:
                    print(f"    Errors: {row['errors']}")
                
            print(f"\nOutput files located in: {output_dir}")
            
            print("\nOutput directory contents:")
            for dir_name in ['corrections', 'reports', 'processed_pdfs', 'logs', 'ocr_results']:
                dir_path = output_dir / dir_name
                print(f"\n{dir_name}:")
                if dir_path.exists():
                    for file in dir_path.glob('*'):
                        print(f"  - {file.name}")
                else:
                    print("  Directory not found!")
        else:
            print("\nNo files were processed.")
            print(f"Input directory: {input_dir}")
            print("Please ensure PDF files are present in the input directory")
            
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()