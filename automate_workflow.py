#!/usr/bin/env python3

import argparse
import logging
import subprocess
import shutil
import sys
from pathlib import Path
from datetime import datetime
from decouple import config, Csv # Csv for comma-separated list in config

# --- Configuration ---
# BASE_SCRIPT_DIR will be the directory where this automate_workflow.py script is located.
BASE_SCRIPT_DIR = Path(__file__).resolve().parent

# Load configurations using python-decouple.
# These would typically be in a.env file or settings.ini.
# Example.env content:
# PURDUE_DOWNLOADER_SCRIPT_NAME="purdue_downloader.py"
# UNIFIED_PROJECT_DIR_NAME="unified_project"
# DEFAULT_DOWNLOAD_BASE_DIR_NAME="downloaded_materials"
# UNIFIED_PROJECT_EXECUTABLE_NAME="run_project.sh" # or main.py, etc.
# LOG_DIR_NAME="logs"
# LOG_FILE_NAME="automation_workflow.log"
# LOG_LEVEL="INFO"

PURDUE_DOWNLOADER_SCRIPT_NAME = config('PURDUE_DOWNLOADER_SCRIPT_NAME', default='purdue_downloader.py')
UNIFIED_PROJECT_DIR_NAME = config('UNIFIED_PROJECT_DIR_NAME', default='unified_project')
DEFAULT_DOWNLOAD_BASE_DIR_NAME = config('DEFAULT_DOWNLOAD_BASE_DIR_NAME', default='downloaded_materials')
UNIFIED_PROJECT_EXECUTABLE_NAME = config('UNIFIED_PROJECT_EXECUTABLE_NAME', default='run_project.sh')
LOG_DIR_NAME = config('LOG_DIR_NAME', default='logs')
LOG_FILE_NAME = config('LOG_FILE_NAME', default='automation_workflow.log')
CONFIG_LOG_LEVEL = config('LOG_LEVEL', default='INFO').upper()

# Construct full paths
PURDUE_DOWNLOADER_SCRIPT_PATH = BASE_SCRIPT_DIR / PURDUE_DOWNLOADER_SCRIPT_NAME
UNIFIED_PROJECT_DIR = BASE_SCRIPT_DIR / UNIFIED_PROJECT_DIR_NAME
LOG_DIR = BASE_SCRIPT_DIR / LOG_DIR_NAME
LOG_FILE_PATH = LOG_DIR / LOG_FILE_NAME

# Initialize logger - will be configured by setup_logging
logger = logging.getLogger(__name__) # Using __name__ is a common practice [1, 2]

# --- Logging Setup ---
def setup_logging(log_level_str: str = 'INFO', log_file: Path = LOG_FILE_PATH):
    """Configures logging for the application."""
    numeric_level = getattr(logging, log_level_str.upper(), None)
    if not isinstance(numeric_level, int):
        # Fallback to INFO if invalid level string is provided
        logger.warning(f"Invalid log level: {log_level_str}. Defaulting to INFO.")
        numeric_level = logging.INFO
    
    # Ensure log directory exists [3, 4]
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        # If log directory creation fails, print to stderr and exit or continue with console logging only
        sys.stderr.write(f"Warning: Could not create log directory {log_file.parent}. Error: {e}\n")
        # Depending on policy, you might want to exit or just not use file logging.
        # For this example, we'll proceed without file logging if it fails.
        log_file = None


    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S' # Consistent timestamp format [1, 2]
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove any existing handlers to avoid duplicate logs if re-configured
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional, if log_file is successfully determined)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, mode='a') # Append mode
            file_handler.setFormatter(log_formatter)
            root_logger.addHandler(file_handler)
            root_logger.info(f"Logging to file: {log_file}")
        except OSError as e:
            sys.stderr.write(f"Warning: Could not set up log file handler for {log_file}. Error: {e}\n")
    
    root_logger.info(f"Logging configured with level {log_level_str.upper()}.")


# --- Stage 1: Execute purdue_downloader.py ---
def run_purdue_downloader(base_url: str, download_target_dir: Path, script_path: Path) -> list[Path]:
    """
    Executes purdue_downloader.py to download files.
    Returns a list of paths to the downloaded PDF files.
    """
    logger.info(f"Executing {script_path.name} with base URL: {base_url} to {download_target_dir}")
    
    download_target_dir.mkdir(parents=True, exist_ok=True) # [1, 3, 5, 4]
    
    # Adapt this command to the actual arguments purdue_downloader.py expects
    command = [
        'python3', 
        str(script_path),
        '--base-url', base_url,
        '--output-dir', str(download_target_dir)
    ]
    
    try:
        # `check=True` raises CalledProcessError for non-zero exit codes [6, 7, 8]
        # `capture_output=True` captures stdout/stderr [6, 9, 10]
        # `text=True` decodes stdout/stderr as text
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True,
            cwd=script_path.parent # Run script from its own directory [6]
        )
        logger.info(f"{script_path.name} executed successfully.")
        if result.stdout: # Log stdout if not empty
            logger.debug(f"{script_path.name} STDOUT:\n{result.stdout.strip()}")
        if result.stderr: # Log stderr if not empty
            logger.warning(f"{script_path.name} STDERR:\n{result.stderr.strip()}")
            
        # Identify downloaded files (assuming PDFs in the target directory)
        downloaded_files = list(download_target_dir.glob('*.pdf')) # [11, 12]
        logger.info(f"Found {len(downloaded_files)} downloaded PDF files in {download_target_dir}")
        return downloaded_files

    except subprocess.CalledProcessError as e:
        logger.error(f"{script_path.name} failed. Return code: {e.returncode}")
        logger.error(f"Command: {' '.join(e.cmd)}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout.strip()}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr.strip()}")
        raise # Re-raise to be caught by main error handler
    except FileNotFoundError:
        logger.error(f"The script {script_path} or python3 interpreter was not found.")
        raise


