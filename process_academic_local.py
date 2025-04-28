#!/usr/bin/env python3
"""
Local academic paper processing script.

This script processes academic papers without requiring Docker,
using the unified_project structure and components.
"""

import argparse
import logging
import os
import sys
import time
import concurrent.futures
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import yaml
from PIL import Image

# Add project path to import modules from unified_project
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

# Increase PIL image size limit for large PDF documents
# This is needed to process very large academic posters and documents
Image.MAX_IMAGE_PIXELS = None  # Disable the DecompressionBomb check

# Import core components from unified_project
try:
    # Import unified_project core components
    from unified_project.src.core.service_container import ServiceContainer, get_container
    from unified_project.src.core.config import get_config_provider
    from unified_project.src.core.interfaces import DocumentProcessor, Enhancer
    
    # Import academic processing components
    from unified_project.src.academic.processor import AcademicProcessor, AcademicPaperConfig
    from unified_project.src.academic.structure_analyzer import AcademicStructureAnalyzer
    
    # Import enhancers for PDF accessibility
    from unified_project.src.enhancers.pdf_enhancer import PDFEnhancer
    
    # Required dependencies
    import fitz  # PyMuPDF
    import pikepdf
    import cv2
    import pytesseract
    import numpy as np
    from PIL import Image
    from pdf2image import convert_from_path
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure you have installed the required dependencies:")
    print("pip install pikepdf pytesseract opencv-python pillow numpy pyyaml pymupdf pdf2image")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("academic_processor_local")

