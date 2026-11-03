"""
Unit tests for src/transcript_ocr (TIFF -> per-page TXT).

Tesseract is mocked here so these run fast; real OCR is covered in
tests/integration/test_transcript_ocr_real.py.
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytesseract
import pytest
from PIL import Image
from typer.testing import CliRunner

from src.transcript_ocr import main as transcript_main
from src.transcript_ocr.batch_processor import TranscriptBatchProcessor
from src.transcript_ocr.filename_parser import (
    FilenameParseError,
    is_valid_tiff_filename,
    parse_tiff_filename,
)
from src.transcript_ocr.main import app
from src.transcript_ocr.tiff_ocr_processor import OCRError, TiffOCRProcessor

pytestmark = pytest.mark.unit

runner = CliRunner()

REF_A = "1f4d822f499c9eacb2f15403dd53e468"
REF_B = "abc123"


def make_tiff(path: Path) -> Path:
    """A tiny blank TIFF; OCR is mocked so content doesn't matter."""
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("L", (20, 20), 255).save(path)
    return path


def fake_ocr(tiff_path):
    """Stand-in for process_tiff_safe: deterministic text per file."""
    return f"text of {Path(tiff_path).name}", None


@pytest.fixture
def mocked_processor():
    processor = TranscriptBatchProcessor()
    with patch.object(processor.ocr_processor, "process_tiff_safe", side_effect=fake_ocr):
        yield processor


# ----------------------------------------------------------------------
# filename_parser
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "name, collection, ref, page",
    [
        (f"MSP00213_{REF_A}_00001.tif", "MSP00213", REF_A, 1),
        ("MSP00213_abc123_00042.tiff", "MSP00213", "abc123", 42),
        ("msp1_ABC_99999.TIF", "msp1", "ABC", 99999),
    ],
)
def test_parse_valid_names(name, collection, ref, page):
    info = parse_tiff_filename(name)
    assert (info.collection, info.reference_id, info.page_number) == (collection, ref, page)
    assert info.original_filename == name
    assert info.transcript_key == (collection, ref)


@pytest.mark.parametrize(
    "value",
    [
        Path("/data/scans/MSP1_abc_00001.tif"),
        "/data/scans/MSP1_abc_00001.tif",
        "C:\\scans\\MSP1_abc_00001.tif",
    ],
)
def test_parse_accepts_paths(value):
    info = parse_tiff_filename(value)
    assert info.original_filename == "MSP1_abc_00001.tif"


@pytest.mark.parametrize(
    "name",
    [
        "MSP1_abc_0001.tif",     # 4-digit page
        "MSP1_abc_000001.tif",   # 6-digit page
        "MSP1_abc.tif",          # no page
        "MSP-1_abc_00001.tif",   # hyphen in collection
        "MSP1_ab_c_00001.tif",   # extra underscore
        "MSP1_abc_00001.png",    # not a TIFF
        "MSP1_abc_00001.tif.bak",
        "",
    ],
)
def test_parse_rejects_bad_names(name):
    with pytest.raises(FilenameParseError):
        parse_tiff_filename(name)
    assert is_valid_tiff_filename(name) is False


# ----------------------------------------------------------------------
# tiff_ocr_processor
# ----------------------------------------------------------------------


def test_ocr_missing_file(tmp_path):
    with pytest.raises(OCRError, match="not found"):
        TiffOCRProcessor().process_tiff(tmp_path / "missing.tif")


def test_ocr_unreadable_file(tmp_path):
    bad = tmp_path / "MSP1_abc_00001.tif"
    bad.write_bytes(b"not an image")
    with pytest.raises(OCRError, match="Failed to open"):
        TiffOCRProcessor().process_tiff(bad)


def test_ocr_passes_settings_and_strips_text(tmp_path):
    tiff = make_tiff(tmp_path / "page.tif")
    processor = TiffOCRProcessor(language="fra", dpi=400, psm=6, oem=1)
    with patch.object(pytesseract, "image_to_string", return_value="  Bonjour\n\n") as ocr:
        assert processor.process_tiff(tiff) == "Bonjour"
    assert ocr.call_args.kwargs["lang"] == "fra"
    assert ocr.call_args.kwargs["config"] == "--psm 6 --oem 1 --dpi 400"


def test_ocr_wraps_tesseract_errors(tmp_path):
    tiff = make_tiff(tmp_path / "page.tif")
    error = pytesseract.TesseractError(1, "bad language")
    with patch.object(pytesseract, "image_to_string", side_effect=error):
        with pytest.raises(OCRError, match="Tesseract OCR failed"):
            TiffOCRProcessor().process_tiff(tiff)


