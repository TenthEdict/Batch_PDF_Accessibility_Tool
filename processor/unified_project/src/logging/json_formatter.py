#!/usr/bin/env python3
"""
Structured JSON Logging Formatter for ePubs Accessibility Enhancement Project.

This module provides structured JSON logging capabilities including:
- JSON log output formatting
- Correlation IDs for request tracking
- Log level filtering
- Performance metrics in logs
- Contextual information enrichment
"""

import json
import logging
import uuid
import time
import threading
from datetime import datetime
from typing import Any, Dict, Optional, Union
from pathlib import Path
import traceback
import sys


class CorrelationContext:
    """Thread-local correlation context for request tracking."""
    
    def __init__(self):
        self._local = threading.local()
    
    @property
    def correlation_id(self) -> Optional[str]:
        """Get the current correlation ID."""
        return getattr(self._local, 'correlation_id', None)
    
    @correlation_id.setter
    def correlation_id(self, value: Optional[str]):
        """Set the current correlation ID."""
        self._local.correlation_id = value
    
    @property
    def request_id(self) -> Optional[str]:
        """Get the current request ID."""
        return getattr(self._local, 'request_id', None)
    
    @request_id.setter
    def request_id(self, value: Optional[str]):
        """Set the current request ID."""
        self._local.request_id = value
    
    @property
    def user_id(self) -> Optional[str]:
        """Get the current user ID."""
        return getattr(self._local, 'user_id', None)
    
    @user_id.setter
    def user_id(self, value: Optional[str]):
        """Set the current user ID."""
        self._local.user_id = value
    
    def clear(self):
        """Clear all context values."""
        if hasattr(self._local, 'correlation_id'):
            delattr(self._local, 'correlation_id')
        if hasattr(self._local, 'request_id'):
            delattr(self._local, 'request_id')
        if hasattr(self._local, 'user_id'):
            delattr(self._local, 'user_id')


# Global correlation context
correlation_context = CorrelationContext()


