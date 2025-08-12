#!/usr/bin/env python3
"""
Parallel Processing Implementation for ePubs Accessibility Enhancement Project.

This module provides advanced parallel processing capabilities including:
- Configurable worker pool size
- Progress tracking with rich library
- Error isolation and recovery
- Memory management for large batches
- Job queuing and distribution
"""

import multiprocessing as mp
import queue
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import threading
import signal
import os
import sys

# Optional rich library for progress tracking
try:
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from processor.unified_project.src.services.enhancement_service import EnhancementService
from processor.unified_project.src.batch.advanced_batch_processor import BatchProcessingConfiguration


@dataclass
class ProcessingJob:
    """Represents a single processing job."""
    job_id: str
    input_path: Path
    output_path: Path
    mode: str = "academic"
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class ProcessingResult:
    """Represents the result of a processing job."""
    job_id: str
    success: bool
    output_path: Optional[Path] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    memory_usage_mb: float = 0.0
    file_size_mb: float = 0.0
    completed_at: datetime = field(default_factory=datetime.now)


class WorkerPool:
    """Manages a pool of worker processes for parallel processing."""
    
    def __init__(self, num_workers: int = None, max_memory_mb: int = 2048):
        """
        Initialize worker pool.
        
        Args:
            num_workers: Number of worker processes (defaults to CPU count)
            max_memory_mb: Maximum memory per worker in MB
        """
        self.num_workers = num_workers or min(mp.cpu_count(), 8)  # Cap at 8 workers
        self.max_memory_mb = max_memory_mb
        self.workers: List[mp.Process] = []
        self.job_queue: mp.Queue = mp.Queue()
        self.result_queue: mp.Queue = mp.Queue()
        self.stop_event = mp.Event()
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            'jobs_processed': 0,
            'jobs_successful': 0,
            'jobs_failed': 0,
            'total_processing_time': 0.0,
            'total_memory_usage': 0.0
        }
    
    def start_workers(self):
        """Start all worker processes."""
        self.logger.info(f"Starting {self.num_workers} worker processes")
        
        for i in range(self.num_workers):
            worker = mp.Process(
                target=self._worker_process,
                args=(i, self.job_queue, self.result_queue, self.stop_event),
                name=f"Worker-{i}"
            )
            worker.start()
            self.workers.append(worker)
        
        self.logger.info(f"Started {len(self.workers)} worker processes")
    
    def stop_workers(self, timeout: int = 30):
        """Stop all worker processes gracefully."""
        self.logger.info("Stopping worker processes...")
        self.stop_event.set()
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=timeout)
            if worker.is_alive():
                self.logger.warning(f"Force terminating worker {worker.name}")
                worker.terminate()
                worker.join(timeout=5)
        
        self.workers.clear()
        self.logger.info("All worker processes stopped")
    
    def _worker_process(self, worker_id: int, job_queue: mp.Queue, 
                       result_queue: mp.Queue, stop_event: mp.Event):
        """Worker process function."""
        worker_logger = logging.getLogger(f"Worker-{worker_id}")
        worker_logger.info(f"Worker {worker_id} started")
        
        # Initialize enhancement service
        enhancement_service = EnhancementService()
        
        while not stop_event.is_set():
            try:
                # Get job with timeout
                job = job_queue.get(timeout=1.0)
                
                if job is None:  # Poison pill
                    break
                
                worker_logger.info(f"Processing job {job.job_id}: {job.input_path.name}")
                
                # Process the job
                start_time = time.time()
                start_memory = self._get_memory_usage()
                
                try:
                    success = enhancement_service.enhance_document(
                        job.input_path,
                        job.output_path,
                        mode=job.mode,
                        **job.parameters
                    )
                    
                    processing_time = time.time() - start_time
                    end_memory = self._get_memory_usage()
                    memory_usage = end_memory - start_memory
                    
                    # Get file size
                    file_size = job.input_path.stat().st_size / (1024 * 1024) if job.input_path.exists() else 0
                    
                    result = ProcessingResult(
                        job_id=job.job_id,
                        success=success,
                        output_path=job.output_path if success else None,
                        processing_time=processing_time,
                        memory_usage_mb=memory_usage,
                        file_size_mb=file_size
                    )
                    
                    if not success:
                        result.error_message = "Enhancement service returned False"
                    
                except Exception as e:
                    processing_time = time.time() - start_time
                    worker_logger.error(f"Error processing job {job.job_id}: {e}")
                    
                    result = ProcessingResult(
                        job_id=job.job_id,
                        success=False,
                        error_message=str(e),
                        processing_time=processing_time
                    )
                
                # Send result
                result_queue.put(result)
                
            except queue.Empty:
                continue
            except Exception as e:
                worker_logger.error(f"Worker {worker_id} error: {e}")
                continue
        
        worker_logger.info(f"Worker {worker_id} stopped")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except ImportError:
            return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get worker pool statistics."""
        return self.stats.copy()


class ParallelProcessor:
    """Advanced parallel processor with progress tracking and error handling."""
    
    def __init__(self, config: BatchProcessingConfiguration, 
                 num_workers: int = None,
                 enable_progress_bar: bool = True):
        """
        Initialize parallel processor.
        
        Args:
            config: Batch processing configuration
            num_workers: Number of worker processes
            enable_progress_bar: Enable progress bar display
        """
        self.config = config
        self.enable_progress_bar = enable_progress_bar and RICH_AVAILABLE
        self.logger = logging.getLogger(__name__)
        
        # Initialize worker pool
        self.worker_pool = WorkerPool(num_workers=num_workers)
        
        # Job tracking
        self.jobs: Dict[str, ProcessingJob] = {}
        self.results: Dict[str, ProcessingResult] = {}
        self.failed_jobs: List[ProcessingJob] = []
        
        # Progress tracking
        self.total_jobs = 0
        self.completed_jobs = 0
        self.failed_jobs_count = 0
        
        # Performance tracking
        self.start_time = None
        self.end_time = None
    
    def process_batch(self, input_files: List[Path], 
                     output_dir: Path,
                     mode: str = "academic",
                     parameters: Dict[str, Any] = None) -> bool:
        """
        Process a batch of files in parallel.
        
        Args:
            input_files: List of input file paths
            output_dir: Output directory
            mode: Processing mode
            parameters: Additional processing parameters
            
        Returns:
            True if all jobs completed successfully
        """
        self.logger.info(f"Starting parallel batch processing of {len(input_files)} files")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare jobs
        jobs = self._prepare_jobs(input_files, output_dir, mode, parameters or {})
        self.total_jobs = len(jobs)
        
        if self.total_jobs == 0:
            self.logger.warning("No valid jobs to process")
            return True
        
        # Start processing
        self.start_time = datetime.now()
        
        try:
            # Start worker pool
            self.worker_pool.start_workers()
            
            # Submit jobs
            self._submit_jobs(jobs)
            
            # Monitor progress
            success = self._monitor_progress()
            
        finally:
            # Stop worker pool
            self.worker_pool.stop_workers()
            self.end_time = datetime.now()
        
        # Generate report
        self._generate_report()
        
        return success
    
    def _prepare_jobs(self, input_files: List[Path], 
                     output_dir: Path,
                     mode: str,
                     parameters: Dict[str, Any]) -> List[ProcessingJob]:
        """Prepare processing jobs from input files."""
        jobs = []
        
        for i, input_file in enumerate(input_files):
            if not input_file.exists():
                self.logger.warning(f"Input file not found: {input_file}")
                continue
            
            # Generate output path
            output_filename = f"{input_file.stem}_enhanced{input_file.suffix}"
            output_path = output_dir / output_filename
            
            # Create job
            job = ProcessingJob(
                job_id=f"job_{i:06d}_{int(time.time())}",
                input_path=input_file,
                output_path=output_path,
                mode=mode,
                parameters=parameters.copy(),
                priority=0
            )
            
            jobs.append(job)
            self.jobs[job.job_id] = job
        
        self.logger.info(f"Prepared {len(jobs)} jobs for processing")
        return jobs
    
    def _submit_jobs(self, jobs: List[ProcessingJob]):
        """Submit jobs to worker pool."""
        for job in jobs:
            self.worker_pool.job_queue.put(job)
        
        # Add poison pills to stop workers
        for _ in range(self.worker_pool.num_workers):
            self.worker_pool.job_queue.put(None)
    
    def _monitor_progress(self) -> bool:
        """Monitor processing progress and collect results."""
        if self.enable_progress_bar:
            return self._monitor_progress_with_bar()
        else:
            return self._monitor_progress_simple()
    
    def _monitor_progress_with_bar(self) -> bool:
        """Monitor progress with rich progress bar."""
        console = Console()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task(
                f"Processing {self.total_jobs} files...", 
                total=self.total_jobs
            )
            
            while self.completed_jobs < self.total_jobs:
                try:
                    # Get result with timeout
                    result = self.worker_pool.result_queue.get(timeout=1.0)
                    
                    # Store result
                    self.results[result.job_id] = result
                    self.completed_jobs += 1
                    
                    # Update progress
                    progress.update(task, completed=self.completed_jobs)
                    
                    # Log result
                    if result.success:
                        self.logger.info(f"Job {result.job_id} completed successfully in {result.processing_time:.2f}s")
                    else:
                        self.failed_jobs_count += 1
                        self.logger.error(f"Job {result.job_id} failed: {result.error_message}")
                        
                        # Add to failed jobs for retry
                        if result.job_id in self.jobs:
                            job = self.jobs[result.job_id]
                            if job.retry_count < job.max_retries:
                                job.retry_count += 1
                                self.failed_jobs.append(job)
                    
                except queue.Empty:
                    continue
        
        return self.failed_jobs_count == 0
    
    def _monitor_progress_simple(self) -> bool:
        """Monitor progress without progress bar."""
        while self.completed_jobs < self.total_jobs:
            try:
                # Get result with timeout
                result = self.worker_pool.result_queue.get(timeout=1.0)
                
                # Store result
                self.results[result.job_id] = result
                self.completed_jobs += 1
                
                # Log progress
                progress_percent = (self.completed_jobs / self.total_jobs) * 100
                self.logger.info(f"Progress: {self.completed_jobs}/{self.total_jobs} ({progress_percent:.1f}%)")
                
                # Log result
                if result.success:
                    self.logger.info(f"Job {result.job_id} completed successfully in {result.processing_time:.2f}s")
                else:
                    self.failed_jobs_count += 1
                    self.logger.error(f"Job {result.job_id} failed: {result.error_message}")
                    
                    # Add to failed jobs for retry
                    if result.job_id in self.jobs:
                        job = self.jobs[result.job_id]
                        if job.retry_count < job.max_retries:
                            job.retry_count += 1
                            self.failed_jobs.append(job)
                
            except queue.Empty:
                continue
        
        return self.failed_jobs_count == 0
    
    def _generate_report(self):
        """Generate processing report."""
        if not self.start_time or not self.end_time:
            return
        
        total_time = (self.end_time - self.start_time).total_seconds()
        success_count = sum(1 for r in self.results.values() if r.success)
        failure_count = len(self.results) - success_count
        
        # Calculate statistics
        total_processing_time = sum(r.processing_time for r in self.results.values())
        total_memory_usage = sum(r.memory_usage_mb for r in self.results.values())
        total_file_size = sum(r.file_size_mb for r in self.results.values())
        
        avg_processing_time = total_processing_time / len(self.results) if self.results else 0
        avg_memory_usage = total_memory_usage / len(self.results) if self.results else 0
        
        # Log summary
        self.logger.info("=" * 60)
        self.logger.info("PARALLEL PROCESSING SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Jobs: {self.total_jobs}")
        self.logger.info(f"Successful: {success_count}")
        self.logger.info(f"Failed: {failure_count}")
        self.logger.info(f"Success Rate: {(success_count/self.total_jobs)*100:.1f}%" if self.total_jobs > 0 else "N/A")
        self.logger.info(f"Total Time: {total_time:.2f}s")
        self.logger.info(f"Average Processing Time: {avg_processing_time:.2f}s")
        self.logger.info(f"Total Memory Usage: {total_memory_usage:.2f} MB")
        self.logger.info(f"Average Memory Usage: {avg_memory_usage:.2f} MB")
        self.logger.info(f"Total File Size: {total_file_size:.2f} MB")
        self.logger.info(f"Workers Used: {self.worker_pool.num_workers}")
        self.logger.info("=" * 60)
        
        # Display rich table if available
        if RICH_AVAILABLE and self.enable_progress_bar:
            self._display_results_table()
    
    def _display_results_table(self):
        """Display results in a rich table."""
        console = Console()
        table = Table(title="Processing Results")
        
        table.add_column("Job ID", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Time (s)", style="yellow")
        table.add_column("Memory (MB)", style="blue")
        table.add_column("File Size (MB)", style="magenta")
        table.add_column("Error", style="red")
        
        for job_id, result in self.results.items():
            status = "✅ Success" if result.success else "❌ Failed"
            error = result.error_message or ""
            
            table.add_row(
                job_id,
                status,
                f"{result.processing_time:.2f}",
                f"{result.memory_usage_mb:.2f}",
                f"{result.file_size_mb:.2f}",
                error
            )
        
        console.print(table)
    
    def get_results(self) -> Dict[str, ProcessingResult]:
        """Get all processing results."""
        return self.results.copy()
    
    def get_failed_jobs(self) -> List[ProcessingJob]:
        """Get list of failed jobs for retry."""
        return self.failed_jobs.copy()
    
    def retry_failed_jobs(self) -> bool:
        """Retry failed jobs."""
        if not self.failed_jobs:
            self.logger.info("No failed jobs to retry")
            return True
        
        self.logger.info(f"Retrying {len(self.failed_jobs)} failed jobs")
        
        # Reset counters
        self.completed_jobs = 0
        self.failed_jobs_count = 0
        
        # Retry failed jobs
        return self.process_batch(
            [job.input_path for job in self.failed_jobs],
            self.failed_jobs[0].output_path.parent,
            self.failed_jobs[0].mode,
            self.failed_jobs[0].parameters
        )


def create_parallel_processor(config: BatchProcessingConfiguration,
                            num_workers: int = None,
                            enable_progress_bar: bool = True) -> ParallelProcessor:
    """Create a parallel processor instance."""
    return ParallelProcessor(config, num_workers, enable_progress_bar)


if __name__ == "__main__":
    # Example usage
    import logging
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create configuration
    config = BatchProcessingConfiguration(
        input_dir="data/input",
        output_dir="data/output/parallel",
        enable_detailed_logging=True
    )
    
    # Create parallel processor
    processor = create_parallel_processor(config, num_workers=4)
    
    # Example input files (replace with actual files)
    input_files = [
        Path("data/input/sample1.pdf"),
        Path("data/input/sample2.pdf"),
        Path("data/input/sample3.pdf")
    ]
    
    # Process batch
    success = processor.process_batch(
        input_files=input_files,
        output_dir=Path("data/output/parallel"),
        mode="academic"
    )
    
    print(f"Batch processing {'completed successfully' if success else 'failed'}")
