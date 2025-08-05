#!/bin/bash
# ePubs_Main Workflow Script
# This script automates the entire workflow of downloading documents with scraper,
# processing them with processor, and returning them to their original directories.

set -e  # Exit on any error

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup logging
LOG_DIR="${REPO_ROOT}/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/workflow_$(date +%Y%m%d_%H%M%S).log"

# Function to log messages to both console and log file
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    # Write to log file with timestamp and level
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    # Only INFO, SUCCESS, WARNING, and ERROR messages go to console
    if [[ "$level" == "INFO" || "$level" == "SUCCESS" || "$level" == "WARNING" || "$level" == "ERROR" ]]; then
        # Format console output with colors
        case "$level" in
            "INFO")    echo -e "\033[0;34m[INFO]\033[0m $message" ;;
            "SUCCESS") echo -e "\033[0;32m[SUCCESS]\033[0m $message" ;;
            "WARNING") echo -e "\033[0;33m[WARNING]\033[0m $message" ;;
            "ERROR")   echo -e "\033[0;31m[ERROR]\033[0m $message" ;;
        esac
    fi
}

# Function to run commands and log output
run_cmd() {
    local cmd="$1"
    local desc="$2"
    local log_prefix="$3"
    
    log "DEBUG" "Running command: $cmd"
    log "INFO" "$desc"
    
    # Run the command and capture output
    local output
    if ! output=$(eval "$cmd" 2>&1); then
        log "ERROR" "Command failed: $cmd"
        log "ERROR" "Output: $output"
        echo "$output" >> "$LOG_FILE"
        return 1
    fi
    
    # Log output with prefix for easier log parsing
    while IFS= read -r line; do
        log "DEBUG" "[$log_prefix] $line"
    done <<< "$output"
    
    return 0
}

# Make sure Python virtual environment is available
if [ ! -d "${REPO_ROOT}/venv" ]; then
    log "INFO" "Creating Python virtual environment..."
    python3 -m venv "${REPO_ROOT}/venv" >> "$LOG_FILE" 2>&1
    source "${REPO_ROOT}/venv/bin/activate"
    log "DEBUG" "Installing requirements..."
    pip install -r "${REPO_ROOT}/requirements.txt" >> "$LOG_FILE" 2>&1
    pip install -r "${REPO_ROOT}/processor/unified_project/requirements.txt" >> "$LOG_FILE" 2>&1
    log "SUCCESS" "Virtual environment created and dependencies installed"
else
    source "${REPO_ROOT}/venv/bin/activate"
    
    # Check if selenium is installed, if not install requirements
    if ! python -c "import selenium" &>/dev/null; then
        log "INFO" "Installing required dependencies..."
        pip install -r "${REPO_ROOT}/requirements.txt" >> "$LOG_FILE" 2>&1
        log "SUCCESS" "Dependencies installed"
    fi
fi

# Function to display usage
function show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  --url URL              URL to download documents from"
    echo "  --file FILE            Text file containing URLs to download from"
    echo "  --workers N            Number of worker threads for processing (default: 1)"
    echo "  --username USERNAME    Username for Purdue authentication"
    echo "                         (if not provided, will try to read from credentials.txt file"
    echo "                          or prompt interactively)"
    echo "  --password PASSWORD    Password for Purdue authentication"
    echo "                         (if not provided, will try to read from credentials.txt file"
    echo "                          or prompt interactively for secure entry)"
    echo "  --skip-download        Skip the download step and process existing files"
    echo "                         (still requires --url or --file to determine which directories to process)"
    echo "  --verbose              Show more detailed output in the terminal"
    echo "  --quiet                Show only success, warning, and error messages in the terminal"
    echo "                         (all logs are still saved to the log file)"
    echo "  --help                 Display this help message"
    echo ""
    echo "EXAMPLES:"
    echo "  $0 --url https://docs.lib.purdue.edu/modvis/2024/"
    echo "  $0 --file urls.txt --workers 2"
    echo "  $0 --skip-download --url https://docs.lib.purdue.edu/biopub/ --workers 4"
    echo "  $0 --file urls.txt --quiet  # Run with minimal console output"
    echo ""
    echo "Log files are saved in: ${LOG_DIR}"
}

