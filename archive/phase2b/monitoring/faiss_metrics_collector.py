"""
FAISS Vector Database Performance Metrics Collection
=================================================

Comprehensive metrics collection system for Phase 2B FAISS vector database operations.
Tracks performance, utilization, and optimization opportunities for institutional deployment.

This module provides systematic measurement of:
- FAISS index operation timing (search, add, train)
- Vector similarity search performance
- Index utilization and efficiency metrics
- Memory usage and optimization recommendations
"""

import time
import threading
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import psutil


@dataclass
class FAISSOperationMetric:
    """Individual FAISS operation performance metric."""
    operation_type: str  # 'search', 'add', 'train', 'save', 'load'
    operation_id: str
    timestamp: datetime
    duration_ms: float
    vector_count: int
    dimension_count: int
    index_type: str  # 'Flat', 'IVF', 'HNSW'
    memory_usage_mb: float
    cpu_usage_percent: float
    success: bool
    error_message: Optional[str] = None
    additional_metadata: Optional[Dict[str, Any]] = None


@dataclass
class FAISSPerformanceSummary:
    """Aggregated FAISS performance summary for reporting."""
    collection_period: str
    total_operations: int
    successful_operations: int
    average_operation_time_ms: float
    fastest_operation_ms: float
    slowest_operation_ms: float
    total_vectors_processed: int
    average_vectors_per_second: float
    memory_efficiency_score: float
    index_type_distribution: Dict[str, int]
    operation_type_distribution: Dict[str, int]
    error_rate_percent: float
    recommendations: List[str]