# --- Stage 1.5: Prepare Input for Unified Project ---
def prepare_unified_project_input(downloaded_files: list[Path], unified_input_dir: Path):
    """Moves downloaded files to the unified_project input directory."""
    logger.info(f"Preparing input for unified_project in {unified_input_dir}...")
    unified_input_dir.mkdir(parents=True, exist_ok=True) # [1, 3, 5, 4]

    moved_files_count = 0
    if not downloaded_files:
        logger.info("No downloaded files to move to unified_project input.")
        return

    for src_file_path in downloaded_files:
        if not src_file_path.is_file():
            logger.warning(f"Source {src_file_path} is not a file or was already moved, skipping.")
            continue
        
        dest_file_path = unified_input_dir / src_file_path.name
        try:
            shutil.move(str(src_file_path), str(dest_file_path)) # [13, 14, 15, 16, 17, 18, 19]
            logger.debug(f"Moved {src_file_path} to {dest_file_path}")
            moved_files_count += 1
        except shutil.Error as e:
            logger.error(f"Error moving {src_file_path} to {dest_file_path}: {e}")
        except FileNotFoundError:
            logger.error(f"Source file {src_file_path} not found for moving. It might have been moved or deleted by another process.")
        except Exception as e: # Catch any other unexpected error during move
            logger.error(f"An unexpected error occurred while moving {src_file_path}: {e}")
            
    logger.info(f"Moved {moved_files_count} files to {unified_input_dir}.")
    if moved_files_count!= len(downloaded_files):
        logger.warning("Not all identified downloaded files were moved. Check logs for details.")


# --- Stage 2: Execute unified_project ---
def execute_unified_project(project_dir: Path, executable_name: str):
    """Executes the unified_project."""
    executable_path = project_dir / executable_name
    if not executable_path.is_file():
        logger.error(f"Executable {executable_path} not found in {project_dir}.")
        raise FileNotFoundError(f"Project executable {executable_path} not found.")

    logger.info(f"Executing unified_project: {executable_path}")
    
    # Determine command based on file type, or make it more configurable
    if executable_path.suffix == '.py':
        command = ['python3', str(executable_path)]
    elif executable_path.suffix == '.sh':
        command = ['bash', str(executable_path)]
    else: 
        command = [str(executable_path)] # For generic executables

    try:
        result = subprocess.run(
            command,
            cwd=str(project_dir),  # Execute from within the project's directory [6]
            capture_output=True,
            text=True,
            check=True # [6, 7, 8]
        )
        logger.info(f"unified_project ({executable_name}) executed successfully.")
        if result.stdout:
            logger.debug(f"unified_project STDOUT:\n{result.stdout.strip()}")
        if result.stderr:
            logger.warning(f"unified_project STDERR:\n{result.stderr.strip()}")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"unified_project ({executable_name}) execution failed. Return code: {e.returncode}")
        logger.error(f"Command: {' '.join(e.cmd)}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout.strip()}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr.strip()}")
        raise
    except FileNotFoundError: # e.g. if 'bash' or 'python3' interpreter not found
        logger.error(f"The script {executable_path} or its interpreter was not found.")
        raise


# --- Stage 3: Process unified_project/output/ ---
def process_unified_project_output(project_output_dir: Path, final_processed_dir: Path):
    """Moves files from unified_project's output to the final processed directory."""
    logger.info(f"Processing output from {project_output_dir} to {final_processed_dir}...")
    
    if not project_output_dir.is_dir():
        logger.warning(f"Project output directory {project_output_dir} does not exist. No files to move.")
        return

    final_processed_dir.mkdir(parents=True, exist_ok=True) # [1, 3, 5, 4]

    # List all files and directories to move. If only files, add f.is_file()
    output_items = list(project_output_dir.iterdir()) # [11, 12]
    
    moved_items_count = 0
    if not output_items:
        logger.info(f"No items found in {project_output_dir} to move.")
        return

    for src_item_path in output_items:
        dest_item_path = final_processed_dir / src_item_path.name
        try:
            shutil.move(str(src_item_path), str(dest_item_path)) # [13, 14, 15, 16, 17, 18, 19]
            logger.debug(f"Moved {src_item_path} to {dest_item_path}")
            moved_items_count += 1
        except shutil.Error as e: # Catches errors like destination already exists and is not a directory
            logger.error(f"Error moving {src_item_path} to {dest_item_path}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while moving {src_item_path}: {e}")
            
    logger.info(f"Moved {moved_items_count} output items to {final_processed_dir}.")
    if moved_items_count!= len(output_items):
        logger.warning("Not all identified output items were moved. Check logs for details.")