# Default values
WORKERS=1
SKIP_DOWNLOAD=false
SEARCH_DIRS=()
VERBOSE=false
QUIET=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --url)
            URL="$2"
            shift 2
            ;;
        --file)
            FILE="$2"
            shift 2
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --username)
            USERNAME="$2"
            shift 2
            ;;
        --password)
            PASSWORD="$2"
            shift 2
            ;;
        --skip-download)
            SKIP_DOWNLOAD=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --quiet)
            QUIET=true
            shift
            ;;
        --search-dir)
            SEARCH_DIRS+=("$2")
            shift 2
            ;;
        --series)
            # Convert series name to search path
            SERIES="$2"
            if [[ $SERIES =~ ^[a-zA-Z] ]]; then
                FIRST_CHAR=$(echo "${SERIES:0:1}" | tr '[:upper:]' '[:lower:]')
                SEARCH_PATH="/mnt/s/Departments/ePubs/Accessibility_Project/${FIRST_CHAR}_series/${SERIES}"
                SEARCH_DIRS+=("$SEARCH_PATH")
            fi
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Override log function based on verbosity mode
if [ "$VERBOSE" = true ]; then
    # In verbose mode, all log levels go to console
    log() {
        local level="$1"
        local message="$2"
        local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
        
        # Write to log file with timestamp and level
        echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
        
        # In verbose mode, all log levels go to console
        case "$level" in
            "DEBUG")   echo -e "\033[0;36m[DEBUG]\033[0m $message" ;;
            "INFO")    echo -e "\033[0;34m[INFO]\033[0m $message" ;;
            "SUCCESS") echo -e "\033[0;32m[SUCCESS]\033[0m $message" ;;
            "WARNING") echo -e "\033[0;33m[WARNING]\033[0m $message" ;;
            "ERROR")   echo -e "\033[0;31m[ERROR]\033[0m $message" ;;
            *)         echo -e "[$level] $message" ;;
        esac
    }
elif [ "$QUIET" = true ]; then
    # In quiet mode, only SUCCESS, WARNING, and ERROR go to console
    log() {
        local level="$1"
        local message="$2"
        local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
        
        # Write to log file with timestamp and level
        echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
        
        # In quiet mode, only SUCCESS, WARNING, and ERROR go to console
        case "$level" in
            "SUCCESS") echo -e "\033[0;32m[SUCCESS]\033[0m $message" ;;
            "WARNING") echo -e "\033[0;33m[WARNING]\033[0m $message" ;;
            "ERROR")   echo -e "\033[0;31m[ERROR]\033[0m $message" ;;
        esac
    }
fi

# Check required arguments
if [ -z "$URL" ] && [ -z "$FILE" ]; then
    log "ERROR" "Either --url or --file must be specified (even when using --skip-download)."
    log "ERROR" "The URL or file is needed to determine which directories to process."
    show_usage
    exit 1
fi

# Temporary directory for intermediary files
TEMP_DIR="${REPO_ROOT}/temp_processing"
mkdir -p "${TEMP_DIR}/input"
mkdir -p "${TEMP_DIR}/output"

log "INFO" "============================================================"
log "INFO" "ePubs Workflow Automation"
log "INFO" "============================================================"
log "DEBUG" "Repository root: ${REPO_ROOT}"
log "DEBUG" "Log file: ${LOG_FILE}"

# Step 1: Download documents with scraper
DOWNLOADED_DIRS=()
DETECTED_SERIES=()

