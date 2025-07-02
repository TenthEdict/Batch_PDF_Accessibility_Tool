#!/usr/bin/env python3
"""
CLI for processing all PDF files in a directory.
"""

import logging
import typer
from pathlib import Path
import time


from processor.unified_project.src.services.enhancement_service import EnhancementService

app = typer.Typer(
    help="ePubs Accessibility Enhancement Tool: A CLI for batch-processing PDFs in a directory."
)

def setup_logging(verbose: bool):
    """Sets up logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Reduce verbosity of noisy libraries
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("ocrmypdf").setLevel(logging.WARNING)


@app.command()
def process_directory(
    input_dir: Path = typer.Argument(
        ..., help="Path to the directory containing input PDF files.", exists=True, file_okay=False, dir_okay=True, readable=True
    ),
    output_dir: Path = typer.Argument(
        ..., help="Path to the directory where output PDF files will be saved.", file_okay=False, dir_okay=True, writable=True
    ),
    mode: str = typer.Option(
        "academic", help="Processing mode ('academic', 'basic', etc.)."
    ),
    language: str = typer.Option("en-US", help="Set the document language for all files."),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """
    Process all PDF files in a directory to perform OCR and enhance accessibility.
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    logger.info(f"Starting batch processing for directory: {input_dir}")

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all PDF files in the input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}. Exiting.")
        raise typer.Exit(code=0)

    total_files = len(pdf_files)
    logger.info(f"Found {total_files} PDF files to process.")

    enhancement_service = EnhancementService()
    
    success_count = 0
    failure_count = 0
    start_time = time.time()

    for index, input_path in enumerate(pdf_files):
        output_path = output_dir / input_path.name
        logger.info(f"Processing file {index + 1}/{total_files}: {input_path.name}")

        # Prepare keyword arguments for the service
        enhancement_kwargs = {
            "language": language,
            # Title and author are not set in batch mode, 
            # as they are typically document-specific.
        }

        try:
            success = enhancement_service.enhance_document(
                input_path, output_path, mode=mode, **enhancement_kwargs
            )
            if success:
                logger.info(f"Successfully processed and saved to: {output_path}")
                success_count += 1
            else:
                logger.error(f"Failed to process file: {input_path}")
                failure_count += 1
        except Exception as e:
            logger.critical(f"An unexpected error occurred while processing {input_path}: {e}", exc_info=True)
            failure_count += 1

    end_time = time.time()
    total_time = end_time - start_time

    logger.info("==================== Batch Processing Summary ====================")
    logger.info(f"Total files found: {total_files}")
    logger.info(f"Successfully processed: {success_count}")
    logger.info(f"Failed to process: {failure_count}")
    logger.info(f"Total processing time: {total_time:.2f} seconds")
    logger.info("================================================================")

    if failure_count > 0:
        raise typer.Exit(code=1)
    else:
        raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