class AcademicPaperProcessor(DocumentProcessor):
    """
    Local academic paper processor that integrates with the unified_project framework.
    
    This class serves as a bridge between the command-line interface and the
    academic processor components in the unified_project.
    """
    
    def __init__(self, config_path: Union[str, Path], options: Dict[str, Any] = None):
        """
        Initialize the academic paper processor.
        
        Args:
            config_path: Path to the configuration file
            options: Additional processing options
        """
        self.logger = logging.getLogger(__name__)
        self.options = options or {}
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Get the environment name from config path
        env_name = Path(config_path).stem if config_path else None
        
        # Initialize the service container
        self.container = self._setup_container(env_name)
        
        # Get required components from container
        self.academic_processor = self.container.get("academic_processor")
        self.structure_analyzer = self.container.get("structure_analyzer")
        
        # Always use PDF enhancer as specified
        self.enhancer = self.container.get("pdf_enhancer")
    
    def _load_config(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not config_path or not os.path.exists(config_path):
            self.logger.warning(f"Config file not found: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}
    
    def _setup_container(self, environment: Optional[str] = None) -> ServiceContainer:
        """Set up and configure the service container."""
        container = get_container()
        
        # Register configuration provider
        config_provider = get_config_provider()
        if not container.has("config_provider"):
            container.register_instance("config_provider", config_provider)
        
        # Register academic processor components
        container.register(
            "academic_processor", 
            lambda c: AcademicProcessor(self._create_academic_config()),
            singleton=True
        )
        
        container.register(
            "structure_analyzer", 
            lambda c: AcademicStructureAnalyzer(),
            singleton=True
        )
        
        # Register PDF enhancer
        container.register(
            "pdf_enhancer", 
            lambda c: PDFEnhancer(environment),
            singleton=True
        )
        
        return container
    
    def _create_academic_config(self) -> AcademicPaperConfig:
        """Create academic paper configuration from options and config file."""
        ocr_config = self.config.get('ocr', {})
        academic_config = self.config.get('academic', {})
        content_detection = self.config.get('content_detection', {})
        
        # Always enable table detection as required
        return AcademicPaperConfig(
            language=ocr_config.get('language', 'eng'),
            psm=ocr_config.get('psm', 1),
            oem=ocr_config.get('oem', 3),
            enhance_contrast=academic_config.get('preprocessing', {}).get('enhance_contrast', True),
            denoise=academic_config.get('preprocessing', {}).get('denoise', False),
            sharpen=academic_config.get('preprocessing', {}).get('sharpen', True),
            math_detection=self.options.get('math_detection', content_detection.get('formulas', True)),
            table_detection=True,  # Always enable table detection
            citation_detection=self.options.get('citation_detection', content_detection.get('citations', True)),
        )
    
    def process(self, input_path: Union[str, Path], output_path: Union[str, Path], **kwargs) -> bool:
        """
        Process an academic paper to enhance its accessibility.
        
        Args:
            input_path: Path to the input document
            output_path: Path where the processed document should be saved
            **kwargs: Additional processor-specific parameters
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        self.logger.info(f"Processing academic paper: {input_path}")
        start_time = time.time()
        file_name = Path(input_path).name
        
        try:
            timeout = kwargs.get('timeout', 1800)  # Default timeout: 30 minutes
            
            # Open the PDF with pikepdf for modification
            with pikepdf.open(input_path) as pdf:
                # Convert PDF pages to images for OCR and analysis
                page_images = self._convert_pdf_to_images(input_path)
                print(f"  [{file_name}] Converted {len(page_images)} pages to images")
                self.logger.info(f"Converted {len(page_images)} pages to images")
                
                # Process each page with the academic processor
                all_results = []
                page_errors = False
                for page_num, page_image in enumerate(page_images):
                    # Check for timeout
                    if time.time() - start_time > timeout:
                        self.logger.warning(f"Timeout reached ({timeout}s)")
                        break
                    
                    # Print status update for every 5th page or first/last page
                    if page_num == 0 or page_num == len(page_images)-1 or page_num % 5 == 0:
                        print(f"  [{file_name}] Processing page {page_num+1}/{len(page_images)}")
                        sys.stdout.flush()  # Force output to display
                    self.logger.info(f"Processing page {page_num+1} of {len(page_images)}")
                    
                    try:
                        # Process the page using the academic processor
                        page_results = self._process_page(page_image, page_num)
                        if 'error' in page_results:
                            page_errors = True
                        all_results.append(page_results)
                    except Exception as e:
                        self.logger.error(f"Error processing page {page_num}: {e}")
                        page_errors = True
                        all_results.append({'page': page_num, 'error': str(e)})
                
                if page_errors:
                    self.logger.warning("Some pages had processing errors")
                    return False
                
                # Extract the filename for title generation
                filename = str(Path(input_path).name)
                print(f"  [{file_name}] Enhancing PDF...")
                
                # Apply the content analysis to enhance the PDF
                enhanced_pdf = self.enhancer.enhance(
                    pdf,
                    filename=filename,
                    title=kwargs.get('title'),
                    author=kwargs.get('author'),
                    language=kwargs.get('language', 'en-US'),
                    extract_title_from_h1=True,  # Always use H1 detection for title
                    extract_title_from_filename=True,  # Use filename as fallback
                )
                
                # Save the enhanced PDF
                enhanced_pdf.save(output_path)
                
            processing_time = time.time() - start_time
            print(f"  [{file_name}] Completed in {processing_time:.2f}s")
            self.logger.info(f"Successfully processed in {processing_time:.2f}s: {output_path}")
            return True
                
        except Exception as e:
            self.logger.error(f"Error processing {input_path}: {e}")
            return False

    def _convert_pdf_to_images(self, pdf_path: Union[str, Path]) -> List[Image.Image]:
        """
        Convert PDF pages to PIL images for processing.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of PIL Image objects, one per page
        """
        try:
            file_name = Path(pdf_path).name
            print(f"  [{file_name}] Starting PDF conversion (this may take a while)...")
            sys.stdout.flush()  # Force output to display
            
            # First try to get PDF info to determine size
            import fitz  # PyMuPDF
            try:
                doc = fitz.open(pdf_path)
                num_pages = doc.page_count
                # Calculate approx document size based on first page
                if num_pages > 0:
                    first_page = doc[0]
                    width, height = first_page.rect.width, first_page.rect.height
                    page_area = width * height
                    doc.close()
                    
                    # Adjust DPI based on page size to prevent memory issues
                    if page_area > 1000000:  # Very large page (e.g., poster)
                        dpi = 200  # Lower DPI for large format documents
                        print(f"  [{file_name}] Large document detected - using 200 DPI")
                    elif page_area > 500000:  # Larger than standard
                        dpi = 250  # Medium DPI
                        print(f"  [{file_name}] Medium-large document - using 250 DPI")
                    else:
                        dpi = 300  # Standard DPI for normal documents
                        print(f"  [{file_name}] Normal document - using 300 DPI")
                else:
                    dpi = 300  # Default to lower DPI if can't determine
            except Exception:
                # If we can't get document info, default to lower DPI
                dpi = 300
                print(f"  [{file_name}] Unable to determine document size - using safe 300 DPI")
            
            sys.stdout.flush()  # Force output to display
            self.logger.info(f"Converting PDF to images with DPI={dpi}")
            
            # Add memory optimization for large PDFs
            # Using single-thread processing to avoid thread contention
            try:
                images = convert_from_path(
                    pdf_path, 
                    dpi=dpi,
                    # Disable multithreading to avoid resource contention
                    thread_count=1,
                    # Use memory-efficient mode
                    use_pdftocairo=True,
                    # Use grayscale to reduce memory usage if color not critical
                    grayscale=True
                )
            except Exception as conversion_error:
                # If conversion fails even with adjusted DPI, try with much lower DPI
                if "decompression bomb" in str(conversion_error) or "exceeds limit" in str(conversion_error):
                    print(f"  [{file_name}] First conversion attempt failed. Retrying with lower DPI...")
                    sys.stdout.flush()
                    images = convert_from_path(
                        pdf_path, 
                        dpi=100,  # Much lower DPI for problematic files
                        thread_count=1,
                        use_pdftocairo=True,
                        grayscale=True
                    )
                else:
                    # Re-raise if it's not a size-related error
                    raise
            
            print(f"  [{file_name}] PDF conversion complete. Found {len(images)} pages.")
            sys.stdout.flush()  # Force output to display
            return images
        except Exception as e:
            self.logger.error(f"Error converting PDF to images: {e}")
            print(f"  ERROR converting PDF to images: {e}")
            sys.stdout.flush()  # Force output to display
            raise RuntimeError(f"Failed to convert PDF to images: {e}")

    def _process_page(self, page_image: Image.Image, page_num: int) -> Dict[str, Any]:
        """
        Process a single page image using the academic processor.
        
        Args:
            page_image: PIL Image of the page
            page_num: Page number
            
        Returns:
            Dict containing OCR results and detected structures
        """
        try:
            # Use the academic processor to analyze the page
            results = self.academic_processor.process_academic_paper(page_image, page_num)
            
            # Additional structure analysis
            if hasattr(self.structure_analyzer, "detect_sections"):
                ocr_text = results.get('text', '')
                section_analysis = self.structure_analyzer.detect_sections(ocr_text)
                results['structure_analysis'] = section_analysis
                
                # Detect figures and tables using the structure analyzer
                if hasattr(self.structure_analyzer, "detect_figures_and_tables"):
                    figures_tables = self.structure_analyzer.detect_figures_and_tables(ocr_text)
                    results['figures_tables'] = figures_tables
                
                # Detect citations 
                if hasattr(self.structure_analyzer, "detect_citations"):
                    citation_results = self.structure_analyzer.detect_citations(ocr_text)
                    results['citations'] = citation_results
            
            return results
        except Exception as e:
            # Propagate the exception to be handled at the process level
            # This ensures the overall process is marked as failed when page processing fails
            self.logger.error(f"Error processing page {page_num}: {e}")
            raise RuntimeError(f"Error processing page {page_num}: {e}")

def process_file(processor, input_file, output_file, args):
    """
    Process a single file with the given processor.
    
    Args:
        processor: The document processor instance
        input_file: Path to the input file
        output_file: Path to the output file
        args: Command-line arguments
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    file_name = input_file.name
    print(f"\n▶ STARTED: {file_name}")
    logger.info(f"Processing file: {input_file}")
    
    # Create output directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    result = processor.process(
        input_file, 
        output_file,
        timeout=args.timeout,
        title=args.title,
        author=args.author,
        language=args.language
    )
    
    return result

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Local Academic Paper Accessibility Processor"
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="Input PDF file or directory containing PDF files"
    )
    
    parser.add_argument(
        "output",
        type=str,
        help="Output PDF file or directory for processed PDFs"
    )
    
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process a batch of documents from input directory"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="unified_project/config/academic.yaml",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Processing timeout in seconds per file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # Threading options
    parser.add_argument(
        "--max-workers",
        type=int,
        default=2,  # Default to lower thread count to avoid resource contention
        help="Maximum number of worker threads for parallel processing"
    )
    
    # Academic paper specific options
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
    
    return parser.parse_args()