def test_ocr_safe_returns_error_instead_of_raising(tmp_path):
    text, error = TiffOCRProcessor().process_tiff_safe(tmp_path / "missing.tif")
    assert text is None
    assert "not found" in error


# ----------------------------------------------------------------------
# batch_processor: discovery and grouping
# ----------------------------------------------------------------------


def test_discover_groups_sorts_and_recurses(tmp_path):
    # Out-of-order pages, a nested folder, and both extensions
    make_tiff(tmp_path / f"MSP00213_{REF_A}_00010.tif")
    make_tiff(tmp_path / "nested" / f"MSP00213_{REF_A}_00002.tiff")
    make_tiff(tmp_path / f"MSP00213_{REF_A}_00001.tif")
    make_tiff(tmp_path / f"MSP00213_{REF_B}_00001.tif")
    make_tiff(tmp_path / f"OTHER1_{REF_B}_00001.tif")

    groups = TranscriptBatchProcessor().discover_and_group(tmp_path)

    assert set(groups) == {("MSP00213", REF_A), ("MSP00213", REF_B), ("OTHER1", REF_B)}
    assert [info.page_number for _, info in groups[("MSP00213", REF_A)]] == [1, 2, 10]


def test_discover_finds_uppercase_extensions(tmp_path):
    """The name pattern is case-insensitive, so discovery must be too (Linux FS)."""
    make_tiff(tmp_path / "MSP1_abc_00001.TIF")
    make_tiff(tmp_path / "MSP1_abc_00002.TIFF")
    make_tiff(tmp_path / "MSP1_abc_00003.Tif")

    groups = TranscriptBatchProcessor().discover_and_group(tmp_path)

    assert [info.page_number for _, info in groups[("MSP1", "abc")]] == [1, 2, 3]


def test_discover_skips_non_matching_names(tmp_path):
    make_tiff(tmp_path / "MSP1_abc_00001.tif")
    make_tiff(tmp_path / "scan_0001.tif")
    (tmp_path / "MSP1_abc_00002.txt").write_text("not a tiff")

    groups = TranscriptBatchProcessor().discover_and_group(tmp_path)

    assert list(groups) == [("MSP1", "abc")]
    assert len(groups[("MSP1", "abc")]) == 1


def test_discover_filters(tmp_path):
    for coll, ref in [("A1", "r1"), ("A1", "r2"), ("B1", "r1")]:
        make_tiff(tmp_path / f"{coll}_{ref}_00001.tif")
    processor = TranscriptBatchProcessor()

    assert set(processor.discover_and_group(tmp_path, collection_filter="A1")) == {
        ("A1", "r1"), ("A1", "r2")
    }
    assert set(processor.discover_and_group(tmp_path, ref_ids_filter={"r1"})) == {
        ("A1", "r1"), ("B1", "r1")
    }
    assert set(
        processor.discover_and_group(tmp_path, collection_filter="A1", ref_ids_filter={"r2"})
    ) == {("A1", "r2")}


def test_empty_ref_ids_filter_matches_nothing(tmp_path):
    """An empty filter (e.g. a refs file of only comments) must not mean 'everything'."""
    make_tiff(tmp_path / "A1_r1_00001.tif")
    assert TranscriptBatchProcessor().discover_and_group(tmp_path, ref_ids_filter=set()) == {}


def test_list_collections_counts_pages(tmp_path):
    for page in (1, 2, 3):
        make_tiff(tmp_path / f"A1_r1_0000{page}.tif")
    make_tiff(tmp_path / "B1_r9_00001.tif")

    assert TranscriptBatchProcessor().list_collections(tmp_path) == {
        "A1": {"r1": 3},
        "B1": {"r9": 1},
    }


# ----------------------------------------------------------------------
# batch_processor: per-page output
# ----------------------------------------------------------------------


def _make_two_transcripts(input_dir: Path):
    for page in (1, 2, 3):
        make_tiff(input_dir / f"MSP00213_{REF_A}_0000{page}.tif")
    make_tiff(input_dir / "sub" / f"MSP00213_{REF_B}_00001.tif")


def test_process_writes_one_txt_per_page(mocked_processor, tmp_path):
    _make_two_transcripts(tmp_path / "in")
    out = tmp_path / "out"

    summary = mocked_processor.process(tmp_path / "in", out)

    ref_dir = out / "MSP00213" / REF_A
    expected = [f"MSP00213_{REF_A}_0000{p}.txt" for p in (1, 2, 3)]
    assert sorted(p.name for p in ref_dir.iterdir()) == expected
    for name in expected:
        tiff_name = name.replace(".txt", ".tif")
        assert (ref_dir / name).read_text(encoding="utf-8") == f"text of {tiff_name}"
    # The flat output folder doesn't mirror input subfolders
    assert (out / "MSP00213" / REF_B / f"MSP00213_{REF_B}_00001.txt").exists()

    # Old behaviour (one combined {reference_id}.txt) is gone
    assert not (out / "MSP00213" / f"{REF_A}.txt").exists()

    assert summary["total_transcripts"] == 2
    assert summary["total_pages"] == 4
    assert summary["total_files_generated"] == 4
    assert summary["collections"]["MSP00213"] == {
        "transcripts": 2, "pages": 4, "files": 4, "errors": 0
    }