class JSONFormatter(logging.Formatter):
    """
    Structured JSON log formatter with correlation tracking and performance metrics.
    
    Features:
    - JSON structured output
    - Correlation ID tracking
    - Performance metrics
    - Contextual information
    - Error details with stack traces
    """
    
    def __init__(self, 
                 include_correlation: bool = True,
                 include_performance: bool = True,
                 include_context: bool = True,
                 include_stack_trace: bool = True,
                 max_stack_depth: int = 10):
        """
        Initialize JSON formatter.
        
        Args:
            include_correlation: Include correlation IDs in logs
            include_performance: Include performance metrics
            include_context: Include contextual information
            include_stack_trace: Include stack traces for errors
            max_stack_depth: Maximum stack trace depth
        """
        super().__init__()
        self.include_correlation = include_correlation
        self.include_performance = include_performance
        self.include_context = include_context
        self.include_stack_trace = include_stack_trace
        self.max_stack_depth = max_stack_depth
        
        # Performance tracking
        self._start_times = {}
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add correlation information
        if self.include_correlation:
            correlation_id = correlation_context.correlation_id
            request_id = correlation_context.request_id
            user_id = correlation_context.user_id
            
            if correlation_id:
                log_entry["correlation_id"] = correlation_id
            if request_id:
                log_entry["request_id"] = request_id
            if user_id:
                log_entry["user_id"] = user_id
        
        # Add performance metrics
        if self.include_performance:
            performance_data = self._get_performance_metrics(record)
            if performance_data:
                log_entry["performance"] = performance_data
        
        # Add contextual information
        if self.include_context:
            context_data = self._get_context_data(record)
            if context_data:
                log_entry["context"] = context_data
        
        # Add exception information
        if record.exc_info:
            log_entry["exception"] = self._format_exception(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, 'extra_fields') and record.extra_fields:
            log_entry.update(record.extra_fields)
        
        # Add custom attributes
        for attr in ['file_path', 'operation', 'duration', 'status_code', 'error_code']:
            if hasattr(record, attr):
                log_entry[attr] = getattr(record, attr)
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)
    
    def _get_performance_metrics(self, record: logging.LogRecord) -> Optional[Dict[str, Any]]:
        """Extract performance metrics from log record."""
        metrics = {}
        
        # Check if this is a performance-related log
        if hasattr(record, 'duration'):
            metrics['duration_ms'] = round(record.duration * 1000, 2)
        
        if hasattr(record, 'memory_usage'):
            metrics['memory_usage_mb'] = round(record.memory_usage / (1024 * 1024), 2)
        
        if hasattr(record, 'cpu_usage'):
            metrics['cpu_usage_percent'] = round(record.cpu_usage, 2)
        
        # Add thread information
        metrics['thread_id'] = record.thread
        metrics['thread_name'] = record.threadName
        
        # Add process information
        metrics['process_id'] = record.process
        
        return metrics if metrics else None
    
    def _get_context_data(self, record: logging.LogRecord) -> Optional[Dict[str, Any]]:
        """Extract contextual information from log record."""
        context = {}
        
        # Add file processing context
        if hasattr(record, 'file_path'):
            context['file_path'] = str(record.file_path)
            if hasattr(record, 'file_size'):
                context['file_size_mb'] = round(record.file_size / (1024 * 1024), 2)
        
        # Add operation context
        if hasattr(record, 'operation'):
            context['operation'] = record.operation
        
        # Add enhancement context
        if hasattr(record, 'enhancement_mode'):
            context['enhancement_mode'] = record.enhancement_mode
        
        if hasattr(record, 'enhancers_used'):
            context['enhancers_used'] = record.enhancers_used
        
        # Add batch processing context
        if hasattr(record, 'batch_id'):
            context['batch_id'] = record.batch_id
        
        if hasattr(record, 'batch_size'):
            context['batch_size'] = record.batch_size
        
        if hasattr(record, 'batch_progress'):
            context['batch_progress'] = record.batch_progress
        
        return context if context else None
    
    def _format_exception(self, exc_info) -> Dict[str, Any]:
        """Format exception information."""
        exc_type, exc_value, exc_traceback = exc_info
        
        exception_data = {
            "type": exc_type.__name__ if exc_type else None,
            "message": str(exc_value) if exc_value else None,
            "module": exc_type.__module__ if exc_type else None
        }
        
        if self.include_stack_trace and exc_traceback:
            # Extract stack trace frames
            frames = traceback.extract_tb(exc_traceback)
            stack_trace = []
            
            for i, frame in enumerate(frames[-self.max_stack_depth:]):
                stack_trace.append({
                    "frame": i + 1,
                    "filename": frame.filename,
                    "line": frame.lineno,
                    "function": frame.name,
                    "line_content": frame.line
                })
            
            exception_data["stack_trace"] = stack_trace
        
        return exception_data


class CorrelationFilter(logging.Filter):
    """Filter to add correlation information to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation information to log record."""
        record.correlation_id = correlation_context.correlation_id
        record.request_id = correlation_context.request_id
        record.user_id = correlation_context.user_id
        return True


