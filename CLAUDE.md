# SmolDocling Document Processing - Development Guide

## Build & Setup Commands
- Create virtual environment: `python -m venv venv`
- Activate virtual environment: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt`
- Run the processing pipeline: `./run.sh`

## Project Structure
- Input documents in `/data/input` directory
- Processed results in `/data/output` directory
- Source code in `/src` directory
- Tests in `/tests` directory

## Dependencies
- docling-core
- mlx-vlm (Apple Silicon optimized)
- pillow
- pymupdf
- python-docx
- python-pptx
- opencv-python
- scikit-image

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