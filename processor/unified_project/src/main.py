#!/usr/bin/env python3
"""
Unified CLI interface for the ePubs Accessibility Enhancement Project.
"""

import logging
import typer
from pathlib import Path

from processor.unified_project.src.services.enhancement_service import EnhancementService

app = typer.Typer(
    help="ePubs Accessibility Enhancement Tool: A unified CLI for enhancing document accessibility."
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
def process(
    input_path: Path = typer.Argument(
        ..., help="Path to the input PDF file.", exists=True, file_okay=True, dir_okay=False
    ),
    output_path: Path = typer.Argument(
        ..., help="Path to the output PDF file.", writable=True
    ),
    mode: str = typer.Option(
        "academic", help="Processing mode ('academic', 'basic', etc.)."
    ),
    title: str = typer.Option(None, help="Set the document title."),
    author: str = typer.Option(None, help="Set the document author."),
    language: str = typer.Option("en-US", help="Set the document language."),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
):
    """
    Process a single PDF file to perform OCR and enhance its accessibility.
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    logger.info(f"Starting processing for: {input_path}")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    enhancement_service = EnhancementService()

    # Prepare keyword arguments for the service
    enhancement_kwargs = {
        "title": title,
        "author": author,
        "language": language,
    }

    success = enhancement_service.enhance_document(
        input_path, output_path, mode=mode, **enhancement_kwargs
    )

    if success:
        logger.info(f"Successfully processed file and saved to: {output_path}")
        raise typer.Exit(code=0)
    else:
        logger.error(f"Failed to process file: {input_path}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()