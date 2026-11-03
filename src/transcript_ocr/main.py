"""CLI for TIFF Transcript OCR.

Usage:
    python3 -m src.transcript_ocr process input_dir/ output_dir/
    python3 -m src.transcript_ocr process input_dir/ output_dir/ --collection MSP00213
    python3 -m src.transcript_ocr list-collections input_dir/
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from .batch_processor import TranscriptBatchProcessor

app = typer.Typer(
    name="transcript-ocr",
    help="OCR single-page TIFF files into one text file per page.",
    add_completion=False,
)
console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with Rich handler."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, console=console)],
    )


def load_ref_ids_from_file(filepath: Path) -> set:
    """Load reference IDs from a file (one per line)."""
    if not filepath.exists():
        console.print(f"[red]Error:[/red] Reference IDs file not found: {filepath}")
        raise typer.Exit(1)

    ref_ids = set()
    for line in filepath.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            ref_ids.add(line)
    return ref_ids


@app.command()
def process(
    input_dir: Path = typer.Argument(
        ...,
        help="Input directory containing TIFF files",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    output_dir: Path = typer.Argument(
        ...,
        help="Output directory for transcript files",
    ),
    collection: Optional[str] = typer.Option(
        None,
        "--collection",
        "-c",
        help="Filter to specific collection (e.g., MSP00213)",
    ),
    ref_ids: Optional[str] = typer.Option(
        None,
        "--ref-ids",
        "-r",
        help="Comma-separated reference IDs to process",
    ),
    ref_ids_file: Optional[Path] = typer.Option(
        None,
        "--ref-ids-file",
        "-f",
        help="File containing reference IDs (one per line)",
    ),
    ocr_lang: str = typer.Option(
        "eng",
        "--ocr-lang",
        "-l",
        help="Tesseract language code",
    ),
    dpi: int = typer.Option(
        300,
        "--dpi",
        help="DPI hint for Tesseract",
    ),
    workers: int = typer.Option(
        1,
        "--workers",
        "-w",
        help="Number of parallel workers",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
):
    """OCR TIFF files into one text file per page.

    Groups TIFF files by collection and reference ID parsed from filenames,
    then writes each page's text to output_dir/{collection}/{reference_id}/.
    """
    setup_logging(verbose)

    # Parse reference ID filters
    ref_ids_filter = None
    if ref_ids:
        ref_ids_filter = set(r.strip() for r in ref_ids.split(","))
    elif ref_ids_file:
        ref_ids_filter = load_ref_ids_from_file(ref_ids_file)
        if not ref_ids_filter:
            console.print(
                f"[yellow]Warning:[/yellow] {ref_ids_file} contains no reference IDs; "
                "nothing will be processed"
            )

    # Show what we're processing
    console.print(f"[bold]Input directory:[/bold] {input_dir}")
    console.print(f"[bold]Output directory:[/bold] {output_dir}")
    if collection:
        console.print(f"[bold]Collection filter:[/bold] {collection}")
    if ref_ids_filter:
        console.print(f"[bold]Reference ID filter:[/bold] {len(ref_ids_filter)} IDs")
    console.print()

    # Process
    processor = TranscriptBatchProcessor(language=ocr_lang, dpi=dpi)
    summary = processor.process(
        input_dir=input_dir,
        output_dir=output_dir,
        workers=workers,
        collection_filter=collection,
        ref_ids_filter=ref_ids_filter,
    )

    # Display summary
    console.print()
    console.print("[bold]Processing Summary:[/bold]")
    console.print(f"  Total transcripts:     {summary.get('total_transcripts', 0)}")
    console.print(
        f"  [green]Successful:[/green]           {summary.get('successful_transcripts', 0)}"
    )
    console.print(
        f"  [red]Failed:[/red]               {summary.get('failed_transcripts', 0)}"
    )
    console.print(f"  Total pages OCR'd:     {summary.get('total_pages', 0)}")
    console.print(f"  OCR errors:            {summary.get('total_ocr_errors', 0)}")
    console.print(f"  Total duration:        {summary.get('total_duration', 0):.1f}s")

    if summary.get("failed_details"):
        console.print()
        console.print("[bold red]Failed transcripts:[/bold red]")
        for fail in summary["failed_details"]:
            console.print(
                f"  {fail['collection']}/{fail['reference_id']}: {fail.get('error', 'Unknown error')}"
            )


@app.command("list-collections")
def list_collections(
    input_dir: Path = typer.Argument(
        ...,
        help="Input directory containing TIFF files",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    collection: Optional[str] = typer.Option(
        None,
        "--collection",
        "-c",
        help="Filter to specific collection",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
):
    """List collections and reference IDs found in the input directory.

    Useful for previewing what would be processed before running OCR.
    """
    setup_logging(verbose)

    processor = TranscriptBatchProcessor()
    collections = processor.list_collections(input_dir, collection_filter=collection)

    if not collections:
        console.print("[yellow]No matching TIFF files found.[/yellow]")
        return

    # Summary
    total_transcripts = sum(len(refs) for refs in collections.values())
    total_pages = sum(
        sum(pages for pages in refs.values()) for refs in collections.values()
    )
    console.print(f"[bold]Found {total_transcripts} transcripts across {len(collections)} collections ({total_pages} total pages)[/bold]")
    console.print()

    # Table per collection
    for coll_name in sorted(collections.keys()):
        refs = collections[coll_name]
        table = Table(title=f"Collection: {coll_name}")
        table.add_column("Reference ID", style="cyan")
        table.add_column("Pages", justify="right")

        for ref_id in sorted(refs.keys()):
            table.add_row(ref_id, str(refs[ref_id]))

        console.print(table)
        console.print()


@app.command()
def version():
    """Show version information."""
    console.print("transcript-ocr v1.0.0")
    console.print("Part of ePubs Accessibility Enhancement toolkit")


if __name__ == "__main__":
    app()
