"""
Integration tests for the simplified processor pipeline.

These use real assertions (no try/except returning False) so failures are
reported as failures. The end-to-end test builds its own PDF, so it never
silently skips for lack of sample data.
"""

from pathlib import Path

import fitz  # PyMuPDF
import pikepdf
import pytest

from src.processor.simple_enhancement_service import SimpleEnhancementService
from src.processor.simple_ocr_enhancer import SimpleOCREnhancer
from src.processor.simple_pdfua_enhancer import SimplePDFUAEnhancer


@pytest.fixture
def born_digital_pdf(tmp_path: Path) -> Path:
    """A small two-page PDF with a real (non-OCR) text layer."""
    path = tmp_path / "born_digital.pdf"
    doc = fitz.open()
    for page_num in range(2):
        page = doc.new_page()
        page.insert_text((72, 100), f"Chapter {page_num} Heading", fontsize=20)
        for line in range(20):
            page.insert_text(
                (72, 140 + line * 20),
                f"This is line {line} of body text on page {page_num}.",
                fontsize=11,
            )
    doc.save(path)
    doc.close()
    return path


@pytest.mark.unit
def test_ocr_enhancer_defaults():
    enhancer = SimpleOCREnhancer()
    assert enhancer.text_threshold == 100
    assert enhancer.dpi == 300
    assert enhancer.language == "eng"


@pytest.mark.unit
def test_pdfua_enhancer_name():
    assert SimplePDFUAEnhancer().name == "simple_pdfua_enhancer"


@pytest.mark.unit
def test_service_wires_enhancers():
    service = SimpleEnhancementService()
    assert isinstance(service.ocr_enhancer, SimpleOCREnhancer)
    assert isinstance(service.pdfua_enhancer, SimplePDFUAEnhancer)


@pytest.mark.integration
def test_end_to_end_untagged_output(born_digital_pdf: Path, tmp_path: Path):
    output_path = tmp_path / "out" / "result.pdf"

    success = SimpleEnhancementService().enhance_document(
        born_digital_pdf, output_path, skip_ocr=True, title="Test Document"
    )

    assert success
    assert output_path.exists() and output_path.stat().st_size > 0

    with pikepdf.open(output_path) as pdf:
        assert pdf.check() == []

        # Untagged output: must not claim to be tagged or PDF/UA conformant
        assert "/StructTreeRoot" not in pdf.Root
        assert bool(pdf.Root.MarkInfo.Marked) is False
        assert "/Suspects" not in pdf.Root.MarkInfo
        for intent in pdf.Root.get("/OutputIntents", []):
            assert intent.get("/S") != "/GTS_PDFUA1"

        assert str(pdf.Root.Lang) == "en-US"

        with pdf.open_metadata() as meta:
            assert "pdfuaid:part" not in meta
            assert meta.get("dc:title") == "Test Document"

    # Text layer survives unchanged
    with fitz.open(born_digital_pdf) as before, fitz.open(output_path) as after:
        for page_before, page_after in zip(before, after):
            assert page_after.get_text("words") == page_before.get_text("words")
