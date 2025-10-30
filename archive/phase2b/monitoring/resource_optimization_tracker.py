"""
Resource Usage Optimization Tracking System
=========================================

Comprehensive resource monitoring and optimization tracking for Phase 2B ePubs processing.
Provides real-time monitoring of CPU, memory, disk I/O, and network usage with intelligent
optimization recommendations for institutional deployment environments.

This module integrates with:
- FAISS vector database resource usage
- Hierarchical cache system resource optimization
- ML pattern learning resource efficiency
- Batch processing resource management
- Cross-platform resource monitoring (Windows/macOS/Linux)
"""

import time
import threading
import json
import psutil
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, NamedTuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import logging
import subprocess


class ResourceType(Enum):
    """Types of system resources being monitored."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK = "network"
    GPU = "gpu"  # Future support for GPU acceleration
    PROCESS = "process"


class OptimizationLevel(Enum):
    """Resource optimization levels."""
    CONSERVATIVE = "conservative"  # Minimal resource usage
    BALANCED = "balanced"         # Balanced performance/resource usage
    AGGRESSIVE = "aggressive"     # Maximum performance
    CUSTOM = "custom"            # Custom optimization profile


@dataclass
class ResourceSnapshot:
    """Point-in-time resource usage snapshot."""
    timestamp: datetime
    
    # CPU metrics
    cpu_percent: float
    cpu_count: int
    cpu_freq_current: float
    cpu_freq_max: float
    load_average: Tuple[float, float, float]  # 1, 5, 15 minute averages
    
    # Memory metrics
    memory_total_gb: float
    memory_available_gb: float
    memory_used_gb: float
    memory_percent: float
    swap_total_gb: float
    swap_used_gb: float
    swap_percent: float
    
    # Disk I/O metrics
    disk_read_bytes: int
    disk_write_bytes: int
    disk_read_count: int
    disk_write_count: int
    disk_read_time: float
    disk_write_time: float
    disk_usage_percent: float
    
    # Network metrics
    network_bytes_sent: int
    network_bytes_recv: int
    network_packets_sent: int
    network_packets_recv: int
    network_errors_in: int
    network_errors_out: int
    
    # Process-specific metrics
    process_cpu_percent: float
    process_memory_mb: float
    process_memory_percent: float
    process_num_threads: int
    process_num_fds: int  # File descriptors (Unix) or handles (Windows)
    
    # System information
    system_uptime: float
    boot_time: datetime


@dataclass
class ResourceThreshold:
    """Resource usage thresholds for optimization triggers."""
    resource_type: ResourceType
    warning_threshold: float
    critical_threshold: float
    optimization_threshold: float
    measurement_unit: str
    description: str


@dataclass
class OptimizationRecommendation:
    """Resource optimization recommendation."""
    recommendation_id: str
    timestamp: datetime
    resource_type: ResourceType
    severity: str  # 'info', 'warning', 'critical'
    current_usage: float
    recommended_action: str
    expected_improvement: float
    implementation_complexity: str  # 'low', 'medium', 'high'
    estimated_impact: str
    related_components: List[str]


@dataclass
class ResourceOptimizationProfile:
    """Resource optimization configuration profile."""
    profile_name: str
    optimization_level: OptimizationLevel
    
    # Processing configuration
    max_parallel_workers: int
    memory_limit_gb: float
    cpu_limit_percent: float
    
    # Cache configuration
    cache_memory_limit_mb: int
    cache_disk_limit_gb: float
    
    # FAISS configuration
    faiss_memory_limit_mb: int
    faiss_index_type_preference: str  # 'Flat', 'IVF', 'HNSW'
    
    # ML optimization settings
    ml_batch_size: int
    ml_memory_limit_mb: int
    
    # Monitoring configuration
    monitoring_interval_seconds: float
    resource_history_retention_hours: int


class ResourceOptimizationTracker:
    """
    Comprehensive resource usage monitoring and optimization tracking system.
    
    Provides real-time resource monitoring, intelligent optimization recommendations,
    and adaptive resource management for Phase 2B ePubs processing workflows.
    """
    
    def __init__(self,
                 monitoring_interval: float = 1.0,
                 history_retention_hours: int = 24,
                 optimization_enabled: bool = True,
                 metrics_persistence_path: Optional[Path] = None):
        """
        Initialize resource optimization tracking system.
        
        Args:
            monitoring_interval: Seconds between resource snapshots
            history_retention_hours: Hours of resource history to retain
            optimization_enabled: Enable automatic optimization recommendations
            metrics_persistence_path: Path for metrics persistence
        """
        self.monitoring_interval = monitoring_interval
        self.history_retention_hours = history_retention_hours
        self.optimization_enabled = optimization_enabled
        self.metrics_persistence_path = metrics_persistence_path or Path.home() / ".epubs" / "resource_metrics"
        
        # Thread-safe resource monitoring
        self._monitoring_lock = threading.RLock()
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_active = False
        
        # Resource history storage
        max_snapshots = int(history_retention_hours * 3600 / monitoring_interval)
        self._resource_history: deque = deque(maxlen=max_snapshots)
        
        # Resource thresholds
        self._resource_thresholds = self._initialize_default_thresholds()
        
        # Optimization tracking
        self._optimization_recommendations: deque = deque(maxlen=1000)
        self._active_optimizations: Dict[str, datetime] = {}
        self._optimization_history: List[OptimizationRecommendation] = []
        
        # Performance baselines
        self._baseline_metrics: Dict[str, float] = {}
        self._performance_trends: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
        
        # Current optimization profile
        self._current_profile = self._create_default_profile()
        
        # System information
        self._system_info = self._gather_system_info()
        
        # Initial resource snapshot for baseline
        self._initial_snapshot: Optional[ResourceSnapshot] = None
        
        # Logger setup
        self.logger = logging.getLogger(f"{__name__}.ResourceOptimizationTracker")
        
        # Ensure metrics directory exists
        self.metrics_persistence_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Resource Optimization Tracker initialized - "
                        f"Interval: {monitoring_interval}s, Retention: {history_retention_hours}h")
    
    def start_monitoring(self) -> None:
        """Start continuous resource monitoring."""
        with self._monitoring_lock:
            if self._monitoring_active:
                self.logger.warning("Resource monitoring already active")
                return
            
            self._monitoring_active = True
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="ResourceOptimizationTracker"
            )
            self._monitoring_thread.start()
            
            # Take initial snapshot for baseline
            self._initial_snapshot = self._capture_resource_snapshot()
            self._establish_baseline_metrics(self._initial_snapshot)
            
            self.logger.info("Started continuous resource monitoring")
    
    def stop_monitoring(self) -> None:
        """Stop continuous resource monitoring."""
        with self._monitoring_lock:
            if not self._monitoring_active:
                return
            
            self._monitoring_active = False
            if self._monitoring_thread:
                self._monitoring_thread.join(timeout=5.0)
            
            self.logger.info("Stopped resource monitoring")
    
    def capture_snapshot(self) -> ResourceSnapshot:
        """Capture a single resource usage snapshot."""
        return self._capture_resource_snapshot()
    
    def get_current_usage(self) -> Optional[ResourceSnapshot]:
        """Get the most recent resource usage snapshot."""
        with self._monitoring_lock:
            return self._resource_history[-1] if self._resource_history else None
    
    def get_usage_history(self, 
                         time_window: Optional[timedelta] = None) -> List[ResourceSnapshot]:
        """
        Get resource usage history for specified time window.
        
        Args:
            time_window: Time window for history (default: all available)
            
        Returns:
            List of resource snapshots in chronological order
        """
        with self._monitoring_lock:
            history = list(self._resource_history)
            
            if time_window:
                cutoff_time = datetime.now() - time_window
                history = [snapshot for snapshot in history if snapshot.timestamp >= cutoff_time]
            
            return sorted(history, key=lambda x: x.timestamp)
    
    def set_optimization_profile(self, profile: ResourceOptimizationProfile) -> None:
        """Set the current resource optimization profile."""
        with self._monitoring_lock:
            self._current_profile = profile
            self._apply_optimization_profile(profile)
            
            self.logger.info(f"Applied optimization profile: {profile.profile_name} "
                           f"({profile.optimization_level.value})")
    
    def get_optimization_recommendations(self,
                                       time_window: Optional[timedelta] = None,
                                       severity_filter: Optional[str] = None) -> List[OptimizationRecommendation]:
        """
        Get resource optimization recommendations.
        
        Args:
            time_window: Time window for recommendations
            severity_filter: Filter by severity ('info', 'warning', 'critical')
            
        Returns:
            List of optimization recommendations
        """
        with self._monitoring_lock:
            recommendations = list(self._optimization_recommendations)
            
            if time_window:
                cutoff_time = datetime.now() - time_window
                recommendations = [rec for rec in recommendations if rec.timestamp >= cutoff_time]
            
            if severity_filter:
                recommendations = [rec for rec in recommendations if rec.severity == severity_filter]
            
            return sorted(recommendations, key=lambda x: x.timestamp, reverse=True)
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive resource optimization report."""
        with self._monitoring_lock:
            current_usage = self.get_current_usage()
            recent_history = self.get_usage_history(timedelta(hours=1))
            recommendations = self.get_optimization_recommendations(timedelta(hours=24))
            
            if not current_usage or not recent_history:
                return {"error": "Insufficient monitoring data"}
            
            # Calculate usage statistics
            avg_cpu = sum(s.cpu_percent for s in recent_history) / len(recent_history)
            avg_memory = sum(s.memory_percent for s in recent_history) / len(recent_history)
            avg_disk_usage = sum(s.disk_usage_percent for s in recent_history) / len(recent_history)
            
            # Performance trends
            cpu_trend = self._calculate_trend([s.cpu_percent for s in recent_history])
            memory_trend = self._calculate_trend([s.memory_percent for s in recent_history])
            
            # Resource efficiency score
            efficiency_score = self._calculate_efficiency_score(current_usage)
            
            # Optimization impact assessment
            potential_improvements = self._assess_optimization_impact(recommendations)
            
            return {
                "report_timestamp": datetime.now().isoformat(),
                "monitoring_duration_hours": len(recent_history) * self.monitoring_interval / 3600,
                "current_usage": {
                    "cpu_percent": current_usage.cpu_percent,
                    "memory_percent": current_usage.memory_percent,
                    "disk_usage_percent": current_usage.disk_usage_percent,
                    "process_memory_mb": current_usage.process_memory_mb
                },
                "average_usage": {
                    "cpu_percent": avg_cpu,
                    "memory_percent": avg_memory,
                    "disk_usage_percent": avg_disk_usage
                },
                "performance_trends": {
                    "cpu_trend": cpu_trend,
                    "memory_trend": memory_trend
                },
                "efficiency_score": efficiency_score,
                "active_profile": {
                    "name": self._current_profile.profile_name,
                    "level": self._current_profile.optimization_level.value,
                    "max_workers": self._current_profile.max_parallel_workers,
                    "memory_limit_gb": self._current_profile.memory_limit_gb
                },
                "recommendations": {
                    "total_count": len(recommendations),
                    "critical_count": len([r for r in recommendations if r.severity == 'critical']),
                    "warning_count": len([r for r in recommendations if r.severity == 'warning']),
                    "top_recommendations": recommendations[:5]
                },
                "optimization_impact": potential_improvements,
                "system_info": self._system_info
            }
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop running in background thread."""
        self.logger.debug("Started resource monitoring loop")
        
        while self._monitoring_active:
            try:
                # Capture resource snapshot
                snapshot = self._capture_resource_snapshot()
                
                with self._monitoring_lock:
                    self._resource_history.append(snapshot)
                
                # Check for optimization opportunities
                if self.optimization_enabled:
                    self._analyze_optimization_opportunities(snapshot)
                
                # Update performance trends
                self._update_performance_trends(snapshot)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(self.monitoring_interval)
        
        self.logger.debug("Stopped resource monitoring loop")
    
    def _capture_resource_snapshot(self) -> ResourceSnapshot:
        """Capture comprehensive resource usage snapshot."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_freq_current = cpu_freq.current if cpu_freq else 0
        cpu_freq_max = cpu_freq.max if cpu_freq else 0
        
        # Load average (Unix-like systems only)
        try:
            load_avg = os.getloadavg()
        except (OSError, AttributeError):
            load_avg = (0.0, 0.0, 0.0)  # Windows fallback
        
        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk I/O metrics
        disk_io = psutil.disk_io_counters()
        disk_usage = psutil.disk_usage('/')
        
        # Network metrics
        network = psutil.net_io_counters()
        
        # Process-specific metrics
        current_process = psutil.Process()
        process_cpu = current_process.cpu_percent()
        process_memory = current_process.memory_info()
        
        # File descriptors/handles
        try:
            process_fds = current_process.num_fds() if hasattr(current_process, 'num_fds') else len(current_process.open_files())
        except (psutil.AccessDenied, AttributeError):
            process_fds = 0
        
        # Boot time
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        return ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            cpu_count=cpu_count,
            cpu_freq_current=cpu_freq_current,
            cpu_freq_max=cpu_freq_max,
            load_average=load_avg,
            memory_total_gb=memory.total / (1024**3),
            memory_available_gb=memory.available / (1024**3),
            memory_used_gb=memory.used / (1024**3),
            memory_percent=memory.percent,
            swap_total_gb=swap.total / (1024**3),
            swap_used_gb=swap.used / (1024**3),
            swap_percent=swap.percent,
            disk_read_bytes=disk_io.read_bytes if disk_io else 0,
            disk_write_bytes=disk_io.write_bytes if disk_io else 0,
            disk_read_count=disk_io.read_count if disk_io else 0,
            disk_write_count=disk_io.write_count if disk_io else 0,
            disk_read_time=disk_io.read_time if disk_io else 0,
            disk_write_time=disk_io.write_time if disk_io else 0,
            disk_usage_percent=disk_usage.percent,
            network_bytes_sent=network.bytes_sent if network else 0,
            network_bytes_recv=network.bytes_recv if network else 0,
            network_packets_sent=network.packets_sent if network else 0,
            network_packets_recv=network.packets_recv if network else 0,
            network_errors_in=network.errin if network else 0,
            network_errors_out=network.errout if network else 0,
            process_cpu_percent=process_cpu,
            process_memory_mb=process_memory.rss / (1024**2),
            process_memory_percent=current_process.memory_percent(),
            process_num_threads=current_process.num_threads(),
            process_num_fds=process_fds,
            system_uptime=(datetime.now() - boot_time).total_seconds(),
            boot_time=boot_time
        )
    
    def _initialize_default_thresholds(self) -> Dict[ResourceType, ResourceThreshold]:
        """Initialize default resource usage thresholds."""
        return {
            ResourceType.CPU: ResourceThreshold(
                resource_type=ResourceType.CPU,
                warning_threshold=70.0,
                critical_threshold=90.0,
                optimization_threshold=80.0,
                measurement_unit="percent",
                description="CPU usage percentage"
            ),
            ResourceType.MEMORY: ResourceThreshold(
                resource_type=ResourceType.MEMORY,
                warning_threshold=75.0,
                critical_threshold=90.0,
                optimization_threshold=85.0,
                measurement_unit="percent",
                description="Memory usage percentage"
            ),
            ResourceType.DISK_IO: ResourceThreshold(
                resource_type=ResourceType.DISK_IO,
                warning_threshold=80.0,
                critical_threshold=95.0,
                optimization_threshold=90.0,
                measurement_unit="percent",
                description="Disk usage percentage"
            )
        }
    
    def _create_default_profile(self) -> ResourceOptimizationProfile:
        """Create default resource optimization profile."""
        return ResourceOptimizationProfile(
            profile_name="Balanced Default",
            optimization_level=OptimizationLevel.BALANCED,
            max_parallel_workers=2,  # Updated based on recent optimization
            memory_limit_gb=8.0,
            cpu_limit_percent=80.0,
            cache_memory_limit_mb=512,
            cache_disk_limit_gb=2.0,
            faiss_memory_limit_mb=1024,
            faiss_index_type_preference="IVF",
            ml_batch_size=32,
            ml_memory_limit_mb=512,
            monitoring_interval_seconds=1.0,
            resource_history_retention_hours=24
        )
    
    def _gather_system_info(self) -> Dict[str, Any]:
        """Gather comprehensive system information."""
        return {
            "platform": platform.platform(),
            "system": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0]
        }
    
    def _establish_baseline_metrics(self, snapshot: ResourceSnapshot) -> None:
        """Establish baseline performance metrics."""
        self._baseline_metrics = {
            "cpu_percent": snapshot.cpu_percent,
            "memory_percent": snapshot.memory_percent,
            "disk_usage_percent": snapshot.disk_usage_percent,
            "process_memory_mb": snapshot.process_memory_mb
        }
        
        self.logger.info(f"Established baseline metrics: CPU {snapshot.cpu_percent:.1f}%, "
                        f"Memory {snapshot.memory_percent:.1f}%, "
                        f"Process Memory {snapshot.process_memory_mb:.1f}MB")
    
    def _analyze_optimization_opportunities(self, snapshot: ResourceSnapshot) -> None:
        """Analyze current snapshot for optimization opportunities."""
        recommendations = []
        
        # CPU optimization analysis
        if snapshot.cpu_percent > self._resource_thresholds[ResourceType.CPU].critical_threshold:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"cpu_critical_{int(time.time())}",
                timestamp=snapshot.timestamp,
                resource_type=ResourceType.CPU,
                severity="critical",
                current_usage=snapshot.cpu_percent,
                recommended_action="Reduce parallel workers or enable CPU throttling",
                expected_improvement=20.0,
                implementation_complexity="low",
                estimated_impact="Immediate CPU usage reduction",
                related_components=["batch_processor", "parallel_workers"]
            ))
        
        # Memory optimization analysis
        if snapshot.memory_percent > self._resource_thresholds[ResourceType.MEMORY].warning_threshold:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"memory_warning_{int(time.time())}",
                timestamp=snapshot.timestamp,
                resource_type=ResourceType.MEMORY,
                severity="warning",
                current_usage=snapshot.memory_percent,
                recommended_action="Enable memory cache compression or reduce cache size",
                expected_improvement=15.0,
                implementation_complexity="medium",
                estimated_impact="Reduced memory pressure",
                related_components=["hierarchical_cache", "faiss_index"]
            ))
        
        # Process memory analysis
        if snapshot.process_memory_mb > 2048:  # 2GB threshold
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"process_memory_{int(time.time())}",
                timestamp=snapshot.timestamp,
                resource_type=ResourceType.PROCESS,
                severity="info",
                current_usage=snapshot.process_memory_mb,
                recommended_action="Consider batch size reduction or memory cleanup",
                expected_improvement=30.0,
                implementation_complexity="low",
                estimated_impact="Reduced process memory footprint",
                related_components=["ml_enhancer", "document_processor"]
            ))
        
        # Store recommendations
        with self._monitoring_lock:
            for rec in recommendations:
                self._optimization_recommendations.append(rec)
    
    def _update_performance_trends(self, snapshot: ResourceSnapshot) -> None:
        """Update performance trend tracking."""
        timestamp = snapshot.timestamp
        
        # Update trends for key metrics
        trends = {
            "cpu_percent": snapshot.cpu_percent,
            "memory_percent": snapshot.memory_percent,
            "process_memory_mb": snapshot.process_memory_mb,
            "disk_usage_percent": snapshot.disk_usage_percent
        }
        
        for metric, value in trends.items():
            self._performance_trends[metric].append((timestamp, value))
            
            # Keep only last 24 hours of trend data
            cutoff_time = timestamp - timedelta(hours=24)
            self._performance_trends[metric] = [
                (ts, val) for ts, val in self._performance_trends[metric] if ts >= cutoff_time
            ]
    
    def _apply_optimization_profile(self, profile: ResourceOptimizationProfile) -> None:
        """Apply resource optimization profile settings."""
        # This would integrate with actual system components
        # For now, we log the profile application
        self.logger.info(f"Applied optimization profile: {profile.profile_name}")
        self.logger.info(f"  - Max parallel workers: {profile.max_parallel_workers}")
        self.logger.info(f"  - Memory limit: {profile.memory_limit_gb}GB")
        self.logger.info(f"  - CPU limit: {profile.cpu_limit_percent}%")
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values."""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        first_half_avg = sum(values[:len(values)//2]) / (len(values)//2)
        second_half_avg = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        change_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_efficiency_score(self, snapshot: ResourceSnapshot) -> float:
        """Calculate overall resource efficiency score (0-100)."""
        # CPU efficiency (lower usage is more efficient for background processing)
        cpu_efficiency = max(0, 100 - snapshot.cpu_percent)
        
        # Memory efficiency
        memory_efficiency = max(0, 100 - snapshot.memory_percent)
        
        # Process efficiency (relative to baseline)
        baseline_memory = self._baseline_metrics.get("process_memory_mb", snapshot.process_memory_mb)
        memory_growth = (snapshot.process_memory_mb / baseline_memory - 1) * 100 if baseline_memory > 0 else 0
        process_efficiency = max(0, 100 - memory_growth)
        
        # Weighted efficiency score
        efficiency_score = (
            cpu_efficiency * 0.4 +
            memory_efficiency * 0.4 +
            process_efficiency * 0.2
        )
        
        return min(100, max(0, efficiency_score))
    
    def _assess_optimization_impact(self, recommendations: List[OptimizationRecommendation]) -> Dict[str, Any]:
        """Assess potential impact of optimization recommendations."""
        if not recommendations:
            return {"total_recommendations": 0, "potential_improvement": 0}
        
        total_cpu_improvement = sum(
            rec.expected_improvement for rec in recommendations 
            if rec.resource_type == ResourceType.CPU
        )
        
        total_memory_improvement = sum(
            rec.expected_improvement for rec in recommendations 
            if rec.resource_type == ResourceType.MEMORY
        )
        
        critical_issues = len([rec for rec in recommendations if rec.severity == "critical"])
        
        return {
            "total_recommendations": len(recommendations),
            "critical_issues": critical_issues,
            "potential_cpu_improvement_percent": min(50, total_cpu_improvement),
            "potential_memory_improvement_percent": min(50, total_memory_improvement),
            "implementation_complexity": self._assess_implementation_complexity(recommendations)
        }
    
    def _assess_implementation_complexity(self, recommendations: List[OptimizationRecommendation]) -> str:
        """Assess overall implementation complexity of recommendations."""
        complexity_scores = {"low": 1, "medium": 2, "high": 3}
        
        if not recommendations:
            return "none"
        
        avg_complexity = sum(
            complexity_scores.get(rec.implementation_complexity, 2) 
            for rec in recommendations
        ) / len(recommendations)
        
        if avg_complexity <= 1.5:
            return "low"
        elif avg_complexity <= 2.5:
            return "medium"
        else:
            return "high"
    
    def persist_metrics(self, format_type: str = "json") -> Path:
        """Persist resource optimization metrics to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resource_optimization_metrics_{timestamp}.{format_type}"
        output_path = self.metrics_persistence_path / filename
        
        optimization_report = self.generate_optimization_report()
        
        with self._monitoring_lock:
            if format_type == "json":
                metrics_data = {
                    "collection_metadata": {
                        "collection_time": datetime.now().isoformat(),
                        "monitoring_active": self._monitoring_active,
                        "total_snapshots": len(self._resource_history),
                        "monitoring_interval": self.monitoring_interval
                    },
                    "optimization_report": optimization_report,
                    "current_profile": asdict(self._current_profile),
                    "resource_thresholds": {
                        rt.name: asdict(threshold) 
                        for rt, threshold in self._resource_thresholds.items()
                    }
                }
                
                with open(output_path, 'w') as f:
                    json.dump(metrics_data, f, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        self.logger.info(f"Persisted resource optimization metrics to {output_path}")
        return output_path


# Global resource optimization tracker
_global_resource_tracker: Optional[ResourceOptimizationTracker] = None


def get_resource_tracker() -> ResourceOptimizationTracker:
    """Get global resource optimization tracker."""
    global _global_resource_tracker
    if _global_resource_tracker is None:
        _global_resource_tracker = ResourceOptimizationTracker()
    return _global_resource_tracker


def initialize_resource_tracking(monitoring_interval: float = 1.0,
                                optimization_enabled: bool = True,
                                persistence_path: Optional[Path] = None) -> ResourceOptimizationTracker:
    """Initialize global resource optimization tracking."""
    global _global_resource_tracker
    _global_resource_tracker = ResourceOptimizationTracker(
        monitoring_interval=monitoring_interval,
        optimization_enabled=optimization_enabled,
        metrics_persistence_path=persistence_path
    )
    return _global_resource_tracker
