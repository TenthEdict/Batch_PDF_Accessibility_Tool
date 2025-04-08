#!/usr/bin/env python3
"""
Command Line Interface for ePubs Accessibility Enhancement Project.
Provides a unified interface for all accessibility enhancement tools.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
import yaml

# Add parent directory to path to allow importing modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

logger = logging.getLogger(__name__)

def setup_logging(verbose=False):
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def load_config(config_path):
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        dict: Configuration data
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.debug(f"Loaded configuration from: {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {}

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="ePubs Accessibility Enhancement Project CLI"
    )
    
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/default.yaml", 
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose logging"
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # OCR command
    ocr_parser = subparsers.add_parser("ocr", help="Run OCR on documents")
    ocr_parser.add_argument("--input", required=True, help="Input PDF file or directory")
    ocr_parser.add_argument("--output", required=True, help="Output PDF file or directory")
    ocr_parser.add_argument("--historical", action="store_true", help="Enable historical document mode")
    ocr_parser.add_argument("--jbig2", action="store_true", help="Use JBIG2-optimized OCR")
    ocr_parser.add_argument("--dpi", type=int, default=300, help="DPI for image processing")
    
    # Enhance command
    enhance_parser = subparsers.add_parser("enhance", help="Enhance document accessibility")
    enhance_parser.add_argument("--input", required=True, help="Input PDF file or directory")
    enhance_parser.add_argument("--output", required=True, help="Output PDF file or directory")
    enhance_parser.add_argument("--level", choices=["basic", "advanced", "ua"], default="basic", 
                               help="Enhancement level")
    enhance_parser.add_argument("--title", help="Document title")
    enhance_parser.add_argument("--author", help="Document author")
    enhance_parser.add_argument("--language", default="en-US", help="Document language")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate document accessibility")
    validate_parser.add_argument("--input", required=True, help="Input PDF file or directory")
    validate_parser.add_argument("--output", help="Output report file or directory")
    validate_parser.add_argument("--format", choices=["json", "csv"], default="json", 
                               help="Report format")
    
    # Metadata command
    metadata_parser = subparsers.add_parser("metadata", help="Update document metadata")
    metadata_parser.add_argument("--input", required=True, help="Input PDF file or directory")
    metadata_parser.add_argument("--output", required=True, help="Output PDF file or directory")
    metadata_parser.add_argument("--excel", help="Path to Excel file with metadata")
    metadata_parser.add_argument("--title", help="Document title")
    metadata_parser.add_argument("--author", help="Document author")
    metadata_parser.add_argument("--language", default="en-US", help="Document language")
    metadata_parser.add_argument("--no-tag", action="store_true", help="Do not mark document as tagged")
    metadata_parser.add_argument("--no-pdfua", action="store_true", help="Do not add PDF/UA identifier")
    
    return parser.parse_args()

def run_ocr_command(args, config):
    """Run OCR command."""
    from src.ocr.processor import OCRProcessor, OCRConfig
    from src.ocr.jbig2_processor import JBIG2OCRProcessor
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    # Create output directory if needed
    if output_path.is_dir() or not output_path.suffix:
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if args.jbig2:
        # Use JBIG2-optimized OCR processor
        logger.info("Using JBIG2-optimized OCR processor")
        
        processor = JBIG2OCRProcessor(
            min_confidence=config.get('ocr', {}).get('min_confidence', 40),
            dpi=args.dpi
        )
        
        if input_path.is_dir():
            # Process all PDF files in directory
            pdf_files = list(input_path.glob('*.pdf'))
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            for pdf_file in pdf_files:
                output_file = output_path / pdf_file.name
                logger.info(f"Processing: {pdf_file.name}")
                processor.make_searchable_pdf(pdf_file, output_file)
        else:
            # Process single PDF file
            if not output_path.suffix:
                output_file = output_path / input_path.name
            else:
                output_file = output_path
            
            logger.info(f"Processing: {input_path}")
            processor.make_searchable_pdf(input_path, output_file)
    else:
        # Use standard OCR processor
        logger.info("Using standard OCR processor")
        
        # Configure OCR based on args and config
        ocr_config = OCRConfig(
            language=config.get('ocr', {}).get('language', 'eng'),
            psm=config.get('ocr', {}).get('psm', 3),
            oem=config.get('ocr', {}).get('oem', 1)
        )
        
        processor = OCRProcessor(config=ocr_config)
        
        # Set document mode if historical
        if args.historical:
            logger.info("Enabling historical document mode")
            processor.document_mode = 'historical'
        
        # TODO: Implement standard OCR processing
        logger.warning("Standard OCR processing not yet implemented")
        
    return 0

def run_enhance_command(args, config):
    """Run enhance command."""
    if args.level == "basic":
        from src.enhancers.basic_enhancer import BasicEnhancer
        enhancer = BasicEnhancer()
    else:
        logger.warning(f"Enhancement level '{args.level}' not yet implemented")
        return 1
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    # Create output directory if needed
    if output_path.is_dir() or not output_path.suffix:
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if input_path.is_dir():
        # Process all PDF files in directory
        pdf_files = list(input_path.glob('*.pdf'))
        logger.info(f"Found {len(pdf_files)} PDF files to enhance")
        
        for pdf_file in pdf_files:
            output_file = output_path / pdf_file.name
            logger.info(f"Enhancing: {pdf_file.name}")
            enhancer.enhance_pdf_accessibility(
                pdf_file,
                output_file,
                args.title,
                args.author,
                args.language
            )
    else:
        # Process single PDF file
        if not output_path.suffix:
            output_file = output_path / input_path.name
        else:
            output_file = output_path
        
        logger.info(f"Enhancing: {input_path}")
        enhancer.enhance_pdf_accessibility(
            input_path,
            output_file,
            args.title,
            args.author,
            args.language
        )
    
    return 0

def run_validate_command(args, config):
    """Run validate command."""
    from src.validation.accessibility_validator import AccessibilityValidator
    
    validator = AccessibilityValidator()
    input_path = Path(args.input)
    
    if input_path.is_dir():
        # Validate all PDF files in directory
        output_dir = Path(args.output) if args.output else input_path
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Validating PDF files in: {input_path}")
        results = validator.batch_validate(
            input_path,
            args.format,
            output_dir
        )
        
        # Print summary
        passed = sum(1 for result in results if result.get('passes', False))
        logger.info(f"Validation Results:")
        logger.info(f"Total PDFs: {len(results)}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {len(results) - passed}")
    else:
        # Validate single PDF file
        logger.info(f"Validating: {input_path}")
        result = validator.validate_pdf(input_path)
        
        if args.output:
            output_path = Path(args.output)
            if output_path.is_dir():
                output_path = output_path / f"{input_path.stem}_validation.{args.format}"
        else:
            output_path = input_path.with_suffix(f".{args.format}")
        
        # Generate report
        if args.format == "json":
            validator.generate_json_report(result, output_path)
        else:  # csv
            validator.generate_csv_report([result], output_path)
        
        # Print summary
        logger.info(f"Validation Results for: {result.get('filename', '')}")
        logger.info(f"Overall Score: {result.get('overall_score', 0)}/100")
        logger.info(f"Passes: {'Yes' if result.get('passes', False) else 'No'}")
    
    return 0

def run_metadata_command(args, config):
    """Run metadata command."""
    from src.metadata.metadata_editor import MetadataEditor
    
    editor = MetadataEditor()
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    # Create output directory if needed
    if output_path.is_dir() or not output_path.suffix:
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if args.excel:
        # Batch update from Excel
        logger.info(f"Updating metadata from Excel: {args.excel}")
        editor.batch_update_from_excel(
            args.excel,
            input_path,
            output_path,
            not args.no_tag,
            not args.no_pdfua
        )
    elif input_path.is_dir():
        # Process all PDF files in directory
        pdf_files = list(input_path.glob('*.pdf'))
        logger.info(f"Found {len(pdf_files)} PDF files to update")
        
        for pdf_file in pdf_files:
            output_file = output_path / pdf_file.name
            logger.info(f"Updating metadata: {pdf_file.name}")
            editor.update_metadata(
                pdf_file,
                output_file,
                args.title,
                args.author,
                args.language,
                not args.no_tag,
                not args.no_pdfua
            )
    else:
        # Process single PDF file
        if not output_path.suffix:
            output_file = output_path / input_path.name
        else:
            output_file = output_path
        
        logger.info(f"Updating metadata: {input_path}")
        editor.update_metadata(
            input_path,
            output_file,
            args.title,
            args.author,
            args.language,
            not args.no_tag,
            not args.no_pdfua
        )
    
    return 0

def main():
    """Main entry point."""
    args = parse_args()
    setup_logging(args.verbose)
    
    logger.info("Starting ePubs Accessibility Enhancement Project CLI")
    
    # Load configuration
    config = load_config(args.config)
    
    # Execute the appropriate command
    if args.command == "ocr":
        return run_ocr_command(args, config)
    elif args.command == "enhance":
        return run_enhance_command(args, config)
    elif args.command == "validate":
        return run_validate_command(args, config)
    elif args.command == "metadata":
        return run_metadata_command(args, config)
    else:
        logger.error("No command specified")
        return 1

if __name__ == "__main__":
    sys.exit(main())