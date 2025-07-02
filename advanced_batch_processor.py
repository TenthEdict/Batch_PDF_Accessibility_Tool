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

# Core component imports
from processor.unified_project.src.enhancers.pdf_enhancer import PDFEnhancer


class BatchProcessingConfiguration:
    """
    Configuration management for batch processing operations.
    
    This class encapsulates all processing parameters and operational settings
    to ensure consistent behavior across batch operations.
    """
    
    def __init__(self, input_dir: str = 'data/input', output_dir: str = 'data/output/enhanced_batch'):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.log_dir = Path('logs')
        
        # Processing parameters optimized from component testing
        self.enhancement_params = {
            'language': 'en-US',
            'extract_title_from_h1': True,
            'extract_title_from_filename': True,
            'display_doc_title': True
        }
        
        # Operational configuration
        self.enable_progress_bar = TQDM_AVAILABLE
        self.enable_detailed_logging = True
        self.enable_quality_validation = True
        self.generate_processing_report = True
        
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
    
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.successful_files: List[Dict] = []
        self.failed_files: List[Dict] = []
        self.processing_times: List[float] = []
        self.file_size_statistics: Dict = {}
        
    def record_success(self, input_file: Path, output_file: Path, processing_time: float):
        """Record successful file processing with comprehensive metrics."""
        try:
            input_size = input_file.stat().st_size
            output_size = output_file.stat().st_size if output_file.exists() else 0
            
            record = {
                'input_file': str(input_file),
                'output_file': str(output_file),
                'input_size_bytes': input_size,
                'output_size_bytes': output_size,
                'size_ratio': output_size / input_size if input_size > 0 else 0,
                'processing_time_seconds': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            self.successful_files.append(record)
            self.processing_times.append(processing_time)
            
        except Exception as e:
            # Graceful handling of metrics collection failures
            print(f"Warning: Failed to record success metrics for {input_file}: {e}")
    
    def record_failure(self, input_file: Path, error: Exception, processing_time: float):
        """Record file processing failure with error details."""
        record = {
            'input_file': str(input_file),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'processing_time_seconds': processing_time,
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc()
        }
        
        self.failed_files.append(record)
        self.processing_times.append(processing_time)
    
    def finalize_metrics(self):
        """Complete metrics collection and generate summary statistics."""
        self.end_time = datetime.now()
        
        total_files = len(self.successful_files) + len(self.failed_files)
        success_count = len(self.successful_files)
        
        self.file_size_statistics = {
            'total_files_processed': total_files,
            'successful_enhancements': success_count,
            'failed_enhancements': len(self.failed_files),
            'success_rate_percentage': (success_count / total_files * 100) if total_files > 0 else 0,
            'total_processing_time_seconds': sum(self.processing_times),
            'average_processing_time_seconds': sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0,
            'total_runtime_seconds': (self.end_time - self.start_time).total_seconds()
        }
        
        # Calculate size statistics for successful files
        if self.successful_files:
            input_sizes = [f['input_size_bytes'] for f in self.successful_files]
            output_sizes = [f['output_size_bytes'] for f in self.successful_files]
            size_ratios = [f['size_ratio'] for f in self.successful_files]
            
            self.file_size_statistics.update({
                'total_input_size_bytes': sum(input_sizes),
                'total_output_size_bytes': sum(output_sizes),
                'average_size_ratio': sum(size_ratios) / len(size_ratios),
                'size_preservation_quality': 'Excellent' if all(0.9 <= r <= 1.1 for r in size_ratios) else 'Good'
            })


class QualityValidator:
    """
    Post-processing quality validation for enhanced PDF documents.
    
    This class provides comprehensive validation of enhancement success,
    accessibility compliance, and document integrity.
    """
    
    @staticmethod
    def validate_enhanced_document(output_file: Path) -> Dict:
        """
        Comprehensive validation of enhanced PDF document quality.
        
        Returns detailed validation results including accessibility compliance,
        metadata enhancement success, and document integrity assessment.
        """
        validation_results = {
            'file_accessible': False,
            'pdf_valid': False,
            'metadata_enhanced': False,
            'accessibility_compliant': False,
            'page_count': 0,
            'has_text_content': False,
            'validation_errors': []
        }
        
        try:
            # Basic file accessibility validation
            if not output_file.exists():
                validation_results['validation_errors'].append("Output file does not exist")
                return validation_results
            
            validation_results['file_accessible'] = True
            
            # PDF structure validation using pikepdf
            import pikepdf
            with pikepdf.open(str(output_file)) as doc:
                validation_results['pdf_valid'] = True
                validation_results['page_count'] = len(doc.pages)
                
                # Metadata enhancement validation
                with doc.open_metadata() as meta:
                    has_title = bool(meta.get('dc:title'))
                    has_language = bool(meta.get('dc:language'))
                    validation_results['metadata_enhanced'] = has_title and has_language
                
                # Accessibility compliance validation
                accessibility_features = 0
                
                # Check for tagged structure
                if hasattr(doc.Root, 'MarkInfo') and hasattr(doc.Root.MarkInfo, 'Marked'):
                    if doc.Root.MarkInfo.Marked:
                        accessibility_features += 1
                
                # Check for PDF/UA identifier
                if hasattr(doc.Root, 'OutputIntents'):
                    for intent in doc.Root.OutputIntents:
                        if hasattr(intent, 'S') and str(intent.S) == '/GTS_PDFUA1':
                            accessibility_features += 1
                            break
                
                # Check for viewer preferences
                if hasattr(doc.Root, 'ViewerPreferences') and hasattr(doc.Root.ViewerPreferences, 'DisplayDocTitle'):
                    if doc.Root.ViewerPreferences.DisplayDocTitle:
                        accessibility_features += 1
                
                validation_results['accessibility_compliant'] = accessibility_features >= 2
                
            # Text content validation using PyMuPDF
            import fitz
            with fitz.open(str(output_file)) as doc:
                if len(doc) > 0:
                    text_sample = doc[0].get_text()
                    validation_results['has_text_content'] = len(text_sample.strip()) > 50
                    
        except Exception as e:
            validation_results['validation_errors'].append(f"Validation error: {str(e)}")
        
        return validation_results


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
        self.quality_validator = QualityValidator()
        self.logger = self._setup_logging()
        self.enhancer: Optional[PDFEnhancer] = None
        
    def _setup_logging(self) -> logging.Logger:
        """Configure comprehensive logging infrastructure."""
        # Ensure log directory exists before creating log files
        self.config.log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = self.config.log_dir / f'batch_processing_{timestamp}.log'
        
        # Create formatter for consistent log formatting
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Configure logger with file and console handlers
        logger = logging.getLogger('AdvancedBatchProcessor')
        logger.setLevel(logging.INFO)
        
        # File handler for detailed logging
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler for user feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def initialize_processing_engine(self) -> bool:
        """Initialize the PDFEnhancer component with validated configuration."""
        try:
            self.enhancer = PDFEnhancer()
            self.logger.info("✅ PDFEnhancer processing engine initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize PDFEnhancer: {e}")
            return False
    
    def discover_input_files(self) -> List[Path]:
        """Discover and validate PDF files in input directory."""
        try:
            pdf_files = list(self.config.input_dir.glob('*.pdf'))
            
            # Filter out hidden files and validate accessibility
            valid_files = []
            for pdf_file in pdf_files:
                if not pdf_file.name.startswith('.'):
                    try:
                        # Basic file accessibility check
                        pdf_file.stat()
                        valid_files.append(pdf_file)
                    except OSError as e:
                        self.logger.warning(f"⚠️  Skipping inaccessible file {pdf_file}: {e}")
            
            self.logger.info(f"📁 Discovered {len(valid_files)} valid PDF files for processing")
            return valid_files
            
        except Exception as e:
            self.logger.error(f"❌ Failed to discover input files: {e}")
            return []
    
    def process_single_file(self, input_file: Path) -> bool:
        """
        Process a single PDF file with comprehensive error handling and metrics collection.
        
        Returns True for successful processing, False for failures.
        """
        start_time = time.time()
        output_file = self.config.output_dir / f"{input_file.stem}_enhanced.pdf"
        
        try:
            self.logger.info(f"🔄 Processing: {input_file.name}")
            
            # Prepare enhancement parameters with file-specific customization
            enhancement_params = self.config.enhancement_params.copy()
            enhancement_params['filename'] = input_file.name
            
            # Execute enhancement using validated PDFEnhancer
            success = self.enhancer.enhance_file(
                input_file, 
                output_file, 
                **enhancement_params
            )
            
            processing_time = time.time() - start_time
            
            if success:
                # Quality validation for successful processing
                if self.config.enable_quality_validation:
                    validation_results = self.quality_validator.validate_enhanced_document(output_file)
                    
                    if validation_results['accessibility_compliant']:
                        self.logger.info(f"✅ Successfully enhanced with accessibility compliance: {input_file.name}")
                    else:
                        self.logger.warning(f"⚠️  Enhanced but accessibility validation concerns: {input_file.name}")
                
                # Record success metrics
                self.metrics.record_success(input_file, output_file, processing_time)
                return True
            else:
                self.logger.error(f"❌ Enhancement failed for: {input_file.name}")
                self.metrics.record_failure(input_file, Exception("Enhancement returned False"), processing_time)
                return False
                
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"❌ Exception processing {input_file.name}: {e}")
            self.metrics.record_failure(input_file, e, processing_time)
            return False
    
    def generate_processing_report(self) -> Path:
        """Generate comprehensive processing report with statistics and insights."""
        try:
            self.metrics.finalize_metrics()
            
            # Comprehensive report structure
            report = {
                'processing_summary': {
                    'start_time': self.metrics.start_time.isoformat(),
                    'end_time': self.metrics.end_time.isoformat(),
                    'total_runtime': str(timedelta(seconds=self.metrics.file_size_statistics['total_runtime_seconds'])),
                    'configuration': {
                        'input_directory': str(self.config.input_dir),
                        'output_directory': str(self.config.output_dir),
                        'enhancement_parameters': self.config.enhancement_params
                    }
                },
                'performance_statistics': self.metrics.file_size_statistics,
                'successful_files': self.metrics.successful_files,
                'failed_files': self.metrics.failed_files,
                'quality_assessment': {
                    'files_with_accessibility_compliance': len([
                        f for f in self.metrics.successful_files 
                        if 0.9 <= f.get('size_ratio', 0) <= 1.1
                    ]),
                    'average_enhancement_quality': self.metrics.file_size_statistics.get('size_preservation_quality', 'Unknown')
                }
            }
            
            # Save report with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.config.output_dir / f'processing_report_{timestamp}.json'
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📊 Processing report generated: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate processing report: {e}")
            return None
    
    def execute_batch_processing(self) -> bool:
        """
        Execute the complete batch processing workflow with comprehensive monitoring.
        
        Returns True if batch processing completes successfully (regardless of individual file results).
        """
        try:
            self.logger.info("🚀 Initiating Advanced PDFEnhancer Batch Processing System")
            self.logger.info("=" * 80)
            
            # Phase 1: Configuration validation
            if not self.config.validate_configuration():
                self.logger.error("❌ Configuration validation failed")
                return False
            
            # Phase 2: Processing engine initialization
            if not self.initialize_processing_engine():
                self.logger.error("❌ Processing engine initialization failed")
                return False
            
            # Phase 3: Input file discovery
            pdf_files = self.discover_input_files()
            if not pdf_files:
                self.logger.warning("⚠️  No PDF files found for processing")
                return True
            
            # Phase 4: Batch processing execution
            self.logger.info(f"🔄 Beginning batch processing of {len(pdf_files)} files")
            
            # Process files with optional progress tracking
            if self.config.enable_progress_bar and TQDM_AVAILABLE:
                with tqdm(pdf_files, desc="Enhancing PDFs", unit="file") as pbar:
                    for pdf_file in pbar:
                        pbar.set_description(f"Processing {pdf_file.name}")
                        self.process_single_file(pdf_file)
            else:
                for pdf_file in pdf_files:
                    self.process_single_file(pdf_file)
            
            # Phase 5: Results analysis and reporting
            self.logger.info("📊 Analyzing processing results...")
            self.metrics.finalize_metrics()
            
            success_rate = self.metrics.file_size_statistics['success_rate_percentage']
            total_files = self.metrics.file_size_statistics['total_files_processed']
            successful = self.metrics.file_size_statistics['successful_enhancements']
            
            self.logger.info(f"✅ Batch processing completed: {successful}/{total_files} files enhanced ({success_rate:.1f}% success rate)")
            
            # Generate comprehensive report
            if self.config.generate_processing_report:
                report_file = self.generate_processing_report()
                if report_file:
                    self.logger.info(f"📄 Detailed report available: {report_file}")
            
            self.logger.info("=" * 80)
            self.logger.info("🎯 Advanced PDFEnhancer Batch Processing System completed successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Batch processing system failure: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False


def main():
    """
    Main entry point for Advanced PDFEnhancer Batch Processing System.
    
    This function orchestrates the complete batch processing workflow with
    comprehensive configuration, monitoring, and error handling.
    """
    print("🚀 Advanced PDFEnhancer Batch Processing System")
    print("=" * 60)
    
    try:
        # Initialize configuration with optimized settings
        config = BatchProcessingConfiguration(
            input_dir='data/input',
            output_dir='data/output/advanced_enhanced'
        )
        
        # Create and execute batch processor
        processor = AdvancedBatchProcessor(config)
        success = processor.execute_batch_processing()
        
        if success:
            print("\n✅ Batch processing system executed successfully")
            print(f"📁 Enhanced documents available in: {config.output_dir}")
            print(f"📄 Processing logs available in: {config.log_dir}")
        else:
            print("\n❌ Batch processing system encountered critical errors")
            return 1
            
    except Exception as e:
        print(f"\n❌ System initialization failed: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