if [ "$SKIP_DOWNLOAD" = false ]; then
    log "INFO" "Step 1: Downloading documents..."
    
    # Check for credentials file and read from it if it exists
    CREDENTIALS_FILE="${REPO_ROOT}/credentials.txt"
    if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
        if [ -f "$CREDENTIALS_FILE" ]; then
            log "INFO" "Reading credentials from credentials.txt file"
            # Read first line as username, second line as password
            # Extract the values after the label (if present)
            USERNAME=$(sed -n '1p' "$CREDENTIALS_FILE" | sed -E 's/^USERNAME:\s*(.*)$/\1/' | tr -d '\r')
            PASSWORD=$(sed -n '2p' "$CREDENTIALS_FILE" | sed -E 's/^PASSWORD:\s*(.*)$/\1/' | tr -d '\r')
            
            if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
                log "DEBUG" "Successfully read credentials from file"
            else
                log "WARNING" "Could not read valid credentials from credentials.txt"
            fi
        else
            log "DEBUG" "No credentials.txt file found at ${CREDENTIALS_FILE}"
        fi
    fi
    
    # Prompt for credentials if still not available
    if [ -z "$USERNAME" ]; then
        log "INFO" "No username provided. Please enter your Purdue username:"
        read -p "Username: " USERNAME
        log "DEBUG" "Username entered from prompt"
    fi
    
    if [ -z "$PASSWORD" ]; then
        log "INFO" "No password provided. Please enter your Purdue password:"
        read -s -p "Password: " PASSWORD
        echo  # Add a newline after password input
        log "DEBUG" "Password entered from prompt"
    fi
    
    # Prepare scraper command
    SCRAPER_CMD="python3 -m scraper.purdue_downloader"
    
    # Extract series from URL or file contents
    if [ -n "$URL" ]; then
        SCRAPER_CMD="${SCRAPER_CMD} --url ${URL}"
        
        # Extract the series from the URL to determine search path
        SERIES=$(echo "$URL" | sed -E 's|^https?://[^/]+/([^/]+).*|\1|')
        
        # Determine the series prefix based on the first character
        if [[ $SERIES =~ ^[a-zA-Z] ]]; then
            FIRST_CHAR=$(echo "${SERIES:0:1}" | tr '[:upper:]' '[:lower:]')
            SEARCH_PATH="/mnt/s/Departments/ePubs/Accessibility_Project/${FIRST_CHAR}_series/${SERIES}"
            DOWNLOADED_DIRS+=("$SEARCH_PATH")
            DETECTED_SERIES+=("$SERIES")
            log "DEBUG" "Will search for PDFs in series: $SERIES"
        fi
    elif [ -n "$FILE" ]; then
        SCRAPER_CMD="${SCRAPER_CMD} --file ${FILE}"
        
        # For a file with URLs, extract all possible series for search
        if [ -f "$FILE" ]; then
            log "DEBUG" "Extracting series from URL file: $FILE"
            while read -r line; do
                if [[ "$line" == http* ]]; then
                    SERIES=$(echo "$line" | sed -E 's|^https?://[^/]+/([^/]+).*|\1|')
                    if [[ $SERIES =~ ^[a-zA-Z] ]]; then
                        FIRST_CHAR=$(echo "${SERIES:0:1}" | tr '[:upper:]' '[:lower:]')
                        SEARCH_PATH="/mnt/s/Departments/ePubs/Accessibility_Project/${FIRST_CHAR}_series/${SERIES}"
                        DOWNLOADED_DIRS+=("$SEARCH_PATH")
                        DETECTED_SERIES+=("$SERIES")
                        log "DEBUG" "Will search for PDFs in series: $SERIES"
                    fi
                fi
            done < "$FILE"
        fi
    fi
    
    # Always include username and password if they are set (either from args or prompt)
    if [ -n "$USERNAME" ]; then
        SCRAPER_CMD="${SCRAPER_CMD} --username \"${USERNAME}\""
        log "DEBUG" "Using provided username for authentication"
    fi
    
    if [ -n "$PASSWORD" ]; then
        SCRAPER_CMD="${SCRAPER_CMD} --password \"${PASSWORD}\""
        log "DEBUG" "Using provided password for authentication"
    else
        log "WARNING" "No password provided. Authentication may fail."
    fi
    
    # Run the scraper from the repository root
    log "INFO" "Starting download for ${#DETECTED_SERIES[@]} series: ${DETECTED_SERIES[*]}"
    cd "${REPO_ROOT}"
    
    # Run scraper with output redirected to log file but preserve any errors to console
    log "DEBUG" "Running command: ${SCRAPER_CMD}"
    
    # Execute scraper command with proper handling based on quiet mode
    if [ "$QUIET" = true ]; then
        # In quiet mode, redirect all output to log file only
        if ! eval "${SCRAPER_CMD}" >> "$LOG_FILE" 2>> "$LOG_FILE"; then
            log "ERROR" "Download step failed. Check log for details: $LOG_FILE"
            exit 1
        fi
    else
        # In normal or verbose mode, preserve errors to console
        if ! eval "${SCRAPER_CMD}" >> "$LOG_FILE" 2> >(tee -a "$LOG_FILE" >&2); then
            log "ERROR" "Download step failed. Check log for details: $LOG_FILE"
            exit 1
        fi
    fi
    
    log "SUCCESS" "Download step completed successfully"
