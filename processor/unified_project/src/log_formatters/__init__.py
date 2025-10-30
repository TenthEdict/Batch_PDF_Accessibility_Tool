#!/usr/bin/env python3
"""
Structured JSON logging for ePubs Accessibility Enhancement Project.

This module provides structured logging capabilities including:
- JSON log output formatting
- Correlation IDs for request tracking
- Performance metrics in logs
- Contextual information enrichment
"""

from .json_formatter import (
    # Core classes
    CorrelationContext,
    JSONFormatter,
    CorrelationFilter,
    PerformanceFilter,
    CorrelationContextManager,

    # Global context instance
    correlation_context,

    # Setup functions
    setup_json_logging,

    # Context management functions
    set_correlation_id,
    set_request_id,
    set_user_id,
    clear_correlation_context,
    get_correlation_id,
    get_request_id,
    get_user_id,
    create_correlation_context,
)

__all__ = [
    # Core classes
    'CorrelationContext',
    'JSONFormatter',
    'CorrelationFilter',
    'PerformanceFilter',
    'CorrelationContextManager',

    # Global context
    'correlation_context',

    # Setup functions
    'setup_json_logging',

    # Context management
    'set_correlation_id',
    'set_request_id',
    'set_user_id',
    'clear_correlation_context',
    'get_correlation_id',
    'get_request_id',
    'get_user_id',
    'create_correlation_context',
]
