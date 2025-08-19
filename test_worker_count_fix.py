#!/usr/bin/env python3
"""
Test script to verify that the worker count fix is working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from processor.unified_project.src.batch.advanced_batch_processor import BatchProcessingConfiguration
from processor.unified_project.src.batch.parallel_batch_processor import ParallelBatchProcessor

# Test Phase2B if available
try:
    from processor.unified_project.src.batch.phase2b_enhanced_processor import create_phase2b_batch_processor
    PHASE2B_AVAILABLE = True
except ImportError:
    PHASE2B_AVAILABLE = False

def test_worker_count_fix():
    """Test that worker count parameter is properly respected."""
    print("🧪 Testing Worker Count Fix")
    print("=" * 50)
    
    # Create test configuration
    config = BatchProcessingConfiguration(
        input_dir="data/input",
        output_dir="data/output/test"
    )
    
    print("\n1. Testing ParallelBatchProcessor with max_workers=2")
    processor = ParallelBatchProcessor(config, max_workers=2)
    print(f"   ✅ Expected: 2 workers")
    print(f"   ✅ Actual: {processor.optimal_workers} workers")
    
    if processor.optimal_workers != 2:
        print(f"   ❌ FAILED: Expected 2 workers, got {processor.optimal_workers}")
        return False
    
    print("\n2. Testing ParallelBatchProcessor with max_workers=4")
    processor = ParallelBatchProcessor(config, max_workers=4)
    print(f"   ✅ Expected: 4 workers")
    print(f"   ✅ Actual: {processor.optimal_workers} workers")
    
    if processor.optimal_workers != 4:
        print(f"   ❌ FAILED: Expected 4 workers, got {processor.optimal_workers}")
        return False
    
    print("\n3. Testing ParallelBatchProcessor with auto-detection (None)")
    processor = ParallelBatchProcessor(config, max_workers=None)
    auto_workers = processor.optimal_workers
    print(f"   ✅ Auto-detected: {auto_workers} workers")
    
    if PHASE2B_AVAILABLE:
        print("\n4. Testing Phase2B processor with max_workers=3")
        try:
            processor = create_phase2b_batch_processor(config, max_workers=3)
            print(f"   ✅ Expected: 3 workers")
            print(f"   ✅ Actual: {processor.optimal_workers} workers")
            
            if processor.optimal_workers != 3:
                print(f"   ❌ FAILED: Expected 3 workers, got {processor.optimal_workers}")
                return False
        except Exception as e:
            print(f"   ❌ FAILED: Phase2B test failed: {e}")
            return False
    else:
        print("\n4. Phase2B not available - skipping Phase2B test")
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Worker count parameter is now properly respected")
    print("✅ Resource throttling issue should be resolved")
    return True

if __name__ == "__main__":
    success = test_worker_count_fix()
    sys.exit(0 if success else 1)