# --- Main Orchestration ---
def main():
    # Argument Parsing [20, 21]
    parser = argparse.ArgumentParser(
        description="Automated PDF downloading and processing workflow.",
        prog="automate_workflow" # Sets program name for help messages [20]
    )
    parser.add_argument(
        '--base-url', 
        required=True, 
        help="Base URL for purdue_downloader.py to fetch PDFs from."
    )
    parser.add_argument(
        '--run-id', 
        help="A unique identifier for this workflow run. "
             "Used for creating unique download and processed directories. "
             "Defaults to current timestamp (YYYYMMDD_HHMMSS).",
        default=datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    parser.add_argument(
        '--log-level',
        help="Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL). "
             f"Defaults to value from config or INFO if not set.",
        default=CONFIG_LOG_LEVEL # Use the value loaded from config as default
    )

    args = parser.parse_args()

    # Setup Logging
    setup_logging(log_level_str=args.log_level, log_file=LOG_FILE_PATH)

    logger.info(f"Starting automated workflow for run ID: {args.run_id} with base URL: {args.base_url}")

    # Define key directories
    # original_download_location is where purdue_downloader saves files initially.
    # It's unique per run_id.
    original_download_location = BASE_SCRIPT_DIR / DEFAULT_DOWNLOAD_BASE_DIR_NAME / args.run_id # [22, 23, 24]
    
    unified_input_dir = UNIFIED_PROJECT_DIR / 'input'
    unified_output_dir = UNIFIED_PROJECT_DIR / 'output'
    
    # final_processed_dir is inside the original_download_location, in a 'processed' subfolder
    final_processed_dir = original_download_location / 'processed'

    try:
        logger.info(f"Using Purdue downloader script: {PURDUE_DOWNLOADER_SCRIPT_PATH}")
        logger.info(f"Using Unified Project directory: {UNIFIED_PROJECT_DIR}")
        logger.info(f"Unified Project executable: {UNIFIED_PROJECT_EXECUTABLE_NAME}")
        logger.info(f"Initial download location for this run: {original_download_location}")
        logger.info(f"Unified Project input directory: {unified_input_dir}")
        logger.info(f"Unified Project output directory: {unified_output_dir}")
        logger.info(f"Final processed output location for this run: {final_processed_dir}")

        # Ensure the base directory for this run's downloads exists
        original_download_location.mkdir(parents=True, exist_ok=True) # [1, 3, 5, 4]
        logger.info(f"Ensured base download directory exists: {original_download_location}")

        # --- Stage 1: Download PDFs ---
        logger.info("--- Stage 1: Downloading PDFs ---")
        downloaded_files = run_purdue_downloader(args.base_url, original_download_location, PURDUE_DOWNLOADER_SCRIPT_PATH)
        
        if not downloaded_files:
            logger.warning("No files were downloaded by purdue_downloader.py. "
                           "Proceeding, but unified_project may not have input.")
            # Depending on requirements, you might choose to exit here:
            # logger.info("Exiting workflow as no files were downloaded.")
            # sys.exit(0) # Or sys.exit(1) if this is an error condition

        # --- Stage 1.5: Prepare input for unified_project ---
        logger.info("--- Stage 1.5: Preparing input for Unified Project ---")
        prepare_unified_project_input(downloaded_files, unified_input_dir)

        # --- Stage 2: Execute unified_project ---
        logger.info("--- Stage 2: Executing Unified Project ---")
        execute_unified_project(UNIFIED_PROJECT_DIR, UNIFIED_PROJECT_EXECUTABLE_NAME)

        # --- Stage 3: Process output from unified_project ---
        logger.info("--- Stage 3: Processing Unified Project Output ---")
        process_unified_project_output(unified_output_dir, final_processed_dir)

        logger.info(f"Workflow completed successfully for run ID: {args.run_id}.")

    except subprocess.CalledProcessError as e:
        # Already logged in detail by the helper functions, but main can add context
        logger.critical(f"A critical subprocess failed during workflow for run ID {args.run_id}. See logs for details. Aborting.")
        sys.exit(1) # Indicate failure
    except FileNotFoundError as e:
        logger.critical(f"A required file or directory was not found: {e.filename}. Aborting workflow for run ID {args.run_id}.")
        sys.exit(1)
    except Exception as e: # Catch-all for other unexpected errors [25, 26]
        logger.exception(f"An unexpected error occurred during the workflow for run ID {args.run_id}. Aborting.") #.exception includes traceback [27, 28]
        sys.exit(1)
    finally: # [25, 26]
        logger.info(f"Workflow execution finished for run ID: {args.run_id}.")

# --- Script Entry Point ---
if __name__ == "__main__": # [29]
    main()
