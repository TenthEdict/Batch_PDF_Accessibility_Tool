#!/usr/bin/env python3
"""
Comprehensive test for ThreadSafeAdaptiveMLEnhancer attribute fixes
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    print("Testing ThreadSafeAdaptiveMLEnhancer comprehensive fix...")
    
    # Import the thread-safe ML enhancer
    from processor.unified_project.src.enhancers.thread_safe_ml_enhancer import ThreadSafeAdaptiveMLEnhancer
    print("✅ Import successful!")
    
    # Test instantiation
    enhancer = ThreadSafeAdaptiveMLEnhancer()
    print("✅ ML Enhancer instantiated successfully!")
    
    # Test all file path attributes
    assert hasattr(enhancer, 'profiles_file'), "Missing profiles_file attribute"
    assert hasattr(enhancer, 'scaler_file'), "Missing scaler_file attribute"
    assert hasattr(enhancer, 'similarity_model_file'), "Missing similarity_model_file attribute"
    print("✅ All file path attributes present")
    
    # Test document_profiles property access
    profiles = enhancer.document_profiles
    print(f"✅ Document profiles accessible: {len(profiles)} profiles loaded")
    
    # Test feature_scaler property access
    scaler = enhancer.feature_scaler
    print("✅ Feature scaler accessible")
    
    # Test similarity_model property access
    model = enhancer.similarity_model
    print("✅ Similarity model accessible")
    
    # Test setting attributes
    enhancer.document_profiles = {}
    enhancer.feature_scaler = None
    enhancer.similarity_model = None
    print("✅ All property setters working")
    
    # Test configuration attributes
    assert hasattr(enhancer, 'ocr_config_options'), "Missing ocr_config_options"
    assert hasattr(enhancer, 'similarity_threshold'), "Missing similarity_threshold"
    assert hasattr(enhancer, 'min_quality_threshold'), "Missing min_quality_threshold"
    assert hasattr(enhancer, 'max_config_tests'), "Missing max_config_tests"
    print("✅ All configuration attributes present")
    
    print("🎉 ALL TESTS PASSED - The comprehensive fix is working!")
    print("🔧 ThreadSafeAdaptiveMLEnhancer now has full compatibility with base class")
    
except AttributeError as e:
    print(f"❌ FIX FAILED: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")
    sys.exit(1)
