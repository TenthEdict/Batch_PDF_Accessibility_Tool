# ePubs Accessibility Enhancement Project

## Overview
A comprehensive toolkit for enhancing document accessibility, particularly for academic publications and historical documents. This project automates PDF accessibility improvements through OCR, structural analysis, and content enhancement.

## Features
- Advanced OCR with historical document optimization
- PDF/UA tagging and structure enhancement
- Accessibility validation and reporting
- Metadata standardization
- Academic document processing (tables, equations, references)
- Batch processing capabilities

## Directory Structure
- `/src` - Core source code
- `/tests` - Test files and validation scripts
- `/data` - Input/output directories
- `/scripts` - Automation and utility scripts
- `/config` - Configuration files

## Setup and Usage
1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Process documents: `python -m src.main --input=data/input --output=data/output`

## Docker Support
The project can be run in a containerized environment:
```
docker build -t epubs-accessibility .
docker run -v /path/to/input:/app/data/input -v /path/to/output:/app/data/output epubs-accessibility
```