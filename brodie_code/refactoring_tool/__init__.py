"""
Automated Refactoring Tool for Python Projects
Provides utilities for automated code refactoring and improvement.
"""

from .refactoring_script import (
    RefactoringTool,
    RefactoringChange,
    main
)

__version__ = '0.1.0'
__author__ = 'Your Organization'
__license__ = 'MIT'

__all__ = [
    'RefactoringTool',
    'RefactoringChange',
    'main'
]

# Package-level configuration
DEFAULT_CONFIG = {
    'dry_run': True,
    'log_level': 'INFO',
    'backup': True
}

def create_refactoring_tool(project_root: str, **kwargs) -> RefactoringTool:
    """
    Factory function to create a configured RefactoringTool instance.
    
    Args:
        project_root: Root directory of the project to refactor
        **kwargs: Additional configuration options
        
    Returns:
        Configured RefactoringTool instance
    """
    return RefactoringTool(project_root, **kwargs)
