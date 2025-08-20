#!/usr/bin/env python3
"""
Advanced PDFEnhancer Batch Processing System

This module implements a sophisticated batch processing solution that combines
the validated reliability of the PDFEnhancer component with comprehensive
operational monitoring, error handling, and quality assurance capabilities.

Architecture:
- Processing Engine: Direct PDFEnhancer integration with optimal parameters
- Operational Management: Comprehensive logging, progress tracking, error handling
- Quality Assurance: Post-processing validation and accessibility metrics
- Result Documentation: Detailed reporting with actionable insights
"""

import sys
import json
import time
from pathlib import Path
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import traceback

# Third-party imports for enhanced functionality
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Info: tqdm not available, progress bar disabled")

# Core component imports - updated for unified architecture
from ..enhancers.pdf_enhancer import PDFEnhancer
from ..enhancers.ocr_enhancer import OCREnhancer#!/usr/bin/env python3
"""
Advanced PDFEnhancer Batch Processing System

This module implements a sophisticated batch processing solution that combines
the validated reliability of the PDFEnhancer component with comprehensive
operational monitoring, error handling, and quality assurance capabilities.

Architecture:
- Processing Engine: Direct PDFEnhancer integration with optimal parameters
- Operational Management: Comprehensive logging, progress tracking, error handling
- Quality Assurance: Post-processing validation and accessibility metrics
- Result Documentation: Detailed reporting with actionable insights
"""

import sys
import json
import time
from pathlib import Path
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import traceback

# Third-party imports for enhanced functionality
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Info: tqdm not available, progress bar disabled")

# Core component imports - updated for unified architecture
from ..enhancers.pdf_enhancer import PDFEnhancer
from ..enhancers.ocr_enhancer import OCREnhancer


