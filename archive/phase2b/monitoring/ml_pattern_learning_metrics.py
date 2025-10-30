"""
ML Pattern Learning Effectiveness Measurement Framework
====================================================

Comprehensive metrics collection system for Phase 2B machine learning optimization components.
Tracks effectiveness of document pattern learning, OCR configuration optimization,
and adaptive enhancement strategies for institutional deployment analytics.

This module provides systematic measurement of:
- Document similarity analysis accuracy and performance
- OCR configuration optimization success rates
- Pattern learning convergence and effectiveness
- Knowledge base growth and utilization metrics
- Cross-session learning persistence and improvement
"""

import time
import threading
import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import logging
import hashlib


class MLOperationType(Enum):
    """Types of ML operations for metrics tracking."""
    SIMILARITY_ANALYSIS = "similarity_analysis"
    OCR_OPTIMIZATION = "ocr_optimization"
    PATTERN_LEARNING = "pattern_learning"
    KNOWLEDGE_UPDATE = "knowledge_update"
    PREDICTION = "prediction"
    FEATURE_EXTRACTION = "feature_extraction"


class LearningEffectiveness(Enum):
    """Learning effectiveness levels."""
    EXCELLENT = "excellent"  # >90% accuracy/improvement
    GOOD = "good"           # 70-90% accuracy/improvement
    MODERATE = "moderate"   # 50-70% accuracy/improvement
    POOR = "poor"          # <50% accuracy/improvement
    UNKNOWN = "unknown"     # Insufficient data


@dataclass
class MLOperationMetric:
    """Individual ML operation performance metric."""
    operation_type: MLOperationType
    operation_id: str
    timestamp: datetime
    duration_ms: float
    
    # Input characteristics
    document_count: int
    feature_dimensions: int
    similarity_threshold: float
    
    # Performance metrics
    accuracy_score: Optional[float] = None  # 0.0-1.0
    confidence_score: Optional[float] = None  # 0.0-1.0
    improvement_ratio: Optional[float] = None  # Before/after comparison
    
    # Resource usage
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # Learning outcomes
    patterns_learned: int = 0
    knowledge_base_size: int = 0
    convergence_achieved: bool = False
    
    # Quality metrics
    false_positive_rate: Optional[float] = None
    false_negative_rate: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    
    # Metadata
    document_types: List[str] = None
    ocr_settings_optimized: Dict[str, Any] = None
    error_message: Optional[str] = None
    success: bool = True


@dataclass
class PatternLearningProgress:
    """Progress tracking for pattern learning over time."""
    learning_session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    
    # Learning progression
    initial_accuracy: float
    current_accuracy: float
    target_accuracy: float
    improvement_rate: float  # accuracy improvement per iteration
    
    # Data processed
    documents_processed: int
    unique_patterns_identified: int
    pattern_confidence_distribution: Dict[str, int]
    
    # Convergence metrics
    iterations_completed: int
    convergence_threshold: float
    stability_window: int  # iterations
    converged: bool
    
    # Performance trends
    accuracy_trend: List[Tuple[datetime, float]]
    processing_speed_trend: List[Tuple[datetime, float]]
    
    # Knowledge base impact
    knowledge_base_growth: int  # new entries added
    existing_entries_updated: int


@dataclass
class MLSystemMetrics:
    """Comprehensive ML system performance summary."""
    collection_timestamp: datetime
    collection_period: str
    
    # Overall performance
    total_ml_operations: int
    successful_operations: int
    average_operation_time_ms: float
    overall_accuracy_score: float
    overall_confidence_score: float
    
    # Learning effectiveness
    pattern_learning_effectiveness: LearningEffectiveness
    ocr_optimization_success_rate: float
    similarity_analysis_accuracy: float
    knowledge_base_utilization: float
    
    # Resource efficiency
    average_memory_usage_mb: float
    average_cpu_usage_percent: float
    resource_efficiency_score: float
    
    # Quality metrics
    precision_score: float
    recall_score: float
    f1_score: float
    
    # Progress tracking
    active_learning_sessions: int
    completed_learning_sessions: int
    knowledge_base_size: int
    cross_session_improvements: Dict[str, float]
    
    # Optimization insights
    most_effective_patterns: List[str]
    optimal_ocr_configurations: Dict[str, Any]
    performance_bottlenecks: List[str]
    improvement_recommendations: List[str]


