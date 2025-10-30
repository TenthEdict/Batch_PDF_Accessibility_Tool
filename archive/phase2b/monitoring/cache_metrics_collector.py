"""
Hierarchical Cache Performance Metrics Collection
==============================================

Enhanced metrics collection system for Phase 2B hierarchical caching architecture.
Provides comprehensive tracking of cache performance across all three levels:
- Memory Cache (L1): Hot data with LRU eviction
- SSD Cache (L2): Frequently accessed data
- Disk Cache (L3): Long-term storage

This module extends the existing cache system with detailed performance analytics,
optimization recommendations, and cross-level performance correlation analysis.
"""

import time
import threading
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import logging


class CacheLevel(Enum):
    """Cache hierarchy levels for metrics tracking."""
    MEMORY = "L1_Memory"
    SSD = "L2_SSD" 
    DISK = "L3_Disk"


@dataclass
class CacheOperationMetric:
    """Individual cache operation performance metric."""
    operation_type: str  # 'get', 'put', 'evict', 'prefetch'
    cache_level: CacheLevel
    operation_id: str
    timestamp: datetime
    duration_ms: float
    key_hash: str  # Anonymized key for privacy
    data_size_bytes: int
    hit: bool  # True for cache hit, False for miss
    promotion: bool = False  # True if data was promoted to higher level
    demotion: bool = False  # True if data was demoted to lower level
    compression_ratio: float = 1.0
    tags: List[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CacheLevelMetrics:
    """Aggregated metrics for a specific cache level."""
    cache_level: CacheLevel
    collection_period: str
    total_operations: int
    total_gets: int
    total_puts: int
    total_evictions: int
    cache_hits: int
    cache_misses: int
    hit_rate_percent: float
    miss_rate_percent: float
    average_get_time_ms: float
    average_put_time_ms: float
    total_data_bytes: int
    current_entries: int
    promotion_count: int  # Items promoted to higher level
    demotion_count: int   # Items demoted to lower level
    compression_effectiveness: float
    optimization_score: float  # 0-100 performance score


@dataclass
class HierarchicalCacheMetrics:
    """Comprehensive hierarchical cache performance summary."""
    collection_timestamp: datetime
    collection_period: str
    
    # Per-level metrics
    memory_metrics: CacheLevelMetrics
    ssd_metrics: CacheLevelMetrics
    disk_metrics: CacheLevelMetrics
    
    # Cross-level analytics
    overall_hit_rate_percent: float
    cache_efficiency_score: float  # Weighted efficiency across levels
    data_flow_optimization: float  # How well data flows between levels
    
    # Performance insights
    hottest_access_patterns: List[str]
    optimization_recommendations: List[str]
    performance_trends: Dict[str, float]
    
    # Predictive metrics
    prefetch_accuracy_percent: float
    cache_warming_effectiveness: float


class HierarchicalCacheMetricsCollector:
    """
    Comprehensive metrics collection for hierarchical cache system.
    
    Provides detailed analytics across all cache levels with cross-level 
    performance correlation, optimization recommendations, and predictive insights.
    """
    
    def __init__(self, 
                 max_metrics_history: int = 50000,
                 metrics_persistence_path: Optional[Path] = None,
                 collection_enabled: bool = True,
                 detailed_tracking: bool = True):
        """
        Initialize hierarchical cache metrics collection.
        
        Args:
            max_metrics_history: Maximum metrics to retain in memory
            metrics_persistence_path: Path for metrics persistence
            collection_enabled: Enable/disable metrics collection
            detailed_tracking: Enable detailed operation tracking
        """
        self.max_metrics_history = max_metrics_history
        self.collection_enabled = collection_enabled
        self.detailed_tracking = detailed_tracking
        self.metrics_persistence_path = metrics_persistence_path or Path.home() / ".epubs" / "cache_metrics"
        
        # Thread-safe metrics storage
        self._metrics_lock = threading.RLock()
        
        # Per-level operation tracking
        self._memory_operations: deque = deque(maxlen=max_metrics_history)
        self._ssd_operations: deque = deque(maxlen=max_metrics_history)
        self._disk_operations: deque = deque(maxlen=max_metrics_history)
        
        # Performance counters per level
        self._level_counters = {
            CacheLevel.MEMORY: defaultdict(int),
            CacheLevel.SSD: defaultdict(int),
            CacheLevel.DISK: defaultdict(int)
        }
        
        # Timing statistics per level
        self._level_timings = {
            CacheLevel.MEMORY: defaultdict(list),
            CacheLevel.SSD: defaultdict(list),
            CacheLevel.DISK: defaultdict(list)
        }
        
        # Data flow tracking (promotions/demotions)
        self._data_flow_events = deque(maxlen=10000)
        
        # Access pattern tracking
        self._access_patterns = defaultdict(int)
        self._key_access_frequency = defaultdict(int)
        
        # Performance baseline tracking
        self._performance_baselines = {}
        self._optimization_history = []
        
        # Logger setup
        self.logger = logging.getLogger(f"{__name__}.HierarchicalCacheMetricsCollector")
        
        # Ensure metrics directory exists
        self.metrics_persistence_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Hierarchical Cache Metrics Collector initialized - "
                        f"History: {max_metrics_history}, Detailed: {detailed_tracking}")
    
    def record_cache_operation(self,
                              operation_type: str,
                              cache_level: CacheLevel,
                              key: str,
                              duration_ms: float,
                              data_size_bytes: int = 0,
                              hit: bool = False,
                              promotion: bool = False,
                              demotion: bool = False,
                              compression_ratio: float = 1.0,
                              tags: List[str] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Record a cache operation for metrics tracking.
        
        Args:
            operation_type: Type of operation ('get', 'put', 'evict', 'prefetch')
            cache_level: Which cache level the operation occurred on
            key: Cache key (will be hashed for privacy)
            duration_ms: Operation duration in milliseconds
            data_size_bytes: Size of data involved
            hit: Whether this was a cache hit
            promotion: Whether data was promoted to higher level
            demotion: Whether data was demoted to lower level
            compression_ratio: Compression effectiveness
            tags: Operation tags for categorization
            metadata: Additional operation metadata
            
        Returns:
            Operation ID for tracking
        """
        if not self.collection_enabled:
            return ""
            
        with self._metrics_lock:
            # Generate operation ID and anonymize key
            operation_id = f"{cache_level.value}_{int(time.time() * 1000000)}"
            key_hash = self._hash_key(key)
            
            # Create metric record
            metric = CacheOperationMetric(
                operation_type=operation_type,
                cache_level=cache_level,
                operation_id=operation_id,
                timestamp=datetime.now(),
                duration_ms=duration_ms,
                key_hash=key_hash,
                data_size_bytes=data_size_bytes,
                hit=hit,
                promotion=promotion,
                demotion=demotion,
                compression_ratio=compression_ratio,
                tags=tags or [],
                metadata=metadata
            )
            
            # Store in appropriate level queue
            if cache_level == CacheLevel.MEMORY:
                self._memory_operations.append(metric)
            elif cache_level == CacheLevel.SSD:
                self._ssd_operations.append(metric)
            elif cache_level == CacheLevel.DISK:
                self._disk_operations.append(metric)
            
            # Update counters
            self._level_counters[cache_level][operation_type] += 1
            self._level_counters[cache_level]['total_operations'] += 1
            
            if hit:
                self._level_counters[cache_level]['hits'] += 1
            else:
                self._level_counters[cache_level]['misses'] += 1
                
            # Track timing
            self._level_timings[cache_level][operation_type].append(duration_ms)
            
            # Track data flow events
            if promotion or demotion:
                self._data_flow_events.append({
                    'timestamp': datetime.now(),
                    'key_hash': key_hash,
                    'source_level': cache_level.value,
                    'promotion': promotion,
                    'demotion': demotion,
                    'data_size': data_size_bytes
                })
            
            # Track access patterns
            if self.detailed_tracking:
                pattern_key = f"{operation_type}_{cache_level.value}"
                self._access_patterns[pattern_key] += 1
                self._key_access_frequency[key_hash] += 1
                
            self.logger.debug(f"Recorded cache operation: {operation_type} on {cache_level.value} - "
                            f"Hit: {hit}, Duration: {duration_ms:.2f}ms")
            
            return operation_id
    
    def get_level_metrics(self, 
                         cache_level: CacheLevel,
                         time_window: Optional[timedelta] = None) -> CacheLevelMetrics:
        """
        Get comprehensive metrics for a specific cache level.
        
        Args:
            cache_level: Cache level to analyze
            time_window: Time window for analysis (default: all available)
            
        Returns:
            Aggregated metrics for the specified cache level
        """
        with self._metrics_lock:
            # Get operations for this level
            if cache_level == CacheLevel.MEMORY:
                operations = list(self._memory_operations)
            elif cache_level == CacheLevel.SSD:
                operations = list(self._ssd_operations)
            elif cache_level == CacheLevel.DISK:
                operations = list(self._disk_operations)
            else:
                operations = []
            
            # Filter by time window if specified
            if time_window:
                cutoff_time = datetime.now() - time_window
                operations = [op for op in operations if op.timestamp >= cutoff_time]
            
            if not operations:
                return self._empty_level_metrics(cache_level)
            
            # Calculate aggregated metrics
            total_ops = len(operations)
            get_ops = [op for op in operations if op.operation_type == 'get']
            put_ops = [op for op in operations if op.operation_type == 'put']
            evict_ops = [op for op in operations if op.operation_type == 'evict']
            
            hits = len([op for op in operations if op.hit])
            misses = total_ops - hits
            
            hit_rate = (hits / total_ops * 100) if total_ops > 0 else 0
            miss_rate = 100 - hit_rate
            
            # Calculate average timings
            avg_get_time = (sum(op.duration_ms for op in get_ops) / len(get_ops)) if get_ops else 0
            avg_put_time = (sum(op.duration_ms for op in put_ops) / len(put_ops)) if put_ops else 0
            
            # Data size calculations
            total_data = sum(op.data_size_bytes for op in operations)
            
            # Data flow calculations
            promotions = len([op for op in operations if op.promotion])
            demotions = len([op for op in operations if op.demotion])
            
            # Compression effectiveness
            compression_ratios = [op.compression_ratio for op in operations if op.compression_ratio > 0]
            avg_compression = (sum(compression_ratios) / len(compression_ratios)) if compression_ratios else 1.0
            
            # Calculate optimization score (0-100)
            optimization_score = self._calculate_optimization_score(
                hit_rate, avg_get_time, avg_put_time, avg_compression
            )
            
            return CacheLevelMetrics(
                cache_level=cache_level,
                collection_period=f"Last {total_ops} operations",
                total_operations=total_ops,
                total_gets=len(get_ops),
                total_puts=len(put_ops),
                total_evictions=len(evict_ops),
                cache_hits=hits,
                cache_misses=misses,
                hit_rate_percent=hit_rate,
                miss_rate_percent=miss_rate,
                average_get_time_ms=avg_get_time,
                average_put_time_ms=avg_put_time,
                total_data_bytes=total_data,
                current_entries=self._level_counters[cache_level]['current_entries'],
                promotion_count=promotions,
                demotion_count=demotions,
                compression_effectiveness=avg_compression,
                optimization_score=optimization_score
            )
    
    def get_hierarchical_summary(self,
                               time_window: Optional[timedelta] = None) -> HierarchicalCacheMetrics:
        """
        Generate comprehensive hierarchical cache performance summary.
        
        Args:
            time_window: Time window for analysis
            
        Returns:
            Complete hierarchical cache metrics summary
        """
        with self._metrics_lock:
            # Get metrics for each level
            memory_metrics = self.get_level_metrics(CacheLevel.MEMORY, time_window)
            ssd_metrics = self.get_level_metrics(CacheLevel.SSD, time_window)
            disk_metrics = self.get_level_metrics(CacheLevel.DISK, time_window)
            
            # Calculate overall hit rate (weighted by operations)
            total_ops = memory_metrics.total_operations + ssd_metrics.total_operations + disk_metrics.total_operations
            total_hits = memory_metrics.cache_hits + ssd_metrics.cache_hits + disk_metrics.cache_hits
            overall_hit_rate = (total_hits / total_ops * 100) if total_ops > 0 else 0
            
            # Calculate cache efficiency score (weighted by level importance)
            # Memory cache is most important, disk least important
            efficiency_score = (
                memory_metrics.optimization_score * 0.5 +
                ssd_metrics.optimization_score * 0.3 +
                disk_metrics.optimization_score * 0.2
            )
            
            # Calculate data flow optimization
            data_flow_opt = self._calculate_data_flow_optimization()
            
            # Generate recommendations
            recommendations = self._generate_cache_recommendations(
                memory_metrics, ssd_metrics, disk_metrics
            )
            
            # Get hottest access patterns
            hottest_patterns = self._get_hottest_access_patterns()
            
            # Calculate performance trends
            trends = self._calculate_performance_trends()
            
            # Calculate predictive metrics
            prefetch_accuracy = self._calculate_prefetch_accuracy()
            warming_effectiveness = self._calculate_cache_warming_effectiveness()
            
            return HierarchicalCacheMetrics(
                collection_timestamp=datetime.now(),
                collection_period=f"Analysis of {total_ops} total operations",
                memory_metrics=memory_metrics,
                ssd_metrics=ssd_metrics,
                disk_metrics=disk_metrics,
                overall_hit_rate_percent=overall_hit_rate,
                cache_efficiency_score=efficiency_score,
                data_flow_optimization=data_flow_opt,
                hottest_access_patterns=hottest_patterns,
                optimization_recommendations=recommendations,
                performance_trends=trends,
                prefetch_accuracy_percent=prefetch_accuracy,
                cache_warming_effectiveness=warming_effectiveness
            )
    
    def _hash_key(self, key: str) -> str:
        """Generate anonymized hash of cache key for privacy."""
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def _empty_level_metrics(self, cache_level: CacheLevel) -> CacheLevelMetrics:
        """Generate empty metrics for a cache level."""
        return CacheLevelMetrics(
            cache_level=cache_level,
            collection_period="No operations recorded",
            total_operations=0,
            total_gets=0,
            total_puts=0,
            total_evictions=0,
            cache_hits=0,
            cache_misses=0,
            hit_rate_percent=0.0,
            miss_rate_percent=0.0,
            average_get_time_ms=0.0,
            average_put_time_ms=0.0,
            total_data_bytes=0,
            current_entries=0,
            promotion_count=0,
            demotion_count=0,
            compression_effectiveness=1.0,
            optimization_score=0.0
        )
    
    def _calculate_optimization_score(self, 
                                    hit_rate: float,
                                    avg_get_time: float,
                                    avg_put_time: float,
                                    compression_ratio: float) -> float:
        """Calculate optimization score (0-100) for cache level."""
        # Hit rate component (0-40 points)
        hit_score = min(40, hit_rate * 0.4)
        
        # Speed component (0-30 points) - faster is better
        # Assume good performance: get < 10ms, put < 50ms
        get_score = max(0, 15 - (avg_get_time / 10) * 15) if avg_get_time > 0 else 15
        put_score = max(0, 15 - (avg_put_time / 50) * 15) if avg_put_time > 0 else 15
        
        # Compression component (0-30 points)
        compression_score = min(30, (compression_ratio - 1) * 30) if compression_ratio > 1 else 0
        
        return min(100, hit_score + get_score + put_score + compression_score)
    
    def _calculate_data_flow_optimization(self) -> float:
        """Calculate how well data flows between cache levels."""
        if not self._data_flow_events:
            return 50.0  # Neutral score
            
        recent_events = [e for e in self._data_flow_events 
                        if e['timestamp'] > datetime.now() - timedelta(hours=1)]
        
        if not recent_events:
            return 50.0
            
        promotions = len([e for e in recent_events if e['promotion']])
        demotions = len([e for e in recent_events if e['demotion']])
        total_flow = promotions + demotions
        
        if total_flow == 0:
            return 50.0
            
        # More promotions indicate good data flow optimization
        flow_ratio = promotions / total_flow
        return flow_ratio * 100
    
    def _generate_cache_recommendations(self,
                                      memory_metrics: CacheLevelMetrics,
                                      ssd_metrics: CacheLevelMetrics,
                                      disk_metrics: CacheLevelMetrics) -> List[str]:
        """Generate optimization recommendations based on metrics."""
        recommendations = []
        
        # Memory cache recommendations
        if memory_metrics.hit_rate_percent < 70:
            recommendations.append("Memory cache hit rate is low - consider increasing memory cache size")
        
        if memory_metrics.average_get_time_ms > 10:
            recommendations.append("Memory cache get operations are slow - review data structure efficiency")
            
        # SSD cache recommendations
        if ssd_metrics.hit_rate_percent < 50:
            recommendations.append("SSD cache effectiveness is low - review caching strategy")
            
        # Cross-level recommendations
        memory_to_ssd_ratio = memory_metrics.total_operations / max(ssd_metrics.total_operations, 1)
        if memory_to_ssd_ratio < 2:
            recommendations.append("Memory cache may be undersized relative to SSD cache usage")
            
        # Data flow recommendations
        if memory_metrics.promotion_count > memory_metrics.demotion_count * 2:
            recommendations.append("High promotion rate - consider preemptive cache warming")
            
        return recommendations if recommendations else ["Cache performance appears optimal"]
    
    def _get_hottest_access_patterns(self, limit: int = 10) -> List[str]:
        """Get the most frequent access patterns."""
        sorted_patterns = sorted(self._access_patterns.items(), 
                               key=lambda x: x[1], reverse=True)
        return [pattern for pattern, count in sorted_patterns[:limit]]
    
    def _calculate_performance_trends(self) -> Dict[str, float]:
        """Calculate performance trends over time."""
        # Simplified trend calculation
        return {
            "memory_hit_rate_trend": 0.0,  # Placeholder for trend calculation
            "ssd_hit_rate_trend": 0.0,
            "overall_efficiency_trend": 0.0
        }
    
    def _calculate_prefetch_accuracy(self) -> float:
        """Calculate accuracy of prefetch operations."""
        prefetch_ops = []
        for ops in [self._memory_operations, self._ssd_operations, self._disk_operations]:
            prefetch_ops.extend([op for op in ops if op.operation_type == 'prefetch'])
        
        if not prefetch_ops:
            return 0.0
            
        successful_prefetches = len([op for op in prefetch_ops if op.hit])
        return (successful_prefetches / len(prefetch_ops)) * 100
    
    def _calculate_cache_warming_effectiveness(self) -> float:
        """Calculate effectiveness of cache warming strategies."""
        # Simplified calculation - could be enhanced with more sophisticated analysis
        warming_ops = []
        for ops in [self._memory_operations, self._ssd_operations, self._disk_operations]:
            warming_ops.extend([op for op in ops 
                              if op.metadata and op.metadata.get('warming', False)])
        
        if not warming_ops:
            return 0.0
            
        effective_warming = len([op for op in warming_ops 
                               if op.metadata.get('subsequent_hit', False)])
        return (effective_warming / len(warming_ops)) * 100
    
    def persist_metrics(self, format_type: str = "json") -> Path:
        """Persist hierarchical cache metrics to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hierarchical_cache_metrics_{timestamp}.{format_type}"
        output_path = self.metrics_persistence_path / filename
        
        # Generate comprehensive summary
        summary = self.get_hierarchical_summary()
        
        with self._metrics_lock:
            if format_type == "json":
                metrics_data = {
                    "collection_metadata": {
                        "collection_time": datetime.now().isoformat(),
                        "total_memory_operations": len(self._memory_operations),
                        "total_ssd_operations": len(self._ssd_operations),
                        "total_disk_operations": len(self._disk_operations),
                        "collection_enabled": self.collection_enabled
                    },
                    "hierarchical_summary": asdict(summary),
                    "detailed_tracking_enabled": self.detailed_tracking
                }
                
                with open(output_path, 'w') as f:
                    json.dump(metrics_data, f, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        self.logger.info(f"Persisted hierarchical cache metrics to {output_path}")
        return output_path


# Global hierarchical cache metrics collector
_global_cache_metrics_collector: Optional[HierarchicalCacheMetricsCollector] = None


def get_cache_metrics_collector() -> HierarchicalCacheMetricsCollector:
    """Get global hierarchical cache metrics collector."""
    global _global_cache_metrics_collector
    if _global_cache_metrics_collector is None:
        _global_cache_metrics_collector = HierarchicalCacheMetricsCollector()
    return _global_cache_metrics_collector


def initialize_cache_metrics(enabled: bool = True,
                            detailed_tracking: bool = True,
                            persistence_path: Optional[Path] = None) -> HierarchicalCacheMetricsCollector:
    """Initialize global hierarchical cache metrics collection."""
    global _global_cache_metrics_collector
    _global_cache_metrics_collector = HierarchicalCacheMetricsCollector(
        collection_enabled=enabled,
        detailed_tracking=detailed_tracking,
        metrics_persistence_path=persistence_path
    )
    return _global_cache_metrics_collector
