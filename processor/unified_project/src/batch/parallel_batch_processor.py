#!/usr/bin/env python3
"""
Parallel Batch Processing System for ePubs Accessibility Enhancement

This module implements high-performance parallel batch processing with:
- ThreadPoolExecutor for concurrent document processing
- Dynamic worker scaling based on system resources
- Memory monitoring and automatic throttling
- Enhanced performance tracking for parallel operations
- Thread-safe ML pattern matching optimization
- Backward compatibility with existing batch processor

Architecture:
- Parallel Processing Engine: ThreadPoolExecutor with dynamic scaling
- Resource Management: Memory monitoring and worker throttling
- ML Optimization: Thread-safe adaptive ML enhancer integration
- Performance Monitoring: Enhanced tracking for parallel operations
"""

import sys
import json
import time
import threading
import queue
from pathlib import Path
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable, Any
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
import multiprocessing
import platform

# Resource monitoring imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available - resource monitoring disabled")

# Progress bar support
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Info: tqdm not available - progress bar disabled")

# Core component imports
from .advanced_batch_processor import BatchProcessingConfiguration, ProcessingMetrics
from ..services.enhancement_service import EnhancementService
from ..monitoring.performance_tracker import get_performance_tracker

logger = logging.getLogger(__name__)


class ResourceMonitor:
    """
    System resource monitoring for dynamic worker scaling.
    
    Monitors CPU, memory, and disk usage to optimize parallel processing
    performance without overwhelming system resources.
    """
    
    def __init__(self, memory_threshold: float = 0.85, cpu_threshold: float = 0.80):
        """
        Initialize resource monitor.
        
        Args:
            memory_threshold: Memory usage threshold (0.0-1.0) for throttling
            cpu_threshold: CPU usage threshold (0.0-1.0) for throttling
        """
        self.memory_threshold = memory_threshold
        self.cpu_threshold = cpu_threshold
        self.monitoring_active = PSUTIL_AVAILABLE
        self._lock = threading.Lock()
        
        # Resource usage history
        self.memory_history = []
        self.cpu_history = []
        self.max_history_size = 10
        
        logger.info(f"Resource monitor initialized - Memory threshold: {memory_threshold:.1%}, CPU threshold: {cpu_threshold:.1%}")
    
    def get_current_usage(self) -> Dict[str, float]:
        """Get current system resource usage."""
        if not self.monitoring_active:
            return {'memory_percent': 0.5, 'cpu_percent': 0.5, 'available_memory_gb': 4.0}
        
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            usage = {
                'memory_percent': memory.percent / 100.0,
                'cpu_percent': cpu_percent / 100.0,
                'available_memory_gb': memory.available / (1024**3),
                'total_memory_gb': memory.total / (1024**3)
            }
            
            # Update history
            with self._lock:
                self.memory_history.append(usage['memory_percent'])
                self.cpu_history.append(usage['cpu_percent'])
                
                # Trim history
                if len(self.memory_history) > self.max_history_size:
                    self.memory_history.pop(0)
                if len(self.cpu_history) > self.max_history_size:
                    self.cpu_history.pop(0)
            
            return usage
            
        except Exception as e:
            logger.warning(f"Resource monitoring failed: {e}")
            return {'memory_percent': 0.5, 'cpu_percent': 0.5, 'available_memory_gb': 4.0}
    
    def should_throttle(self) -> bool:
        """Check if processing should be throttled due to resource usage."""
        usage = self.get_current_usage()
        
        memory_throttle = usage['memory_percent'] > self.memory_threshold
        cpu_throttle = usage['cpu_percent'] > self.cpu_threshold
        
        if memory_throttle or cpu_throttle:
            logger.warning(f"Resource throttling triggered - Memory: {usage['memory_percent']:.1%}, CPU: {usage['cpu_percent']:.1%}")
            return True
        
        return False
    
    def get_optimal_worker_count(self, max_workers: Optional[int] = None) -> int:
        """
        Calculate optimal worker count based on system resources.
        
        Args:
            max_workers: Maximum number of workers allowed
            
        Returns:
            int: Optimal number of workers
        """
        # Base worker count on CPU cores
        cpu_count = multiprocessing.cpu_count()
        
        # Conservative approach: use 75% of CPU cores for I/O bound tasks
        base_workers = max(1, int(cpu_count * 0.75))
        
        # Adjust based on current resource usage
        usage = self.get_current_usage()
        
        # Reduce workers if memory usage is high
        if usage['memory_percent'] > 0.7:
            base_workers = max(1, int(base_workers * 0.6))
        elif usage['memory_percent'] > 0.6:
            base_workers = max(1, int(base_workers * 0.8))
        
        # Apply maximum constraint
        if max_workers:
            base_workers = min(base_workers, max_workers)
        
        # Hard limit: Maximum 2 parallel workers to prevent CPU throttling
        base_workers = min(base_workers, 2)
        
        logger.info(f"Optimal worker count: {base_workers} (CPU cores: {cpu_count}, Memory usage: {usage['memory_percent']:.1%}, Max allowed: 2)")
        return base_workers


