#!/usr/bin/env python3
"""
Unified CLI interface for the ePubs Accessibility Enhancement Project.

This module provides a consolidated command-line interface that unifies
all processing capabilities into a single entry point.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Add the project root to the path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from processor.unified_project.src.core.service_container import get_container
    from processor.unified_project.src.enhancement.pipeline import EnhancementPipeline, EnhancementConfig, EnhancementOrchestrator
    from processor.unified_project.src.academic.processor import AcademicProcessor
    from processor.unified_project.src.cli.accessibility_cli import AccessibilityProcessor
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you have installed the package with: pip install -e .")
    sys.exit(1)


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def create_common_parser() -> argparse.ArgumentParser:
    """Create the common argument parser with shared options."""
    parser = argparse.ArgumentParser(
        description="ePubs Accessibility Enhancement Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s process input.pdf output.pdf --mode academic
  %(prog)s process-batch input_dir output_dir --mode accessibility
  %(prog)s enhance input.pdf output.pdf --title "Document Title"
  %(prog)s validate document.pdf --report-format html
        """
    )
    
    # Global options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--environment",
        type=str,
        choices=["academic", "default"],
        default="default",
        help="Processing environment"
    )
    
    return parser


def add_processing_arguments(parser: argparse.ArgumentParser):
    """Add processing-related arguments to parser."""
    parser.add_argument(
        "input",
        type=str,
        help="Input file or directory"
    )
    
    parser.add_argument(
        "output", 
        type=str,
        help="Output file or directory"
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["academic", "accessibility", "basic"],
        default="basic",
        help="Processing mode"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Processing timeout in seconds per file"
    )
    
    parser.add_argument(
        "--max-workers",
        type=int,
        default=2,
        help="Maximum number of worker threads for parallel processing"
    )


def add_enhancement_arguments(parser: argparse.ArgumentParser):
    """Add enhancement-related arguments to parser."""
    parser.add_argument(
        "--title",
        type=str,
        help="Document title (overrides automatic detection)"
    )
    
    parser.add_argument(
        "--author",
        type=str,
        help="Document author"
    )
    
    parser.add_argument(
        "--language",
        type=str,
        default="en-US",
        help="Document language"
    )
    
    parser.add_argument(
        "--no-title-extraction",
        action="store_true",
        help="Disable automatic title extraction from H1 tags and filename"
    )
    
    parser.add_argument(
        "--add-pdfua",
        action="store_true", 
        help="Add PDF/UA compliance identifiers"
    )


def add_academic_arguments(parser: argparse.ArgumentParser):
    """Add academic processing arguments to parser."""
    parser.add_argument(
        "--detect-math",
        action="store_true",
        help="Enable math formula detection"
    )
    
    parser.add_argument(
        "--detect-citations", 
        action="store_true",
        help="Enable citation detection"
    )
    
    parser.add_argument(
        "--detect-tables",
        action="store_true",
        default=True,
        help="Enable table detection (default: enabled)"
    )


def process_command(args) -> int:
    """Handle the process command."""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return 1
    
    try:
        if args.mode == "academic":
            # Use academic processor
            from process_academic_local import AcademicPaperProcessor
            processor = AcademicPaperProcessor(
                config_path=args.config or "unified_project/config/academic.yaml",
                options={
                    'math_detection': args.detect_math,
                    'citation_detection': args.detect_citations,
                }
            )
        elif args.mode == "accessibility":
            # Use accessibility processor
            processor = AccessibilityProcessor(
                config_path=args.config,
                environment=args.environment
            )
        else:
            # Use basic enhancement orchestrator
            pipeline = EnhancementPipeline(environment=args.environment)
            processor = EnhancementOrchestrator(pipeline, args.environment)
        
        # Process the file or directory
        if input_path.is_file():
            success = processor.process(
                input_path, 
                output_path,
                timeout=args.timeout,
                title=args.title,
                author=args.author,
                language=args.language
            )
        else:
            # Batch processing
            success = process_batch(processor, input_path, output_path, args)
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return 1


