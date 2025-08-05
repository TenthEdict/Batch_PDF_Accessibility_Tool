# ePubs Accessibility Enhancement Project

This monorepo contains all components of the ePubs Accessibility Enhancement Project, which provides specialized tools for enhancing document accessibility across both historical and academic publications.

## Project Structure

The repository is now organized into two main components:

- **[/scraper](./scraper/)**: Document acquisition tools for downloading PDFs from library resources.
- **[/processor](./processor/)**: Core document processing components for enhancing accessibility, now consolidated into a unified, functional pipeline.

## Features

- **Unified Document Processing**: A single, coherent architecture for all document processing tasks.
- **Robust OCR and Font Embedding**: Utilizes `ocrmypdf` to provide reliable text recognition and ensure all fonts are embedded.
- **PDF/UA Compliance**: Automatically adds PDF/UA-1 identifiers and other accessibility metadata to processed documents.
- **Hardened Web Scraper**: The `scraper` has been refactored with more resilient selectors and explicit waits to improve reliability.
- **Streamlined Codebase**: Removed obsolete scripts, modules, and directories to reduce technical debt and improve maintainability.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- System dependencies: poppler-utils, tesseract-ocr

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-org/ePubs_Main.git
    cd ePubs_Main
    ```
2.  Set up the Python environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  Install system dependencies (Ubuntu/Debian):
    ```bash
    sudo apt-get update
    sudo apt-get install -y poppler-utils tesseract-ocr
    ```

## Usage

### Document Acquisition

Download documents from Purdue library resources:
```bash
python -m scraper.purdue_downloader --url https://docs.lib.purdue.edu/modvis/2024/va
```

### End-to-End Processing

Process a single PDF to apply OCR, embed fonts, and add accessibility metadata:
```bash
python -m processor.unified_project.src.main process input.pdf output.pdf
```

---

## Gemini AI Summary of Work Completed

This section documents the analysis and refactoring work performed by the Gemini AI assistant.

### 1. Core Problem Identification and Refactoring

-   **Initial State**: The project was in a partially refactored state. The `processor/core` directory was intended to be `processor/unified_project`, leading to broken imports and a non-functional `main.py`. The `scraper` was functional but brittle.
-   **Refactoring Actions**:
    -   Completed the renaming of `processor/core` to `processor/unified_project`.
    -   Updated all references in documentation, scripts, and configuration to use the correct paths.
    -   Replaced the non-functional `main.py` with a streamlined, `typer`-based CLI.

### 2. Implementation of Core Processing Logic

-   **Problem**: The project had a sophisticated structure but lacked the core implementation for its primary tasks. The system could not perform OCR, edit metadata, or embed fonts.
-   **Implemented Solution**:
    -   **Dependencies**: Added `ocrmypdf` and `pikepdf` to `requirements.txt` to provide robust, industry-standard tools for PDF manipulation.
    -   **`OCREnhancer`**: Created a new enhancer that leverages `ocrmypdf` to perform high-quality OCR and embed missing fonts in a single step.
    -   **`PDFEnhancer`**: Modified the existing `PDFEnhancer` to add the critical PDF/UA-1 identifier and other accessibility metadata.
    -   **`EnhancementService`**: Refactored the service to create a clear, sequential pipeline: documents are first passed to the `OCREnhancer` and the result is then passed to the `PDFEnhancer`.

### 3. Codebase Cleanup and Hardening

-   **Problem**: The repository contained numerous unused scripts, obsolete modules, and leftover backup files from previous refactoring efforts. The `scraper` used unreliable `time.sleep()` calls and brittle XPath selectors.
-   **Cleanup and Hardening Actions**:
    -   **Removed Obsolete Components**: Deleted the entire `automation/` directory, along with numerous unused scripts and modules from the `processor/` directory (e.g., `process_academic_local.py`, `ocr/`, `metadata/`).
    -   **Hardened Scraper**: Replaced all `time.sleep()` calls with explicit `WebDriverWait` conditions and updated XPath selectors to more resilient CSS selectors.
    -   **Improved Package Structure**: Populated the `__init__.py` files in key packages (`enhancers`, `academic`, `validation`) to create a cleaner, more accessible package structure.

## Recommended Next Steps

While the project is now in a stable and functional state, the following steps would further enhance its quality and capabilities:

### 1. Enhance Configuration Management

-   **Problem**: The `EnhancementService` currently has a hardcoded, sequential pipeline. The original vision (evident from the `hydra` setup and `config` modules) was for a more flexible, configuration-driven pipeline.
-   **Recommendation**: Refactor the `EnhancementService` to dynamically load and orchestrate enhancers based on a configuration file (e.g., `academic.yaml`). This would allow users to easily customize the processing workflow (e.g., skip OCR, add new enhancement steps) without changing the code.

### 2. Implement Comprehensive Unit and Integration Tests

-   **Problem**: The project has a `tests/` directory, but it contains very few tests and does not cover the new `OCREnhancer` or the refactored `EnhancementService`.
-   **Recommendation**:
    -   Write unit tests for the `OCREnhancer` and `PDFEnhancer` to verify their functionality in isolation.
    -   Create integration tests for the `EnhancementService` to ensure the end-to-end pipeline works as expected.
    -   Use mocking to simulate external dependencies like `ocrmypdf` to make tests faster and more reliable.

### 3. Activate and Utilize the `academic` Module

-   **Problem**: The `processor/unified_project/src/academic/` directory contains sophisticated logic for analyzing the structure of academic papers (detecting columns, formulas, citations, etc.), but it is not currently integrated into the main processing pipeline.
-   **Recommendation**:
    -   Create a new `AcademicStructureEnhancer` that utilizes the `AcademicStructureAnalyzer`.
    -   Integrate this new enhancer into the main pipeline (likely after the OCR step).
    -   The output of this enhancer could then be used to generate more detailed accessibility tags (e.g., marking up tables, figures, and headings correctly).

### 4. Improve Error Handling and Reporting

-   **Problem**: While basic error handling has been implemented, the system could provide more detailed feedback to the user.
-   **Recommendation**:
    -   Implement more specific exception handling in the `EnhancementService` to catch and report errors from each stage of the pipeline (OCR, metadata editing, etc.).
    -   Generate a simple report (e.g., a JSON or text file) for each processed document that details the enhancements applied and any warnings or errors that occurred.