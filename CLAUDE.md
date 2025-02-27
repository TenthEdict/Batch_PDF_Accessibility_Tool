# PDF Accessibility Checker - Development Guide

## Build & Test Commands
- Install dependencies: `pip install -e .`
- Run all tests: `python -m unittest discover -s refactoring_tool/tests`
- Run single test: `python -m unittest refactoring_tool.tests.test_refactoring.TestRefactoringTool.test_fix_imports`
- Run code analysis: `./shell_scripts/analyze.sh`
- Run Docker container: `./shell_scripts/container.sh`
- Run OCR processing (basic): `./shell_scripts/container.sh process`
- Run OCR with custom resources: `./shell_scripts/container.sh process 16g 8 14400` (16GB RAM, 8 CPUs, 4hr timeout)
- Diagnose system: `./shell_scripts/container.sh diagnose`
- Clean output directory: `./shell_scripts/clean_output.sh`

## Docker Environment
- TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
- OCR files in `/app/input` directory
- Results in `/app/output` directory
- Default resources: 8GB RAM, 4 CPUs, 2hr timeout

## Code Style Guidelines
- **Imports**: Standard lib → third-party → local (group and alphabetize)
- **Formatting**: 4-space indentation, 88-char line length (PEP 8)
- **Type Hints**: Required for function signatures with arrow syntax
- **Docstrings**: Triple quotes with Args/Returns sections
- **Error Handling**: Specific exception types, avoid bare excepts
- **Resources**: Always use context managers (with statements)
- **Classes**: Single responsibility, split large classes
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Logging**: Use logger, not print statements