else
    log "INFO" "Skipping download step as requested"
    
    # Even when skipping download, use the URL or file to determine search paths
    if [ -n "$URL" ]; then
        # Extract the series from the URL to determine search path
        SERIES=$(echo "$URL" | sed -E 's|^https?://[^/]+/([^/]+).*|\1|')
        
        # Determine the series prefix based on the first character
        if [[ $SERIES =~ ^[a-zA-Z] ]]; then
            FIRST_CHAR=$(echo "${SERIES:0:1}" | tr '[:upper:]' '[:lower:]')
            SEARCH_PATH="/mnt/s/Departments/ePubs/Accessibility_Project/${FIRST_CHAR}_series/${SERIES}"
            DOWNLOADED_DIRS+=("$SEARCH_PATH")
            DETECTED_SERIES+=("$SERIES")
            log "INFO" "Will search for PDFs in series: $SERIES"
        fi
    elif [ -n "$FILE" ]; then
        # For a file with URLs, extract all possible series for search
        if [ -f "$FILE" ]; then
            log "DEBUG" "Extracting series from URL file: $FILE"
            while read -r line; do
                if [[ "$line" == http* ]]; then
                    SERIES=$(echo "$line" | sed -E 's|^https?://[^/]+/([^/]+).*|\1|')
                    if [[ $SERIES =~ ^[a-zA-Z] ]]; then
                        FIRST_CHAR=$(echo "${SERIES:0:1}" | tr '[:upper:]' '[:lower:]')
                        SEARCH_PATH="/mnt/s/Departments/ePubs/Accessibility_Project/${FIRST_CHAR}_series/${SERIES}"
                        DOWNLOADED_DIRS+=("$SEARCH_PATH")
                        DETECTED_SERIES+=("$SERIES")
                        log "DEBUG" "Will search for PDFs in series: $SERIES"
                    fi
                fi
            done < "$FILE"
            
            log "INFO" "Found ${#DETECTED_SERIES[@]} series in file: ${DETECTED_SERIES[*]}"
        fi
    fi
    
    # If no valid series was found from URL or file, issue a warning
    if [ ${#DOWNLOADED_DIRS[@]} -eq 0 ]; then
        log "ERROR" "No valid series found from provided URL or file."
        log "ERROR" "Cannot determine which directories to search. Please provide a valid URL or file."
        exit 1
    fi
fi

# Step 2: Find PDFs to process, but only in the directories that were updated during download
log "INFO" "Step 2: Finding PDFs to process..."

# Default location is S: drive structure, where scraper saves files
S_DRIVE_PATH="/mnt/s/Departments/ePubs/Accessibility_Project"

if [ ! -d "$S_DRIVE_PATH" ]; then
    log "WARNING" "S: drive structure not found at $S_DRIVE_PATH"
    log "INFO" "Checking if S: drive needs to be mounted..."
    
    # Try to mount the S: drive if in WSL
    if grep -q Microsoft /proc/version; then
        log "INFO" "WSL environment detected. Attempting to mount S: drive..."
        if [ ! -d "/mnt/s" ]; then
            sudo mkdir -p /mnt/s
        fi
        sudo mount -t drvfs S: /mnt/s
        
        if [ ! -d "$S_DRIVE_PATH" ]; then
            log "ERROR" "Failed to find S: drive structure even after mounting attempt."
            exit 1
        else
            log "SUCCESS" "S: drive mounted successfully."
        fi
    else
        log "ERROR" "S: drive structure not found and not running in WSL."
        exit 1
    fi
fi

# If no specific directories were identified, search the entire structure
if [ ${#DOWNLOADED_DIRS[@]} -eq 0 ]; then
    log "WARNING" "No specific directories identified, searching entire structure..."
    DOWNLOADED_DIRS+=("$S_DRIVE_PATH")
fi

# Find all PDF files in the specific directories that don't have a processed version
FOUND_PDFS=()
SERIES_PDF_COUNTS=()

for search_dir in "${DOWNLOADED_DIRS[@]}"; do
    log "DEBUG" "Searching for unprocessed PDFs in: $search_dir"
    
    # Count PDFs found in this directory
    count=0
    
    while IFS= read -r -d '' pdf_file; do
        # Check if this PDF already has a processed version
        original_dir=$(dirname "$pdf_file")
        processed_dir="${original_dir}/processed"
        pdf_filename=$(basename "$pdf_file")
        processed_pdf="${processed_dir}/${pdf_filename}"
        
        if [ ! -f "$processed_pdf" ]; then
            FOUND_PDFS+=("$pdf_file")
            count=$((count + 1))
        fi
    done < <(find "$search_dir" -type f -name "*.pdf" -not -path "*/processed/*" -print0 2>/dev/null)
    
    # Extract series name from search_dir for better reporting
    series_name=$(basename "$search_dir")
    SERIES_PDF_COUNTS+=("$series_name:$count")
    
    log "DEBUG" "Found $count unprocessed PDFs in $series_name"
done

PDF_COUNT=${#FOUND_PDFS[@]}
log "INFO" "Found $PDF_COUNT unprocessed PDFs across ${#DETECTED_SERIES[@]} series"

# Display breakdown by series
for series_count in "${SERIES_PDF_COUNTS[@]}"; do
    IFS=':' read -r series count <<< "$series_count"
    if [ "$count" -gt 0 ]; then
        log "INFO" "  - $series: $count PDFs"
    fi
done

if [ $PDF_COUNT -eq 0 ]; then
    log "INFO" "No unprocessed PDFs found. Exiting."
    exit 0
fi

# Step 3: Copy PDFs to temporary input directory for processing
log "INFO" "Step 3: Preparing PDFs for processing..."

# Clear existing files in temp directories
rm -rf "${TEMP_DIR}/input"/*
rm -rf "${TEMP_DIR}/output"/*
mkdir -p "${TEMP_DIR}/input"
mkdir -p "${TEMP_DIR}/output"

# Create a mapping file to track original locations
MAPPING_FILE="${TEMP_DIR}/file_mapping.txt"
rm -f "$MAPPING_FILE"
touch "$MAPPING_FILE"

# Progress tracking
prepared_count=0

for pdf_file in "${FOUND_PDFS[@]}"; do
    # Create a unique filename to avoid collisions
    pdf_filename=$(basename "$pdf_file")
    unique_name="$(date +%s%N)_${pdf_filename}"
    dest_path="${TEMP_DIR}/input/${unique_name}"
    
    # Copy file to temp directory
    cp "$pdf_file" "$dest_path"
    
    # Store the mapping for later use
    echo "${unique_name}|${pdf_file}" >> "$MAPPING_FILE"
    
    # Update progress counter
    prepared_count=$((prepared_count + 1))
    
    # Show progress only for larger batches or in verbose mode
    if [ "$VERBOSE" = true ] || [ $((prepared_count % 10)) -eq 0 ] || [ $prepared_count -eq $PDF_COUNT ]; then
        log "DEBUG" "Prepared $prepared_count/$PDF_COUNT PDFs for processing"
    fi
done

log "SUCCESS" "All PDFs prepared for processing"

# Step 4: Process PDFs with the processor
log "INFO" "Step 4: Processing PDFs for accessibility..."

# Run the processor in batch mode
cd "${REPO_ROOT}"
process_cmd="python3 -u ./processor/process_academic_local.py --batch --max-workers $WORKERS ${TEMP_DIR}/input ${TEMP_DIR}/output"

log "DEBUG" "Running processor command: $process_cmd"

# Execute processor command with proper handling based on quiet mode
if [ "$QUIET" = true ]; then
    # In quiet mode, redirect all output to log file only
    if ! eval "$process_cmd" >> "$LOG_FILE" 2>> "$LOG_FILE"; then
        log "ERROR" "Processing step failed. Check log for details: $LOG_FILE"
        exit 1
    fi
else
    # In normal or verbose mode, preserve errors to console
    if ! eval "$process_cmd" >> "$LOG_FILE" 2> >(tee -a "$LOG_FILE" >&2); then
        log "ERROR" "Processing step failed. Check log for details: $LOG_FILE"
        exit 1
    fi
fi

log "SUCCESS" "Processing completed successfully"

# Step 5: Move processed files back to their original locations
log "INFO" "Step 5: Moving processed files to their original locations..."

# Read the mapping file and move processed files back
processed_count=0
failed_count=0

while IFS="|" read -r unique_name original_path; do
    if [ -z "$unique_name" ] || [ -z "$original_path" ]; then
        continue
    fi
    
    processed_file="${TEMP_DIR}/output/${unique_name}"
    
    if [ -f "$processed_file" ]; then
        # Get the original directory and create processed subdirectory
        original_dir=$(dirname "$original_path")
        processed_dir="${original_dir}/processed"
        mkdir -p "$processed_dir"
        
        # Move the processed file to the processed subdirectory
        original_filename=$(basename "$original_path")
        cp "$processed_file" "${processed_dir}/${original_filename}"
        
        log "DEBUG" "Moved processed file to: ${processed_dir}/${original_filename}"
        processed_count=$((processed_count + 1))
        
        # Show progress for larger batches
        if [ $((processed_count % 10)) -eq 0 ] || [ $processed_count -eq $PDF_COUNT ]; then
            log "DEBUG" "Moved $processed_count/$PDF_COUNT processed files"
        fi
    else
        log "WARNING" "Processed file not found for $unique_name"
        failed_count=$((failed_count + 1))
    fi
done < "$MAPPING_FILE"

# Final summary
log "INFO" "============================================================"
log "SUCCESS" "Workflow completed successfully!"
log "INFO" "============================================================"
log "INFO" "Summary:"
log "INFO" "- Processed $PDF_COUNT PDFs across ${#DETECTED_SERIES[@]} series"
log "INFO" "- Successfully processed and moved: $processed_count files"
if [ $failed_count -gt 0 ]; then
    log "WARNING" "- Failed to process: $failed_count files"
fi
log "INFO" "- Processed files placed in 'processed/' subdirectories within original locations"
log "INFO" "- Log file: $LOG_FILE"

# Show series breakdown in summary
for series_count in "${SERIES_PDF_COUNTS[@]}"; do
    IFS=':' read -r series count <<< "$series_count"
    if [ "$count" -gt 0 ]; then
        log "INFO" "  - $series: $count PDFs"
    fi
done

log "INFO" "To process more files, run this script again."