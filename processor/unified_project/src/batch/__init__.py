"""
Batch processing module for ePubs Accessibility Enhancement.

This module provides advanced batch processing capabilities for PDF accessibility
enhancement with comprehensive monitoring, error handling, and quality assurance.

Features:
- Sequential batch processing (AdvancedBatchProcessor)
- Parallel batch processing with dynamic worker scaling (ParallelBatchProcessor)
- Enhanced batch processor with automatic mode selection (EnhancedBatchProcessor)
- Resource monitoring and performance optimization
"""

from .advanced_batch_processor import AdvancedBatchProcessor, BatchProcessingConfiguration
from .parallel_batch_processor import (
    ParallelBatchProcessor, 
    EnhancedBatchProcessor,
    ResourceMonitor,
    ParallelProcessingMetrics
)

__all__ = [
    'AdvancedBatchProcessor', 
    'BatchProcessingConfiguration',
    'ParallelBatchProcessor',
    'EnhancedBatchProcessor', 
    'ResourceMonitor',
    'ParallelProcessingMetrics'
]