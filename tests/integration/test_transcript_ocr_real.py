"""
Real-Tesseract tests for src/transcript_ocr: TIFF pages in, per-page TXT out.
"""

from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont
from typer.testing import CliRunner

from src.transcript_ocr.batch_processor import TranscriptBatchProcessor
from src.transcript_ocr.main import app
from tests.pdf_factories import TESSERACT_AVAILABLE

pytestmark = [
    pytest.mark.integration,
    pytest.mark.ocr,
    pytest.mark.skipif(not TESSERACT_AVAILABLE, reason="Tesseract not installed"),
]


def make_text_tiff(path: Path, text: str) -> Path:
    """A 300-dpi TIFF with one line of large, clean text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("L", (1800, 400), 255)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 56)
    except OSError:
        font = ImageFont.load_default(size=56)
    draw.text((60, 150), text, fill=0, font=font)
    image.save(path, dpi=(300, 300))
    return path


PAGES = {
    "MSP00213_abc123_00001.tif": "Letter from the archive",
    "MSP00213_abc123_00002.tif": "Second page of the letter",
    "MSP00213_def456_00001.tif": "Another reference entirely",
}


@pytest.fixture
def tiff_dir(tmp_path) -> Path:
    for name, text in PAGES.items():
        make_text_tiff(tmp_path / "in" / name, text)
    return tmp_path / "in"


def _normalise(text: str) -> str:
    return " ".join(text.split()).lower()


@pytest.mark.parametrize("workers", [1, 2])
def test_real_ocr_writes_correct_text_per_page(tiff_dir, tmp_path, workers):
    out = tmp_path / f"out{workers}"

    summary = TranscriptBatchProcessor().process(tiff_dir, out, workers=workers)

    assert summary["total_ocr_errors"] == 0
    assert summary["total_files_generated"] == 3
    for name, text in PAGES.items():
        collection, ref, _ = name.split("_")
        page_file = out / collection / ref / name.replace(".tif", ".txt")
        assert _normalise(page_file.read_text(encoding="utf-8")) == _normalise(text)


def test_real_ocr_cli_end_to_end(tiff_dir, tmp_path):
    out = tmp_path / "out"

    result = CliRunner().invoke(app, ["process", str(tiff_dir), str(out), "--ref-ids", "abc123"])

    assert result.exit_code == 0, result.output
    written = sorted(p.relative_to(out).as_posix() for p in out.rglob("*.txt"))
    assert written == [
        "MSP00213/abc123/MSP00213_abc123_00001.txt",
        "MSP00213/abc123/MSP00213_abc123_00002.txt",
    ]
