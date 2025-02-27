import ast
import difflib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import re
import logging
from dataclasses import dataclass


@dataclass
class CodeBlock:
    """Represents a block of code for analysis."""
    content: str
    start_line: int
    end_line: int
    complexity: int = 0


class CodeAnalysisHelpers:
    """Helper functions for code analysis."""

    @staticmethod
    def calculate_complexity(node: ast.AST) ->int:
        """Calculate cyclomatic complexity of an AST node."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.
                ExceptHandler, ast.With, ast.Assert, ast.Raise)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    @staticmethod
    def extract_code_blocks(content: str) ->List[CodeBlock]:
        """Extract logical blocks of code from content."""
        blocks = []
        current_block = []
        start_line = 1
        for i, line in enumerate(content.split('\n'), 1):
            if line.strip():
                current_block.append(line)
            elif current_block:
                blocks.append(CodeBlock(content='\n'.join(current_block),
                    start_line=start_line, end_line=i - 1))
                current_block = []
                start_line = i + 1
        if current_block:
            blocks.append(CodeBlock(content='\n'.join(current_block),
                start_line=start_line, end_line=len(content.split('\n'))))
        return blocks

    @staticmethod
    def normalize_code(content: str) ->str:
        """Normalize code for comparison (removing whitespace and variable names)."""
        content = re.sub('#.*$', '', content, flags=re.MULTILINE)
        content = re.sub('\\s+', ' ', content)
        content = re.sub('\\b[a-zA-Z_]\\w*\\b', 'VAR', content)
        return content.strip()


class ImportHelpers:
    """Helper functions for import handling."""

    @staticmethod
    def analyze_imports(tree: ast.AST) ->Dict[str, Set[str]]:
        """Analyze imports in an AST."""
        imports = {'stdlib': set(), 'third_party': set(), 'local': set()}
        stdlib_modules = set(sys.stdlib_module_names)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module_name = node.module if isinstance(node, ast.ImportFrom
                    ) else node.names[0].name
                base_module = module_name.split('.')[0]
                if base_module in stdlib_modules:
                    imports['stdlib'].add(module_name)
                elif base_module in ('accessibility_checker',):
                    imports['local'].add(module_name)
                else:
                    imports['third_party'].add(module_name)
        return imports

    @staticmethod
    def organize_imports(content: str) ->str:
        """Organize imports by category."""
        tree = ast.parse(content)
        imports = ImportHelpers.analyze_imports(tree)
        organized = []
        for category in ['stdlib', 'third_party', 'local']:
            if imports[category]:
                sorted_imports = sorted(imports[category])
                organized.extend([f'import {imp}' for imp in sorted_imports])
                organized.append('')
        import_end = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_end = max(import_end, node.end_lineno)
        lines = content.split('\n')
        return '\n'.join(organized + lines[import_end:])


class AsyncHelpers:
    """Helper functions for async code handling."""

    @staticmethod
    def is_async_compatible(func_node: ast.FunctionDef) ->bool:
        """Check if a function is compatible with async conversion."""
        has_blocking = False
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in {'open', 'read', 'write'}:
                        has_blocking = True
                        break
        return has_blocking

    @staticmethod
    def convert_to_async(func_node: ast.FunctionDef) ->ast.AsyncFunctionDef:
        """Convert a function to its async equivalent."""
        return ast.AsyncFunctionDef(name=func_node.name, args=func_node.
            args, body=AsyncHelpers.convert_body_to_async(func_node.body),
            decorator_list=func_node.decorator_list, returns=func_node.returns)

    @staticmethod
    def convert_body_to_async(body: List[ast.stmt]) ->List[ast.stmt]:
        """Convert function body to use async operations."""
        new_body = []
        for node in body:
            if isinstance(node, ast.Call):
                if AsyncHelpers.is_async_compatible(node):
                    new_body.append(ast.Await(node))
            else:
                new_body.append(node)
        return new_body


class ResourceHelpers:
    """Helper functions for resource management."""

    @staticmethod
    def has_context_manager(node: ast.AST) ->bool:
        """Check if code uses context managers properly."""
        for child in ast.walk(node):
            if isinstance(child, ast.With):
                return True
        return False

    @staticmethod
    def wrap_with_context_manager(node: ast.AST) ->ast.With:
        """Wrap code with appropriate context manager."""
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == 'open':
                return ast.With(items=[ast.withitem(context_expr=node,
                    optional_vars=ast.Name(id='f', ctx=ast.Store()))], body=[])
        return node


class BackupHelpers:
    """Helper functions for backup and safety."""

    @staticmethod
    def create_backup(file_path: Path) ->Path:
        """Create a backup of a file."""
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path

    @staticmethod
    def generate_diff(original: str, modified: str) ->str:
        """Generate a diff between original and modified code."""
        diff = difflib.unified_diff(original.splitlines(keepends=True),
            modified.splitlines(keepends=True), fromfile='original', tofile
            ='modified')
        return ''.join(diff)

    @staticmethod
    def restore_backup(backup_path: Path) ->None:
        """Restore file from backup."""
        original_path = backup_path.with_suffix('')
        import shutil
        shutil.move(backup_path, original_path)


def setup_logging(log_file: Optional[str]=None) ->logging.Logger:
    """Set up logging for the refactoring tool."""
    logger = logging.getLogger('refactoring_tool')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger
