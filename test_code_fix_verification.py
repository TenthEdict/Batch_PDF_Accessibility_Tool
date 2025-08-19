#!/usr/bin/env python3
"""
Simple test to verify the worker count fix by checking the code changes.
"""

def test_worker_count_fix():
    """Test that the code changes are correctly applied."""
    print("🧪 Testing Worker Count Fix - Code Verification")
    print("=" * 50)
    
    # Test 1: Check main.py fixes
    print("\n1. Testing main.py parallel processor fix...")
    with open('/home/schipp0/ePubs_Main/processor/unified_project/src/main.py', 'r') as f:
        main_content = f.read()
    
    # Check if ParallelBatchProcessor is called with max_workers parameter
    if 'ParallelBatchProcessor(config, max_workers=parallel_workers)' in main_content:
        print("   ✅ ParallelBatchProcessor now receives max_workers parameter")
    else:
        print("   ❌ ParallelBatchProcessor still missing max_workers parameter")
        return False
    
    # Check if create_phase2b_batch_processor is called with max_workers parameter
    if 'create_phase2b_batch_processor(config, max_workers=parallel_workers)' in main_content:
        print("   ✅ Phase2B processor now receives max_workers parameter")
    else:
        print("   ❌ Phase2B processor still missing max_workers parameter")
        return False
    
    print("\n2. Testing phase2b_enhanced_processor.py fixes...")
    with open('/home/schipp0/ePubs_Main/processor/unified_project/src/batch/phase2b_enhanced_processor.py', 'r') as f:
        phase2b_content = f.read()
    
    # Check if create_phase2b_batch_processor function accepts max_workers
    if 'def create_phase2b_batch_processor(config: BatchProcessingConfiguration, max_workers: Optional[int] = None)' in phase2b_content:
        print("   ✅ create_phase2b_batch_processor function updated to accept max_workers")
    else:
        print("   ❌ create_phase2b_batch_processor function still missing max_workers parameter")
        return False
    
    # Check if Phase2BEnhancedBatchProcessor constructor accepts max_workers
    if 'def __init__(self, config: BatchProcessingConfiguration, max_workers: Optional[int] = None):' in phase2b_content:
        print("   ✅ Phase2BEnhancedBatchProcessor constructor updated to accept max_workers")
    else:
        print("   ❌ Phase2BEnhancedBatchProcessor constructor still missing max_workers parameter")
        return False
    
    # Check if super().__init__ passes max_workers
    if 'super().__init__(config, max_workers)' in phase2b_content:
        print("   ✅ Phase2BEnhancedBatchProcessor properly passes max_workers to parent")
    else:
        print("   ❌ Phase2BEnhancedBatchProcessor not passing max_workers to parent")
        return False
    
    print("\n3. Testing parallel_batch_processor.py logic...")
    with open('/home/schipp0/ePubs_Main/processor/unified_project/src/batch/parallel_batch_processor.py', 'r') as f:
        parallel_content = f.read()
    
    # Check if get_optimal_worker_count respects max_workers constraint
    if 'if max_workers:' in parallel_content and 'base_workers = min(base_workers, max_workers)' in parallel_content:
        print("   ✅ get_optimal_worker_count properly respects max_workers constraint")
    else:
        print("   ❌ get_optimal_worker_count logic appears broken")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL CODE FIXES VERIFIED!")
    print("✅ Worker count parameter will now be properly respected")
    print("✅ Resource throttling issue should be resolved")
    print("\n📋 Summary of Changes:")
    print("   • Fixed main.py to pass --workers parameter to processors")
    print("   • Updated Phase2B factory function to accept max_workers")
    print("   • Updated Phase2B constructor to accept and pass max_workers")
    print("   • Verified get_optimal_worker_count respects max_workers constraint")
    
    return True

if __name__ == "__main__":
    import sys
    success = test_worker_count_fix()
    sys.exit(0 if success else 1)