class BatchProcessingConfiguration:
    """
    Configuration management for batch processing operations.
    
    This class encapsulates all processing parameters and operational settings
    to ensure consistent behavior across batch operations.
    """
    
    def __init__(self, input_dir: str = 'data/input', output_dir: str = 'data/output/enhanced_batch', 
                 log_dir: str = 'logs', enable_detailed_logging: bool = True, enhancement_params: Optional[Dict] = None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.log_dir = Path(log_dir)
        
        # Processing parameters optimized from component testing
        self.enhancement_params = enhancement_params or {
            'language': 'en-US',
            'extract_title_from_h1': True,
            'extract_title_from_filename': True,
            'display_doc_title': True
        }
        
        # Operational configuration
        self.enable_progress_bar = TQDM_AVAILABLE
        self.enable_detailed_logging = enable_detailed_logging
        self.enable_quality_validation = True
        self.generate_processing_report = True
        self.force_ocr = True  # Always perform OCR on all files        
    def validate_configuration(self) -> bool:
        """Validate configuration parameters and directory accessibility."""
        try:
            if not self.input_dir.exists():
                raise FileNotFoundError(f"Input directory not found: {self.input_dir}")
            
            # Create output and log directories
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


class ProcessingMetrics:
    """
    Comprehensive metrics collection and analysis for batch processing operations.
    
    This class provides detailed tracking of processing performance, quality metrics,
    and operational statistics for production monitoring and optimization.
    """
    
    def __init__(self, total_files: int = 0, successful_files: int = 0, failed_files: int = 0, 
                 processing_time: float = 0.0, total_size_mb: float = 0.0, compression_ratio: float = 0.0):
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.successful_files: List[Dict] = []
        self.failed_files: List[Dict] = []
        self.processing_times: List[float] = []
        self.file_size_statistics: Dict = {}
        
        # Phase 2B Enhanced Processor compatibility parameters
        self.total_files_count = total_files
        self.initial_successful_count = successful_files
        self.initial_failed_count = failed_files
        self.initial_processing_time = processing_time
        self.total_size_mb = total_size_mb
        self.compression_ratio = compression_ratio
        
    def record_success(self, input_file: Path, output_file: Path, processing_time: float):
        """Record successful file processing with comprehensive metrics."""
        try:
            input_size = input_file.stat().st_size if input_file.exists() else 0
            output_size = output_file.stat().st_size if output_file.exists() else 0
            
            success_record = {
                'input_file': str(input_file),
                'output_file': str(output_file),
                'processing_time': processing_time,
                'input_size': input_size,
                'output_size': output_size,
                'size_change': output_size - input_size,
                'timestamp': datetime.now().isoformat()
            }
            
            self.successful_files.append(success_record)
            self.processing_times.append(processing_time)
            
        except Exception as e:
            print(f"Warning: Could not record success metrics: {e}")
            
    def record_failure(self, input_file: Path, error_message: str, processing_time: Optional[float] = None):
        """Record failed file processing with error details."""
        failure_record = {
            'input_file': str(input_file),
            'error_message': error_message,
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat()
        }
        
        self.failed_files.append(failure_record)
        
        if processing_time is not None:
            self.processing_times.append(processing_time)        
    def finalize_metrics(self):
        """Finalize metrics collection and compute summary statistics."""
        self.end_time = datetime.now()
        
        if self.processing_times:
            self.file_size_statistics = {
                'total_files_processed': len(self.successful_files) + len(self.failed_files),
                'successful_files': len(self.successful_files),
                'failed_files': len(self.failed_files),
                'success_rate': len(self.successful_files) / (len(self.successful_files) + len(self.failed_files)) * 100,
                'average_processing_time': sum(self.processing_times) / len(self.processing_times),
                'total_processing_time': sum(self.processing_times),
                'total_duration': (self.end_time - self.start_time).total_seconds()
            }
        
    def generate_report(self) -> Dict:
        """Generate comprehensive processing report."""
        self.finalize_metrics()
        
        return {
            'processing_summary': self.file_size_statistics,
            'successful_files': self.successful_files,
            'failed_files': self.failed_files,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None
        }


class AdvancedBatchProcessor:
    """
    Advanced batch processing system for PDF accessibility enhancement.
    
    This class orchestrates the complete batch processing workflow, integrating
    the validated PDFEnhancer component with comprehensive operational monitoring,
    error handling, and quality assurance capabilities.
    """
    
    def __init__(self, config: BatchProcessingConfiguration):
        self.config = config
        self.metrics = ProcessingMetrics()
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Configure logging for batch processing operations."""
        logger = logging.getLogger('AdvancedBatchProcessor')
        
        if self.config.enable_detailed_logging:
            handler = logging.FileHandler(self.config.log_dir / 'batch_processing.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
        return logger    
    def process_batch(self) -> bool:
        """
        Execute batch processing of all PDF files in the input directory.
        
        Returns:
            bool: True if batch processing completed successfully, False otherwise
        """
        try:
            # Validate configuration
            if not self.config.validate_configuration():
                return False
            
            # Find all PDF files
            pdf_files = list(self.config.input_dir.glob("*.pdf"))
            
            if not pdf_files:
                self.logger.warning(f"No PDF files found in {self.config.input_dir}")
                return False
            
            self.logger.info(f"Starting batch processing of {len(pdf_files)} files")
            
            # Initialize progress bar if available
            iterator = tqdm(pdf_files, desc="Processing PDFs") if self.config.enable_progress_bar else pdf_files
            
            # Process each file
            for pdf_file in iterator:
                self._process_single_file(pdf_file)
            
            # Generate final report
            if self.config.generate_processing_report:
                self._generate_final_report()
            
            self.logger.info("Batch processing completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {str(e)}")
            return False
    
    def _process_single_file(self, input_file: Path):
        """Process a single PDF file with comprehensive error handling."""
        start_time = time.time()
        # Create output filename with "_enhanced" suffix instead of "enhanced_" prefix
        base_name = input_file.stem  # filename without extension
        extension = input_file.suffix  # .pdf
        output_file = self.config.output_dir / f"{base_name}_enhanced{extension}"
        
        try:
            self.logger.info(f"Processing: {input_file.name}")
            
            # Import here to avoid circular imports
            from ..services.enhancement_service import EnhancementService
            
            # Process the file using the unified enhancement service
            enhancement_service = EnhancementService()
            success = enhancement_service.enhance_document(
                input_file, 
                output_file, 
                mode="academic",
                **self.config.enhancement_params
            )
            
            processing_time = time.time() - start_time
            
            if success:
                self.metrics.record_success(input_file, output_file, processing_time)
                self.logger.info(f"Successfully processed: {input_file.name}")
            else:
                self.metrics.record_failure(input_file, "Enhancement service returned False", processing_time)
                self.logger.error(f"Failed to process: {input_file.name}")
                
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"Exception during processing: {str(e)}"
            self.metrics.record_failure(input_file, error_message, processing_time)
            self.logger.error(f"Error processing {input_file.name}: {error_message}")
    
    def _generate_final_report(self):
        """Generate and save the final processing report."""
        try:
            report = self.metrics.generate_report()
            report_path = self.config.output_dir / "batch_processing_report.json"
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Processing report saved to: {report_path}")
            
            # Print summary to console
            summary = report['processing_summary']
            print(f"\n--- Batch Processing Summary ---")
            print(f"Total files: {summary.get('total_files_processed', 0)}")
            print(f"Successful: {summary.get('successful_files', 0)}")
            print(f"Failed: {summary.get('failed_files', 0)}")
            print(f"Success rate: {summary.get('success_rate', 0):.1f}%")
            print(f"Total duration: {summary.get('total_duration', 0):.1f} seconds")
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {str(e)}")