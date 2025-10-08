#!/usr/bin/env python3
"""
Enhanced logging utilities with security-conscious error handling.

This module provides secure logging that prevents information disclosure
while maintaining useful debugging capabilities.
"""

import logging
import traceback
import re
from pathlib import Path
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Patterns to sanitize from error messages
SENSITIVE_PATTERNS = [
    (re.compile(r'/Users/[^/\s]+'), '/Users/***'),  # macOS user paths
    (re.compile(r'/home/[^/\s]+'), '/home/***'),    # Linux user paths
    (re.compile(r'C:\\Users\\[^\\]+'), 'C:\\Users\\***'),  # Windows user paths
    (re.compile(r'/etc/[^\s]+'), '/etc/***'),       # System config paths
    (re.compile(r'password[=:]\s*\S+', re.IGNORECASE), 'password=***'),  # Passwords
    (re.compile(r'token[=:]\s*\S+', re.IGNORECASE), 'token=***'),        # Tokens
    (re.compile(r'api[_-]?key[=:]\s*\S+', re.IGNORECASE), 'api_key=***'), # API keys
]

# Stack trace depth limit for production
MAX_TRACEBACK_DEPTH = 3


def sanitize_message(message: str) -> str:
    """
    Sanitize error message to remove sensitive information.
    
    Args:
        message: Original error message
        
    Returns:
        Sanitized message
    """
    sanitized = message
    
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    
    return sanitized


def sanitize_path(path: Path) -> str:
    """
    Sanitize file path for safe logging.
    
    Args:
        path: Path to sanitize
        
    Returns:
        Sanitized path string
    """
    try:
        # Just show filename and immediate parent
        if len(path.parts) > 2:
            return f".../{path.parts[-2]}/{path.parts[-1]}"
        else:
            return str(path)
    except Exception:
        return "***"


def get_safe_traceback(depth: int = MAX_TRACEBACK_DEPTH) -> str:
    """
    Get sanitized traceback with limited depth.
    
    Args:
        depth: Maximum number of stack frames to include
        
    Returns:
        Sanitized traceback string
    """
    try:
        tb_lines = traceback.format_exc().split('\n')
        
        # Limit depth
        if len(tb_lines) > depth * 2:
            tb_lines = tb_lines[:depth * 2] + ['... (traceback truncated for security)']
        
        # Sanitize each line
        sanitized_lines = [sanitize_message(line) for line in tb_lines]
        
        return '\n'.join(sanitized_lines)
    except Exception:
        return "Error getting traceback"


def log_error_safe(
    logger_instance: logging.Logger,
    message: str,
    error: Optional[Exception] = None,
    include_traceback: bool = False
):
    """
    Log error message with security-conscious sanitization.
    
    Args:
        logger_instance: Logger to use
        message: Error message
        error: Optional exception object
        include_traceback: Whether to include sanitized traceback
    """
    # Sanitize main message
    safe_message = sanitize_message(message)
    
    # Add error details if provided
    if error:
        error_msg = str(error)
        safe_error_msg = sanitize_message(error_msg)
        safe_message = f"{safe_message}: {safe_error_msg}"
    
    # Log the sanitized message
    logger_instance.error(safe_message)
    
    # Optionally include sanitized traceback (debug mode only)
    if include_traceback and logger_instance.isEnabledFor(logging.DEBUG):
        safe_tb = get_safe_traceback()
        logger_instance.debug(f"Traceback:\n{safe_tb}")


def log_warning_safe(
    logger_instance: logging.Logger,
    message: str,
    path: Optional[Path] = None
):
    """
    Log warning message with path sanitization.
    
    Args:
        logger_instance: Logger to use
        message: Warning message
        path: Optional path to sanitize
    """
    safe_message = sanitize_message(message)
    
    if path:
        safe_path = sanitize_path(path)
        safe_message = f"{safe_message}: {safe_path}"
    
    logger_instance.warning(safe_message)


def log_info_safe(
    logger_instance: logging.Logger,
    message: str,
    path: Optional[Path] = None
):
    """
    Log info message with path sanitization.
    
    Args:
        logger_instance: Logger to use
        message: Info message
        path: Optional path to sanitize
    """
    safe_message = sanitize_message(message)
    
    if path:
        safe_path = sanitize_path(path)
        safe_message = f"{safe_message}: {safe_path}"
    
    logger_instance.info(safe_message)


class SecureLogger:
    """
    Wrapper for standard logger with automatic sanitization.
    
    Usage:
        logger = SecureLogger(logging.getLogger(__name__))
        logger.error("Failed to process", error=e, include_traceback=True)
    """
    
    def __init__(self, logger_instance: logging.Logger):
        """
        Initialize secure logger wrapper.
        
        Args:
            logger_instance: Standard logger to wrap
        """
        self._logger = logger_instance
    
    def error(
        self,
        message: str,
        error: Optional[Exception] = None,
        include_traceback: bool = False
    ):
        """Log error with sanitization."""
        log_error_safe(self._logger, message, error, include_traceback)
    
    def warning(self, message: str, path: Optional[Path] = None):
        """Log warning with sanitization."""
        log_warning_safe(self._logger, message, path)
    
    def info(self, message: str, path: Optional[Path] = None):
        """Log info with sanitization."""
        log_info_safe(self._logger, message, path)
    
    def debug(self, message: str):
        """Log debug message (sanitized)."""
        safe_message = sanitize_message(message)
        self._logger.debug(safe_message)
    
    def isEnabledFor(self, level: int) -> bool:
        """Check if logging level is enabled."""
        return self._logger.isEnabledFor(level)


def create_secure_logger(name: str) -> SecureLogger:
    """
    Create a secure logger wrapper.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        SecureLogger instance
    """
    return SecureLogger(logging.getLogger(name))