class PerformanceFilter(logging.Filter):
    """Filter to add performance metrics to log records."""
    
    def __init__(self, track_duration: bool = True, track_memory: bool = True):
        super().__init__()
        self.track_duration = track_duration
        self.track_memory = track_memory
        self._start_times = {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add performance metrics to log record."""
        if self.track_duration:
            # Track operation duration
            if hasattr(record, 'operation_id'):
                op_id = record.operation_id
                if op_id in self._start_times:
                    record.duration = time.time() - self._start_times[op_id]
                    del self._start_times[op_id]
        
        if self.track_memory:
            # Add memory usage if available
            try:
                import psutil
                process = psutil.Process()
                record.memory_usage = process.memory_info().rss
            except ImportError:
                pass
        
        return True


def setup_json_logging(level: str = "INFO",
                      include_correlation: bool = True,
                      include_performance: bool = True,
                      include_context: bool = True,
                      log_file: Optional[Union[str, Path]] = None) -> logging.Logger:
    """
    Setup JSON logging configuration.
    
    Args:
        level: Logging level
        include_correlation: Include correlation tracking
        include_performance: Include performance metrics
        include_context: Include contextual information
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    # Create formatter
    formatter = JSONFormatter(
        include_correlation=include_correlation,
        include_performance=include_performance,
        include_context=include_context
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Create file handler if specified
    handlers = [console_handler]
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add new handlers
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Add filters
    if include_correlation:
        correlation_filter = CorrelationFilter()
        for handler in handlers:
            handler.addFilter(correlation_filter)
    
    if include_performance:
        performance_filter = PerformanceFilter()
        for handler in handlers:
            handler.addFilter(performance_filter)
    
    return root_logger


def set_correlation_id(correlation_id: Optional[str] = None):
    """Set the current correlation ID."""
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_context.correlation_id = correlation_id
    return correlation_id


def set_request_id(request_id: Optional[str] = None):
    """Set the current request ID."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    correlation_context.request_id = request_id
    return request_id


def set_user_id(user_id: str):
    """Set the current user ID."""
    correlation_context.user_id = user_id


def clear_correlation_context():
    """Clear all correlation context."""
    correlation_context.clear()


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID."""
    return correlation_context.correlation_id


def get_request_id() -> Optional[str]:
    """Get the current request ID."""
    return correlation_context.request_id


def get_user_id() -> Optional[str]:
    """Get the current user ID."""
    return correlation_context.user_id


class CorrelationContextManager:
    """Context manager for correlation tracking."""
    
    def __init__(self, correlation_id: Optional[str] = None, 
                 request_id: Optional[str] = None,
                 user_id: Optional[str] = None):
        self.correlation_id = correlation_id
        self.request_id = request_id
        self.user_id = user_id
        self.previous_correlation_id = None
        self.previous_request_id = None
        self.previous_user_id = None
    
    def __enter__(self):
        """Set correlation context."""
        # Store previous values
        self.previous_correlation_id = get_correlation_id()
        self.previous_request_id = get_request_id()
        self.previous_user_id = get_user_id()
        
        # Set new values
        if self.correlation_id:
            set_correlation_id(self.correlation_id)
        if self.request_id:
            set_request_id(self.request_id)
        if self.user_id:
            set_user_id(self.user_id)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore previous correlation context."""
        # Restore previous values
        if self.previous_correlation_id is not None:
            correlation_context.correlation_id = self.previous_correlation_id
        else:
            correlation_context.correlation_id = None
        
        if self.previous_request_id is not None:
            correlation_context.request_id = self.previous_request_id
        else:
            correlation_context.request_id = None
        
        if self.previous_user_id is not None:
            correlation_context.user_id = self.previous_user_id
        else:
            correlation_context.user_id = None


# Convenience function for correlation context
def create_correlation_context(correlation_id: Optional[str] = None,
                              request_id: Optional[str] = None,
                              user_id: Optional[str] = None):
    """Create a correlation context manager."""
    return CorrelationContextManager(correlation_id, request_id, user_id)


if __name__ == "__main__":
    # Example usage
    import logging
    
    # Setup JSON logging
    logger = setup_json_logging(level="DEBUG", log_file="logs/app.json")
    
    # Set correlation context
    with create_correlation_context(correlation_id="req-123", user_id="user-456"):
        logger.info("Processing document", extra={
            'file_path': '/path/to/document.pdf',
            'operation': 'enhancement',
            'enhancement_mode': 'academic'
        })
        
        try:
            # Simulate some work
            time.sleep(0.1)
            logger.debug("Document processed successfully")
        except Exception as e:
            logger.error("Processing failed", exc_info=True)
    
    logger.info("Request completed")
