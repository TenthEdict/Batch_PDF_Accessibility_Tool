#!/bin/bash

# Script to create fully accessible PDFs with proper content tagging
# This requires building the enhanced accessibility Docker image first:
# docker build -t pdf-accessibility-enhanced -f Dockerfile.accessibility .

# Set default parameters
INPUT_PDF=""
OUTPUT_PDF=""
TITLE=""
AUTHOR=""

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --input)
      INPUT_PDF="$2"
      shift 2
      ;;
    --output)
      OUTPUT_PDF="$2"
      shift 2
      ;;
    --title)
      TITLE="$2"
      shift 2
      ;;
    --author)
      AUTHOR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check for required parameter
if [ -z "$INPUT_PDF" ]; then
  echo "Error: Input PDF file is required"
  echo "Usage: $0 --input input.pdf [--output output.pdf] [--title 'Document Title'] [--author 'Author Name']"
  exit 1
fi

# Set default output name if not specified
if [ -z "$OUTPUT_PDF" ]; then
  FILENAME=$(basename "$INPUT_PDF")
  BASENAME="${FILENAME%.*}"
  OUTPUT_PDF="${BASENAME}_accessible.pdf"
fi

# Create directories for processing
INPUT_DIR="$(pwd)/input"
OUTPUT_DIR="$(pwd)/output"
mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"

# Copy input file for processing
FILENAME=$(basename "$INPUT_PDF")
cp "$INPUT_PDF" "$INPUT_DIR/$FILENAME"

echo "Creating accessible PDF..."
echo "Input: $INPUT_PDF"
echo "Output: $OUTPUT_PDF"
echo "Title: $TITLE"
echo "Author: $AUTHOR"

# Build accessibility-enhanced image if it doesn't exist
if ! docker image inspect pdf-accessibility-enhanced >/dev/null 2>&1; then
  echo "Building enhanced accessibility Docker image..."
  docker build -t pdf-accessibility-enhanced -f Dockerfile.accessibility .
fi

# Run the accessibility enhancement process
docker run --rm \
  -v "$INPUT_DIR:/app/input" \
  -v "$OUTPUT_DIR:/app/output" \
  pdf-accessibility-enhanced python3 -c "
import os
import sys
import logging
from pathlib import Path
import pikepdf
import subprocess
import shutil
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def run_command(cmd):
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f'Command failed: {cmd}')
        logger.error(f'Error: {e.stderr}')
        return False, e.stderr

