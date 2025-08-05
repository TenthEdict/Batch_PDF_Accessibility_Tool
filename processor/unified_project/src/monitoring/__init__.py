"""
Monitoring and Performance Tracking Module for ePubs Accessibility Enhancement.

This module provides local SQLite-based performance tracking, metrics collection,
and performance reporting for document processing operations.
"""

from .performance_tracker import PerformanceTracker, get_performance_tracker, track_operation

__all__ = [
    'PerformanceTracker',
    'get_performance_tracker', 
    'track_operation'
]