def test_process_result_lists_output_files(mocked_processor, tmp_path):
    make_tiff(tmp_path / "in" / "A1_r1_00001.tif")
    make_tiff(tmp_path / "in" / "A1_r1_00002.tif")
    groups = mocked_processor.discover_and_group(tmp_path / "in")

    result = mocked_processor._process_transcript("A1", "r1", groups[("A1", "r1")], tmp_path / "out")

    assert result["output_dir"] == str(tmp_path / "out" / "A1" / "r1")
    assert [Path(f).name for f in result["output_files"]] == ["A1_r1_00001.txt", "A1_r1_00002.txt"]
    assert result["total_pages"] == 2 and result["successful_pages"] == 2
    assert "output_path" not in result


def test_process_writes_summary_json(mocked_processor, tmp_path):
    _make_two_transcripts(tmp_path / "in")
    summary = mocked_processor.process(tmp_path / "in", tmp_path / "out")

    saved = json.loads((tmp_path / "out" / "batch_summary.json").read_text())
    assert saved["total_files_generated"] == summary["total_files_generated"] == 4


def test_ocr_error_writes_empty_page_and_counts_it(tmp_path):
    for page in (1, 2):
        make_tiff(tmp_path / "in" / f"A1_r1_0000{page}.tif")
    processor = TranscriptBatchProcessor()

    def flaky(path):
        if Path(path).name.endswith("00002.tif"):
            return None, "Tesseract OCR failed"
        return "page one", None

    with patch.object(processor.ocr_processor, "process_tiff_safe", side_effect=flaky):
        summary = processor.process(tmp_path / "in", tmp_path / "out")

    ref_dir = tmp_path / "out" / "A1" / "r1"
    assert (ref_dir / "A1_r1_00001.txt").read_text() == "page one"
    # A placeholder keeps page numbering complete
    assert (ref_dir / "A1_r1_00002.txt").read_text() == ""
    assert summary["total_ocr_errors"] == 1
    assert summary["collections"]["A1"]["errors"] == 1


def test_parallel_matches_sequential(tmp_path):
    for coll, ref in [("A1", "r1"), ("A1", "r2"), ("B1", "r1"), ("B1", "r3")]:
        for page in (1, 2):
            make_tiff(tmp_path / "in" / f"{coll}_{ref}_0000{page}.tif")

    outputs = {}
    for workers in (1, 4):
        processor = TranscriptBatchProcessor()
        with patch.object(processor.ocr_processor, "process_tiff_safe", side_effect=fake_ocr):
            summary = processor.process(tmp_path / "in", tmp_path / f"out{workers}", workers=workers)
        assert summary["total_files_generated"] == 8
        root = tmp_path / f"out{workers}"
        outputs[workers] = {
            str(p.relative_to(root)): p.read_text()
            for p in root.rglob("*.txt")
        }

    assert outputs[1] == outputs[4]


def test_parallel_failure_reported(mocked_processor, tmp_path):
    make_tiff(tmp_path / "in" / "A1_r1_00001.tif")
    make_tiff(tmp_path / "in" / "A1_r2_00001.tif")
    original = mocked_processor._process_transcript

    def explode_on_r2(collection, reference_id, pages, output_dir):
        if reference_id == "r2":
            raise PermissionError("output not writable")
        return original(collection, reference_id, pages, output_dir)

    with patch.object(mocked_processor, "_process_transcript", side_effect=explode_on_r2):
        summary = mocked_processor.process(tmp_path / "in", tmp_path / "out", workers=2)

    assert summary["successful_transcripts"] == 1
    assert summary["failed_transcripts"] == 1
    assert summary["failed_details"] == [
        {"collection": "A1", "reference_id": "r2", "error": "output not writable"}
    ]


def test_process_with_no_matches(mocked_processor, tmp_path):
    (tmp_path / "in").mkdir()
    summary = mocked_processor.process(tmp_path / "in", tmp_path / "out")
    assert summary["total_transcripts"] == 0
    assert not (tmp_path / "out").exists()


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def _fake_summary(**overrides):
    summary = {
        "success": True,
        "total_transcripts": 1,
        "successful_transcripts": 1,
        "failed_transcripts": 0,
        "total_pages": 2,
        "total_files_generated": 2,
        "total_ocr_errors": 0,
        "total_duration": 0.5,
        "failed_details": [],
    }
    summary.update(overrides)
    return summary