def display_progress_bar(current, total, width=30):
    """Display a text-based progress bar with percentage."""
    progress = min(1.0, current / total) if total > 0 else 0
    filled_width = int(width * progress)
    bar = "█" * filled_width + "░" * (width - filled_width)
    percent = int(progress * 100)
    return f"[{bar}] {current}/{total} ({percent}%)"

def main():
    """Main entry point."""
    args = parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        # Reduce logging noise in console by setting higher log level
        logging.getLogger().setLevel(logging.WARNING)
        # Keep only the main logger at INFO level
        logger.setLevel(logging.INFO)
    
    # Convert arguments to options dictionary
    options = {
        "math_detection": args.detect_math,
        "table_detection": True,  # Always enable table detection
        "citation_detection": args.detect_citations,
    }
    
    # Initialize the academic paper processor
    processor = AcademicPaperProcessor(args.config, options)
    
    # Get terminal width for better formatting
    terminal_width = shutil.get_terminal_size().columns
    
    # Print banner
    print("\n" + "=" * terminal_width)
    print("  Academic Paper Accessibility Processor (Local Mode)".center(terminal_width))
    print("=" * terminal_width + "\n")
    
    print("Processing with settings:")
    print(f"  Mode:         Academic papers")
    print(f"  Enhancement:  PDF/UA compatible")
    print(f"  Tables:       Enabled")  # Always enabled
    print(f"  Math:         {'Enabled' if args.detect_math else 'Disabled'}")
    print(f"  Citations:    {'Enabled' if args.detect_citations else 'Disabled'}")
    print(f"  Timeout:      {args.timeout}s")
    print(f"  Batch:        {args.batch}")
    print(f"  Config:       {args.config}")
    print(f"  Max Workers:  {args.max_workers}")
    print()
    
    # Create output directory if needed
    output_path = Path(args.output)
    if args.batch:
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Process files
    if args.batch:
        # Find all PDF files in input directory
        input_dir = Path(args.input)
        pdf_files = list(input_dir.glob("**/*.pdf"))
        
        print(f"Processing batch:")
        print(f"  Input directory:  {args.input}")
        print(f"  Output directory: {args.output}")
        print(f"  Found {len(pdf_files)} PDF files to process")
        print(f"  Using {args.max_workers} worker threads")
        
        # Process files in parallel using ThreadPoolExecutor
        # This allows multiple documents to be processed concurrently
        # while keeping pages within each document sequential
        success_count = 0
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            # Create a list of future objects for each file
            future_to_file = {}
            
            for input_file in pdf_files:
                # Create relative path for output
                rel_path = input_file.relative_to(input_dir)
                output_file = output_path / rel_path
                
                # Submit file for processing
                future = executor.submit(
                    process_file, 
                    processor, 
                    input_file, 
                    output_file, 
                    args
                )
                future_to_file[future] = input_file
            
            # Track active tasks and create shared progress tracking
            active_tasks = {}
            completed_tasks = 0
            failed_tasks = 0
            total_tasks = len(pdf_files)
            
            # Display initial progress bar
            progress_bar = display_progress_bar(0, total_tasks)
            print(f"\nOverall Progress: {progress_bar}")
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                input_file = future_to_file[future]
                file_name = input_file.name
                
                try:
                    success = future.result()
                    if success:
                        success_count += 1
                        completed_tasks += 1
                        print(f"\n✓ COMPLETED: {file_name}")
                    else:
                        failed_tasks += 1
                        print(f"\n❌ FAILED: {file_name}")
                except Exception as e:
                    failed_tasks += 1
                    print(f"\n❌ ERROR: {file_name}")
                    print(f"  Error details: {e}")
                
                # Update progress bar after each file is processed
                processed = completed_tasks + failed_tasks
                progress_bar = display_progress_bar(processed, total_tasks)
                print(f"Overall Progress: {progress_bar}")
                print(f"Success: {completed_tasks} | Failed: {failed_tasks} | Remaining: {total_tasks - processed}")
                sys.stdout.flush()  # Force output to display
        
        total_time = time.time() - start_time
        avg_time_per_file = total_time / total_tasks if total_tasks > 0 else 0
        
        # Final summary
        print("\n" + "=" * shutil.get_terminal_size().columns)
        print(f"Processing Complete:")
        print(f"- Successfully processed: {success_count}/{len(pdf_files)} files")
        print(f"- Total processing time: {total_time:.2f}s")
        print(f"- Average time per file: {avg_time_per_file:.2f}s")
    else:
        # Process single file
        input_path = Path(args.input)
        output_path = Path(args.output)
        
        success = processor.process(
            input_path, 
            output_path,
            timeout=args.timeout,
            title=args.title,
            author=args.author,
            language=args.language
        )
        
        if not success:
            print("\n❌ Processing failed")
            return 1
    
    print("\n✓ Processing complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())