class FAISSMetricsCollector:
    """
    Thread-safe FAISS vector database metrics collection system.
    
    Designed for Phase 2B production environments with comprehensive
    performance tracking and optimization recommendation generation.
    """
    
    def __init__(self, 
                 max_metrics_history: int = 10000,
                 metrics_persistence_path: Optional[Path] = None,
                 collection_enabled: bool = True):
        """
        Initialize FAISS metrics collection system.
        
        Args:
            max_metrics_history: Maximum number of metrics to retain in memory
            metrics_persistence_path: Optional path for metrics persistence
            collection_enabled: Enable/disable metrics collection
        """
        self.max_metrics_history = max_metrics_history
        self.collection_enabled = collection_enabled
        self.metrics_persistence_path = metrics_persistence_path or Path.home() / ".epubs" / "metrics"
        
        # Thread-safe metrics storage
        self._metrics_lock = threading.RLock()
        self._operation_metrics: deque = deque(maxlen=max_metrics_history)
        self._active_operations: Dict[str, float] = {}  # operation_id -> start_time
        
        # Performance tracking
        self._performance_counters = defaultdict(list)
        self._index_utilization = defaultdict(int)
        self._error_tracking = defaultdict(int)
        
        # Optimization tracking
        self._optimization_recommendations = []
        self._baseline_performance: Optional[Dict[str, float]] = None
        
        # Logger setup
        self.logger = logging.getLogger(f"{__name__}.FAISSMetricsCollector")
        
        # Ensure metrics directory exists
        self.metrics_persistence_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"FAISS Metrics Collector initialized - History: {max_metrics_history}, "
                        f"Persistence: {self.metrics_persistence_path}")
    
    def start_operation(self, 
                       operation_type: str,
                       operation_id: str,
                       vector_count: int = 0,
                       dimension_count: int = 0,
                       index_type: str = "Unknown",
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Mark the start of a FAISS operation for timing.
        
        Args:
            operation_type: Type of operation ('search', 'add', 'train', etc.)
            operation_id: Unique identifier for this operation
            vector_count: Number of vectors involved
            dimension_count: Vector dimension count
            index_type: FAISS index type being used
            metadata: Additional operation metadata
            
        Returns:
            Operation ID for completion tracking
        """
        if not self.collection_enabled:
            return operation_id
            
        with self._metrics_lock:
            start_time = time.time()
            self._active_operations[operation_id] = start_time
            
            self.logger.debug(f"Started FAISS operation: {operation_type} ({operation_id}) - "
                            f"Vectors: {vector_count}, Dimensions: {dimension_count}, "
                            f"Index: {index_type}")
            
            return operation_id
    
    def complete_operation(self,
                          operation_id: str,
                          success: bool = True,
                          error_message: Optional[str] = None,
                          additional_metadata: Optional[Dict[str, Any]] = None) -> Optional[FAISSOperationMetric]:
        """
        Mark the completion of a FAISS operation and record metrics.
        
        Args:
            operation_id: Operation ID from start_operation
            success: Whether the operation succeeded
            error_message: Error message if operation failed
            additional_metadata: Additional metadata to record
            
        Returns:
            Recorded metric or None if operation not found
        """
        if not self.collection_enabled:
            return None
            
        with self._metrics_lock:
            if operation_id not in self._active_operations:
                self.logger.warning(f"Attempted to complete unknown operation: {operation_id}")
                return None
                
            # Calculate duration
            start_time = self._active_operations.pop(operation_id)
            duration_ms = (time.time() - start_time) * 1000
            
            # Get current system metrics
            current_process = psutil.Process()
            memory_usage_mb = current_process.memory_info().rss / 1024 / 1024
            cpu_usage_percent = current_process.cpu_percent()
            
            # Extract operation details from metadata if available
            operation_type = additional_metadata.get('operation_type', 'unknown') if additional_metadata else 'unknown'
            vector_count = additional_metadata.get('vector_count', 0) if additional_metadata else 0
            dimension_count = additional_metadata.get('dimension_count', 0) if additional_metadata else 0
            index_type = additional_metadata.get('index_type', 'Unknown') if additional_metadata else 'Unknown'
            
            # Create metric record
            metric = FAISSOperationMetric(
                operation_type=operation_type,
                operation_id=operation_id,
                timestamp=datetime.now(),
                duration_ms=duration_ms,
                vector_count=vector_count,
                dimension_count=dimension_count,
                index_type=index_type,
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage_percent,
                success=success,
                error_message=error_message,
                additional_metadata=additional_metadata
            )
            
            # Store metric
            self._operation_metrics.append(metric)
            
            # Update performance counters
            self._performance_counters[operation_type].append(duration_ms)
            self._index_utilization[index_type] += 1
            
            if not success:
                self._error_tracking[operation_type] += 1
                
            self.logger.debug(f"Completed FAISS operation: {operation_type} ({operation_id}) - "
                            f"Duration: {duration_ms:.2f}ms, Success: {success}")
            
            # Trigger optimization analysis if threshold reached
            if len(self._operation_metrics) % 100 == 0:
                self._analyze_performance_trends()
                
            return metric
    
    def get_performance_summary(self, 
                               time_window: Optional[timedelta] = None,
                               operation_type_filter: Optional[str] = None) -> FAISSPerformanceSummary:
        """
        Generate comprehensive performance summary for specified time window.
        
        Args:
            time_window: Time window for metrics (default: all available)
            operation_type_filter: Filter by specific operation type
            
        Returns:
            Aggregated performance summary
        """
        with self._metrics_lock:
            # Filter metrics by time window and operation type
            filtered_metrics = list(self._operation_metrics)
            
            if time_window:
                cutoff_time = datetime.now() - time_window
                filtered_metrics = [m for m in filtered_metrics if m.timestamp >= cutoff_time]
                
            if operation_type_filter:
                filtered_metrics = [m for m in filtered_metrics if m.operation_type == operation_type_filter]
                
            if not filtered_metrics:
                return self._empty_performance_summary()
                
            # Calculate summary statistics
            successful_ops = [m for m in filtered_metrics if m.success]
            operation_times = [m.duration_ms for m in filtered_metrics]
            
            # Index type distribution
            index_dist = defaultdict(int)
            for metric in filtered_metrics:
                index_dist[metric.index_type] += 1
                
            # Operation type distribution
            op_dist = defaultdict(int)
            for metric in filtered_metrics:
                op_dist[metric.operation_type] += 1
                
            # Calculate efficiency metrics
            total_vectors = sum(m.vector_count for m in filtered_metrics)
            total_time_seconds = sum(operation_times) / 1000
            vectors_per_second = total_vectors / total_time_seconds if total_time_seconds > 0 else 0
            
            # Memory efficiency (simplified metric)
            avg_memory = sum(m.memory_usage_mb for m in filtered_metrics) / len(filtered_metrics)
            memory_efficiency = min(100.0, (1000.0 / avg_memory) * 100) if avg_memory > 0 else 0
            
            # Generate recommendations
            recommendations = self._generate_optimization_recommendations(filtered_metrics)
            
            return FAISSPerformanceSummary(
                collection_period=f"Last {len(filtered_metrics)} operations",
                total_operations=len(filtered_metrics),
                successful_operations=len(successful_ops),
                average_operation_time_ms=sum(operation_times) / len(operation_times),
                fastest_operation_ms=min(operation_times),
                slowest_operation_ms=max(operation_times),
                total_vectors_processed=total_vectors,
                average_vectors_per_second=vectors_per_second,
                memory_efficiency_score=memory_efficiency,
                index_type_distribution=dict(index_dist),
                operation_type_distribution=dict(op_dist),
                error_rate_percent=(len(filtered_metrics) - len(successful_ops)) / len(filtered_metrics) * 100,
                recommendations=recommendations
            )
    
    def persist_metrics(self, format_type: str = "json") -> Path:
        """
        Persist collected metrics to disk.
        
        Args:
            format_type: Output format ('json' or 'csv')
            
        Returns:
            Path to persisted metrics file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"faiss_metrics_{timestamp}.{format_type}"
        output_path = self.metrics_persistence_path / filename
        
        with self._metrics_lock:
            if format_type == "json":
                metrics_data = {
                    "collection_metadata": {
                        "collection_time": datetime.now().isoformat(),
                        "total_metrics": len(self._operation_metrics),
                        "collection_enabled": self.collection_enabled
                    },
                    "metrics": [asdict(metric) for metric in self._operation_metrics]
                }
                
                with open(output_path, 'w') as f:
                    json.dump(metrics_data, f, indent=2, default=str)
                    
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        self.logger.info(f"Persisted {len(self._operation_metrics)} FAISS metrics to {output_path}")
        return output_path
    
    def _empty_performance_summary(self) -> FAISSPerformanceSummary:
        """Generate empty performance summary for cases with no metrics."""
        return FAISSPerformanceSummary(
            collection_period="No metrics available",
            total_operations=0,
            successful_operations=0,
            average_operation_time_ms=0.0,
            fastest_operation_ms=0.0,
            slowest_operation_ms=0.0,
            total_vectors_processed=0,
            average_vectors_per_second=0.0,
            memory_efficiency_score=0.0,
            index_type_distribution={},
            operation_type_distribution={},
            error_rate_percent=0.0,
            recommendations=["No metrics collected yet - enable metrics collection to see recommendations"]
        )
    
    def _analyze_performance_trends(self) -> None:
        """Analyze performance trends and update optimization recommendations."""
        if len(self._operation_metrics) < 10:
            return
            
        recent_metrics = list(self._operation_metrics)[-100:]  # Last 100 operations
        
        # Analyze trends
        search_times = [m.duration_ms for m in recent_metrics if m.operation_type == 'search']
        if len(search_times) > 10:
            avg_search_time = sum(search_times) / len(search_times)
            if avg_search_time > 1000:  # 1 second threshold
                self._optimization_recommendations.append(
                    "Consider optimizing FAISS index type - search operations averaging >1s"
                )
    
    def _generate_optimization_recommendations(self, metrics: List[FAISSOperationMetric]) -> List[str]:
        """Generate optimization recommendations based on metrics analysis."""
        recommendations = []
        
        if not metrics:
            return ["No metrics available for analysis"]
            
        # Analyze search performance
        search_metrics = [m for m in metrics if m.operation_type == 'search']
        if search_metrics:
            avg_search_time = sum(m.duration_ms for m in search_metrics) / len(search_metrics)
            if avg_search_time > 500:
                recommendations.append("Search operations are slow - consider IVF or HNSW index types")
                
        # Analyze memory usage
        avg_memory = sum(m.memory_usage_mb for m in metrics) / len(metrics)
        if avg_memory > 1000:
            recommendations.append("High memory usage detected - consider index compression")
            
        # Analyze error rates
        error_count = len([m for m in metrics if not m.success])
        error_rate = error_count / len(metrics) * 100
        if error_rate > 5:
            recommendations.append(f"High error rate ({error_rate:.1f}%) - review FAISS configuration")
            
        # Index type recommendations
        index_usage = defaultdict(int)
        for m in metrics:
            index_usage[m.index_type] += 1
            
        if 'Flat' in index_usage and index_usage['Flat'] > len(metrics) * 0.8:
            recommendations.append("Consider advanced index types (IVF/HNSW) for better performance")
            
        return recommendations if recommendations else ["Performance appears optimal - no recommendations"]


# Global metrics collector instance for easy access
_global_faiss_metrics_collector: Optional[FAISSMetricsCollector] = None


def get_faiss_metrics_collector() -> FAISSMetricsCollector:
    """Get global FAISS metrics collector instance."""
    global _global_faiss_metrics_collector
    if _global_faiss_metrics_collector is None:
        _global_faiss_metrics_collector = FAISSMetricsCollector()
    return _global_faiss_metrics_collector


def initialize_faiss_metrics(enabled: bool = True, 
                           persistence_path: Optional[Path] = None) -> FAISSMetricsCollector:
    """Initialize global FAISS metrics collection."""
    global _global_faiss_metrics_collector
    _global_faiss_metrics_collector = FAISSMetricsCollector(
        collection_enabled=enabled,
        metrics_persistence_path=persistence_path
    )
    return _global_faiss_metrics_collector