def test_cli_process_passes_options(tmp_path):
    with patch.object(transcript_main, "TranscriptBatchProcessor") as cls:
        cls.return_value.process.return_value = _fake_summary()
        result = runner.invoke(
            app,
            [
                "process", str(tmp_path), str(tmp_path / "out"),
                "--collection", "MSP00213", "--ref-ids", "r1, r2 ,r3",
                "--ocr-lang", "deu", "--dpi", "400", "--workers", "3",
            ],
        )

    assert result.exit_code == 0, result.output
    cls.assert_called_once_with(language="deu", dpi=400)
    cls.return_value.process.assert_called_once_with(
        input_dir=tmp_path,
        output_dir=tmp_path / "out",
        workers=3,
        collection_filter="MSP00213",
        ref_ids_filter={"r1", "r2", "r3"},
    )


def test_cli_ref_ids_file(tmp_path):
    refs = tmp_path / "refs.txt"
    refs.write_text("# header comment\nr1\n\n  r2  \n#r3\n")

    with patch.object(transcript_main, "TranscriptBatchProcessor") as cls:
        cls.return_value.process.return_value = _fake_summary()
        result = runner.invoke(
            app, ["process", str(tmp_path), str(tmp_path / "out"), "--ref-ids-file", str(refs)]
        )

    assert result.exit_code == 0, result.output
    assert cls.return_value.process.call_args.kwargs["ref_ids_filter"] == {"r1", "r2"}


def test_cli_ref_ids_takes_precedence_over_file(tmp_path):
    refs = tmp_path / "refs.txt"
    refs.write_text("from_file\n")

    with patch.object(transcript_main, "TranscriptBatchProcessor") as cls:
        cls.return_value.process.return_value = _fake_summary()
        runner.invoke(
            app,
            ["process", str(tmp_path), str(tmp_path / "out"),
             "--ref-ids", "from_flag", "--ref-ids-file", str(refs)],
        )

    assert cls.return_value.process.call_args.kwargs["ref_ids_filter"] == {"from_flag"}


def test_cli_missing_ref_ids_file(tmp_path):
    result = runner.invoke(
        app, ["process", str(tmp_path), str(tmp_path / "out"), "--ref-ids-file", str(tmp_path / "nope.txt")]
    )
    assert result.exit_code == 1
    assert "not found" in result.output


def test_cli_missing_input_dir(tmp_path):
    result = runner.invoke(app, ["process", str(tmp_path / "missing"), str(tmp_path / "out")])
    assert result.exit_code != 0


def test_cli_shows_failures(tmp_path):
    summary = _fake_summary(
        failed_transcripts=1,
        failed_details=[{"collection": "A1", "reference_id": "r2", "error": "disk full"}],
    )
    with patch.object(transcript_main, "TranscriptBatchProcessor") as cls:
        cls.return_value.process.return_value = summary
        result = runner.invoke(app, ["process", str(tmp_path), str(tmp_path / "out")])

    assert "A1/r2: disk full" in result.output


def test_cli_list_collections(tmp_path):
    for page in (1, 2):
        make_tiff(tmp_path / f"MSP00213_{REF_B}_0000{page}.tif")
    make_tiff(tmp_path / "OTHER1_xyz_00001.tif")

    result = runner.invoke(app, ["list-collections", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert "Found 2 transcripts across 2 collections (3 total pages)" in result.output
    assert "MSP00213" in result.output and REF_B in result.output


def test_cli_list_collections_empty(tmp_path):
    result = runner.invoke(app, ["list-collections", str(tmp_path)])
    assert result.exit_code == 0
    assert "No matching TIFF files found" in result.output


def test_cli_help_describes_per_page_output():
    for args in (["--help"], ["process", "--help"]):
        output = " ".join(runner.invoke(app, args).output.split())
        assert "combines pages" not in output
        assert "structured transcripts" not in output


def test_cli_warns_when_ref_ids_file_is_empty(tmp_path):
    make_tiff(tmp_path / "in" / "A1_r1_00001.tif")
    refs = tmp_path / "refs.txt"
    refs.write_text("# only comments\n\n")

    result = runner.invoke(
        app, ["process", str(tmp_path / "in"), str(tmp_path / "out"), "--ref-ids-file", str(refs)]
    )

    assert result.exit_code == 0, result.output
    assert "contains no reference IDs" in " ".join(result.output.split())
    assert not (tmp_path / "out").exists()  # nothing matched, nothing written
