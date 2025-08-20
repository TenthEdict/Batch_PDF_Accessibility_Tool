#!/usr/bin/env python3
"""
Quick test for ThreadSafeAdaptiveMLEnhancer document_profiles fix
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    print("Testing ThreadSafeAdaptiveMLEnhancer fix...")
    
    # Import the thread-safe ML enhancer
    from processor.unified_project.src.enhancers.thread_safe_ml_enhancer import ThreadSafeAdaptiveMLEnhancer
    print("✅ Import successful!")
    
    # Test instantiation
    enhancer = ThreadSafeAdaptiveMLEnhancer()
    print("✅ ML Enhancer instantiated successfully!")
    
    # Test document_profiles property access
    profiles = enhancer.document_profiles
    print(f"✅ Document profiles accessible: {len(profiles)} profiles loaded")
    
    # Test setting document_profiles
    enhancer.document_profiles = {}
    print("✅ Document profiles setter working")
    
    print("🎉 ALL TESTS PASSED - The fix is working!")
    
except AttributeError as e:
    if "document_profiles" in str(e):
        print(f"❌ FIX FAILED: {e}")
        sys.exit(1)
    else:
        raise
except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")
    sys.exit(1)
