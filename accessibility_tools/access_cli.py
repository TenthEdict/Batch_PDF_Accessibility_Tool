#!/usr/bin/env python3
"""
PDF Accessibility Tools CLI

A unified command-line interface for all PDF accessibility tools.

Usage:
  python access_cli.py enhance <input> <output> [options]
  python access_cli.py batch-enhance <input_dir> <output_dir> [options]
  python access_cli.py validate <input> [options]
  python access_cli.py batch-validate <input_dir> <output_dir> [options]
  python access_cli.py analyze <input> [options]
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

# Import command functions
try:
    from accessibility_tools.core.enhance_pdf import enhance_pdf_accessibility as basic_enhance
    from accessibility_tools.core.enhance_pdf_journal import process_directory as journal_enhance
    from accessibility_tools.core.enhance_pdf_advanced import enhance_pdf_accessibility as advanced_enhance
    from accessibility_tools.core.enhance_pdf_advanced import process_directory as batch_advanced_enhance
    from accessibility_tools.validation.validate_accessibility import AccessibilityChecker, print_report
    from accessibility_tools.validation.batch_validate import process_directory as batch_validate
except ImportError as e:
    # Handle relative imports for direct execution
    try:
        sys.path.append(str(Path(__file__).parent))
        from core.enhance_pdf import enhance_pdf_accessibility as basic_enhance
        from core.enhance_pdf_journal import process_directory as journal_enhance
        from core.enhance_pdf_advanced import enhance_pdf_accessibility as advanced_enhance
        from core.enhance_pdf_advanced import process_directory as batch_advanced_enhance
        from validation.validate_accessibility import AccessibilityChecker, print_report
        from validation.batch_validate import process_directory as batch_validate
    except ImportError:
        print(f"Error importing required modules: {e}")
        print("Make sure you're running this script from the project root or accessibility_tools directory.")
        sys.exit(1)

def enhance_command(args):
    """Run enhance command with the appropriate enhancer based on level"""
    input_path = args.input
    output_path = args.output
    
    print(f"Enhancing PDF: {input_path}")
    print(f"Enhancement level: {args.level}")
    
    if args.level == "basic":
        result = basic_enhance(input_path, output_path, args.title, args.author)
    elif args.level == "journal":
        # For journal, we'll run the single file version
        result = basic_enhance(input_path, output_path, args.title, args.author)
    elif args.level == "advanced":
        result = advanced_enhance(input_path, output_path, args.title, args.author, args.language)
    else:
        print(f"Unknown enhancement level: {args.level}")
        return 1
        
    if result:
        print(f"Enhancement completed successfully: {output_path}")
        return 0
    else:
        print("Enhancement failed")
        return 1

def batch_enhance_command(args):
    """Run batch enhance command with the appropriate enhancer"""
    input_dir = args.input_dir
    output_dir = args.output_dir
    
    print(f"Batch enhancing PDFs in directory: {input_dir}")
    print(f"Enhancement level: {args.level}")
    
    if args.level == "basic" or args.level == "journal":
        result = journal_enhance(input_dir, output_dir)
    elif args.level == "advanced":
        result = batch_advanced_enhance(input_dir, output_dir)
    else:
        print(f"Unknown enhancement level: {args.level}")
        return 1
        
    if result:
        print(f"Batch enhancement completed successfully. Results saved to: {output_dir}")
        return 0
    else:
        print("Batch enhancement failed")
        return 1

def validate_command(args):
    """Run validate command"""
    pdf_path = args.input
    
    print(f"Validating PDF: {pdf_path}")
    
    checker = AccessibilityChecker(pdf_path)
    results = checker.check(detailed=args.detailed)
    
    print_report(results, detailed=args.detailed)
    
    if args.json:
        import json
        with open(args.json, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {args.json}")
    
    return 0 if results["is_accessible"] else 1

def batch_validate_command(args):
    """Run batch validate command"""
    input_dir = args.input_dir
    output_dir = args.output_dir
    
    print(f"Batch validating PDFs in directory: {input_dir}")
    
    result = batch_validate(
        input_dir, 
        output_dir, 
        detailed=not args.simple,
        max_workers=args.workers
    )
    
    if result:
        print(f"Batch validation completed successfully. Reports saved to: {output_dir}")
        return 0
    else:
        print("Batch validation failed")
        return 1

def analyze_command(args):
    """Run analyze command"""
    # This is a simplified analysis that calls the validator with detailed output
    pdf_path = args.input
    
    print(f"Analyzing PDF structure: {pdf_path}")
    
    checker = AccessibilityChecker(pdf_path)
    results = checker.check(detailed=True)
    
    print_report(results, detailed=True)
    
    if args.json:
        import json
        with open(args.json, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Analysis results saved to: {args.json}")
    
    return 0

def main():
    # Create main parser
    parser = argparse.ArgumentParser(
        description="PDF Accessibility Tools CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Enhance command
    enhance_parser = subparsers.add_parser("enhance", help="Enhance a single PDF with accessibility features")
    enhance_parser.add_argument("input", help="Input PDF file")
    enhance_parser.add_argument("output", help="Output PDF file")
    enhance_parser.add_argument("--level", choices=["basic", "journal", "advanced"], default="advanced", 
                              help="Enhancement level (default: advanced)")
    enhance_parser.add_argument("--title", help="Document title")
    enhance_parser.add_argument("--author", help="Document author")
    enhance_parser.add_argument("--language", default="en-US", help="Document language (default: en-US)")
    
    # Batch enhance command
    batch_enhance_parser = subparsers.add_parser("batch-enhance", help="Enhance multiple PDFs in a directory")
    batch_enhance_parser.add_argument("input_dir", help="Input directory containing PDFs")
    batch_enhance_parser.add_argument("output_dir", help="Output directory for enhanced PDFs")
    batch_enhance_parser.add_argument("--level", choices=["basic", "journal", "advanced"], default="advanced", 
                                    help="Enhancement level (default: advanced)")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate PDF accessibility")
    validate_parser.add_argument("input", help="PDF file to validate")
    validate_parser.add_argument("--detailed", action="store_true", help="Show detailed validation report")
    validate_parser.add_argument("--json", help="Save validation results to JSON file")
    
    # Batch validate command
    batch_validate_parser = subparsers.add_parser("batch-validate", help="Validate multiple PDFs in a directory")
    batch_validate_parser.add_argument("input_dir", help="Input directory containing PDFs")
    batch_validate_parser.add_argument("output_dir", help="Output directory for validation reports")
    batch_validate_parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers (default: 4)")
    batch_validate_parser.add_argument("--simple", action="store_true", help="Generate simplified reports")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze PDF structure and accessibility")
    analyze_parser.add_argument("input", help="PDF file to analyze")
    analyze_parser.add_argument("--json", help="Save analysis results to JSON file")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run command
    if args.command == "enhance":
        return enhance_command(args)
    elif args.command == "batch-enhance":
        return batch_enhance_command(args)
    elif args.command == "validate":
        return validate_command(args)
    elif args.command == "batch-validate":
        return batch_validate_command(args)
    elif args.command == "analyze":
        return analyze_command(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())