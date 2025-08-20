#!/usr/bin/env python3
"""
Comprehensive diagnostic test suite for AccessibilityModelManager.

Validates thread-safety, caching performance, model loading, and Phase 2B integration
readiness for production accessibility training pipeline deployment.
"""

import pytest
import tempfile
import threading
import time
import json
import pickle
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from enhancers.accessibility_model_manager import (
        AccessibilityModelManager, 
        ModelMetadata, 
        ModelCacheEntry
    )
    import joblib
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    pytest.skip(f"Required dependencies not available: {e}", allow_module_level=True)


class TestAccessibilityModelManager:
    """Comprehensive test suite for AccessibilityModelManager diagnostic validation."""
    
    @pytest.fixture
    def temp_model_dir(self):
        """Create temporary directory with mock accessibility models."""
        with tempfile.TemporaryDirectory() as temp_dir:
            model_dir = Path(temp_dir)
            
            # Create mock accessibility classification model
            clf_model = LogisticRegression(random_state=42)
            X_dummy = np.random.rand(100, 128)  # 128-dimensional accessibility features
            y_dummy = np.random.randint(0, 2, 100)
            clf_model.fit(X_dummy, y_dummy)
            
            clf_path = model_dir / "accessibility_classifier_v1.joblib"
            joblib.dump(clf_model, clf_path)
            
            # Create model metadata file
            clf_metadata = {
                "model_version": "1.0.0",
                "compatibility_version": "2.0",
                "performance_metrics": {
                    "accuracy": 0.92,
                    "precision": 0.89,
                    "recall": 0.94,
                    "f1_score": 0.91
                },
                "training_dataset_size": 1000,
                "wcag_compliance_patterns": ["heading_structure", "alt_text", "reading_order"]
            }
            
            metadata_path = model_dir / "accessibility_classifier_v1_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(clf_metadata, f, indent=2)
            
            # Create second model for multi-model testing
            rf_model = RandomForestClassifier(n_estimators=10, random_state=42)
            rf_model.fit(X_dummy, y_dummy)
            
            rf_path = model_dir / "accessibility_regressor_v2.joblib"
            joblib.dump(rf_model, rf_path)
            
            rf_metadata = {
                "model_version": "2.1.0",
                "compatibility_version": "2.0",
                "performance_metrics": {
                    "mse": 0.15,
                    "r2_score": 0.88,
                    "mae": 0.12
                }
            }
            
            rf_metadata_path = model_dir / "accessibility_regressor_v2_metadata.json"
            with open(rf_metadata_path, 'w') as f:
                json.dump(rf_metadata, f, indent=2)
            
            yield model_dir
    
    @pytest.fixture
    def model_manager(self):
        """Create AccessibilityModelManager instance for testing."""
        return AccessibilityModelManager(
            cache_size_mb=64,  # Small cache for testing
            max_models=3,
            enable_persistence=False
        )
    
    def test_initialization_and_configuration(self, model_manager):
        """Test AccessibilityModelManager initialization and configuration."""
        assert model_manager.cache_size_mb == 64
        assert model_manager.max_models == 3
        assert model_manager.enable_persistence == False
        
        # Check internal state initialization
        assert len(model_manager._model_cache) == 0
        assert len(model_manager._model_registry) == 0
        assert model_manager._current_cache_size == 0
        
        # Verify thread safety components
        assert model_manager._cache_lock is not None
        assert model_manager._registry_lock is not None
        assert model_manager._stats_lock is not None
    
    def test_model_discovery_and_registration(self, model_manager, temp_model_dir):
        """Test intelligent model discovery and registration functionality."""
        # Test model discovery
        discovered_models = model_manager.discover_and_register_models([temp_model_dir])
        
        # Verify discovery results
        assert len(discovered_models) == 2
        assert "accessibility_classifier_v1_1.0.0" in discovered_models
        assert "accessibility_regressor_v2_2.1.0" in discovered_models
        
        # Test model registry
        available_models = model_manager.get_available_models()
        assert len(available_models) == 2
        
        # Verify model metadata extraction
        clf_info = model_manager.get_model_info("accessibility_classifier_v1_1.0.0")
        assert clf_info is not None
        assert clf_info['model_type'] == 'classifier'
        assert clf_info['input_dimensions'] == 128
        assert clf_info['performance_metrics']['accuracy'] == 0.92
        
        rf_info = model_manager.get_model_info("accessibility_regressor_v2_2.1.0")
        assert rf_info is not None
        assert rf_info['model_type'] == 'classifier'  # RandomForest has predict_proba
        assert rf_info['input_dimensions'] == 128
    
    def test_model_loading_and_caching(self, model_manager, temp_model_dir):
        """Test model loading with LRU caching behavior."""
        # Register models first
        model_manager.discover_and_register_models([temp_model_dir])
        
        # Test initial model loading (cache miss)
        model1 = model_manager.load_model("accessibility_classifier_v1_1.0.0")
        assert model1 is not None
        assert hasattr(model1, 'predict')
        
        # Verify cache entry created
        assert len(model_manager._model_cache) == 1
        assert model_manager._current_cache_size > 0
        
        # Test cache hit
        stats_before = model_manager.get_performance_stats()
        model1_cached = model_manager.load_model("accessibility_classifier_v1_1.0.0")
        stats_after = model_manager.get_performance_stats()
        
        assert model1 is model1_cached  # Same object reference
        assert stats_after['cache_hits'] == stats_before['cache_hits'] + 1
        
        # Test LRU behavior with cache limit
        model2 = model_manager.load_model("accessibility_regressor_v2_2.1.0")
        assert model2 is not None
        assert len(model_manager._model_cache) == 2
    
    def test_concurrent_model_access(self, model_manager, temp_model_dir):
        """Test thread-safety under concurrent model access."""
        model_manager.discover_and_register_models([temp_model_dir])
        
        results = []
        errors = []
        
        def load_model_worker(model_key, worker_id):
            """Worker function for concurrent model loading."""
            try:
                for i in range(5):  # Multiple loads per worker
                    model = model_manager.load_model(model_key)
                    if model is not None:
                        # Simulate model usage
                        if hasattr(model, 'predict'):
                            dummy_input = np.random.rand(1, 128)
                            prediction = model.predict(dummy_input)
                            results.append(f"worker_{worker_id}_iteration_{i}_success")
                        time.sleep(0.01)  # Small delay to increase contention
                    else:
                        errors.append(f"worker_{worker_id}_iteration_{i}_failed_load")
            except Exception as e:
                errors.append(f"worker_{worker_id}_exception_{str(e)}")
        
        # Test concurrent access with multiple threads
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            model_keys = ["accessibility_classifier_v1_1.0.0", "accessibility_regressor_v2_2.1.0"]
            
            for worker_id in range(8):
                model_key = model_keys[worker_id % len(model_keys)]
                future = executor.submit(load_model_worker, model_key, worker_id)
                futures.append(future)
            
            # Wait for all workers to complete
            for future in as_completed(futures):
                future.result()  # Will raise exception if worker failed
        
        # Verify no errors and successful concurrent operations
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        assert len(results) == 40  # 8 workers * 5 iterations each
        
        # Verify cache integrity after concurrent access
        stats = model_manager.get_performance_stats()
        assert stats['cache_hits'] > 0
        assert len(model_manager._model_cache) <= model_manager.max_models
    
    def test_memory_management_and_cache_eviction(self, model_manager, temp_model_dir):
        """Test memory management and LRU cache eviction behavior."""
        model_manager.discover_and_register_models([temp_model_dir])
        
        # Load models to fill cache
        model1 = model_manager.load_model("accessibility_classifier_v1_1.0.0")
        model2 = model_manager.load_model("accessibility_regressor_v2_2.1.0")
        
        initial_cache_size = model_manager._current_cache_size
        initial_model_count = len(model_manager._model_cache)
        
        assert initial_cache_size > 0
        assert initial_model_count == 2
        
        # Test memory usage reporting
        stats = model_manager.get_performance_stats()
        assert stats['memory_usage_mb'] > 0
        assert stats['cache_utilization'] > 0
        
        # Test cache cleanup
        model_manager.cleanup_cache(max_age_hours=0.001)  # Very short age for testing
        time.sleep(0.1)  # Wait for cleanup age threshold
        model_manager.cleanup_cache(max_age_hours=0.001)
        
        # Note: Cleanup only removes old entries, so cache might still have recent models
        final_stats = model_manager.get_performance_stats()
        assert final_stats['last_cleanup'] > stats['last_cleanup']
    
    def test_performance_statistics_tracking(self, model_manager, temp_model_dir):
        """Test comprehensive performance statistics tracking."""
        model_manager.discover_and_register_models([temp_model_dir])
        
        # Initial statistics
        initial_stats = model_manager.get_performance_stats()
        assert initial_stats['models_loaded'] == 0
        assert initial_stats['cache_hits'] == 0
        assert initial_stats['cache_misses'] == 0
        assert initial_stats['cache_hit_rate'] == 0
        
        # Load model and verify statistics update
        model = model_manager.load_model("accessibility_classifier_v1_1.0.0")
        assert model is not None
        
        stats_after_load = model_manager.get_performance_stats()
        assert stats_after_load['models_loaded'] == 1
        assert stats_after_load['cache_misses'] == 1
        assert stats_after_load['total_load_time'] > 0
        
        # Load same model again (cache hit)
        model_cached = model_manager.load_model("accessibility_classifier_v1_1.0.0")
        
        final_stats = model_manager.get_performance_stats()
        assert final_stats['cache_hits'] == 1
        assert final_stats['cache_hit_rate'] == 50.0  # 1 hit out of 2 total requests
        assert final_stats['cached_models'] == 1
    
    def test_error_handling_and_robustness(self, model_manager):
        """Test error handling for invalid models and edge cases."""
        # Test loading non-existent model
        model = model_manager.load_model("nonexistent_model")
        assert model is None
        
        # Test getting info for non-existent model
        info = model_manager.get_model_info("nonexistent_model")
        assert info is None
        
        # Test discovery with non-existent paths
        discovered = model_manager.discover_and_register_models([Path("/nonexistent/path")])
        assert len(discovered) == 0
        
        # Test cache clearing
        model_manager.clear_cache()
        assert len(model_manager._model_cache) == 0
        assert model_manager._current_cache_size == 0
        
        # Verify statistics after cache clear
        stats = model_manager.get_performance_stats()
        assert stats['cached_models'] == 0
        assert stats['memory_usage_mb'] == 0
    
    def test_phase2b_integration_compatibility(self, model_manager, temp_model_dir):
        """Test Phase 2B integration compatibility and threading behavior."""
        model_manager.discover_and_register_models([temp_model_dir])
        
        # Simulate Phase 2B parallel processing scenario
        def simulate_phase2b_worker(worker_id):
            """Simulate Phase 2B worker accessing accessibility models."""
            models_used = []
            
            for doc_id in range(3):  # Process 3 documents per worker
                # Simulate document processing requiring model access
                model = model_manager.load_model("accessibility_classifier_v1_1.0.0")
                if model is not None:
                    # Simulate accessibility pattern classification
                    features = np.random.rand(1, 128)  # 128-dimensional accessibility features
                    prediction = model.predict(features)
                    models_used.append(f"worker_{worker_id}_doc_{doc_id}_classified")
                
                time.sleep(0.05)  # Simulate processing time
            
            return models_used
        
        # Simulate 6 parallel workers (typical Phase 2B configuration)
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(simulate_phase2b_worker, i) for i in range(6)]
            all_results = []
            
            for future in as_completed(futures):
                worker_results = future.result()
                all_results.extend(worker_results)
        
        # Verify successful parallel processing
        assert len(all_results) == 18  # 6 workers * 3 documents each
        
        # Verify cache performance under parallel load
        final_stats = model_manager.get_performance_stats()
        assert final_stats['cache_hits'] > 0  # Should have cache hits from parallel access
        assert final_stats['cache_hit_rate'] > 50  # Good cache utilization expected


if __name__ == "__main__":
    # Run diagnostic tests with verbose output
    pytest.main([
        __file__, 
        "-v", 
        "--tb=short",
        "--capture=no"
    ])
