"""
Integration tests that run real OCR (ocrmypdf + Tesseract).

Slow: deselect with `pytest -m "not slow"`.
"""

import shutil
from pathlib import Path

import pikepdf
import pytest
from pikepdf import Array, Dictionary, Name

from src.processor.simple_batch_processor import SimpleBatchProcessor
from src.processor.simple_enhancement_service import SimpleEnhancementService
from src.processor.simple_ocr_enhancer import SimpleOCREnhancer
from src.processor.simple_pdfua_enhancer import SimplePDFUAEnhancer
from tests.pdf_factories import (
    TESSERACT_AVAILABLE,
    make_born_digital,
    make_orphan_tagged,
    make_scanned,
    make_tagged,
    marked_content_tags,
    ocr_form_count,
    pdfua_claim,
    renders_identically,
    words,
)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow,
    pytest.mark.ocr,
    pytest.mark.skipif(not TESSERACT_AVAILABLE, reason="Tesseract not installed"),
]


def _word_count(path: Path) -> int:
    return sum(len(page) for page in words(path))


@pytest.fixture(scope="module")
def ocr_files(tmp_path_factory):
    """One scanned page, OCR'd once by ocrmypdf and shared by the tests below."""
    workdir = tmp_path_factory.mktemp("ocr")
    scanned = make_scanned(workdir / "scanned.pdf")
    raw = workdir / "raw_ocrmypdf.pdf"
    status = SimpleOCREnhancer().enhance_file_with_status(scanned, raw)
    return {"dir": workdir, "scanned": scanned, "raw": raw, "status": status}


def test_ocr_enhancer_reports_ocr_performed(ocr_files):
    assert ocr_files["status"] == (True, True)


def test_ocrmypdf_still_uses_ocr_form_xobjects(ocr_files):
    """
    Guard: the flattening fix assumes ocrmypdf grafts its text layer as a
    Form XObject named /OCR-...  If a new ocrmypdf version changes that,
    this fails, and _flatten_ocr_text_layers needs revisiting.
    """
    assert ocr_form_count(ocr_files["raw"]) > 0
    assert _word_count(ocr_files["raw"]) > 50


def test_flatten_is_lossless_on_real_ocr_output(ocr_files, tmp_path):
    out = tmp_path / "flattened.pdf"
    assert SimplePDFUAEnhancer().enhance_file(ocr_files["raw"], out, ocr_performed=True)

    assert ocr_form_count(out) == 0
    assert words(out) == words(ocr_files["raw"])
    assert renders_identically(ocr_files["raw"], out)
    with pikepdf.open(out) as pdf:
        assert pdf.check() == []


def test_service_end_to_end_on_scan(ocr_files, tmp_path):
    out = tmp_path / "out" / "scanned.pdf"
    assert SimpleEnhancementService().enhance_document(ocr_files["scanned"], out)

    assert ocr_form_count(out) == 0
    assert "Chapter" in [w[4] for w in words(out)[0]]
    assert pdfua_claim(out) is None
    with pikepdf.open(out) as pdf:
        assert Name.StructTreeRoot not in pdf.Root
        assert bool(pdf.Root.MarkInfo.Marked) is False
        assert pdf.check() == []


@pytest.fixture
def legacy_output(ocr_files, tmp_path) -> Path:
    """Shaped like output from versions before the fix: OCR form + false claims."""
    path = tmp_path / "legacy.pdf"
    with pikepdf.open(ocr_files["raw"]) as pdf:
        pdf.Root.MarkInfo = Dictionary(Marked=True, Suspects=True)
        pdf.Root.OutputIntents = Array(
            [Dictionary(Type=Name.OutputIntent, S=Name.GTS_PDFUA1)]
        )
        with pdf.open_metadata() as meta:
            meta["pdfuaid:part"] = "1"
        pdf.save(path)
    return path


@pytest.mark.parametrize("force_ocr", [False, True])
def test_rerun_on_legacy_output_does_not_duplicate_text(
    ocr_files, legacy_output, tmp_path, force_ocr
):
    out = tmp_path / "rerun.pdf"
    assert SimpleEnhancementService().enhance_document(
        legacy_output, out, force_ocr=force_ocr
    )

    original = _word_count(ocr_files["raw"])
    rerun = _word_count(out)
    # Re-OCR may differ by a word or two; duplication would double the count
    assert abs(rerun - original) <= max(3, original // 20), (original, rerun)
    assert ocr_form_count(out) == 0
    assert pdfua_claim(out) is None
    with pikepdf.open(out) as pdf:
        assert bool(pdf.Root.MarkInfo.Marked) is False
        assert Name.Suspects not in pdf.Root.MarkInfo
        assert Name.OutputIntents not in pdf.Root


def test_parallel_batch_handles_each_file_independently(tmp_path):
    """
    The service is shared across worker threads, so "did OCR run" must be
    per file: the scan gets OCR + flattening while the tagged file in the
    same batch keeps its tags.
    """
    in_dir = tmp_path / "in"
    (in_dir / "sub").mkdir(parents=True)
    make_scanned(in_dir / "scanned.pdf")
    make_tagged(in_dir / "sub" / "tagged.pdf")
    make_orphan_tagged(in_dir / "orphan.pdf")
    make_born_digital(in_dir / "sub" / "digital.pdf")
    out_dir = tmp_path / "out"

    summary = SimpleBatchProcessor().process_batch(in_dir, out_dir, workers=4)

    assert summary["total_files"] == 4
    assert summary["processed"] == 4 and summary["failed"] == 0

    scanned = out_dir / "scanned.pdf"
    assert ocr_form_count(scanned) == 0
    assert _word_count(scanned) > 50

    tagged = out_dir / "sub" / "tagged.pdf"
    assert marked_content_tags(tagged) == marked_content_tags(in_dir / "sub" / "tagged.pdf")
    with pikepdf.open(tagged) as pdf:
        assert Name.StructTreeRoot in pdf.Root

    assert marked_content_tags(out_dir / "orphan.pdf") == ["/OC", "/Artifact"]

    digital = out_dir / "sub" / "digital.pdf"
    assert words(digital) == words(in_dir / "sub" / "digital.pdf")

    # No temp files left in the output tree
    leftovers = {p.name for p in out_dir.rglob("*.pdf")} - {
        "scanned.pdf", "tagged.pdf", "orphan.pdf", "digital.pdf"
    }
    assert not leftovers
