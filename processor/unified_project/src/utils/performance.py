#!/usr/bin/env python3
"""
Performance utilities for efficient file processing and resource management.

This module provides performance optimization functions:
- Memory-efficient file iteration
- Resource limit management
- Progress bar optimization
- Memory cleanup utilities
"""

import gc
import os
import psutil
import logging
from pathlib import Path
from typing import Iterator, Optional, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def iter_pdf_files(directory: Path, pattern: str = "*.pdf") -> Iterator[Path]:
    """
    Memory-efficient iterator over PDF files in a directory.
    
    This replaces list(glob()) to avoid loading all paths into memory.
    
    Args:
        directory: Directory to search
        pattern: File pattern (default: *.pdf)
        
    Yields:
        Path objects for each matching file
    """
    for file_path in directory.glob(pattern):
        if file_path.is_file():
            yield file_path


def count_pdf_files(directory: Path, pattern: str = "*.pdf") -> int:
    """
    Count PDF files without loading all into memory.
    
    Args:
        directory: Directory to search
        pattern: File pattern (default: *.pdf)
        
    Returns:
        Count of matching files
    """
    count = 0
    for _ in iter_pdf_files(directory, pattern):
        count += 1
    return count


class ResourceLimits:
    """
    Resource limit management for batch processing.
    
    Prevents system resource exhaustion during parallel operations.
    """
    
    def __init__(
        self,
        max_memory_percent: float = 80.0,
        max_cpu_percent: float = 90.0,
        max_workers: Optional[int] = None
    ):
        """
        Initialize resource limits.
        
        Args:
            max_memory_percent: Maximum memory usage before throttling (0-100)
            max_cpu_percent: Maximum CPU usage before throttling (0-100)
            max_workers: Maximum parallel workers (None = auto-detect)
        """
        self.max_memory_percent = max_memory_percent
        self.max_cpu_percent = max_cpu_percent
        
        # Auto-detect optimal worker count if not specified
        if max_workers is None:
            cpu_count = os.cpu_count() or 4
            # Use 75% of available CPUs, max 8
            self.max_workers = min(max(cpu_count * 3 // 4, 1), 8)
        else:
            self.max_workers = max_workers
        
        logger.info(f"Resource limits: {self.max_memory_percent}% memory, "
                   f"{self.max_cpu_percent}% CPU, {self.max_workers} workers")
    
    def check_resources(self) -> tuple[bool, Optional[str]]:
        """
        Check if current resource usage is within limits.
        
        Returns:
            Tuple of (within_limits, warning_message)
        """
        try:
            # Check memory
            memory = psutil.virtual_memory()
            if memory.percent > self.max_memory_percent:
                return False, f"Memory usage too high: {memory.percent:.1f}%"
            
            # Check CPU (average over last second)
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > self.max_cpu_percent:
                return False, f"CPU usage too high: {cpu_percent:.1f}%"
            
            return True, None
            
        except Exception as e:
            logger.warning(f"Resource check failed: {e}")
            return True, None  # Allow processing to continue
    
    def get_available_memory_mb(self) -> int:
        """Get available memory in megabytes."""
        try:
            return psutil.virtual_memory().available // (1024 * 1024)
        except Exception:
            return 1024  # Default to 1GB if check fails


@contextmanager
def memory_cleanup():
    """
    Context manager for automatic memory cleanup.
    
    Runs garbage collection before and after operations to prevent leaks.
    
    Usage:
        with memory_cleanup():
            # Memory-intensive operations
            process_large_batch()
    """
    # Initial cleanup
    gc.collect()
    
    try:
        yield
    finally:
        # Final cleanup
        gc.collect()


def should_use_progress_bar(
    total_files: int,
    avg_time_per_file: float = 1.0,
    min_time_threshold: float = 5.0
) -> bool:
    """
    Determine if progress bar overhead is worth it.
    
    For very small batches or quick operations, progress bar overhead
    may exceed the benefit.
    
    Args:
        total_files: Number of files to process
        avg_time_per_file: Estimated time per file in seconds
        min_time_threshold: Minimum total time to justify progress bar
        
    Returns:
        True if progress bar should be used
    """
    estimated_total_time = total_files * avg_time_per_file
    return estimated_total_time >= min_time_threshold


def optimize_io_buffer_size(file_size_mb: float) -> int:
    """
    Calculate optimal I/O buffer size based on file size.
    
    Args:
        file_size_mb: File size in megabytes
        
    Returns:
        Buffer size in bytes
    """
    # Default buffer size
    default_buffer = 64 * 1024  # 64KB
    
    if file_size_mb < 1:
        return default_buffer
    elif file_size_mb < 10:
        return 256 * 1024  # 256KB
    elif file_size_mb < 100:
        return 1024 * 1024  # 1MB
    else:
        return 4 * 1024 * 1024  # 4MB


class BatchChunker:
    """
    Chunk large batches into manageable sizes.
    
    Prevents memory exhaustion and allows progress checkpointing.
    """
    
    def __init__(self, chunk_size: int = 50):
        """
        Initialize batch chunker.
        
        Args:
            chunk_size: Number of files per chunk
        """
        self.chunk_size = chunk_size
    
    def chunk_files(self, files: list[Path]) -> Iterator[list[Path]]:
        """
        Split file list into chunks.
        
        Args:
            files: List of files to chunk
            
        Yields:
            Chunks of files
        """
        for i in range(0, len(files), self.chunk_size):
            yield files[i:i + self.chunk_size]
    
    def chunk_iterator(self, iterator: Iterator[Path]) -> Iterator[list[Path]]:
        """
        Chunk an iterator of files.
        
        Args:
            iterator: Iterator of file paths
            
        Yields:
            Chunks of files
        """
        chunk = []
        for file_path in iterator:
            chunk.append(file_path)
            if len(chunk) >= self.chunk_size:
                yield chunk
                chunk = []
        
        # Yield remaining files
        if chunk:
            yield chunk


def log_resource_usage(operation: str = "Current"):
    """
    Log current system resource usage.
    
    Args:
        operation: Description of operation for logging context
    """
    try:
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        logger.info(
            f"{operation} resource usage: "
            f"Memory {memory.percent:.1f}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB), "
            f"CPU {cpu_percent:.1f}%"
        )
    except Exception as e:
        logger.debug(f"Could not log resource usage: {e}")


# Initialize once at module load for efficiency
_LOGGING_CONFIGURED = False


def configure_logging_once(verbose: bool = False):
    """
    Configure logging only once to avoid redundant setup.
    
    Args:
        verbose: Enable verbose logging
    """
    global _LOGGING_CONFIGURED
    
    if _LOGGING_CONFIGURED:
        return
    
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Reduce verbosity of noisy libraries
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("ocrmypdf").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("fitz").setLevel(logging.WARNING)
    
    _LOGGING_CONFIGURED = True



def should_use_progress_bar(
    total_files: int,
    avg_time_per_file: float = 1.0,
    min_time_threshold: float = 5.0,
    min_files_threshold: int = 3
) -> bool:
    """
    Determine if progress bar overhead is worth it.
    
    For very small batches or quick operations, progress bar overhead
    may exceed the benefit.
    
    Args:
        total_files: Number of files to process
        avg_time_per_file: Estimated time per file in seconds
        min_time_threshold: Minimum total time to justify progress bar
        min_files_threshold: Minimum number of files to justify progress bar
        
    Returns:
        True if progress bar should be used
    """
    # Too few files - skip progress bar
    if total_files < min_files_threshold:
        return False
    
    # Estimate total time
    estimated_total_time = total_files * avg_time_per_file
    
    # Only use if estimated time exceeds threshold
    return estimated_total_time >= min_time_threshold


def create_batch_chunks(
    files: List[Path],
    chunk_size: int = 50
) -> List[List[Path]]:
    """
    Split file list into manageable chunks.
    
    Args:
        files: List of files to chunk
        chunk_size: Files per chunk
        
    Returns:
        List of file chunks
    """
    chunks = []
    for i in range(0, len(files), chunk_size):
        chunks.append(files[i:i + chunk_size])
    return chunks


def get_optimal_chunk_size(
    total_files: int,
    available_memory_mb: int,
    avg_file_size_mb: float = 5.0
) -> int:
    """
    Calculate optimal chunk size based on available memory.
    
    Args:
        total_files: Total number of files
        available_memory_mb: Available memory in MB
        avg_file_size_mb: Average file size in MB
        
    Returns:
        Optimal chunk size
    """
    # Reserve 20% of available memory for processing overhead
    usable_memory = available_memory_mb * 0.8
    
    # Calculate files that fit in memory
    files_per_chunk = int(usable_memory / avg_file_size_mb)
    
    # Clamp to reasonable range (10-100 files)
    files_per_chunk = max(10, min(files_per_chunk, 100))
    
    # Don't chunk if total files is less than calculated chunk size
    if total_files <= files_per_chunk:
        return total_files
    
    return files_per_chunk
