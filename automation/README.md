# ePubs Automation

Automation workflow scripts for the ePubs Accessibility Enhancement Project, providing end-to-end automation for document acquisition, processing, and output management.

## Features

- **End-to-End Workflow**: Orchestrates the complete document processing pipeline
- **Multi-Stage Processing**: Handles document acquisition, processing, and output management
- **Configurable Execution**: Customizable parameters for each workflow stage
- **Detailed Logging**: Comprehensive logging for tracking workflow progress
- **Error Handling**: Robust error handling and recovery mechanisms
- **Run Identification**: Unique run IDs for tracking and organizing processing batches

## Installation

### Prerequisites

- Python 3.8 or higher
- Access to the scraper and processor components
- python-decouple for configuration management

### Setup

1. Install dependencies:
   ```bash
   pip install python-decouple
   ```

2. Create a `.env` file for configuration (optional):
   ```
   PURDUE_DOWNLOADER_SCRIPT_NAME="purdue_downloader.py"
   UNIFIED_PROJECT_DIR_NAME="unified_project"
   DEFAULT_DOWNLOAD_BASE_DIR_NAME="downloaded_materials"
   UNIFIED_PROJECT_EXECUTABLE_NAME="main.py"
   LOG_DIR_NAME="logs"
   LOG_FILE_NAME="automation_workflow.log"
   LOG_LEVEL="INFO"
   ```

## Usage

### Basic Workflow Execution

Run the complete workflow with a specific base URL:

```bash
python automation/automate_workflow.py --base-url https://docs.lib.purdue.edu/modvis/2024/va
```

### Custom Run ID

Specify a custom identifier for the workflow run:

```bash
python automation/automate_workflow.py --base-url https://docs.lib.purdue.edu/modvis/2024/va --run-id batch_modvis_2024
```

### Adjust Logging Level

Control the verbosity of logs:

```bash
python automation/automate_workflow.py --base-url https://docs.lib.purdue.edu/modvis/2024/va --log-level DEBUG
```

## Workflow Stages

The automation script executes the following stages:

1. **Document Acquisition**: Uses the scraper component to download PDFs from the specified URL, organizing them into appropriate directories based on URL structure
2. **Input Preparation**: Copies downloaded files to the processor's input directory while preserving references to their original locations
3. **Document Processing**: Executes the unified project to enhance document accessibility
4. **Output Management**: Places processed files back in their original locations in a 'processed/' subdirectory

## Directory Structure

- **automate_workflow.py**: Main workflow orchestration script
- **logs/**: Directory for workflow execution logs

## Integration Points

- **Scraper Integration**: Calls the scraper component to download documents from specified URLs
- **Processor Integration**: Invokes the unified project to process documents and enhance accessibility

## Workflow Output

The workflow preserves the original directory structure created by the scraper and adds processed files in a `processed/` subdirectory within each directory:

```
/mnt/s/Departments/ePubs/Accessibility_Project/
└── [letter]_series/
    └── [series]/
        └── [year]/
            └── [section]/
                ├── original.pdf
                └── processed/
                    └── original.pdf  # Enhanced accessible version
```

This approach ensures that processed files are always placed next to their original source files, maintaining the organizational structure determined by the URL patterns while clearly separating the enhanced files.