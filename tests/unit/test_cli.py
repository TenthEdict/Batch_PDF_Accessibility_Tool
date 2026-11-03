"""
Tests for the Typer CLI (src/processor/main_simple.py).

Most tests patch the service/processor so they check argument wiring and
exit codes quickly; a few run the real pipeline on born-digital PDFs (no
OCR needed, so no Tesseract).
"""

import json
from pathlib import Path
from unittest.mock import patch

import pikepdf
import pytest
from typer.testing import CliRunner

from src.processor import main_simple
from src.processor.main_simple import app
from tests.pdf_factories import make_born_digital

pytestmark = pytest.mark.unit

runner = CliRunner()


def _summary(**overrides):
    summary = {
        "success": True,
        "total_files": 2,
        "processed": 2,
        "failed": 0,
        "total_duration": 1.5,
        "avg_duration_per_file": 0.75,
        "successful_files": [],
        "failed_files": [],
    }
    summary.update(overrides)
    return summary


# ----------------------------------------------------------------------
# General
# ----------------------------------------------------------------------


def test_help_lists_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("process", "batch-process", "version"):
        assert command in result.output


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Version" in result.output


# ----------------------------------------------------------------------
# process
# ----------------------------------------------------------------------


def test_process_missing_input(tmp_path):
    result = runner.invoke(
        app, ["process", str(tmp_path / "missing.pdf"), str(tmp_path / "out.pdf")]
    )
    assert result.exit_code == 1
    assert "Input file not found" in result.output


def test_process_passes_options_through(tmp_path):
    src = make_born_digital(tmp_path / "in.pdf")
    out = tmp_path / "out.pdf"

    with patch.object(main_simple, "SimpleEnhancementService") as service_cls:
        service_cls.return_value.enhance_document.return_value = True
        result = runner.invoke(
            app,
            [
                "process", str(src), str(out),
                "--title", "My Title", "--author", "A. Author",
                "--language", "fr-FR", "--force-ocr",
                "--text-threshold", "42", "--dpi", "400", "--ocr-lang", "fra",
            ],
        )

    assert result.exit_code == 0, result.output
    service_cls.assert_called_once_with(text_threshold=42, dpi=400, language="fra")
    service_cls.return_value.enhance_document.assert_called_once_with(
        input_path=src,
        output_path=out,
        title="My Title",
        author="A. Author",
        language="fr-FR",
        skip_ocr=False,
        force_ocr=True,
    )


def test_process_defaults(tmp_path):
    src = make_born_digital(tmp_path / "in.pdf")

    with patch.object(main_simple, "SimpleEnhancementService") as service_cls:
        service_cls.return_value.enhance_document.return_value = True
        result = runner.invoke(app, ["process", str(src), str(tmp_path / "o.pdf"), "--skip-ocr"])

    assert result.exit_code == 0, result.output
    service_cls.assert_called_once_with(text_threshold=100, dpi=300, language="eng")
    kwargs = service_cls.return_value.enhance_document.call_args.kwargs
    assert kwargs["title"] is None and kwargs["author"] is None
    assert kwargs["language"] is None  # resolved later: keep the PDF's own
    assert kwargs["skip_ocr"] is True and kwargs["force_ocr"] is False


@pytest.mark.parametrize(
    "behaviour, expected_text",
    [
        ({"return_value": False}, "Failed"),
        ({"side_effect": RuntimeError("boom")}, "boom"),
    ],
)
def test_process_failure_exit_code(tmp_path, behaviour, expected_text):
    src = make_born_digital(tmp_path / "in.pdf")

    with patch.object(main_simple, "SimpleEnhancementService") as service_cls:
        for attr, value in behaviour.items():
            setattr(service_cls.return_value.enhance_document, attr, value)
        result = runner.invoke(app, ["process", str(src), str(tmp_path / "o.pdf")])

    assert result.exit_code == 1
    assert expected_text in result.output


def test_process_end_to_end(tmp_path):
    src = make_born_digital(tmp_path / "in.pdf")
    out = tmp_path / "nested" / "out.pdf"

    result = runner.invoke(
        app, ["process", str(src), str(out), "--title", "CLI Title", "--author", "Tester"]
    )

    assert result.exit_code == 0, result.output
    assert "Success" in result.output
    with pikepdf.open(out) as pdf:
        assert bool(pdf.Root.MarkInfo.Marked) is False
        with pdf.open_metadata() as meta:
            assert meta.get("dc:title") == "CLI Title"
            assert "Tester" in str(meta.get("dc:creator"))
            assert "pdfuaid:part" not in meta


# ----------------------------------------------------------------------
# batch-process
# ----------------------------------------------------------------------


def test_batch_missing_input_dir(tmp_path):
    result = runner.invoke(
        app, ["batch-process", str(tmp_path / "missing"), str(tmp_path / "out")]
    )
    assert result.exit_code == 1
    assert "Input directory not found" in result.output


