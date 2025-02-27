"""
Test suite for the refactoring tool.
Provides comprehensive tests for all refactoring functionality.
"""

from .test_refactoring import (
    TestRefactoringTool,
    TestCodeAnalysisHelpers,
    TestImportHelpers,
    TestAsyncHelpers,
    TestResourceHelpers,
    TestBackupHelpers,
    test_main
)

__all__ = [
    'TestRefactoringTool',
    'TestCodeAnalysisHelpers',
    'TestImportHelpers',
    'TestAsyncHelpers',
    'TestResourceHelpers',
    'TestBackupHelpers',
    'test_main'
]

# Test configuration
TEST_CONFIG = {
    'test_dir': 'test_files',
    'timeout': 30,
    'skip_slow': False
}

def run_all_tests():
    """Run the complete test suite."""
    test_main()

def setup_test_environment():
    """Set up the test environment with necessary files and directories."""
    import tempfile
    import shutil
    from pathlib import Path
    
    test_dir = Path(tempfile.mkdtemp())
    
    # Create test files structure
    (test_dir / 'src').mkdir()
    (test_dir / 'tests').mkdir()
    
    return test_dir

def teardown_test_environment(test_dir):
    """Clean up the test environment."""
    import shutil
    shutil.rmtree(test_dir)

def create_test_file(content: str, extension: str = '.py') -> str:
    """Create a temporary test file with given content."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as f:
        f.write(content.encode('utf-8'))
        return f.name
