# refactoring_tool/tests/test_refactoring.py

import unittest
from pathlib import Path
import tempfile
import shutil
import ast
from unittest.mock import patch, MagicMock

from refactoring_tool import RefactoringTool, RefactoringChange
from refactoring_tool.utils.helpers import (
    CodeAnalysisHelpers,
    ImportHelpers,
    AsyncHelpers,
    ResourceHelpers
)

class TestRefactoringTool(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test files
        self.test_dir = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(self.test_dir))
        
        # Create test files
        self.create_test_files()
        
        # Initialize refactoring tool
        self.tool = RefactoringTool(str(self.test_dir))

    def create_test_files(self):
        """Create test files with known issues."""
        # Test file with import issues
        import_test = self.test_dir / 'import_test.py'
        import_test.write_text('''
from ..core.document import AccessibilityDocumentProcessor
from ..utils.retry import RetryHandler
import os
import sys
from pathlib import Path
        ''')
        
        # Test file with error handling issues
        error_test = self.test_dir / 'error_test.py'
        error_test.write_text('''
def process_file():
    try:
        do_something()
    except Exception as e:
        print(f"Error: {e}")
        ''')
        
        # Test file with resource management issues
        resource_test = self.test_dir / 'resource_test.py'
        resource_test.write_text('''
def read_file(path):
    f = open(path)
    content = f.read()
    f.close()
    return content
        ''')

    def test_fix_imports(self):
        """Test import statement fixing."""
        test_file = self.test_dir / 'import_test.py'
        changes = self.tool.fix_imports(test_file)
        
        self.assertGreater(len(changes), 0)
        self.assertTrue(any('from .document import' in c.new_content for c in changes))

    def test_standardize_error_handling(self):
        """Test error handling standardization."""
        test_file = self.test_dir / 'error_test.py'
        changes = self.tool.standardize_error_handling(test_file)
        
        self.assertGreater(len(changes), 0)
        self.assertTrue(any('except (OCRError, ProcessingError)' in c.new_content for c in changes))

    def test_fix_resource_management(self):
        """Test resource management fixes."""
        test_file = self.test_dir / 'resource_test.py'
        changes = self.tool.fix_resource_management(test_file)
        
        self.assertGreater(len(changes), 0)
        self.assertTrue(any('with open' in c.new_content for c in changes))

    def test_centralize_config(self):
        """Test configuration centralization."""
        changes = self.tool.centralize_config()
        
        self.assertGreater(len(changes), 0)
        self.assertTrue(any('config.py' in c.file_path for c in changes))

    def test_split_large_classes(self):
        """Test class splitting functionality."""
        # Create test file with large class
        large_class = self.test_dir / 'large_class.py'
        large_class.write_text('''
class AccessibilityDocumentProcessor:
    def process_document(self):
        pass
        
    def check_headings(self):
        pass
        
    def detect_tables(self):
        pass
        ''')
        
        changes = self.tool.split_large_classes(large_class)
        
        self.assertGreater(len(changes), 0)
        self.assertTrue(any('class DocumentProcessor' in c.new_content for c in changes))

    def test_standardize_async(self):
        """Test async standardization."""
        # Create test file with sync functions
        sync_file = self.test_dir / 'sync_test.py'
        sync_file.write_text('''
def process_document():
    pass
    
def analyze_text():
    pass
        ''')
        
        changes = self.tool.standardize_async(sync_file)
        
        self.assertGreater(len(changes), 0)
        self.assertTrue(any('async def' in c.new_content for c in changes))

    def test_detect_duplicate_code(self):
        """Test duplicate code detection."""
        # Create test files with duplicate code
        file1 = self.test_dir / 'dup_test1.py'
        file2 = self.test_dir / 'dup_test2.py'
        
        duplicate_code = '''
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
        '''
        
        file1.write_text(duplicate_code)
        file2.write_text(duplicate_code)
        
        changes = self.tool.detect_duplicate_code(file1)
        
        self.assertGreater(len(changes), 0)
        self.assertTrue(any('utils/common.py' in c.file_path for c in changes))

