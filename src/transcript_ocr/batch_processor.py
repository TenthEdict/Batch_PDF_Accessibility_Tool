"""Batch processor for TIFF transcript OCR.

Discovers TIFF files, groups them by collection/reference_id, and writes one
text file per page, with parallel execution support.
"""

import json
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .filename_parser import FilenameParseError, TiffFileInfo, parse_tiff_filename
from .tiff_ocr_processor import TiffOCRProcessor

logger = logging.getLogger(__name__)

try:
    from tqdm import tqdm

    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


class TranscriptBatchProcessor:
    """Batch processor for TIFF transcript OCR."""

    def __init__(
        self,
        language: str = "eng",
        dpi: int = 300,
    ):
        """Initialize the batch processor.

        Args:
            language: Tesseract language code.
            dpi: DPI hint for Tesseract.
        """
        self.ocr_processor = TiffOCRProcessor(language=language, dpi=dpi)

    def discover_and_group(
        self,
        input_dir: Path,
        collection_filter: Optional[str] = None,
        ref_ids_filter: Optional[Set[str]] = None,
    ) -> Dict[Tuple[str, str], List[Tuple[Path, TiffFileInfo]]]:
        """Discover TIFF files and group by collection/reference_id.

        Args:
            input_dir: Directory to search for TIFF files.
            collection_filter: If set, only include files from this collection.
            ref_ids_filter: If set, only include files with these reference IDs.

        Returns:
            Dictionary mapping (collection, reference_id) to list of (path, info) tuples.
        """
        groups: Dict[Tuple[str, str], List[Tuple[Path, TiffFileInfo]]] = defaultdict(
            list
        )
        skipped_count = 0

        # Find all TIFF files. Match the extension case-insensitively (like the
        # filename pattern): rglob("*.tif") misses .TIF on case-sensitive file
        # systems such as Linux/WSL.
        tiff_files = sorted(
            path
            for path in input_dir.rglob("*")
            if path.suffix.lower() in (".tif", ".tiff") and path.is_file()
        )
        logger.info(f"Found {len(tiff_files)} TIFF files in {input_dir}")

        for tiff_path in tiff_files:
            try:
                info = parse_tiff_filename(tiff_path.name)
            except FilenameParseError as e:
                logger.warning(f"Skipping file: {e}")
                skipped_count += 1
                continue

            # Apply filters
            if collection_filter and info.collection != collection_filter:
                continue
            # `is not None`: an empty filter means "match nothing", not "everything"
            if ref_ids_filter is not None and info.reference_id not in ref_ids_filter:
                continue

            groups[info.transcript_key].append((tiff_path, info))

        if skipped_count > 0:
            logger.warning(
                f"Skipped {skipped_count} files that did not match naming pattern"
            )

        # Sort pages within each group by page number
        for key in groups:
            groups[key].sort(key=lambda x: x[1].page_number)

        logger.info(
            f"Grouped into {len(groups)} transcripts "
            f"across {len(set(k[0] for k in groups))} collections"
        )

        return dict(groups)

    def _process_transcript(
        self,
        collection: str,
        reference_id: str,
        pages: List[Tuple[Path, TiffFileInfo]],
        output_dir: Path,
    ) -> Dict:
        """Process a single transcript (all pages for one reference_id).

        Args:
            collection: Collection identifier.
            reference_id: Reference ID.
            pages: List of (path, info) tuples for pages in this transcript.
            output_dir: Base output directory.

        Returns:
            Result dictionary with success status, output path, and stats.
        """
        start_time = datetime.now()
        errors = 0
        output_files: List[str] = []

        # Create output folder: output_dir/{collection}/{reference_id}/
        transcript_output_dir = output_dir / collection / reference_id
        transcript_output_dir.mkdir(parents=True, exist_ok=True)

        for tiff_path, info in pages:
            text, error = self.ocr_processor.process_tiff_safe(tiff_path)

            if error:
                errors += 1
                logger.warning(f"OCR error for {info.original_filename}: {error}")

            # Write individual page file with same base name as TIFF
            txt_filename = Path(info.original_filename).stem + ".txt"
            output_path = transcript_output_dir / txt_filename
            output_path.write_text(text or "", encoding="utf-8")
            output_files.append(str(output_path))

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "collection": collection,
            "reference_id": reference_id,
            "output_dir": str(transcript_output_dir),
            "output_files": output_files,
            "total_pages": len(pages),
            "successful_pages": len(pages) - errors,
            "errors": errors,
            "duration": duration,
            "success": True,
        }

    def process(
        self,
        input_dir: Path,
        output_dir: Path,
        workers: int = 1,
        collection_filter: Optional[str] = None,
        ref_ids_filter: Optional[Set[str]] = None,
    ) -> Dict:
        """Process all TIFF files and generate transcripts.

        Args:
            input_dir: Directory containing TIFF files.
            output_dir: Directory for output transcript files.
            workers: Number of parallel workers.
            collection_filter: If set, only process this collection.
            ref_ids_filter: If set, only process these reference IDs.

        Returns:
            Summary dictionary with processing statistics.
        """
        start_time = datetime.now()

        # Discover and group files
        groups = self.discover_and_group(
            input_dir,
            collection_filter=collection_filter,
            ref_ids_filter=ref_ids_filter,
        )

        if not groups:
            logger.warning("No matching TIFF files found")
            return {
                "success": True,
                "total_transcripts": 0,
                "message": "No matching TIFF files found",
            }

        output_dir.mkdir(parents=True, exist_ok=True)
        results: List[Dict] = []

        if workers > 1:
            results = self._process_parallel(groups, output_dir, workers)
        else:
            results = self._process_sequential(groups, output_dir)

        # Generate summary
        total_duration = (datetime.now() - start_time).total_seconds()
        summary = self._generate_summary(results, total_duration)

        # Save summary to file
        self._save_summary(output_dir, summary)

        return summary

    def _process_sequential(
        self,
        groups: Dict[Tuple[str, str], List[Tuple[Path, TiffFileInfo]]],
        output_dir: Path,
    ) -> List[Dict]:
        """Process transcripts sequentially."""
        results = []

        if TQDM_AVAILABLE:
            iterator = tqdm(groups.items(), desc="Processing transcripts", unit="doc")
        else:
            iterator = groups.items()
            logger.info(f"Processing {len(groups)} transcripts sequentially")

        for (collection, reference_id), pages in iterator:
            result = self._process_transcript(
                collection, reference_id, pages, output_dir
            )
            results.append(result)

        return results

    def _process_parallel(
        self,
        groups: Dict[Tuple[str, str], List[Tuple[Path, TiffFileInfo]]],
        output_dir: Path,
        workers: int,
    ) -> List[Dict]:
        """Process transcripts in parallel."""
        results = []

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_key = {
                executor.submit(
                    self._process_transcript,
                    collection,
                    reference_id,
                    pages,
                    output_dir,
                ): (collection, reference_id)
                for (collection, reference_id), pages in groups.items()
            }

            if TQDM_AVAILABLE:
                iterator = tqdm(
                    as_completed(future_to_key),
                    total=len(groups),
                    desc="Processing transcripts",
                    unit="doc",
                )
            else:
                iterator = as_completed(future_to_key)
                logger.info(
                    f"Processing {len(groups)} transcripts with {workers} workers"
                )

            for future in iterator:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    key = future_to_key[future]
                    logger.error(f"Error processing {key}: {e}")
                    results.append(
                        {
                            "collection": key[0],
                            "reference_id": key[1],
                            "success": False,
                            "error": str(e),
                        }
                    )

        return results

    def _generate_summary(self, results: List[Dict], total_duration: float) -> Dict:
        """Generate summary from processing results."""
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", False)]

        # Group by collection for stats
        collections: Dict[str, Dict] = defaultdict(
            lambda: {"transcripts": 0, "pages": 0, "files": 0, "errors": 0}
        )
        for r in successful:
            col = r["collection"]
            collections[col]["transcripts"] += 1
            collections[col]["pages"] += r.get("total_pages", 0)
            collections[col]["files"] += len(r.get("output_files", []))
            collections[col]["errors"] += r.get("errors", 0)

        total_pages = sum(r.get("total_pages", 0) for r in successful)
        total_files = sum(len(r.get("output_files", [])) for r in successful)
        total_errors = sum(r.get("errors", 0) for r in successful)

        return {
            "success": True,
            "total_transcripts": len(results),
            "successful_transcripts": len(successful),
            "failed_transcripts": len(failed),
            "total_pages": total_pages,
            "total_files_generated": total_files,
            "total_ocr_errors": total_errors,
            "total_duration": total_duration,
            "avg_duration_per_transcript": (
                total_duration / len(results) if results else 0
            ),
            "collections": dict(collections),
            "failed_details": [
                {"collection": r["collection"], "reference_id": r["reference_id"], "error": r.get("error")}
                for r in failed
            ],
            "timestamp": datetime.now().isoformat(),
        }

    def _save_summary(self, output_dir: Path, summary: Dict) -> None:
        """Save summary to JSON file."""
        summary_path = output_dir / "batch_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Saved summary to {summary_path}")

    def list_collections(
        self,
        input_dir: Path,
        collection_filter: Optional[str] = None,
    ) -> Dict[str, Dict[str, int]]:
        """List collections and reference IDs found in input directory.

        Args:
            input_dir: Directory to search.
            collection_filter: If set, only list this collection.

        Returns:
            Dictionary mapping collection -> {reference_id: page_count}.
        """
        groups = self.discover_and_group(
            input_dir, collection_filter=collection_filter
        )

        collections: Dict[str, Dict[str, int]] = defaultdict(dict)
        for (collection, reference_id), pages in groups.items():
            collections[collection][reference_id] = len(pages)

        return dict(collections)
