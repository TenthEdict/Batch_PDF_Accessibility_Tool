#!/usr/bin/env python3
"""
Cache Service for ePubs Enhancement Pipeline

This module provides high-level caching services for the enhancement pipeline,
integrating with the CacheManager to provide seamless caching for OCR results,
ML analysis, and other processing intermediates.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, List, Callable
import time

from .cache_manager import CacheManager

logger = logging.getLogger(__name__)


class CacheService:
    """
    High-level cache service for the enhancement pipeline.
    
    Provides decorators and helper methods for caching enhancement results
    with automatic key generation and cache management.
    """
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize cache service.
        
        Args:
            cache_manager: Optional custom cache manager instance
        """
        self.cache_manager = cache_manager or CacheManager()
        self.logger = logging.getLogger(__name__)
        
        # Default cache settings
        self.default_expiration_hours = {
            'ocr': 24 * 7,      # OCR results: 1 week
            'ml_analysis': 24,   # ML analysis: 1 day  
            'pdf_enhancement': 24 * 3,  # PDF enhancement: 3 days
            'apple_silicon': 24,  # Apple Silicon analysis: 1 day
        }
        
        logger.info("Cache service initialized")
    
    def cached_enhancement(self, operation: str, expires_in_hours: Optional[int] = None):
        """
        Decorator for caching enhancement operation results.
        
        Args:
            operation: Operation type ('ocr', 'ml_analysis', etc.)
            expires_in_hours: Cache expiration in hours (None = use default)
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(self_or_instance, input_path: Path, *args, **kwargs):
                # Generate cache key
                cache_key = self.cache_manager.generate_cache_key(
                    input_path, operation, **kwargs
                )
                
                # Try to get from cache
                cached_result = self.cache_manager.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {operation}: {input_path.name}")
                    return cached_result
                
                # Execute function and cache result
                logger.debug(f"Cache miss for {operation}: {input_path.name}")
                start_time = time.time()
                result = func(self_or_instance, input_path, *args, **kwargs)
                processing_time = time.time() - start_time
                
                # Cache the result with metadata
                expiration = expires_in_hours or self.default_expiration_hours.get(operation, 24)
                metadata = {
                    'operation': operation,
                    'processing_time': processing_time,
                    'file_name': input_path.name,
                    'file_size': input_path.stat().st_size if input_path.exists() else 0
                }
                
                self.cache_manager.put(
                    cache_key, 
                    result, 
                    expires_in_hours=expiration,
                    metadata=metadata
                )
                
                return result
                
            return wrapper
        return decorator
    
    def get_cached_result(self, file_path: Path, operation: str, **kwargs) -> Optional[Any]:
        """
        Get cached result for a specific file and operation.
        
        Args:
            file_path: Path to the file
            operation: Operation type
            **kwargs: Operation parameters
            
        Returns:
            Cached result or None if not found
        """
        cache_key = self.cache_manager.generate_cache_key(file_path, operation, **kwargs)
        return self.cache_manager.get(cache_key)
    
    def store_result(self, file_path: Path, operation: str, result: Any, **kwargs) -> bool:
        """
        Store result in cache.
        
        Args:
            file_path: Path to the file
            operation: Operation type  
            result: Result to cache
            **kwargs: Operation parameters
            
        Returns:
            bool: True if stored successfully
        """
        cache_key = self.cache_manager.generate_cache_key(file_path, operation, **kwargs)
        expiration = self.default_expiration_hours.get(operation, 24)
        
        metadata = {
            'operation': operation,
            'file_name': file_path.name,
            'file_size': file_path.stat().st_size if file_path.exists() else 0
        }
        
        return self.cache_manager.put(
            cache_key, 
            result, 
            expires_in_hours=expiration,
            metadata=metadata
        )
    
    def invalidate_file_cache(self, file_path: Path) -> int:
        """
        Invalidate all cached results for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            int: Number of cache entries invalidated
        """
        # This is a simplified implementation
        # In practice, you'd need to track which keys belong to which files
        logger.warning(f"File cache invalidation not fully implemented for {file_path}")
        return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        return self.cache_manager.get_stats()
    
    def clear_cache(self) -> int:
        """Clear all cache entries."""
        return self.cache_manager.clear_all()
    
    def prune_cache(self) -> int:
        """Remove expired cache entries."""
        return self.cache_manager.prune_expired()
    
    def cleanup_old_cache(self, days_old: int = 30) -> int:
        """Remove cache entries older than specified days."""
        return self.cache_manager.cleanup_old_entries(days_old)
    
    def is_cache_healthy(self) -> Dict[str, Any]:
        """
        Check cache health and return status information.
        
        Returns:
            Dict with health status and recommendations
        """
        try:
            stats = self.get_cache_stats()
            
            health_status = {
                'healthy': True,
                'issues': [],
                'recommendations': []
            }
            
            # Check cache size
            size_mb = stats.get('total_size_mb', 0)
            if size_mb > 1000:  # >1GB
                health_status['issues'].append(f"Large cache size: {size_mb}MB")
                health_status['recommendations'].append("Consider running 'epubs cache prune'")
            
            # Check hit rate
            hit_rate = stats.get('hit_rate_percent', 0)
            if hit_rate < 20:
                health_status['issues'].append(f"Low cache hit rate: {hit_rate}%")
                health_status['recommendations'].append("Cache may not be effective for your workflow")
            
            # Check for errors
            if 'error' in stats:
                health_status['healthy'] = False
                health_status['issues'].append(f"Cache error: {stats['error']}")
            
            return health_status
            
        except Exception as e:
            return {
                'healthy': False,
                'issues': [f"Failed to check cache health: {e}"],
                'recommendations': ["Check cache directory permissions"]
            }