class TestCodeAnalysisHelpers(unittest.TestCase):
    def test_calculate_complexity(self):
        """Test cyclomatic complexity calculation."""
        code = '''
def complex_function(x):
    if x > 0:
        if x < 10:
            return x
        else:
            return x * 2
    return 0
        '''
        
        tree = ast.parse(code)
        complexity = CodeAnalysisHelpers.calculate_complexity(tree)
        
        self.assertEqual(complexity, 3)  # Base + 2 if statements

    def test_normalize_code(self):
        """Test code normalization."""
        code1 = 'def test(x):\n    return x * 2'
        code2 = 'def func(y):\n    return y * 2'
        
        norm1 = CodeAnalysisHelpers.normalize_code(code1)
        norm2 = CodeAnalysisHelpers.normalize_code(code2)
        
        self.assertEqual(norm1, norm2)

    def test_extract_code_blocks(self):
        """Test code block extraction."""
        code = '''
def func1():
    pass

def func2():
    pass
'''
        blocks = CodeAnalysisHelpers.extract_code_blocks(code)
        self.assertEqual(len(blocks), 2)

class TestImportHelpers(unittest.TestCase):
    def test_analyze_imports(self):
        """Test import analysis."""
        code = '''
import os
import sys
from pathlib import Path
from accessibility_checker.utils import helper
import requests
'''
        tree = ast.parse(code)
        imports = ImportHelpers.analyze_imports(tree)
        
        self.assertIn('os', imports['stdlib'])
        self.assertIn('accessibility_checker.utils', imports['local'])
        self.assertIn('requests', imports['third_party'])

    def test_organize_imports(self):
        """Test import organization."""
        code = '''
import requests
import os
from accessibility_checker.utils import helper
from pathlib import Path
'''
        organized = ImportHelpers.organize_imports(code)
        lines = organized.split('\n')
        
        # Verify standard library imports come first
        self.assertTrue(any(line.startswith('import os') for line in lines[:3]))
        
        # Verify local imports come last
        self.assertTrue(any('accessibility_checker' in line for line in lines[-3:]))

class TestAsyncHelpers(unittest.TestCase):
    def test_is_async_compatible(self):
        """Test async compatibility check."""
        code = '''
def blocking_function():
    with open('file.txt') as f:
        return f.read()
'''
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        self.assertTrue(AsyncHelpers.is_async_compatible(func_node))

    def test_convert_to_async(self):
        """Test conversion to async function."""
        code = '''
def sync_function():
    result = process_data()
    return result
'''
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        async_node = AsyncHelpers.convert_to_async(func_node)
        self.assertTrue(isinstance(async_node, ast.AsyncFunctionDef))

class TestResourceHelpers(unittest.TestCase):
    def test_has_context_manager(self):
        """Test context manager detection."""
        code1 = '''
with open('file.txt') as f:
    content = f.read()
'''
        code2 = '''
f = open('file.txt')
content = f.read()
f.close()
'''
        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)
        
        self.assertTrue(ResourceHelpers.has_context_manager(tree1))
        self.assertFalse(ResourceHelpers.has_context_manager(tree2))

    def test_wrap_with_context_manager(self):
        """Test wrapping with context manager."""
        code = "open('file.txt')"
        tree = ast.parse(code)
        call_node = tree.body[0].value
        
        wrapped = ResourceHelpers.wrap_with_context_manager(call_node)
        self.assertTrue(isinstance(wrapped, ast.With))

class TestBackupHelpers(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(self.test_dir))

    def test_create_backup(self):
        """Test file backup creation."""
        # Create test file
        test_file = self.test_dir / 'test.py'
        test_file.write_text('original content')
        
        # Create backup
        backup_path = BackupHelpers.create_backup(test_file)
        
        self.assertTrue(backup_path.exists())
        self.assertEqual(backup_path.read_text(), 'original content')

    def test_generate_diff(self):
        """Test diff generation."""
        original = 'line1\nline2\n'
        modified = 'line1\nline2 modified\n'
        
        diff = BackupHelpers.generate_diff(original, modified)
        
        self.assertIn('-line2', diff)
        self.assertIn('+line2 modified', diff)

    def test_restore_backup(self):
        """Test backup restoration."""
        # Create test file and backup
        test_file = self.test_dir / 'test.py'
        test_file.write_text('original content')
        backup_path = test_file.with_suffix('.py.bak')
        backup_path.write_text('backup content')
        
        # Restore backup
        BackupHelpers.restore_backup(backup_path)
        
        self.assertFalse(backup_path.exists())
        self.assertEqual(test_file.read_text(), 'backup content')

def test_main():
    """Run the test suite."""
    unittest.main()

if __name__ == '__main__':
    test_main()