def enhance_command(args) -> int:
    """Handle the enhance command."""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        logger.error(f"Input file does not exist: {input_path}")
        return 1
    
    try:
        # Create enhancement configuration
        config = EnhancementConfig(
            title=args.title,
            author=args.author,
            language=args.language,
            extract_title_from_h1=not args.no_title_extraction,
            extract_title_from_filename=not args.no_title_extraction,
            add_pdfua_identifiers=args.add_pdfua
        )
        
        # Create enhancement pipeline
        pipeline = EnhancementPipeline(environment=args.environment)
        
        # Enhance the file
        success = pipeline.enhance_file(input_path, output_path, config)
        
        if success:
            logger.info(f"Successfully enhanced: {output_path}")
            return 0
        else:
            logger.error("Enhancement failed")
            return 1
            
    except Exception as e:
        logger.error(f"Enhancement failed: {e}")
        return 1


def validate_command(args) -> int:
    """Handle the validate command."""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        logger.error(f"Input file does not exist: {input_path}")
        return 1
    
    try:
        # Use accessibility validator
        from validation.accessibility_validator import AccessibilityValidator
        
        validator = AccessibilityValidator()
        results = validator.validate(input_path)
        
        # Generate report if requested
        if hasattr(args, 'output') and args.output:
            report_format = getattr(args, 'report_format', 'json')
            success = validator.generate_report(results, args.output, report_format)
            if success:
                logger.info(f"Validation report saved to: {args.output}")
            else:
                logger.error("Failed to generate validation report")
                return 1
        else:
            # Print results to console
            print(f"Validation results for {input_path}:")
            print(f"Overall score: {results.get('overall_score', 'N/A')}")
            print(f"Issues found: {len(results.get('issues', []))}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return 1


def process_batch(processor, input_dir: Path, output_dir: Path, args) -> bool:
    """Process a batch of files."""
    logger = logging.getLogger(__name__)
    
    # Find all PDF files in input directory
    pdf_files = list(input_dir.glob("**/*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return False
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process files with threading if requested
    if args.max_workers > 1:
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            futures = []
            
            for pdf_file in pdf_files:
                rel_path = pdf_file.relative_to(input_dir)
                output_file = output_dir / rel_path
                
                # Create output directory
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Submit processing task
                future = executor.submit(
                    processor.process,
                    pdf_file,
                    output_file,
                    timeout=args.timeout,
                    title=args.title,
                    author=args.author, 
                    language=args.language
                )
                futures.append(future)
            
            # Wait for all tasks to complete
            success_count = 0
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        success_count += 1
                except Exception as e:
                    logger.error(f"Processing error: {e}")
            
            logger.info(f"Processed {success_count}/{len(pdf_files)} files successfully")
            return success_count == len(pdf_files)
    else:
        # Sequential processing
        success_count = 0
        for pdf_file in pdf_files:
            rel_path = pdf_file.relative_to(input_dir)
            output_file = output_dir / rel_path
            
            # Create output directory
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                result = processor.process(
                    pdf_file,
                    output_file,
                    timeout=args.timeout,
                    title=args.title,
                    author=args.author,
                    language=args.language
                )
                if result:
                    success_count += 1
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {e}")
        
        logger.info(f"Processed {success_count}/{len(pdf_files)} files successfully")
        return success_count == len(pdf_files)


def main():
    """Main CLI entry point."""
    parser = create_common_parser()
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process command
    process_parser = subparsers.add_parser(
        "process",
        help="Process documents with accessibility enhancements"
    )
    add_processing_arguments(process_parser)
    add_enhancement_arguments(process_parser)
    add_academic_arguments(process_parser)
    
    # Process-batch command  
    batch_parser = subparsers.add_parser(
        "process-batch",
        help="Process a batch of documents"
    )
    add_processing_arguments(batch_parser)
    add_enhancement_arguments(batch_parser)
    add_academic_arguments(batch_parser)
    
    # Enhance command
    enhance_parser = subparsers.add_parser(
        "enhance", 
        help="Apply accessibility enhancements to documents"
    )
    enhance_parser.add_argument("input", type=str, help="Input file")
    enhance_parser.add_argument("output", type=str, help="Output file")
    add_enhancement_arguments(enhance_parser)
    
    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate document accessibility"
    )
    validate_parser.add_argument("input", type=str, help="Input file")
    validate_parser.add_argument(
        "--output", 
        type=str, 
        help="Output file for validation report"
    )
    validate_parser.add_argument(
        "--report-format",
        type=str,
        choices=["json", "html", "csv"],
        default="json",
        help="Report format"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command in ["process", "process-batch"]:
        return process_command(args)
    elif args.command == "enhance":
        return enhance_command(args)
    elif args.command == "validate":
        return validate_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())