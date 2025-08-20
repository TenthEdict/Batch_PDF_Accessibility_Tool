#!/usr/bin/env python3
"""
AccessibilityModelManager - Enhanced model management and caching for production ML accessibility.

This module provides intelligent model loading, caching, and management capabilities
for the AccessibilityMLEnhancer, optimized for production deployment with Phase 2B
compatibility and high-performance characteristics.

Key Features:
- Intelligent model discovery with scoring and validation
- LRU-based model caching with memory management
- Version management and compatibility tracking
- Performance monitoring and optimization
- Thread-safe operations for parallel processing
"""

import logging
import time
import threading
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from collections import OrderedDict
import pickle

try:
    import joblib
    import numpy as np
    from sklearn.base import BaseEstimator
    MODEL_DEPS_AVAILABLE = True
except ImportError:
    MODEL_DEPS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ModelMetadata:
    """Metadata for accessibility models."""
    
    model_name: str
    model_version: str
    training_timestamp: float
    model_type: str  # 'classifier', 'regressor', etc.
    input_dimensions: int
    performance_metrics: Dict[str, float]
    compatibility_version: str
    file_path: str
    file_size: int
    load_time: float = 0.0
    last_used: float = 0.0
    usage_count: int = 0


@dataclass
class ModelCacheEntry:
    """Cache entry for loaded models."""
    
    model: Any  # The actual model object
    metadata: ModelMetadata
    memory_size: int  # Estimated memory usage in bytes
    cached_at: float
    last_accessed: float
    access_count: int


