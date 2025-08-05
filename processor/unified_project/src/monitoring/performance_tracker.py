#!/usr/bin/env python3
"""
Performance Tracking Module for ePubs Accessibility Enhancement

This module provides local SQLite-based performance tracking and metrics collection
for monitoring document processing performance, system utilization, and optimization effectiveness.
"""

import json
import logging
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import platform
import hashlib

# Optional dependencies with graceful fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Local performance tracking using SQLite for metrics collection.
    
    Tracks processing times, system utilization, cache effectiveness,
    and platform-specific optimizations.
    """
    
    def __init__(self, db_path: Union[str, Path] = None):
        """Initialize performance tracker with SQLite database."""
        if db_path is None:
            # Use platform-appropriate cache directory
            if platform.system() == 'Darwin':  # macOS
                cache_dir = Path.home() / '.epubs' / 'cache'
            else:  # Linux/Ubuntu
                cache_dir = Path.home() / '.cache' / 'epubs'
            
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = cache_dir / 'performance_metrics.db'
        
        self.db_path = Path(db_path)
        self._lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
        # Session tracking
        self.session_id = self._generate_session_id()
        self.session_start = datetime.now()
        
        logger.info(f"Performance tracker initialized: {self.db_path}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier."""
        timestamp = datetime.now().isoformat()
        platform_info = f"{platform.system()}-{platform.machine()}"
        session_string = f"{timestamp}-{platform_info}"
        return hashlib.md5(session_string.encode()).hexdigest()[:12]
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Processing metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    operation_type TEXT NOT NULL,
                    file_path TEXT,
                    file_size_bytes INTEGER,
                    processing_time_seconds REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    enhancers_used TEXT,
                    platform_info TEXT,
                    memory_usage_mb REAL,
                    cpu_usage_percent REAL
                )
            ''')
            
            # System metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_count INTEGER,
                    cpu_usage_percent REAL,
                    memory_total_mb REAL,
                    memory_used_mb REAL,
                    memory_percent REAL,
                    disk_usage_percent REAL,
                    platform_system TEXT,
                    platform_machine TEXT,
                    apple_chip TEXT,
                    gpu_available BOOLEAN
                )
            ''')
            
            # Cache metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    operation TEXT NOT NULL,
                    cache_key TEXT NOT NULL,
                    hit BOOLEAN NOT NULL,
                    response_time_ms REAL,
                    data_size_bytes INTEGER
                )
            ''')
            
            # Optimization metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimization_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    optimization_type TEXT NOT NULL,
                    enabled BOOLEAN NOT NULL,
                    performance_gain_percent REAL,
                    baseline_time_seconds REAL,
                    optimized_time_seconds REAL,
                    configuration TEXT
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_processing_timestamp ON processing_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_processing_session ON processing_metrics(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_timestamp ON cache_metrics(timestamp)')
            
            conn.commit()
            logger.debug("Database initialized successfully")
    
    @contextmanager
    def track_operation(self, operation_type: str, file_path: Optional[str] = None, 
                       enhancers_used: Optional[List[str]] = None):
        """
        Context manager for tracking operation performance.
        
        Usage:
            with tracker.track_operation('pdf_enhancement', 'document.pdf'):
                # perform operation
                result = enhance_document()
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        start_cpu = self._get_cpu_usage()
        
        success = False
        error_message = None
        
        try:
            yield
            success = True
        except Exception as e:
            error_message = str(e)
            logger.error(f"Operation {operation_type} failed: {e}")
            raise
        finally:
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Get file size if file path provided
            file_size = None
            if file_path and Path(file_path).exists():
                file_size = Path(file_path).stat().st_size
            
            # Record processing metrics
            self.record_processing_metric(
                operation_type=operation_type,
                file_path=file_path,
                file_size_bytes=file_size,
                processing_time_seconds=processing_time,
                success=success,
                error_message=error_message,
                enhancers_used=enhancers_used,
                memory_usage_mb=self._get_memory_usage(),
                cpu_usage_percent=self._get_cpu_usage()
            )
    
    def record_processing_metric(self, operation_type: str, processing_time_seconds: float,
                               success: bool, file_path: Optional[str] = None,
                               file_size_bytes: Optional[int] = None,
                               error_message: Optional[str] = None,
                               enhancers_used: Optional[List[str]] = None,
                               memory_usage_mb: Optional[float] = None,
                               cpu_usage_percent: Optional[float] = None):
        """Record a processing operation metric."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get platform info
                    platform_info = self._get_platform_info()
                    
                    cursor.execute('''
                        INSERT INTO processing_metrics (
                            session_id, operation_type, file_path, file_size_bytes,
                            processing_time_seconds, success, error_message, enhancers_used,
                            platform_info, memory_usage_mb, cpu_usage_percent
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        self.session_id, operation_type, file_path, file_size_bytes,
                        processing_time_seconds, success, error_message,
                        json.dumps(enhancers_used) if enhancers_used else None,
                        json.dumps(platform_info), memory_usage_mb, cpu_usage_percent
                    ))
                    
                    conn.commit()
                    logger.debug(f"Recorded processing metric: {operation_type} ({processing_time_seconds:.3f}s)")
                    
            except Exception as e:
                logger.error(f"Failed to record processing metric: {e}")
    
    def record_system_metrics(self):
        """Record current system metrics."""
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available - skipping system metrics")
            return
            
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get system information
                    cpu_count = psutil.cpu_count()
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    # Get platform-specific info
                    apple_chip = None
                    gpu_available = False
                    
                    try:
                        from ..utils.platform_detection import get_apple_chip, is_apple_silicon
                        if is_apple_silicon():
                            apple_chip = get_apple_chip()
                    except ImportError:
                        pass
                    
                    # Check for GPU (basic check)
                    try:
                        import torch
                        gpu_available = torch.cuda.is_available()
                    except ImportError:
                        pass
                    
                    cursor.execute('''
                        INSERT INTO system_metrics (
                            session_id, cpu_count, cpu_usage_percent, memory_total_mb,
                            memory_used_mb, memory_percent, disk_usage_percent,
                            platform_system, platform_machine, apple_chip, gpu_available
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        self.session_id, cpu_count, cpu_percent,
                        memory.total / (1024**2), memory.used / (1024**2), memory.percent,
                        disk.percent, platform.system(), platform.machine(),
                        apple_chip, gpu_available
                    ))
                    
                    conn.commit()
                    logger.debug("Recorded system metrics")
                    
            except Exception as e:
                logger.error(f"Failed to record system metrics: {e}")
    
    def record_cache_metric(self, operation: str, cache_key: str, hit: bool, 
                          response_time_ms: float, data_size_bytes: Optional[int] = None):
        """Record cache operation metric."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO cache_metrics (
                            session_id, operation, cache_key, hit, response_time_ms, data_size_bytes
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        self.session_id, operation, cache_key, hit, response_time_ms, data_size_bytes
                    ))
                    
                    conn.commit()
                    logger.debug(f"Recorded cache metric: {operation} ({'HIT' if hit else 'MISS'})")
                    
            except Exception as e:
                logger.error(f"Failed to record cache metric: {e}")
    
    def record_optimization_metric(self, optimization_type: str, enabled: bool,
                                 baseline_time_seconds: Optional[float] = None,
                                 optimized_time_seconds: Optional[float] = None,
                                 configuration: Optional[Dict[str, Any]] = None):
        """Record optimization effectiveness metric."""
        performance_gain_percent = None
        if baseline_time_seconds and optimized_time_seconds:
            performance_gain_percent = ((baseline_time_seconds - optimized_time_seconds) / 
                                      baseline_time_seconds) * 100
        
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO optimization_metrics (
                            session_id, optimization_type, enabled, performance_gain_percent,
                            baseline_time_seconds, optimized_time_seconds, configuration
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        self.session_id, optimization_type, enabled, performance_gain_percent,
                        baseline_time_seconds, optimized_time_seconds,
                        json.dumps(configuration) if configuration else None
                    ))
                    
                    conn.commit()
                    logger.debug(f"Recorded optimization metric: {optimization_type}")
                    
            except Exception as e:
                logger.error(f"Failed to record optimization metric: {e}")
    
    def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get performance summary for the last N days."""
        since_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Processing metrics summary
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_operations,
                    AVG(processing_time_seconds) as avg_processing_time,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_operations,
                    SUM(file_size_bytes) as total_bytes_processed,
                    AVG(memory_usage_mb) as avg_memory_usage,
                    AVG(cpu_usage_percent) as avg_cpu_usage
                FROM processing_metrics 
                WHERE timestamp > ?
            ''', (since_date,))
            
            processing_stats = cursor.fetchone()
            
            # Cache performance
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_cache_ops,
                    SUM(CASE WHEN hit = 1 THEN 1 ELSE 0 END) as cache_hits,
                    AVG(response_time_ms) as avg_response_time
                FROM cache_metrics 
                WHERE timestamp > ?
            ''', (since_date,))
            
            cache_stats = cursor.fetchone()
            
            # Most common operations
            cursor.execute('''
                SELECT operation_type, COUNT(*) as count, AVG(processing_time_seconds) as avg_time
                FROM processing_metrics 
                WHERE timestamp > ?
                GROUP BY operation_type
                ORDER BY count DESC
                LIMIT 5
            ''', (since_date,))
            
            common_operations = cursor.fetchall()
            
            # Platform performance by chip type
            cursor.execute('''
                SELECT 
                    JSON_EXTRACT(platform_info, '$.apple_chip') as chip,
                    COUNT(*) as operations,
                    AVG(processing_time_seconds) as avg_time
                FROM processing_metrics 
                WHERE timestamp > ? AND JSON_EXTRACT(platform_info, '$.apple_chip') IS NOT NULL
                GROUP BY chip
            ''', (since_date,))
            
            platform_performance = cursor.fetchall()
            
        # Calculate cache hit rate
        cache_hit_rate = 0
        if cache_stats and cache_stats[0] and cache_stats[0] > 0:
            cache_hit_rate = (cache_stats[1] / cache_stats[0]) * 100
        
        # Calculate success rate
        success_rate = 0
        if processing_stats and processing_stats[0] and processing_stats[0] > 0:
            success_rate = (processing_stats[2] / processing_stats[0]) * 100
        
        return {
            'summary_period_days': days,
            'total_operations': processing_stats[0] if processing_stats else 0,
            'success_rate_percent': round(success_rate, 2),
            'avg_processing_time_seconds': round(processing_stats[1] if processing_stats and processing_stats[1] else 0, 3),
            'total_bytes_processed': processing_stats[3] if processing_stats else 0,
            'avg_memory_usage_mb': round(processing_stats[4] if processing_stats and processing_stats[4] else 0, 1),
            'avg_cpu_usage_percent': round(processing_stats[5] if processing_stats and processing_stats[5] else 0, 1),
            'cache_operations': cache_stats[0] if cache_stats else 0,
            'cache_hit_rate_percent': round(cache_hit_rate, 2),
            'avg_cache_response_time_ms': round(cache_stats[2] if cache_stats and cache_stats[2] else 0, 2),
            'common_operations': [
                {'operation': op[0], 'count': op[1], 'avg_time': round(op[2], 3)}
                for op in common_operations
            ],
            'platform_performance': [
                {'chip': perf[0], 'operations': perf[1], 'avg_time': round(perf[2], 3)}
                for perf in platform_performance
            ] if platform_performance else []
        }
    
    def get_recent_metrics(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent processing metrics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    timestamp, operation_type, file_path, processing_time_seconds,
                    success, enhancers_used, memory_usage_mb, cpu_usage_percent
                FROM processing_metrics 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            metrics = []
            for row in cursor.fetchall():
                enhancers = None
                if row[5]:
                    try:
                        enhancers = json.loads(row[5])
                    except:
                        pass
                
                metrics.append({
                    'timestamp': row[0],
                    'operation_type': row[1],
                    'file_path': row[2],
                    'processing_time_seconds': row[3],
                    'success': bool(row[4]),
                    'enhancers_used': enhancers,
                    'memory_usage_mb': row[6],
                    'cpu_usage_percent': row[7]
                })
            
            return metrics
    
    def cleanup_old_metrics(self, days_to_keep: int = 30):
        """Clean up metrics older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Clean up each table
                    tables = ['processing_metrics', 'system_metrics', 'cache_metrics', 'optimization_metrics']
                    total_deleted = 0
                    
                    for table in tables:
                        cursor.execute(f'DELETE FROM {table} WHERE timestamp < ?', (cutoff_date,))
                        deleted = cursor.rowcount
                        total_deleted += deleted
                        logger.debug(f"Deleted {deleted} old records from {table}")
                    
                    # Vacuum database to reclaim space
                    cursor.execute('VACUUM')
                    conn.commit()
                    
                    logger.info(f"Cleaned up {total_deleted} old metric records")
                    
            except Exception as e:
                logger.error(f"Failed to cleanup old metrics: {e}")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if not PSUTIL_AVAILABLE:
            return 0.0
            
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        if not PSUTIL_AVAILABLE:
            return 0.0
            
        try:
            return psutil.cpu_percent()
        except:
            return 0.0
    
    def _get_platform_info(self) -> Dict[str, Any]:
        """Get current platform information."""
        info = {
            'system': platform.system(),
            'machine': platform.machine(),
            'python_version': platform.python_version()
        }
        
        # Add Apple Silicon info if available
        try:
            from ..utils.platform_detection import get_apple_chip, is_apple_silicon
            if is_apple_silicon():
                info['apple_chip'] = get_apple_chip()
        except ImportError:
            pass
        
        return info


# Global performance tracker instance
_global_tracker: Optional[PerformanceTracker] = None


def get_performance_tracker() -> PerformanceTracker:
    """Get global performance tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = PerformanceTracker()
    return _global_tracker


def track_operation(operation_type: str, file_path: Optional[str] = None, 
                   enhancers_used: Optional[List[str]] = None):
    """Decorator/context manager for tracking operation performance."""
    return get_performance_tracker().track_operation(operation_type, file_path, enhancers_used)