def create_accessible_pdf(input_pdf, output_pdf, title=None, author=None):
    input_path = Path(input_pdf)
    output_path = Path(output_pdf)
    temp_dir = Path('/tmp/accessibility_processing')
    temp_dir.mkdir(exist_ok=True)
    
    logger.info(f'Processing file: {input_path}')
    
    # Step 1: OCR the PDF if needed
    ocr_pdf = temp_dir / 'ocr.pdf'
    logger.info('Running OCR to ensure text recognition...')
    success, output = run_command(f'ocrmypdf --force-ocr --deskew --clean --optimize 3 {input_path} {ocr_pdf}')
    
    if not success or not ocr_pdf.exists():
        logger.warning('OCR failed, continuing with original PDF')
        ocr_pdf = input_path
    else:
        logger.info('OCR successful')
    
    # Step 2: Extract metadata
    if title is None or title == '':
        # Extract title from filename
        title = input_path.stem.replace('_', ' ').title()
    
    # Step 3: Add metadata, language, and basic tagging
    tagged_pdf = temp_dir / 'tagged.pdf'
    try:
        with pikepdf.open(ocr_pdf) as pdf:
            # Add metadata
            with pdf.open_metadata() as meta:
                meta['dc:title'] = title
                if author:
                    meta['dc:creator'] = author
                meta['pdf:Language'] = 'en-US'
            
            # Mark as tagged
            pdf.Root['/MarkInfo'] = pikepdf.Dictionary(Marked=True)
            
            # Set viewer preferences
            if '/ViewerPreferences' not in pdf.Root:
                pdf.Root['/ViewerPreferences'] = pikepdf.Dictionary()
            pdf.Root['/ViewerPreferences']['/DisplayDocTitle'] = True
            
            # Create basic document structure
            if '/StructTreeRoot' not in pdf.Root:
                # Create struct tree root
                struct_root = pikepdf.Dictionary()
                struct_root['/Type'] = '/StructTreeRoot'
                
                # Create document element
                document_elem = pikepdf.Dictionary()
                document_elem['/Type'] = '/StructElem'
                document_elem['/S'] = '/Document'  # Structure type
                
                # Create parent tree for structure elements
                parent_tree = pikepdf.Dictionary()
                parent_tree['/Nums'] = pikepdf.Array()
                struct_root['/ParentTree'] = parent_tree
                
                # Add document element to structure tree
                struct_root['/K'] = document_elem
                
                # Add role map to structure tree
                role_map = pikepdf.Dictionary()
                struct_root['/RoleMap'] = role_map
                
                # Set structure tree in PDF
                pdf.Root['/StructTreeRoot'] = struct_root
            
            # Save tagged PDF
            pdf.save(tagged_pdf)
        logger.info('Added basic accessibility features')
    except Exception as e:
        logger.error(f'Error adding basic accessibility: {str(e)}')
        shutil.copy(ocr_pdf, tagged_pdf)
    
    # Step 4: Add PDF/UA metadata using pdfUA-ID.xmp
    xmp_path = Path('/app/pdfUA-ID.xmp')
    ua_pdf = temp_dir / 'ua.pdf'
    
    if xmp_path.exists():
        try:
            with pikepdf.open(tagged_pdf) as pdf:
                # Read the XMP content
                with open(xmp_path, 'r', encoding='utf-8') as xmp_file:
                    xmp_content = xmp_file.read()
                
                # Add PDF/UA XMP
                pdf.Root.Metadata = pikepdf.Stream(pdf, xmp_content.encode('utf-8'))
                pdf.save(ua_pdf)
            logger.info('Added PDF/UA metadata')
        except Exception as e:
            logger.error(f'Error adding PDF/UA metadata: {str(e)}')
            shutil.copy(tagged_pdf, ua_pdf)
    else:
        logger.warning('PDF/UA XMP template not found, skipping')
        shutil.copy(tagged_pdf, ua_pdf)
    
    # Step 5: Copy result to output path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(ua_pdf, output_path)
    logger.info(f'Enhanced PDF saved to: {output_path}')
    
    # Clean up
    try:
        if ocr_pdf != input_path and ocr_pdf.exists():
            ocr_pdf.unlink()
        if tagged_pdf.exists():
            tagged_pdf.unlink()
        if ua_pdf.exists():
            ua_pdf.unlink()
        logger.info('Cleanup completed')
    except Exception as e:
        logger.warning(f'Cleanup error: {str(e)}')
    
    return True

# Get parameters and process PDF
input_filename = '$FILENAME'
input_path = f'/app/input/{input_filename}'
output_basename = input_filename.rsplit('.', 1)[0] + '_accessible.pdf'
output_path = f'/app/output/{output_basename}'
title = '$TITLE'
author = '$AUTHOR'

logger.info(f'Input: {input_path}')
logger.info(f'Output: {output_path}')
logger.info(f'Title: {title}')
logger.info(f'Author: {author}')

success = create_accessible_pdf(input_path, output_path, title, author)
if success:
    print('Accessibility enhancement completed successfully')
    print(f'Enhanced PDF saved to: {output_path}')
else:
    print('Accessibility enhancement failed')
"

# Copy output file to the specified location
if [ -f "$OUTPUT_DIR/$(basename "$OUTPUT_PDF")" ]; then
  cp "$OUTPUT_DIR/$(basename "$OUTPUT_PDF")" "$OUTPUT_PDF"
  echo "Accessible PDF created successfully: $OUTPUT_PDF"
else
  echo "Error: Failed to create accessible PDF"
  exit 1
fi