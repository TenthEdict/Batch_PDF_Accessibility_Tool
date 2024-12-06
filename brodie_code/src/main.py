from pathlib import Path
import logging
from datetime import datetime
import yaml
from accessibility_checker.core.batch import BatchPDFProcessor
from accessibility_checker.utils.config import ConfigurationManager

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

def main():
    # Use project structure paths
    project_dir = Path(__file__).parent.parent
    input_dir = project_dir / "input"
    output_dir = project_dir / "output"
    config_file = project_dir / "config.yaml"
    
    # Set up logging
    log_dir = output_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    setup_logging(log_dir)
    
    try:
        # Load configuration
        logging.info(f"Loading configuration from {config_file}")
        config_manager = ConfigurationManager(str(config_file))
        processing_config = config_manager.get_processing_config()
        
        # Initialize batch processor
        processor = BatchPDFProcessor(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            max_workers=processing_config.max_workers
        )
        
        # Process files
        summary_df = processor.process_directory()
        
        # Print summary
        print("\nProcessing Summary:")
        print(f"Total files processed: {len(summary_df)}")
        print(f"Successfully processed: {sum(summary_df['status'] == 'success')}")
        print(f"Failed: {sum(summary_df['status'] == 'failed')}")
        print(f"\nOutput files located in: {output_dir}")
        
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
