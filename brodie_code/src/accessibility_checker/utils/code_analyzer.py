import os
from pathlib import Path
import ast
import logging
from typing import Dict, List, Set, Optional, Tuple
import pkg_resources
import re
from dataclasses import dataclass
import json
from datetime import datetime


@dataclass
class CodeAnalysisConfig:
    """Configuration for code analysis."""
    ignore_dirs: Set[str] = None
    file_extensions: Set[str] = None
    max_file_size_mb: float = 1.0
    output_dir: Path = Path('/app/output')

    def __post_init__(self) ->None:
        if self.ignore_dirs is None:
            self.ignore_dirs = {'venv', '__pycache__', '.git',
                'node_modules', '.pytest_cache'}
        if self.file_extensions is None:
            self.file_extensions = {'.py', '.yaml', '.yml', '.json', '.sh',
                '.txt'}
        os.makedirs(self.output_dir / 'analysis', exist_ok=True)


class CodeIssue:

    def __init__(self, issue_type: str, location: str, description: str,
        severity: str) ->None:
        self.type = issue_type
        self.location = location
        self.description = description
        self.severity = severity


class CodeAnalyzer:
    """Enhanced code analyzer for Python codebase quality assessment."""

    def __init__(self, config: Optional[CodeAnalysisConfig]=None) ->None:
        self.config = config or CodeAnalysisConfig()
        self.logger = logging.getLogger(__name__)
        self.issues: List[CodeIssue] = []

    def analyze_codebase(self, root_dir: str) ->Dict:
        """Perform comprehensive codebase analysis."""
        root_path = Path(root_dir)
        self.logger.info(f'Analyzing codebase at: {root_path}')
        python_files = self._collect_python_files(root_path)
        config_files = self._collect_config_files(root_path)
        analysis_results = {'dependency_analysis': self.
            _analyze_dependencies(), 'code_quality': self.
            _analyze_code_quality(python_files), 'configuration_analysis':
            self._analyze_configurations(config_files), 'ocr_analysis':
            self._analyze_ocr_implementation(python_files),
            'security_analysis': self._analyze_security_issues(python_files
            ), 'api_usage': self._analyze_api_usage(python_files), 'issues':
            self._format_issues(), 'recommendations': self.
            _generate_recommendations()}
        self._save_analysis_results(analysis_results)
        return analysis_results

    def _save_analysis_results(self, results: Dict) ->Path:
        """Save analysis results to output directory."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        analysis_dir = self.config.output_dir / 'analysis'
        os.makedirs(analysis_dir, exist_ok=True)
        output_file = analysis_dir / f'code_analysis_{timestamp}.json'
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            self.logger.info(f'Analysis results saved to: {output_file}')
            return output_file
        except Exception as e:
            self.logger.error(f'Failed to save analysis results: {str(e)}')
            raise

    def _collect_python_files(self, root_path: Path) ->List[Path]:
        """Collect Python files for analysis."""
        return [path for path in root_path.rglob('*.py') if not any(
            ignore_dir in path.parts for ignore_dir in self.config.ignore_dirs)
            ]

    def _collect_config_files(self, root_path: Path) ->List[Path]:
        """Collect configuration files."""
        config_patterns = ['*.yaml', '*.yml', '*.json', 'requirements.txt',
            'setup.py']
        config_files = []
        for pattern in config_patterns:
            config_files.extend([path for path in root_path.rglob(pattern) if
                not any(ignore_dir in path.parts for ignore_dir in self.
                config.ignore_dirs)])
        return config_files

    def _analyze_dependencies(self) ->Dict:
        """Analyze project dependencies and versions."""
        results = {'missing_dependencies': [], 'version_conflicts': [],
            'outdated_packages': []}
        try:
            requirements = self._parse_requirements()
            for req in requirements:
                try:
                    pkg_resources.require(req)
                except pkg_resources.DistributionNotFound:
                    results['missing_dependencies'].append(req)
                except pkg_resources.VersionConflict as e:
                    results['version_conflicts'].append(str(e))
            ocr_deps = ['pytesseract', 'opencv-python', 'Pillow']
            for dep in ocr_deps:
                if dep not in [r.split('==')[0] for r in requirements]:
                    self.issues.append(CodeIssue('missing_dependency',
                        'requirements.txt',
                        f'Missing OCR dependency: {dep}', 'high'))
        except Exception as e:
            self.logger.error(f'Error analyzing dependencies: {str(e)}')
        return results

    def _parse_requirements(self) ->List[str]:
        """Parse requirements.txt file."""
        requirements = []
        req_path = Path('/app/requirements.txt')
        try:
            if req_path.exists():
                with open(req_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            requirements.append(line)
            else:
                self.logger.warning('requirements.txt not found at: %s',
                    req_path)
        except Exception as e:
            self.logger.error(f'Error parsing requirements.txt: {str(e)}')
        return requirements

    def _analyze_code_quality(self, python_files: List[Path]) ->Dict:
        """Analyze Python code quality."""
        results = {'complexity_issues': [], 'unused_imports': [],
            'error_handling': [], 'documentation': [], 'code_smells': []}
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                analyzer = CodeQualityVisitor()
                analyzer.visit(tree)
                rel_path = self._get_container_path(file_path)
                if analyzer.issues:
                    for issue in analyzer.issues:
                        results[issue.type].append({'file': rel_path,
                            'description': issue.description})
                        self.issues.append(issue)
            except Exception as e:
                self.logger.error(f'Error analyzing {file_path}: {str(e)}')
        return results

    def _analyze_ocr_implementation(self, python_files: List[Path]) ->Dict:
        """Analyze OCR-related code and configurations."""
        results = {'ocr_config_issues': [], 'error_handling': [],
            'performance_concerns': []}
        ocr_files = [f for f in python_files if 'ocr' in str(f)]
        for file_path in ocr_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if ('pytesseract.image_to_string' in content and 'config='
                     not in content):
                    results['ocr_config_issues'].append({'file': self.
                        _get_container_path(file_path), 'issue':
                        'OCR called without configuration parameters'})
                if 'try' not in content:
                    results['error_handling'].append({'file': self.
                        _get_container_path(file_path), 'issue':
                        'Missing error handling in OCR processing'})
            except Exception as e:
                self.logger.error(
                    f'Error analyzing OCR file {file_path}: {str(e)}')
        return results

    def _analyze_configurations(self, config_files: List[Path]) ->Dict:
        """Analyze configuration files."""
        results = {'missing_configs': [], 'invalid_configs': [],
            'security_concerns': []}
        required_configs = {'config.yaml': ['ocr', 'max_workers', 'timeout'
            ], 'setup.py': ['install_requires', 'python_requires']}
        for file_path in config_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                file_name = file_path.name
                if file_name in required_configs:
                    missing = [config for config in required_configs[
                        file_name] if config not in content]
                    if missing:
                        results['missing_configs'].append({'file': self.
                            _get_container_path(file_path), 'missing': missing}
                            )
            except Exception as e:
                self.logger.error(
                    f'Error analyzing config file {file_path}: {str(e)}')
        return results

    def _analyze_security_issues(self, python_files: List[Path]) ->Dict:
        """Analyze security-related issues."""
        results = {'api_key_exposure': [], 'unsafe_operations': [],
            'input_validation': []}
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'os.system(' in content:
                    results['unsafe_operations'].append({'file': self.
                        _get_container_path(file_path), 'issue':
                        'Use of os.system() is potentially unsafe'})
                if 'eval(' in content:
                    results['unsafe_operations'].append({'file': self.
                        _get_container_path(file_path), 'issue':
                        'Use of eval() is unsafe'})
            except Exception as e:
                self.logger.error(
                    f'Error analyzing security in {file_path}: {str(e)}')
        return results

    def _analyze_api_usage(self, python_files: List[Path]) ->Dict:
        """Analyze API usage patterns."""
        results = {'anthropic_api_issues': [], 'error_handling': []}
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'anthropic' in content:
                    if 'max_tokens' not in content:
                        results['anthropic_api_issues'].append({'file':
                            self._get_container_path(file_path), 'issue':
                            'Anthropic API called without max_tokens parameter'
                            })
                    if 'try' not in content:
                        results['error_handling'].append({'file': self.
                            _get_container_path(file_path), 'issue':
                            'Missing error handling in API calls'})
            except Exception as e:
                self.logger.error(
                    f'Error analyzing API usage in {file_path}: {str(e)}')
        return results

    def _get_container_path(self, path: Path) ->str:
        """Convert path to container-relative path for consistent reporting."""
        try:
            if path.is_absolute():
                if str(path).startswith('/app'):
                    return str(path)
                return f'/app/{path.name}'
            return f'/app/{path}'
        except Exception as e:
            self.logger.warning(f'Error converting path {path}: {str(e)}')
            return str(path)

    def _format_issues(self) ->List[Dict]:
        """Format collected issues."""
        return [{'type': issue.type, 'location': issue.location,
            'description': issue.description, 'severity': issue.severity} for
            issue in self.issues]

    def _generate_recommendations(self) ->List[str]:
        """Generate recommendations based on findings."""
        recommendations = []
        issue_types = {issue.type for issue in self.issues}
        if 'missing_dependency' in issue_types:
            recommendations.append(
                'Update requirements.txt to include all necessary OCR dependencies'
                )
        if 'ocr_config_issues' in issue_types:
            recommendations.append(
                'Add explicit configuration parameters to all OCR calls')
        if any('error_handling' in it for it in issue_types):
            recommendations.append(
                'Implement comprehensive error handling across all API calls and OCR operations'
                )
        return recommendations


class CodeQualityVisitor(ast.NodeVisitor):
    """AST visitor for code quality analysis."""

    def __init__(self) ->None:
        self.issues = []
        self.imported_names = set()
        self.used_names = set()

    def visit_Import(self, node) ->None:
        """Record imported names."""
        for name in node.names:
            self.imported_names.add(name.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node) ->None:
        """Record names imported from modules."""
        for name in node.names:
            self.imported_names.add(name.name)
        self.generic_visit(node)

    def visit_Name(self, node) ->None:
        """Record name usage."""
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node) ->None:
        """Check function definitions."""
        if not ast.get_docstring(node):
            self.issues.append(CodeIssue('documentation',
                f'Function {node.name}', 'Missing function docstring',
                'medium'))
        if len(node.body) > 50:
            self.issues.append(CodeIssue('complexity_issues',
                f'Function {node.name}', 'Function is too long (>50 lines)',
                'high'))
        self.generic_visit(node)

    def verify_ocr_functionality(self) ->Dict:
        """Verify OCR functionality with a test image."""
        results = {'status': 'untested', 'issues': []}
        try:
            test_image = Image.new('RGB', (100, 30), color='white')
            d = ImageDraw.Draw(test_image)
            d.text((10, 10), 'Test OCR', fill='black')
            try:
                text = pytesseract.image_to_string(test_image)
                results['status'] = 'working' if 'test' in text.lower(
                    ) else 'unreliable'
            except Exception as e:
                results['status'] = 'failed'
                results['issues'].append(f'OCR test failed: {str(e)}')
        except Exception as e:
            results['status'] = 'setup_failed'
            results['issues'].append(f'Could not run OCR test: {str(e)}')
        return results


async def main():
    """Main function to run code analysis."""
    project_root = Path('/app')
    analyzer = CodeAnalyzer()
    results = analyzer.analyze_codebase(str(project_root))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = (project_root / 'output' / 'analysis' /
        f'code_analysis_{timestamp}.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print('\nAnalysis completed. Found:')
    print(f"- {len(results['issues'])} issues")
    print('\nRecommendations:')
    for rec in results['recommendations']:
        print(f'- {rec}')
    print(f'\nDetailed results saved to: {output_file}')


if __name__ == '__main__':
    import json
    import asyncio
    from datetime import datetime
    asyncio.run(main())
