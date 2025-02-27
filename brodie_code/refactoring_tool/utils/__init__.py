"""
Utility functions and helpers for the refactoring tool.
Provides code analysis, import handling, and resource management utilities.
"""

from .helpers import (
    CodeBlock,
    CodeAnalysisHelpers,
    ImportHelpers,
    AsyncHelpers,
    ResourceHelpers,
    BackupHelpers,
    setup_logging
)

__all__ = [
    'CodeBlock',
    'CodeAnalysisHelpers',
    'ImportHelpers',
    'AsyncHelpers',
    'ResourceHelpers',
    'BackupHelpers',
    'setup_logging'
]

# Version of the utils module
__version__ = '0.1.0'

# Default configurations
DEFAULT_LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'backup_dir': 'backups'
}

def get_code_analyzer():
    """Factory function for code analysis tools."""
    return CodeAnalysisHelpers()

def get_import_analyzer():
    """Factory function for import analysis tools."""
    return ImportHelpers()

def get_backup_helper(backup_dir: str = None):
    """Factory function for backup tools."""
    return BackupHelpers()
