#!/usr/bin/env python3
"""
Simplified CLI for ePubs PDF Accessibility Enhancement.

This CLI provides basic PDF processing with:
- Single file processing
- Batch processing with folder structure preservation
- Simple configuration options
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

# Import simplified services
from src.processor.simple_enhancement_service import SimpleEnhancementService
from src.processor.simple_batch_processor import SimpleBatchProcessor

# Create Typer app
app = typer.Typer(
    name="epubs-simple",
    help="Simplified PDF Accessibility Enhancement Tool",
    add_completion=False
)

console = Console()


def setup_logging(verbose: bool = False):
    """
    Setup logging configuration.

    Args:
        verbose: Enable verbose (DEBUG) logging
    """
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)]
    )


@app.command()
def process(
    input_path: Path = typer.Argument(..., help="Input PDF file"),
    output_path: Path = typer.Argument(..., help="Output PDF file"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Document title"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Document author"),
    language: str = typer.Option("en-US", "--language", "-l", help="Document language"),
    skip_ocr: bool = typer.Option(False, "--skip-ocr", help="Skip OCR processing"),
    force_ocr: bool = typer.Option(False, "--force-ocr", help="Force OCR even if text exists"),
    text_threshold: int = typer.Option(100, "--text-threshold", help="Minimum chars/page to skip OCR"),
    dpi: int = typer.Option(300, "--dpi", help="DPI for OCR image conversion"),
    ocr_language: str = typer.Option("eng", "--ocr-lang", help="Tesseract language code"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
):
    """
    Process a single PDF file with OCR and PDF/UA-1 compliance.

    Examples:
        epubs-simple process input.pdf output.pdf
        epubs-simple process input.pdf output.pdf --title "My Document" --author "John Doe"
        epubs-simple process input.pdf output.pdf --skip-ocr
    """
    setup_logging(verbose)

    logger = logging.getLogger(__name__)

    console.print(f"\n[bold]ePubs Accessibility Enhancement (Simplified)[/bold]")
    console.print(f"Input:  {input_path}")
    console.print(f"Output: {output_path}\n")

    # Validate input
    if not input_path.exists():
        console.print(f"[red]Error: Input file not found: {input_path}[/red]")
        raise typer.Exit(code=1)

    # Create service
    try:
        service = SimpleEnhancementService(
            text_threshold=text_threshold,
            dpi=dpi,
            language=ocr_language
        )

        # Process document
        success = service.enhance_document(
            input_path=input_path,
            output_path=output_path,
            title=title,
            author=author,
            language=language,
            skip_ocr=skip_ocr,
            force_ocr=force_ocr
        )

        if success:
            console.print(f"\n[green]✓ Success![/green] Enhanced PDF saved to: {output_path}")
            raise typer.Exit(code=0)
        else:
            console.print(f"\n[red]✗ Failed![/red] Enhancement unsuccessful")
            raise typer.Exit(code=1)

    except typer.Exit:
        # Let typer.Exit propagate without catching
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        console.print(f"\n[red]✗ Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def batch_process(
    input_dir: Path = typer.Argument(..., help="Input directory containing PDFs"),
    output_dir: Path = typer.Argument(..., help="Output directory for enhanced PDFs"),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of parallel workers (1 = sequential)"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", help="Process subdirectories recursively"),
    skip_ocr: bool = typer.Option(False, "--skip-ocr", help="Skip OCR processing for all files"),
    force_ocr: bool = typer.Option(False, "--force-ocr", help="Force OCR even if text exists"),
    text_threshold: int = typer.Option(100, "--text-threshold", help="Minimum chars/page to skip OCR"),
    dpi: int = typer.Option(300, "--dpi", help="DPI for OCR image conversion"),
    ocr_language: str = typer.Option("eng", "--ocr-lang", help="Tesseract language code"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
):
    """
    Process multiple PDF files preserving folder structure.

    Examples:
        epubs-simple batch-process input_folder/ output_folder/
        epubs-simple batch-process input_folder/ output_folder/ --workers 4
        epubs-simple batch-process input_folder/ output_folder/ --skip-ocr
        epubs-simple batch-process input_folder/ output_folder/ --force-ocr
    """
    setup_logging(verbose)

    logger = logging.getLogger(__name__)

    console.print(f"\n[bold]ePubs Batch Processing (Simplified)[/bold]")
    console.print(f"Input:   {input_dir}")
    console.print(f"Output:  {output_dir}")
    console.print(f"Workers: {workers}")
    console.print(f"Recursive: {recursive}\n")

    # Validate input
    if not input_dir.exists():
        console.print(f"[red]Error: Input directory not found: {input_dir}[/red]")
        raise typer.Exit(code=1)

    # Create processor
    try:
        processor = SimpleBatchProcessor(
            text_threshold=text_threshold,
            dpi=dpi,
            language=ocr_language
        )

        # Process batch
        summary = processor.process_batch(
            input_dir=input_dir,
            output_dir=output_dir,
            workers=workers,
            recursive=recursive,
            skip_ocr=skip_ocr,
            force_ocr=force_ocr
        )

        # Display summary
        if summary.get("success"):
            console.print(f"\n[bold]Processing Summary:[/bold]")
            console.print(f"  Total files:     {summary['total_files']}")
            console.print(f"  [green]Successful:[/green]      {summary['processed']}")
            console.print(f"  [red]Failed:[/red]          {summary['failed']}")
            console.print(f"  Total duration:  {summary['total_duration']:.1f}s")
            console.print(f"  Avg per file:    {summary['avg_duration_per_file']:.1f}s")

            if summary['failed'] > 0:
                console.print(f"\n[yellow]Failed files:[/yellow]")
                for failed in summary['failed_files']:
                    console.print(f"  - {failed['file']}: {failed['error']}")

            console.print(f"\n[green]✓ Batch processing complete![/green]")
            console.print(f"Summary report saved to: {output_dir}/batch_processing_summary.json")

            raise typer.Exit(code=0 if summary['failed'] == 0 else 1)
        else:
            console.print(f"\n[red]✗ Batch processing failed:[/red] {summary.get('error', 'Unknown error')}")
            raise typer.Exit(code=1)

    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        console.print(f"\n[red]✗ Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def version():
    """
    Display version information.
    """
    console.print("\n[bold]ePubs Accessibility Enhancement (Simplified)[/bold]")
    console.print("Version: 1.0.0 (Simplified)")
    console.print("Stage: 2 - Modular Refactoring\n")
    console.print("Features:")
    console.print("  - Simple OCR with Tesseract")
    console.print("  - PDF/UA-1 compliance")
    console.print("  - Orphan tag stripping")
    console.print("  - Batch processing with folder preservation\n")


@app.callback()
def main():
    """
    ePubs PDF Accessibility Enhancement Tool (Simplified Version)

    This tool provides basic PDF preprocessing for accessibility:
    - OCR text layer generation
    - Orphan tag stripping for Acrobat compatibility
    - PDF/UA-1 metadata compliance
    - Batch processing with folder structure preservation

    Workflow:
    1. Run this tool on scanned PDFs
    2. Open enhanced PDFs in Adobe Acrobat Pro
    3. Manually add proper accessibility tags
    4. Export fully compliant PDFs
    """
    pass


if __name__ == "__main__":
    app()