def test_batch_passes_options_through(tmp_path):
    with patch.object(main_simple, "SimpleBatchProcessor") as processor_cls:
        processor_cls.return_value.process_batch.return_value = _summary()
        result = runner.invoke(
            app,
            [
                "batch-process", str(tmp_path), str(tmp_path / "out"),
                "--workers", "3", "--no-recursive", "--skip-ocr",
                "--text-threshold", "7", "--dpi", "150", "--ocr-lang", "deu",
            ],
        )

    assert result.exit_code == 0, result.output
    processor_cls.assert_called_once_with(text_threshold=7, dpi=150, language="deu")
    processor_cls.return_value.process_batch.assert_called_once_with(
        input_dir=tmp_path,
        output_dir=tmp_path / "out",
        workers=3,
        recursive=False,
        skip_ocr=True,
        force_ocr=False,
    )


def test_batch_success_exits_zero(tmp_path):
    """Regression: typer.Exit(0) was swallowed by `except Exception` -> exit 1."""
    with patch.object(main_simple, "SimpleBatchProcessor") as processor_cls:
        processor_cls.return_value.process_batch.return_value = _summary()
        result = runner.invoke(app, ["batch-process", str(tmp_path), str(tmp_path / "out")])

    assert result.exit_code == 0, result.output
    assert "Batch processing complete" in result.output
    assert "Error" not in result.output


def test_batch_partial_failure_exits_one_and_lists_files(tmp_path):
    summary = _summary(
        processed=1, failed=1,
        failed_files=[{"file": "bad.pdf", "error": "corrupt xref"}],
    )
    with patch.object(main_simple, "SimpleBatchProcessor") as processor_cls:
        processor_cls.return_value.process_batch.return_value = summary
        result = runner.invoke(app, ["batch-process", str(tmp_path), str(tmp_path / "out")])

    assert result.exit_code == 1
    assert "bad.pdf" in result.output and "corrupt xref" in result.output


def test_batch_processor_reports_failure(tmp_path):
    with patch.object(main_simple, "SimpleBatchProcessor") as processor_cls:
        processor_cls.return_value.process_batch.return_value = {
            "success": False, "error": "disk full"
        }
        result = runner.invoke(app, ["batch-process", str(tmp_path), str(tmp_path / "out")])

    assert result.exit_code == 1
    assert "disk full" in result.output


def test_batch_empty_directory_exits_zero(tmp_path):
    """No PDFs is not an error; the summary for it lacks duration fields."""
    (tmp_path / "in").mkdir()
    result = runner.invoke(
        app, ["batch-process", str(tmp_path / "in"), str(tmp_path / "out")]
    )
    assert result.exit_code == 0, result.output
    assert "No PDF files found" in result.output


def test_batch_end_to_end_preserves_structure(tmp_path):
    in_dir = tmp_path / "in"
    (in_dir / "a" / "b").mkdir(parents=True)
    make_born_digital(in_dir / "top.pdf")
    make_born_digital(in_dir / "a" / "b" / "deep.pdf")
    out_dir = tmp_path / "out"

    result = runner.invoke(
        app, ["batch-process", str(in_dir), str(out_dir), "--workers", "2"]
    )

    assert result.exit_code == 0, result.output
    assert (out_dir / "top.pdf").exists()
    assert (out_dir / "a" / "b" / "deep.pdf").exists()

    # The summary file the CLI tells the user about must exist
    summary_path = out_dir / "batch_processing_summary.json"
    assert summary_path.name in result.output.replace("\n", "")  # Rich wraps at 80 cols
    summary = json.loads(summary_path.read_text())
    assert summary["processed"] == 2 and summary["failed"] == 0


def test_batch_no_recursive_skips_subdirectories(tmp_path):
    in_dir = tmp_path / "in"
    (in_dir / "sub").mkdir(parents=True)
    make_born_digital(in_dir / "top.pdf")
    make_born_digital(in_dir / "sub" / "nested.pdf")
    out_dir = tmp_path / "out"

    result = runner.invoke(
        app, ["batch-process", str(in_dir), str(out_dir), "--no-recursive"]
    )

    assert result.exit_code == 0, result.output
    assert (out_dir / "top.pdf").exists()
    assert not (out_dir / "sub" / "nested.pdf").exists()


def test_batch_unexpected_exception_exits_one(tmp_path):
    with patch.object(main_simple, "SimpleBatchProcessor") as processor_cls:
        processor_cls.return_value.process_batch.side_effect = OSError("no space left")
        result = runner.invoke(app, ["batch-process", str(tmp_path), str(tmp_path / "out")])

    assert result.exit_code == 1
    assert "no space left" in result.output


def test_help_text_makes_no_pdfua_compliance_claim():
    """Output is untagged until Acrobat tags it, so the CLI must not promise PDF/UA."""
    for args in (["--help"], ["process", "--help"], ["version"]):
        output = runner.invoke(app, args).output.replace("\n", " ")
        assert "PDF/UA-1 compliance" not in output
        assert "PDF/UA-1 metadata compliance" not in output