class ParallelProcessingMetrics(ProcessingMetrics):
    """
    Enhanced metrics collection for parallel processing operations.
    
    Extends base metrics with parallel processing specific tracking:
    - Worker utilization and performance
    - Concurrent processing statistics
    - Resource usage correlation
    - Thread safety for metrics collection
    """
    
    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()
        
        # Parallel processing specific metrics
        self.worker_metrics = {}
        self.concurrent_processing_stats = {
            'max_concurrent_files': 0,
            'average_concurrent_files': 0,
            'worker_utilization': {},
            'throttling_events': 0,
            'resource_usage_samples': []
        }
        
        # Performance correlation tracking
        self.processing_correlation = {
            'memory_usage_vs_time': [],
            'worker_count_vs_throughput': [],
            'file_size_vs_processing_time': []
        }
    
    def record_worker_start(self, worker_id: str, file_path: str):
        """Record worker starting processing."""
        with self._lock:
            if worker_id not in self.worker_metrics:
                self.worker_metrics[worker_id] = {
                    'files_processed': 0,
                    'total_processing_time': 0.0,
                    'start_times': [],
                    'current_file': None
                }
            
            self.worker_metrics[worker_id]['current_file'] = file_path
            self.worker_metrics[worker_id]['start_times'].append(time.time())
    
    def record_worker_completion(self, worker_id: str, processing_time: float, success: bool):
        """Record worker completing processing."""
        with self._lock:
            if worker_id in self.worker_metrics:
                self.worker_metrics[worker_id]['files_processed'] += 1
                self.worker_metrics[worker_id]['total_processing_time'] += processing_time
                self.worker_metrics[worker_id]['current_file'] = None
    
    def record_resource_sample(self, resource_usage: Dict[str, float], active_workers: int):
        """Record resource usage sample."""
        with self._lock:
            sample = {
                'timestamp': time.time(),
                'active_workers': active_workers,
                **resource_usage
            }
            self.concurrent_processing_stats['resource_usage_samples'].append(sample)
            
            # Update max concurrent files
            if active_workers > self.concurrent_processing_stats['max_concurrent_files']:
                self.concurrent_processing_stats['max_concurrent_files'] = active_workers
    
    def record_throttling_event(self):
        """Record a resource throttling event."""
        with self._lock:
            self.concurrent_processing_stats['throttling_events'] += 1
    
    def finalize_parallel_metrics(self):
        """Finalize parallel processing metrics."""
        super().finalize_metrics()
        
        with self._lock:
            # Calculate average concurrent files
            if self.concurrent_processing_stats['resource_usage_samples']:
                total_workers = sum(sample['active_workers'] for sample in self.concurrent_processing_stats['resource_usage_samples'])
                self.concurrent_processing_stats['average_concurrent_files'] = total_workers / len(self.concurrent_processing_stats['resource_usage_samples'])
            
            # Calculate worker utilization
            for worker_id, metrics in self.worker_metrics.items():
                if metrics['files_processed'] > 0:
                    avg_processing_time = metrics['total_processing_time'] / metrics['files_processed']
                    self.concurrent_processing_stats['worker_utilization'][worker_id] = {
                        'files_processed': metrics['files_processed'],
                        'average_processing_time': avg_processing_time,
                        'total_processing_time': metrics['total_processing_time']
                    }
    
    def generate_parallel_report(self) -> Dict:
        """Generate comprehensive parallel processing report."""
        self.finalize_parallel_metrics()
        base_report = super().generate_report()
        
        # Add parallel processing metrics
        base_report['parallel_processing_metrics'] = self.concurrent_processing_stats
        base_report['worker_performance'] = self.concurrent_processing_stats['worker_utilization']
        
        return base_report