class MLPatternLearningMetricsCollector:
    """
    Comprehensive metrics collection for ML pattern learning effectiveness.
    
    Tracks machine learning optimization performance across document processing,
    OCR configuration learning, and adaptive enhancement strategies with
    detailed analytics for institutional deployment confidence.
    """
    
    def __init__(self,
                 max_metrics_history: int = 25000,
                 metrics_persistence_path: Optional[Path] = None,
                 collection_enabled: bool = True,
                 detailed_analytics: bool = True):
        """
        Initialize ML pattern learning metrics collection.
        
        Args:
            max_metrics_history: Maximum metrics to retain in memory
            metrics_persistence_path: Path for metrics persistence
            collection_enabled: Enable/disable metrics collection
            detailed_analytics: Enable detailed learning analytics
        """
        self.max_metrics_history = max_metrics_history
        self.collection_enabled = collection_enabled
        self.detailed_analytics = detailed_analytics
        self.metrics_persistence_path = metrics_persistence_path or Path.home() / ".epubs" / "ml_metrics"
        
        # Thread-safe metrics storage
        self._metrics_lock = threading.RLock()
        
        # Operation metrics by type
        self._ml_operations: deque = deque(maxlen=max_metrics_history)
        self._operation_by_type = {
            op_type: deque(maxlen=max_metrics_history // 5) 
            for op_type in MLOperationType
        }
        
        # Learning session tracking
        self._active_learning_sessions: Dict[str, PatternLearningProgress] = {}
        self._completed_sessions: deque = deque(maxlen=1000)
        
        # Performance analytics
        self._accuracy_trends = defaultdict(list)
        self._performance_baselines = {}
        self._optimization_history = []
        
        # Knowledge base tracking
        self._knowledge_base_metrics = {
            'total_patterns': 0,
            'active_patterns': 0,
            'pattern_quality_scores': [],
            'last_update': datetime.now()
        }
        
        # Cross-session improvement tracking
        self._cross_session_improvements = defaultdict(list)
        
        # Logger setup
        self.logger = logging.getLogger(f"{__name__}.MLPatternLearningMetricsCollector")
        
        # Ensure metrics directory exists
        self.metrics_persistence_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"ML Pattern Learning Metrics Collector initialized - "
                        f"History: {max_metrics_history}, Analytics: {detailed_analytics}")
    
    def start_learning_session(self,
                              session_id: str,
                              target_accuracy: float = 0.85,
                              convergence_threshold: float = 0.01,
                              initial_accuracy: float = 0.0) -> str:
        """
        Start tracking a new pattern learning session.
        
        Args:
            session_id: Unique identifier for the learning session
            target_accuracy: Target accuracy for convergence
            convergence_threshold: Threshold for convergence detection
            initial_accuracy: Starting accuracy baseline
            
        Returns:
            Session ID for tracking
        """
        if not self.collection_enabled:
            return session_id
            
        with self._metrics_lock:
            progress = PatternLearningProgress(
                learning_session_id=session_id,
                start_time=datetime.now(),
                end_time=None,
                initial_accuracy=initial_accuracy,
                current_accuracy=initial_accuracy,
                target_accuracy=target_accuracy,
                improvement_rate=0.0,
                documents_processed=0,
                unique_patterns_identified=0,
                pattern_confidence_distribution={},
                iterations_completed=0,
                convergence_threshold=convergence_threshold,
                stability_window=5,
                converged=False,
                accuracy_trend=[(datetime.now(), initial_accuracy)],
                processing_speed_trend=[],
                knowledge_base_growth=0,
                existing_entries_updated=0
            )
            
            self._active_learning_sessions[session_id] = progress
            
            self.logger.info(f"Started ML learning session: {session_id} - "
                           f"Target: {target_accuracy}, Initial: {initial_accuracy}")
            
            return session_id
    
    def update_learning_progress(self,
                               session_id: str,
                               current_accuracy: float,
                               documents_processed: int = 0,
                               patterns_identified: int = 0,
                               processing_speed_ms: float = 0.0,
                               knowledge_base_updates: int = 0) -> bool:
        """
        Update progress for an active learning session.
        
        Args:
            session_id: Learning session identifier
            current_accuracy: Current accuracy level
            documents_processed: Number of documents processed
            patterns_identified: Number of new patterns identified
            processing_speed_ms: Processing speed in milliseconds
            knowledge_base_updates: Number of knowledge base updates
            
        Returns:
            True if convergence achieved, False otherwise
        """
        if not self.collection_enabled or session_id not in self._active_learning_sessions:
            return False
            
        with self._metrics_lock:
            progress = self._active_learning_sessions[session_id]
            
            # Update progress metrics
            previous_accuracy = progress.current_accuracy
            progress.current_accuracy = current_accuracy
            progress.documents_processed += documents_processed
            progress.unique_patterns_identified += patterns_identified
            progress.iterations_completed += 1
            
            # Calculate improvement rate
            if previous_accuracy > 0:
                progress.improvement_rate = (current_accuracy - previous_accuracy) / previous_accuracy
            
            # Update trends
            progress.accuracy_trend.append((datetime.now(), current_accuracy))
            if processing_speed_ms > 0:
                progress.processing_speed_trend.append((datetime.now(), processing_speed_ms))
            
            # Update knowledge base metrics
            progress.knowledge_base_growth += knowledge_base_updates
            
            # Check convergence
            if len(progress.accuracy_trend) >= progress.stability_window:
                recent_accuracies = [acc for _, acc in progress.accuracy_trend[-progress.stability_window:]]
                accuracy_variance = max(recent_accuracies) - min(recent_accuracies)
                
                if (accuracy_variance <= progress.convergence_threshold and
                    current_accuracy >= progress.target_accuracy):
                    progress.converged = True
                    self.complete_learning_session(session_id)
                    return True
            
            self.logger.debug(f"Updated learning session {session_id}: "
                            f"Accuracy: {current_accuracy:.3f}, "
                            f"Iteration: {progress.iterations_completed}")
            
            return False
    
    def complete_learning_session(self, session_id: str) -> Optional[PatternLearningProgress]:
        """
        Complete a learning session and move to completed sessions.
        
        Args:
            session_id: Learning session identifier
            
        Returns:
            Completed learning progress or None if session not found
        """
        if not self.collection_enabled or session_id not in self._active_learning_sessions:
            return None
            
        with self._metrics_lock:
            progress = self._active_learning_sessions.pop(session_id)
            progress.end_time = datetime.now()
            
            # Calculate final improvement rate
            if progress.initial_accuracy > 0:
                total_improvement = (progress.current_accuracy - progress.initial_accuracy) / progress.initial_accuracy
                progress.improvement_rate = total_improvement
            
            self._completed_sessions.append(progress)
            
            # Update cross-session improvement tracking
            improvement_key = f"accuracy_improvement"
            self._cross_session_improvements[improvement_key].append(progress.improvement_rate)
            
            self.logger.info(f"Completed learning session {session_id}: "
                           f"Final accuracy: {progress.current_accuracy:.3f}, "
                           f"Improvement: {progress.improvement_rate:.3f}, "
                           f"Converged: {progress.converged}")
            
            return progress
    
    def record_ml_operation(self,
                           operation_type: MLOperationType,
                           duration_ms: float,
                           document_count: int = 0,
                           feature_dimensions: int = 0,
                           similarity_threshold: float = 0.0,
                           accuracy_score: Optional[float] = None,
                           confidence_score: Optional[float] = None,
                           patterns_learned: int = 0,
                           ocr_settings: Optional[Dict[str, Any]] = None,
                           success: bool = True,
                           error_message: Optional[str] = None) -> str:
        """
        Record an ML operation for metrics tracking.
        
        Args:
            operation_type: Type of ML operation
            duration_ms: Operation duration in milliseconds
            document_count: Number of documents processed
            feature_dimensions: Feature vector dimensions
            similarity_threshold: Similarity threshold used
            accuracy_score: Operation accuracy (0.0-1.0)
            confidence_score: Operation confidence (0.0-1.0)
            patterns_learned: Number of patterns learned
            ocr_settings: OCR settings used/optimized
            success: Whether operation succeeded
            error_message: Error message if failed
            
        Returns:
            Operation ID for tracking
        """
        if not self.collection_enabled:
            return ""
            
        with self._metrics_lock:
            # Generate operation ID
            operation_id = f"{operation_type.value}_{int(time.time() * 1000000)}"
            
            # Get current resource usage
            import psutil
            current_process = psutil.Process()
            memory_usage_mb = current_process.memory_info().rss / 1024 / 1024
            cpu_usage_percent = current_process.cpu_percent()
            
            # Create metric record
            metric = MLOperationMetric(
                operation_type=operation_type,
                operation_id=operation_id,
                timestamp=datetime.now(),
                duration_ms=duration_ms,
                document_count=document_count,
                feature_dimensions=feature_dimensions,
                similarity_threshold=similarity_threshold,
                accuracy_score=accuracy_score,
                confidence_score=confidence_score,
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage_percent,
                patterns_learned=patterns_learned,
                knowledge_base_size=self._knowledge_base_metrics['total_patterns'],
                ocr_settings_optimized=ocr_settings,
                success=success,
                error_message=error_message
            )
            
            # Store metric
            self._ml_operations.append(metric)
            self._operation_by_type[operation_type].append(metric)
            
            # Update knowledge base metrics
            if patterns_learned > 0:
                self._knowledge_base_metrics['total_patterns'] += patterns_learned
                self._knowledge_base_metrics['last_update'] = datetime.now()
            
            # Track accuracy trends
            if accuracy_score is not None:
                self._accuracy_trends[operation_type.value].append(
                    (datetime.now(), accuracy_score)
                )
            
            self.logger.debug(f"Recorded ML operation: {operation_type.value} - "
                            f"Duration: {duration_ms:.2f}ms, Success: {success}")
            
            return operation_id
    
    def get_ml_system_metrics(self,
                            time_window: Optional[timedelta] = None) -> MLSystemMetrics:
        """
        Generate comprehensive ML system performance metrics.
        
        Args:
            time_window: Time window for analysis (default: all available)
            
        Returns:
            Complete ML system metrics summary
        """
        with self._metrics_lock:
            # Filter operations by time window
            operations = list(self._ml_operations)
            if time_window:
                cutoff_time = datetime.now() - time_window
                operations = [op for op in operations if op.timestamp >= cutoff_time]
            
            if not operations:
                return self._empty_ml_metrics()
            
            # Calculate basic metrics
            total_ops = len(operations)
            successful_ops = len([op for op in operations if op.success])
            avg_duration = sum(op.duration_ms for op in operations) / total_ops
            
            # Calculate accuracy metrics
            accuracy_scores = [op.accuracy_score for op in operations if op.accuracy_score is not None]
            overall_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
            
            confidence_scores = [op.confidence_score for op in operations if op.confidence_score is not None]
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            # Resource usage metrics
            avg_memory = sum(op.memory_usage_mb for op in operations) / total_ops
            avg_cpu = sum(op.cpu_usage_percent for op in operations) / total_ops
            
            # Learning effectiveness assessment
            learning_effectiveness = self._assess_learning_effectiveness(operations)
            
            # OCR optimization success rate
            ocr_ops = [op for op in operations if op.operation_type == MLOperationType.OCR_OPTIMIZATION]
            ocr_success_rate = (len([op for op in ocr_ops if op.success]) / len(ocr_ops) * 100) if ocr_ops else 0
            
            # Quality metrics calculation
            precision, recall, f1 = self._calculate_quality_metrics(operations)
            
            # Cross-session improvements
            cross_session_improvements = {}
            for key, improvements in self._cross_session_improvements.items():
                if improvements:
                    cross_session_improvements[key] = sum(improvements) / len(improvements)
            
            # Generate recommendations
            recommendations = self._generate_ml_recommendations(operations)
            
            return MLSystemMetrics(
                collection_timestamp=datetime.now(),
                collection_period=f"Last {total_ops} operations",
                total_ml_operations=total_ops,
                successful_operations=successful_ops,
                average_operation_time_ms=avg_duration,
                overall_accuracy_score=overall_accuracy,
                overall_confidence_score=overall_confidence,
                pattern_learning_effectiveness=learning_effectiveness,
                ocr_optimization_success_rate=ocr_success_rate,
                similarity_analysis_accuracy=self._calculate_similarity_accuracy(operations),
                knowledge_base_utilization=self._calculate_kb_utilization(),
                average_memory_usage_mb=avg_memory,
                average_cpu_usage_percent=avg_cpu,
                resource_efficiency_score=self._calculate_resource_efficiency(avg_memory, avg_cpu),
                precision_score=precision,
                recall_score=recall,
                f1_score=f1,
                active_learning_sessions=len(self._active_learning_sessions),
                completed_learning_sessions=len(self._completed_sessions),
                knowledge_base_size=self._knowledge_base_metrics['total_patterns'],
                cross_session_improvements=cross_session_improvements,
                most_effective_patterns=self._get_effective_patterns(),
                optimal_ocr_configurations=self._get_optimal_ocr_configs(operations),
                performance_bottlenecks=self._identify_bottlenecks(operations),
                improvement_recommendations=recommendations
            )
    
    def _empty_ml_metrics(self) -> MLSystemMetrics:
        """Generate empty ML metrics for cases with no data."""
        return MLSystemMetrics(
            collection_timestamp=datetime.now(),
            collection_period="No ML operations recorded",
            total_ml_operations=0,
            successful_operations=0,
            average_operation_time_ms=0.0,
            overall_accuracy_score=0.0,
            overall_confidence_score=0.0,
            pattern_learning_effectiveness=LearningEffectiveness.UNKNOWN,
            ocr_optimization_success_rate=0.0,
            similarity_analysis_accuracy=0.0,
            knowledge_base_utilization=0.0,
            average_memory_usage_mb=0.0,
            average_cpu_usage_percent=0.0,
            resource_efficiency_score=0.0,
            precision_score=0.0,
            recall_score=0.0,
            f1_score=0.0,
            active_learning_sessions=0,
            completed_learning_sessions=0,
            knowledge_base_size=0,
            cross_session_improvements={},
            most_effective_patterns=[],
            optimal_ocr_configurations={},
            performance_bottlenecks=[],
            improvement_recommendations=["No ML operations recorded - enable ML processing to see insights"]
        )
    
    def _assess_learning_effectiveness(self, operations: List[MLOperationMetric]) -> LearningEffectiveness:
        """Assess overall learning effectiveness based on operations."""
        learning_ops = [op for op in operations if op.operation_type == MLOperationType.PATTERN_LEARNING]
        
        if not learning_ops:
            return LearningEffectiveness.UNKNOWN
            
        avg_accuracy = sum(op.accuracy_score for op in learning_ops if op.accuracy_score) / len(learning_ops)
        
        if avg_accuracy >= 0.9:
            return LearningEffectiveness.EXCELLENT
        elif avg_accuracy >= 0.7:
            return LearningEffectiveness.GOOD
        elif avg_accuracy >= 0.5:
            return LearningEffectiveness.MODERATE
        else:
            return LearningEffectiveness.POOR
    
    def _calculate_quality_metrics(self, operations: List[MLOperationMetric]) -> Tuple[float, float, float]:
        """Calculate precision, recall, and F1 score from operations."""
        precision_scores = [op.precision for op in operations if op.precision is not None]
        recall_scores = [op.recall for op in operations if op.recall is not None]
        f1_scores = [op.f1_score for op in operations if op.f1_score is not None]
        
        precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0.0
        recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0.0
        f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0
        
        return precision, recall, f1
    
    def _calculate_similarity_accuracy(self, operations: List[MLOperationMetric]) -> float:
        """Calculate similarity analysis accuracy."""
        similarity_ops = [op for op in operations if op.operation_type == MLOperationType.SIMILARITY_ANALYSIS]
        if not similarity_ops:
            return 0.0
            
        accuracy_scores = [op.accuracy_score for op in similarity_ops if op.accuracy_score is not None]
        return sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
    
    def _calculate_kb_utilization(self) -> float:
        """Calculate knowledge base utilization score."""
        total_patterns = self._knowledge_base_metrics['total_patterns']
        if total_patterns == 0:
            return 0.0
            
        # Simplified utilization calculation
        # In a real implementation, this would track pattern usage frequency
        return min(100.0, total_patterns / 1000 * 100)
    
    def _calculate_resource_efficiency(self, avg_memory: float, avg_cpu: float) -> float:
        """Calculate resource efficiency score (0-100)."""
        # Memory efficiency (assume 1GB is reasonable)
        memory_efficiency = max(0, 100 - (avg_memory / 1024 * 100))
        
        # CPU efficiency (lower usage is better for efficiency)
        cpu_efficiency = max(0, 100 - avg_cpu)
        
        return (memory_efficiency + cpu_efficiency) / 2
    
    def _get_effective_patterns(self) -> List[str]:
        """Get most effective pattern types."""
        # Simplified implementation - would track pattern effectiveness in real system
        return ["academic_layout", "citation_format", "table_structure"]
    
    def _get_optimal_ocr_configs(self, operations: List[MLOperationMetric]) -> Dict[str, Any]:
        """Get optimal OCR configurations from successful operations."""
        ocr_ops = [op for op in operations 
                  if op.operation_type == MLOperationType.OCR_OPTIMIZATION 
                  and op.success and op.ocr_settings_optimized]
        
        if not ocr_ops:
            return {}
            
        # Aggregate successful OCR settings
        optimal_configs = {}
        for op in ocr_ops[-10:]:  # Use last 10 successful optimizations
            if op.ocr_settings_optimized:
                optimal_configs.update(op.ocr_settings_optimized)
                
        return optimal_configs
    
    def _identify_bottlenecks(self, operations: List[MLOperationMetric]) -> List[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        # Analyze operation durations by type
        for op_type in MLOperationType:
            type_ops = [op for op in operations if op.operation_type == op_type]
            if type_ops:
                avg_duration = sum(op.duration_ms for op in type_ops) / len(type_ops)
                if avg_duration > 5000:  # 5 second threshold
                    bottlenecks.append(f"{op_type.value} operations are slow (avg: {avg_duration:.0f}ms)")
        
        # Check memory usage
        high_memory_ops = [op for op in operations if op.memory_usage_mb > 1000]
        if len(high_memory_ops) > len(operations) * 0.2:
            bottlenecks.append("High memory usage detected in >20% of operations")
            
        return bottlenecks
    
    def _generate_ml_recommendations(self, operations: List[MLOperationMetric]) -> List[str]:
        """Generate ML optimization recommendations."""
        recommendations = []
        
        # Learning session recommendations
        if len(self._completed_sessions) > 0:
            avg_convergence_time = sum(
                (session.end_time - session.start_time).total_seconds() 
                for session in self._completed_sessions if session.end_time
            ) / len(self._completed_sessions)
            
            if avg_convergence_time > 3600:  # 1 hour
                recommendations.append("Learning sessions taking too long - consider adjusting convergence thresholds")
        
        # Accuracy recommendations
        accuracy_ops = [op for op in operations if op.accuracy_score is not None]
        if accuracy_ops:
            avg_accuracy = sum(op.accuracy_score for op in accuracy_ops) / len(accuracy_ops)
            if avg_accuracy < 0.7:
                recommendations.append("ML accuracy below 70% - review feature extraction and model parameters")
        
        # Resource optimization
        high_memory_ops = [op for op in operations if op.memory_usage_mb > 1000]
        if len(high_memory_ops) > 5:
            recommendations.append("Consider memory optimization for large ML operations")
        
        return recommendations if recommendations else ["ML system performance appears optimal"]
    
    def persist_metrics(self, format_type: str = "json") -> Path:
        """Persist ML pattern learning metrics to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ml_pattern_learning_metrics_{timestamp}.{format_type}"
        output_path = self.metrics_persistence_path / filename
        
        summary = self.get_ml_system_metrics()
        
        with self._metrics_lock:
            if format_type == "json":
                metrics_data = {
                    "collection_metadata": {
                        "collection_time": datetime.now().isoformat(),
                        "total_ml_operations": len(self._ml_operations),
                        "active_learning_sessions": len(self._active_learning_sessions),
                        "completed_learning_sessions": len(self._completed_sessions),
                        "knowledge_base_size": self._knowledge_base_metrics['total_patterns']
                    },
                    "ml_system_summary": asdict(summary),
                    "learning_sessions": [asdict(session) for session in self._completed_sessions]
                }
                
                with open(output_path, 'w') as f:
                    json.dump(metrics_data, f, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        self.logger.info(f"Persisted ML pattern learning metrics to {output_path}")
        return output_path


# Global ML pattern learning metrics collector
_global_ml_metrics_collector: Optional[MLPatternLearningMetricsCollector] = None


def get_ml_metrics_collector() -> MLPatternLearningMetricsCollector:
    """Get global ML pattern learning metrics collector."""
    global _global_ml_metrics_collector
    if _global_ml_metrics_collector is None:
        _global_ml_metrics_collector = MLPatternLearningMetricsCollector()
    return _global_ml_metrics_collector


def initialize_ml_metrics(enabled: bool = True,
                         detailed_analytics: bool = True,
                         persistence_path: Optional[Path] = None) -> MLPatternLearningMetricsCollector:
    """Initialize global ML pattern learning metrics collection."""
    global _global_ml_metrics_collector
    _global_ml_metrics_collector = MLPatternLearningMetricsCollector(
        collection_enabled=enabled,
        detailed_analytics=detailed_analytics,
        metrics_persistence_path=persistence_path
    )
    return _global_ml_metrics_collector