class AccessibilityModelManager:
    """
    Enhanced model management system for AccessibilityMLEnhancer.
    
    Provides intelligent model loading, caching, validation, and performance
    monitoring optimized for production deployment and Phase 2B compatibility.
    """
    
    def __init__(self, 
                 cache_size_mb: int = 512,
                 max_models: int = 10,
                 enable_persistence: bool = True):
        """
        Initialize the model manager.
        
        Args:
            cache_size_mb: Maximum cache size in megabytes
            max_models: Maximum number of models to keep in cache
            enable_persistence: Whether to persist cache metadata
        """
        self.cache_size_mb = cache_size_mb
        self.max_models = max_models
        self.enable_persistence = enable_persistence
        
        # Model cache with LRU behavior
        self._model_cache: OrderedDict[str, ModelCacheEntry] = OrderedDict()
        self._cache_lock = threading.RLock()
        
        # Model registry and metadata
        self._model_registry: Dict[str, ModelMetadata] = {}
        self._registry_lock = threading.RLock()
        
        # Performance tracking
        self._performance_stats = {
            'models_loaded': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_load_time': 0.0,
            'memory_usage_mb': 0.0,
            'last_cleanup': time.time()
        }
        self._stats_lock = threading.Lock()
        
        # Configuration
        self._cache_size_bytes = cache_size_mb * 1024 * 1024
        self._current_cache_size = 0
        
        logger.info(f"AccessibilityModelManager initialized: cache_size={cache_size_mb}MB, max_models={max_models}")
    
    def discover_and_register_models(self, search_paths: List[Path]) -> Dict[str, ModelMetadata]:
        """
        Discover and register accessibility models from search paths.
        
        Args:
            search_paths: List of paths to search for models
            
        Returns:
            Dictionary of discovered model metadata
        """
        discovered_models = {}
        
        with self._registry_lock:
            for search_path in search_paths:
                if not search_path.exists():
                    continue
                
                logger.debug(f"Searching for models in: {search_path}")
                
                # Look for joblib model files
                for model_file in search_path.glob("*.joblib"):
                    try:
                        metadata = self._extract_model_metadata(model_file)
                        if metadata:
                            model_key = f"{metadata.model_name}_{metadata.model_version}"
                            self._model_registry[model_key] = metadata
                            discovered_models[model_key] = metadata
                            logger.info(f"Registered model: {model_key}")
                    
                    except Exception as e:
                        logger.warning(f"Failed to register model {model_file}: {e}")
        
        logger.info(f"Model discovery complete: {len(discovered_models)} models registered")
        return discovered_models
    
    def _extract_model_metadata(self, model_file: Path) -> Optional[ModelMetadata]:
        """
        Extract metadata from a model file.
        
        Args:
            model_file: Path to the model file
            
        Returns:
            ModelMetadata if successful, None otherwise
        """
        try:
            # Get file statistics
            stat = model_file.stat()
            file_size = stat.st_size
            modification_time = stat.st_mtime
            
            # Try to load model to get basic info
            model = joblib.load(model_file)
            
            # Extract model information
            model_name = model_file.stem
            model_type = 'unknown'
            input_dimensions = 0
            
            if hasattr(model, 'n_features_in_'):
                input_dimensions = model.n_features_in_
            
            # Determine model type
            if hasattr(model, 'predict_proba'):
                model_type = 'classifier'
            elif hasattr(model, 'predict'):
                model_type = 'regressor'
            
            # Look for accompanying metadata file
            metadata_file = model_file.parent / f"{model_file.stem}_metadata.json"
            performance_metrics = {}
            model_version = "unknown"
            compatibility_version = "1.0"
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata_json = json.load(f)
                        performance_metrics = metadata_json.get('performance_metrics', {})
                        model_version = metadata_json.get('model_version', 'unknown')
                        compatibility_version = metadata_json.get('compatibility_version', '1.0')
                except Exception as e:
                    logger.warning(f"Could not load metadata file {metadata_file}: {e}")
            
            return ModelMetadata(
                model_name=model_name,
                model_version=model_version,
                training_timestamp=modification_time,
                model_type=model_type,
                input_dimensions=input_dimensions,
                performance_metrics=performance_metrics,
                compatibility_version=compatibility_version,
                file_path=str(model_file),
                file_size=file_size
            )
            
        except Exception as e:
            logger.error(f"Failed to extract metadata from {model_file}: {e}")
            return None
    
    def load_model(self, model_key: str, force_reload: bool = False) -> Optional[Any]:
        """
        Load a model with intelligent caching.
        
        Args:
            model_key: Key identifying the model to load
            force_reload: Whether to force reload even if cached
            
        Returns:
            Loaded model object, or None if loading fails
        """
        with self._cache_lock:
            # Check cache first
            if not force_reload and model_key in self._model_cache:
                cache_entry = self._model_cache[model_key]
                cache_entry.last_accessed = time.time()
                cache_entry.access_count += 1
                
                # Move to end (most recently used)
                self._model_cache.move_to_end(model_key)
                
                with self._stats_lock:
                    self._performance_stats['cache_hits'] += 1
                
                logger.debug(f"Model cache hit: {model_key}")
                return cache_entry.model
            
            # Cache miss - need to load model
            with self._stats_lock:
                self._performance_stats['cache_misses'] += 1
            
            # Get model metadata
            if model_key not in self._model_registry:
                logger.error(f"Model not registered: {model_key}")
                return None
            
            metadata = self._model_registry[model_key]
            
            # Load the model
            start_time = time.time()
            try:
                logger.info(f"Loading model from: {metadata.file_path}")
                model = joblib.load(metadata.file_path)
                
                load_time = time.time() - start_time
                metadata.load_time = load_time
                metadata.last_used = time.time()
                metadata.usage_count += 1
                
                # Estimate memory usage
                memory_size = self._estimate_model_memory(model)
                
                # Ensure cache capacity
                self._ensure_cache_capacity(memory_size)
                
                # Create cache entry
                cache_entry = ModelCacheEntry(
                    model=model,
                    metadata=metadata,
                    memory_size=memory_size,
                    cached_at=time.time(),
                    last_accessed=time.time(),
                    access_count=1
                )
                
                # Add to cache
                self._model_cache[model_key] = cache_entry
                self._current_cache_size += memory_size
                
                # Update statistics
                with self._stats_lock:
                    self._performance_stats['models_loaded'] += 1
                    self._performance_stats['total_load_time'] += load_time
                    self._performance_stats['memory_usage_mb'] = self._current_cache_size / (1024 * 1024)
                
                logger.info(f"Model loaded successfully: {model_key} ({load_time:.3f}s, {memory_size/1024/1024:.1f}MB)")
                
                return model
                
            except Exception as e:
                logger.error(f"Failed to load model {model_key}: {e}")
                return None
    
    def _estimate_model_memory(self, model: Any) -> int:
        """
        Estimate memory usage of a model.
        
        Args:
            model: The model object
            
        Returns:
            Estimated memory usage in bytes
        """
        try:
            # Use pickle to estimate size
            model_bytes = pickle.dumps(model)
            return len(model_bytes)
        except:
            # Fallback estimation
            return 10 * 1024 * 1024  # 10MB default
    
    def _ensure_cache_capacity(self, required_bytes: int):
        """
        Ensure cache has capacity for new model by evicting old ones if necessary.
        
        Args:
            required_bytes: Number of bytes required
        """
        # Check if we need to evict models
        while (self._current_cache_size + required_bytes > self._cache_size_bytes or 
               len(self._model_cache) >= self.max_models):
            
            if not self._model_cache:
                break
            
            # Remove least recently used model
            lru_key, lru_entry = self._model_cache.popitem(last=False)
            self._current_cache_size -= lru_entry.memory_size
            
            logger.debug(f"Evicted model from cache: {lru_key} "
                        f"(freed {lru_entry.memory_size/1024/1024:.1f}MB)")
    
    def get_model_info(self, model_key: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive information about a model.
        
        Args:
            model_key: Key identifying the model
            
        Returns:
            Dictionary with model information
        """
        with self._registry_lock:
            if model_key not in self._model_registry:
                return None
            
            metadata = self._model_registry[model_key]
            info = asdict(metadata)
            
            # Add cache information if cached
            with self._cache_lock:
                if model_key in self._model_cache:
                    cache_entry = self._model_cache[model_key]
                    info['cached'] = True
                    info['cache_info'] = {
                        'cached_at': cache_entry.cached_at,
                        'last_accessed': cache_entry.last_accessed,
                        'access_count': cache_entry.access_count,
                        'memory_size_mb': cache_entry.memory_size / (1024 * 1024)
                    }
                else:
                    info['cached'] = False
            
            return info
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available model keys.
        
        Returns:
            List of model keys
        """
        with self._registry_lock:
            return list(self._model_registry.keys())
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for the model manager.
        
        Returns:
            Dictionary with performance statistics
        """
        with self._stats_lock:
            stats = dict(self._performance_stats)
        
        with self._cache_lock:
            stats['cached_models'] = len(self._model_cache)
            stats['cache_size_mb'] = self._current_cache_size / (1024 * 1024)
            stats['cache_utilization'] = (self._current_cache_size / self._cache_size_bytes) * 100
        
        # Calculate hit rate
        total_requests = stats['cache_hits'] + stats['cache_misses']
        stats['cache_hit_rate'] = (stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return stats
    
    def cleanup_cache(self, max_age_hours: float = 24.0):
        """
        Clean up old cache entries.
        
        Args:
            max_age_hours: Maximum age for cache entries in hours
        """
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()
        
        with self._cache_lock:
            to_remove = []
            
            for model_key, cache_entry in self._model_cache.items():
                age = current_time - cache_entry.cached_at
                last_access_age = current_time - cache_entry.last_accessed
                
                # Remove if too old and not recently accessed
                if age > max_age_seconds and last_access_age > max_age_seconds / 2:
                    to_remove.append(model_key)
            
            for model_key in to_remove:
                cache_entry = self._model_cache.pop(model_key)
                self._current_cache_size -= cache_entry.memory_size
                logger.info(f"Cleaned up old cached model: {model_key}")
        
        with self._stats_lock:
            self._performance_stats['last_cleanup'] = current_time
    
    def clear_cache(self):
        """Clear all cached models."""
        with self._cache_lock:
            self._model_cache.clear()
            self._current_cache_size = 0
        
        logger.info("Model cache cleared")