class ParallelBatchProcessor:
    """
    High-performance parallel batch processor for PDF accessibility enhancement.
    
    Features:
    - Concurrent document processing using ThreadPoolExecutor
    - Dynamic worker scaling based on system resources
    - Memory monitoring and automatic throttling
    - Thread-safe ML pattern matching optimization
    - Enhanced performance tracking and correlation analysis
    """
    
    def __init__(self, config: BatchProcessingConfiguration, max_workers: Optional[int] = None):
        """
        Initialize parallel batch processor.
        
        Args:
            config: Batch processing configuration
            max_workers: Maximum number of worker threads (None for auto-detection)
        """
        self.config = config
        self.metrics = ParallelProcessingMetrics()
        self.logger = self._setup_logging()
        self.performance_tracker = get_performance_tracker()
        
        # Resource monitoring and worker management
        self.resource_monitor = ResourceMonitor()
        self.max_workers = max_workers
        self.optimal_workers = self.resource_monitor.get_optimal_worker_count(max_workers)
        
        # Thread safety
        self._processing_lock = threading.Lock()
        self._enhancement_services = threading.local()
        
        # Performance optimization flags
        self.enable_ml_optimization = True
        self.enable_resource_monitoring = True
        self.throttle_on_high_usage = True
        
        logger.info(f"Parallel batch processor initialized - Max workers: {self.optimal_workers}")
    
    def _setup_logging(self) -> logging.Logger:
        """Configure logging for parallel batch processing."""
        logger = logging.getLogger('ParallelBatchProcessor')
        
        if self.config.enable_detailed_logging:
            handler = logging.FileHandler(self.config.log_dir / 'parallel_batch_processing.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        return logger
    
    def _get_enhancement_service(self) -> EnhancementService:
        """Get thread-local enhancement service instance."""
        if not hasattr(self._enhancement_services, 'service'):
            self._enhancement_services.service = EnhancementService()
        return self._enhancement_services.service
    
    def process_batch_parallel(self) -> bool:
        """
        Execute parallel batch processing of all PDF files.
        
        Uses ThreadPoolExecutor for concurrent processing with dynamic
        resource monitoring and worker scaling.
        
        Returns:
            bool: True if batch processing completed successfully
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
            
            self.logger.info(f"Starting parallel batch processing of {len(pdf_files)} files with {self.optimal_workers} workers")
            
            # Start performance tracking
            with self.performance_tracker.track_operation("parallel_batch_processing"):
                success = self._execute_parallel_processing(pdf_files)
            
            # Generate final report
            if self.config.generate_processing_report:
                self._generate_final_report()
            
            if success:
                self.logger.info("Parallel batch processing completed successfully")
            else:
                self.logger.error("Parallel batch processing completed with errors")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Parallel batch processing failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _execute_parallel_processing(self, pdf_files: List[Path]) -> bool:
        """
        Execute the parallel processing of PDF files.
        
        Args:
            pdf_files: List of PDF files to process
            
        Returns:
            bool: True if processing completed successfully
        """
        # Initialize progress tracking
        completed_files = 0
        total_files = len(pdf_files)
        
        # Create progress bar if available
        progress_bar = None
        if TQDM_AVAILABLE and self.config.enable_progress_bar:
            progress_bar = tqdm(total=total_files, desc="Processing PDFs (Parallel)")
        
        try:
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=self.optimal_workers, thread_name_prefix="PDFWorker") as executor:
                # Submit all jobs
                future_to_file = {
                    executor.submit(self._process_single_file_parallel, pdf_file): pdf_file
                    for pdf_file in pdf_files
                }
                
                # Resource monitoring thread
                monitoring_active = True
                def resource_monitoring():
                    while monitoring_active:
                        if self.enable_resource_monitoring:
                            usage = self.resource_monitor.get_current_usage()
                            active_workers = sum(1 for f in future_to_file if not f.done())
                            self.metrics.record_resource_sample(usage, active_workers)
                            
                            # Check for throttling
                            if self.throttle_on_high_usage and self.resource_monitor.should_throttle():
                                self.metrics.record_throttling_event()
                                time.sleep(3)  # Brief pause to allow resources to recover
                        
                        time.sleep(1)  # Monitor every second
                
                # Start resource monitoring in background
                monitor_thread = threading.Thread(target=resource_monitoring, daemon=True)
                monitor_thread.start()
                
                # Process completed futures
                for future in as_completed(future_to_file):
                    pdf_file = future_to_file[future]
                    
                    try:
                        result = future.result()
                        completed_files += 1
                        
                        if progress_bar:
                            progress_bar.update(1)
                            progress_bar.set_postfix({
                                'Success': f"{len(self.metrics.successful_files)}/{completed_files}",
                                'Workers': self.optimal_workers
                            })
                        
                    except Exception as e:
                        self.logger.error(f"Worker exception for {pdf_file}: {e}")
                        self.metrics.record_failure(pdf_file, f"Worker exception: {str(e)}")
                        completed_files += 1
                        
                        if progress_bar:
                            progress_bar.update(1)
                
                # Stop resource monitoring
                monitoring_active = False
                monitor_thread.join(timeout=2)
                
                if progress_bar:
                    progress_bar.close()
            
            # Calculate success rate
            success_rate = len(self.metrics.successful_files) / total_files if total_files > 0 else 0
            self.logger.info(f"Parallel processing completed: {len(self.metrics.successful_files)}/{total_files} files ({success_rate:.1%} success rate)")
            
            return success_rate > 0.8  # Consider successful if >80% files processed
            
        except Exception as e:
            self.logger.error(f"Parallel execution failed: {e}")
            if progress_bar:
                progress_bar.close()
            return False
    
    def _process_single_file_parallel(self, input_file: Path) -> bool:
        """
        Process a single PDF file in parallel worker thread.
        
        Args:
            input_file: Path to the PDF file to process
            
        Returns:
            bool: True if processing successful
        """
        # Get thread-specific worker ID
        worker_id = threading.current_thread().name
        start_time = time.time()
        
        # Record worker start
        self.metrics.record_worker_start(worker_id, str(input_file))
        
        # Create output filename with "_enhanced" suffix
        base_name = input_file.stem
        extension = input_file.suffix
        output_file = self.config.output_dir / f"{base_name}_enhanced{extension}"
        
        try:
            self.logger.info(f"[{worker_id}] Processing: {input_file.name}")
            
            # Get thread-local enhancement service
            enhancement_service = self._get_enhancement_service()
            
            # Track individual file processing
            with self.performance_tracker.track_operation("single_file_processing", str(input_file), ["parallel_processing"]):
                success = enhancement_service.enhance_document(
                    input_file,
                    output_file,
                    mode="academic",
                    **self.config.enhancement_params
                )
            
            processing_time = time.time() - start_time
            
            # Record results
            if success:
                self.metrics.record_success(input_file, output_file, processing_time)
                self.metrics.record_worker_completion(worker_id, processing_time, True)
                self.logger.info(f"[{worker_id}] Successfully processed: {input_file.name} ({processing_time:.2f}s)")
                return True
            else:
                self.metrics.record_failure(input_file, "Enhancement service returned False", processing_time)
                self.metrics.record_worker_completion(worker_id, processing_time, False)
                self.logger.error(f"[{worker_id}] Failed to process: {input_file.name}")
                return False
                
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"Exception during processing: {str(e)}"
            self.metrics.record_failure(input_file, error_message, processing_time)
            self.metrics.record_worker_completion(worker_id, processing_time, False)
            self.logger.error(f"[{worker_id}] Error processing {input_file.name}: {error_message}")
            return False
    
    def _generate_final_report(self):
        """Generate comprehensive parallel processing report."""
        try:
            report = self.metrics.generate_parallel_report()
            report_path = self.config.output_dir / "parallel_batch_processing_report.json"
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Parallel processing report saved to: {report_path}")
            
            # Print enhanced summary to console
            summary = report['processing_summary']
            parallel_metrics = report.get('parallel_processing_metrics', {})
            
            print(f"\n--- Parallel Batch Processing Summary ---")
            print(f"Total files: {summary.get('total_files_processed', 0)}")
            print(f"Successful: {summary.get('successful_files', 0)}")
            print(f"Failed: {summary.get('failed_files', 0)}")
            print(f"Success rate: {summary.get('success_rate', 0):.1f}%")
            print(f"Total duration: {summary.get('total_duration', 0):.1f} seconds")
            print(f"Average processing time: {summary.get('average_processing_time', 0):.2f} seconds")
            
            # Parallel processing specific metrics
            print(f"\n--- Parallel Processing Metrics ---")
            print(f"Worker threads used: {self.optimal_workers}")
            print(f"Max concurrent files: {parallel_metrics.get('max_concurrent_files', 0)}")
            print(f"Average concurrent files: {parallel_metrics.get('average_concurrent_files', 0):.1f}")
            print(f"Resource throttling events: {parallel_metrics.get('throttling_events', 0)}")
            
            # Worker performance
            worker_performance = report.get('worker_performance', {})
            if worker_performance:
                print(f"\n--- Worker Performance ---")
                for worker_id, metrics in worker_performance.items():
                    print(f"{worker_id}: {metrics['files_processed']} files, {metrics['average_processing_time']:.2f}s avg")
            
        except Exception as e:
            self.logger.error(f"Failed to generate parallel report: {str(e)}")
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive processing statistics.
        
        Returns:
            Dict[str, Any]: Processing statistics including parallel metrics
        """
        base_stats = {
            'total_files': len(self.metrics.successful_files) + len(self.metrics.failed_files),
            'successful_files': len(self.metrics.successful_files),
            'failed_files': len(self.metrics.failed_files),
            'success_rate': len(self.metrics.successful_files) / max(1, len(self.metrics.successful_files) + len(self.metrics.failed_files)),
            'average_processing_time': sum(self.metrics.processing_times) / max(1, len(self.metrics.processing_times)),
            'optimal_workers': self.optimal_workers
        }
        
        # Add parallel processing metrics
        base_stats.update(self.metrics.concurrent_processing_stats)
        
        return base_stats
    
    def optimize_for_system(self) -> Dict[str, Any]:
        """
        Optimize processor settings for current system.
        
        Returns:
            Dict[str, Any]: Optimization recommendations and applied settings
        """
        # Get current system capabilities
        usage = self.resource_monitor.get_current_usage()
        cpu_count = multiprocessing.cpu_count()
        
        optimization_report = {
            'system_info': {
                'cpu_cores': cpu_count,
                'total_memory_gb': usage.get('total_memory_gb', 'unknown'),
                'current_memory_usage': f"{usage['memory_percent']:.1%}",
                'platform': platform.system(),
                'psutil_available': PSUTIL_AVAILABLE
            },
            'current_settings': {
                'optimal_workers': self.optimal_workers,
                'memory_threshold': self.resource_monitor.memory_threshold,
                'cpu_threshold': self.resource_monitor.cpu_threshold
            },
            'recommendations': []
        }
        
        # Generate optimization recommendations
        if usage['memory_percent'] > 0.8:
            optimization_report['recommendations'].append(
                "High memory usage detected - consider reducing worker count or processing smaller batches"
            )
        
        if cpu_count >= 8:
            optimization_report['recommendations'].append(
                f"High-core system detected ({cpu_count} cores) - parallel processing will provide significant speedup"
            )
        
        if usage.get('total_memory_gb', 0) >= 16:
            optimization_report['recommendations'].append(
                "Ample memory available - can process large files efficiently"
            )
        
        if not PSUTIL_AVAILABLE:
            optimization_report['recommendations'].append(
                "Install psutil for enhanced resource monitoring: pip install psutil"
            )
        
        return optimization_report


# Backward compatibility wrapper
class EnhancedBatchProcessor(ParallelBatchProcessor):
    """
    Enhanced batch processor with automatic parallel/sequential selection.
    
    Provides backward compatibility while enabling parallel processing
    when beneficial.
    """
    
    def __init__(self, config: BatchProcessingConfiguration, force_parallel: bool = None):
        """
        Initialize enhanced batch processor.
        
        Args:
            config: Batch processing configuration
            force_parallel: Force parallel processing (None for auto-detection)
        """
        super().__init__(config)
        self.force_parallel = force_parallel
    
    def process_batch(self) -> bool:
        """
        Process batch with automatic parallel/sequential selection.
        
        Returns:
            bool: True if processing successful
        """
        # Determine processing mode
        use_parallel = self._should_use_parallel()
        
        if use_parallel:
            self.logger.info("Using parallel processing mode")
            return self.process_batch_parallel()
        else:
            self.logger.info("Using sequential processing mode")
            return self._process_batch_sequential()
    
    def _should_use_parallel(self) -> bool:
        """Determine whether to use parallel processing."""
        if self.force_parallel is not None:
            return self.force_parallel
        
        # Auto-detection based on system capabilities
        cpu_count = multiprocessing.cpu_count()
        
        # Use parallel processing if:
        # - More than 2 CPU cores available
        # - psutil available for resource monitoring
        # - Not running in constrained environment
        
        use_parallel = (
            cpu_count >= 2 and
            PSUTIL_AVAILABLE and
            not self._is_constrained_environment()
        )
        
        self.logger.info(f"Parallel processing auto-detection: {use_parallel} (CPU cores: {cpu_count}, psutil: {PSUTIL_AVAILABLE})")
        return use_parallel
    
    def _is_constrained_environment(self) -> bool:
        """Check if running in a constrained environment."""
        if not PSUTIL_AVAILABLE:
            return True
        
        try:
            memory = psutil.virtual_memory()
            # Consider constrained if less than 2GB available memory
            return memory.available < (2 * 1024**3)
        except:
            return True
    
    def _process_batch_sequential(self) -> bool:
        """Fallback to sequential processing."""
        # Import the original batch processor for sequential processing
        from .advanced_batch_processor import AdvancedBatchProcessor
        
        sequential_processor = AdvancedBatchProcessor(self.config)
        return sequential_processor.process_batch()
