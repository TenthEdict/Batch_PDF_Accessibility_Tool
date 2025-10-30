"""
Batch processing module for ePubs Accessibility Enhancement.

SIMPLIFIED VERSION (Stage 2): Only exports SimpleBatchProcessor.
Legacy Phase 2B batch processors (AdvancedBatchProcessor, ParallelBatchProcessor)
are still in the codebase but require archived dependencies.
"""

# Import simplified batch processor (primary interface)
from .simple_batch_processor import SimpleBatchProcessor

__all__ = [
    'SimpleBatchProcessor',  # Simplified processor (no Phase 2B dependencies)
]

# Note: Legacy processors (AdvancedBatchProcessor, ParallelBatchProcessor)
# are available in the codebase but require Phase 2B dependencies
# (FAISS, monitoring, caching) which are now archived in /archive/phase2b/
