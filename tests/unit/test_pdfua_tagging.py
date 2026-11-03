"""
Unit tests for tag cleanup, OCR-layer flattening and tagging-state metadata.

None of these need Tesseract: OCR text layers are built synthetically in
the same shape ocrmypdf produces (a /OCR-... Form XObject).
"""

from pathlib import Path
from unittest.mock import patch

import fitz
import pikepdf
import pytest
from pikepdf import Array, Dictionary, Name

from src.processor.simple_enhancement_service import SimpleEnhancementService
from src.processor.simple_ocr_enhancer import SimpleOCREnhancer
from src.processor.simple_pdfua_enhancer import SimplePDFUAEnhancer
from tests.pdf_factories import (
    make_born_digital,
    make_orphan_tagged,
    make_tagged,
    marked_content_tags,
    pdfua_claim,
    renders_identically,
    shown_strings,
    words,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def enhancer() -> SimplePDFUAEnhancer:
    return SimplePDFUAEnhancer()


def _enhance(enhancer, src: Path, dst: Path, ocr_performed: bool) -> Path:
    assert enhancer.enhance_file(src, dst, title="T", ocr_performed=ocr_performed)
    return dst


# ----------------------------------------------------------------------
# Orphan tag stripping
# ----------------------------------------------------------------------


def test_orphan_tags_stripped_but_layers_artifacts_and_text_kept(enhancer, tmp_path):
    src = make_orphan_tagged(tmp_path / "orphan.pdf")
    out = _enhance(enhancer, src, tmp_path / "out.pdf", ocr_performed=False)

    assert marked_content_tags(src) == ["/P", "/Span", "/OC", "/Artifact"]
    assert marked_content_tags(out) == ["/OC", "/Artifact"]
    # Strings containing "EMC" survive (the old regex deleted them)
    assert shown_strings(out) == shown_strings(src)
    # Hidden layer stays hidden, nothing else moves
    assert renders_identically(src, out)

    with pikepdf.open(out) as pdf:
        assert pdf.check() == []
        page = pdf.pages[0].obj
        assert Name.StructParents not in page
        assert all(Name.StructParent not in annot for annot in page.Annots)


def test_orphan_file_loses_legacy_pdfua_claims(enhancer, tmp_path):
    src = make_orphan_tagged(tmp_path / "orphan.pdf", legacy_claims=True)
    out = _enhance(enhancer, src, tmp_path / "out.pdf", ocr_performed=False)

    assert pdfua_claim(src) == "1"
    assert pdfua_claim(out) is None
    with pikepdf.open(out) as pdf:
        assert Name.OutputIntents not in pdf.Root
        assert bool(pdf.Root.MarkInfo.Marked) is False
        assert Name.Suspects not in pdf.Root.MarkInfo


def test_other_output_intents_are_kept(enhancer, tmp_path):
    src = make_orphan_tagged(tmp_path / "orphan.pdf")
    with pikepdf.open(src, allow_overwriting_input=True) as pdf:
        pdf.Root.OutputIntents.append(
            Dictionary(Type=Name.OutputIntent, S=Name.GTS_PDFA1)
        )
        pdf.save(src)

    out = _enhance(enhancer, src, tmp_path / "out.pdf", ocr_performed=False)
    with pikepdf.open(out) as pdf:
        assert [str(i.S) for i in pdf.Root.OutputIntents] == ["/GTS_PDFA1"]


# ----------------------------------------------------------------------
# Valid tagged files
# ----------------------------------------------------------------------


def test_tagged_file_untouched_when_no_ocr(enhancer, tmp_path):
    src = make_tagged(tmp_path / "tagged.pdf")
    out = _enhance(enhancer, src, tmp_path / "out.pdf", ocr_performed=False)

    assert marked_content_tags(out) == marked_content_tags(src)
    assert pdfua_claim(out) == "1"  # the file's own claim, backed by real tags
    with pikepdf.open(out) as pdf:
        assert Name.StructTreeRoot in pdf.Root
        assert bool(pdf.Root.MarkInfo.Marked) is True
        assert Name.StructParents in pdf.pages[0].obj


def test_tagged_file_tree_removed_after_ocr(enhancer, tmp_path):
    """After OCR the tree is incomplete, so it and its MCIDs are removed."""
    src = make_tagged(tmp_path / "tagged.pdf")
    out = _enhance(enhancer, src, tmp_path / "out.pdf", ocr_performed=True)

    assert marked_content_tags(out) == ["/OC", "/Artifact"]
    assert pdfua_claim(out) is None
    with pikepdf.open(out) as pdf:
        assert Name.StructTreeRoot not in pdf.Root
        assert bool(pdf.Root.MarkInfo.Marked) is False


def test_service_keeps_tags_when_ocr_not_needed(tmp_path):
    """
    Regression: ocr_performed used to be `not skip_ocr`, so a tagged file that
    was merely copied through OCR lost its tree and kept orphaned MCIDs.
    """
    src = make_tagged(tmp_path / "tagged.pdf")
    out = tmp_path / "out" / "tagged.pdf"

    assert SimpleEnhancementService().enhance_document(src, out)

    assert marked_content_tags(out) == marked_content_tags(src)
    with pikepdf.open(out) as pdf:
        assert Name.StructTreeRoot in pdf.Root


def test_ocr_enhancer_reports_copy_as_not_performed(tmp_path):
    src = make_born_digital(tmp_path / "digital.pdf")
    out = tmp_path / "copy.pdf"

    assert SimpleOCREnhancer().enhance_file_with_status(src, out) == (True, False)
    assert SimpleOCREnhancer().enhance_file(src, tmp_path / "copy2.pdf") is True


def test_ocr_enhancer_missing_input(tmp_path):
    status = SimpleOCREnhancer().enhance_file_with_status(
        tmp_path / "missing.pdf", tmp_path / "out.pdf"
    )
    assert status == (False, False)


# ----------------------------------------------------------------------
# Marked-content stripper edge cases
# ----------------------------------------------------------------------


def _ops(content: bytes):
    pdf = pikepdf.new()
    return pikepdf.parse_content_stream(pdf.make_stream(content))


def _op_names(instructions):
    return [
        "INLINE" if isinstance(i, pikepdf.ContentStreamInlineImage) else str(i.operator)
        for i in instructions
    ]


def test_stripper_returns_none_when_nothing_to_strip(enhancer):
    ops = _ops(b"/OC /MC0 BDC BT (x) Tj ET EMC")
    assert enhancer._strip_marked_content(ops) is None


def test_stripper_matches_nested_pairs(enhancer):
    ops = _ops(b"/P <</MCID 0>> BDC /OC /MC0 BDC BT (x) Tj ET EMC EMC")
    result = enhancer._strip_marked_content(ops)
    assert _op_names(result) == ["BDC", "BT", "Tj", "ET", "EMC"]
    assert str(result[0].operands[0]) == "/OC"


def test_stripper_drops_unmatched_emc(enhancer):
    result = enhancer._strip_marked_content(_ops(b"BT (x) Tj ET EMC"))
    assert _op_names(result) == ["BT", "Tj", "ET"]


def test_stripper_preserves_inline_images(enhancer):
    content = b"/Figure <</MCID 3>> BDC q 10 0 0 10 0 0 cm BI /W 1 /H 1 /CS /G /BPC 8 ID \x80 EI Q EMC"
    result = enhancer._strip_marked_content(_ops(content))
    assert _op_names(result) == ["q", "cm", "INLINE", "Q"]


def test_orphan_marked_content_in_nested_forms(enhancer, tmp_path):
    pdf = pikepdf.new()
    inner = pdf.make_stream(
        b"/Span <</MCID 1>> BDC 0 0 m 10 10 l S EMC",
        Type=Name.XObject, Subtype=Name.Form, BBox=Array([0, 0, 100, 100]),
        StructParent=2,
    )
    outer = pdf.make_stream(
        b"/P <</MCID 0>> BDC /Inner Do EMC",
        Type=Name.XObject, Subtype=Name.Form, BBox=Array([0, 0, 100, 100]),
        Resources=Dictionary(XObject=Dictionary(Inner=inner)),
        StructParents=1,
    )
    page = Dictionary(
        Type=Name.Page, MediaBox=Array([0, 0, 200, 200]),
        Resources=Dictionary(XObject=Dictionary(Outer=outer)),
    )
    pdf.pages.append(pikepdf.Page(page))
    pdf.pages[0].obj.Contents = pdf.make_stream(b"q /Outer Do Q")
    src = tmp_path / "forms.pdf"
    pdf.save(src)

    out = _enhance(enhancer, src, tmp_path / "out.pdf", ocr_performed=False)

    with pikepdf.open(out) as result:
        outer = result.pages[0].obj.Resources.XObject.Outer
        inner = outer.Resources.XObject.Inner
        for form in (outer, inner):
            assert Name.StructParent not in form and Name.StructParents not in form
            ops = _op_names(pikepdf.parse_content_stream(form))
            assert "BDC" not in ops and "EMC" not in ops
    assert renders_identically(src, out)


# ----------------------------------------------------------------------
# OCR text layer flattening (synthetic ocrmypdf-shaped layer)
# ----------------------------------------------------------------------


def _make_ocr_layered(
    path: Path,
    page_prefix: bytes = b"",
    form_matrix=None,
    form_extra_resources=None,
) -> Path:
    """
    A page shaped like ocrmypdf output: an /OCR-... Form XObject with
    invisible (3 Tr) text, drawn before the visible content.

    The page and form both name their font /F1 but use *different* fonts,
    to exercise the collision-renaming path.
    """
    pdf = pikepdf.new()
    helvetica = pdf.make_indirect(
        Dictionary(Type=Name.Font, Subtype=Name.Type1, BaseFont=Name.Helvetica)
    )
    courier = pdf.make_indirect(
        Dictionary(Type=Name.Font, Subtype=Name.Type1, BaseFont=Name.Courier)
    )
    form_resources = Dictionary(Font=Dictionary(F1=courier))
    for key, value in (form_extra_resources or {}).items():
        form_resources[key] = value
    form = pdf.make_stream(
        b"BT 3 Tr /F1 12 Tf 72 500 Td (Invisible OCR words) Tj ET\n"
        b"BT 3 Tr /F1 12 Tf 72 480 Td (Second OCR line) Tj ET",
        Type=Name.XObject, Subtype=Name.Form, BBox=Array([0, 0, 612, 792]),
        Resources=form_resources,
    )
    if form_matrix is not None:
        form.Matrix = Array(form_matrix)
    page = Dictionary(
        Type=Name.Page, MediaBox=Array([0, 0, 612, 792]),
        Resources=Dictionary(
            Font=Dictionary(F1=helvetica),
            XObject=Dictionary({"/OCR-testlayer": form}),
        ),
    )
    pdf.pages.append(pikepdf.Page(page))
    pdf.pages[0].obj.Contents = pdf.make_stream(
        page_prefix
        + b"q 0.5 0 0 0.5 20 30 cm /OCR-testlayer Do Q\n"
        b"BT /F1 14 Tf 72 700 Td (Visible text) Tj ET"
    )
    pdf.save(path)
    return path


def _fonts_by_word(path: Path) -> dict:
    with fitz.open(path) as doc:
        return {
            span["text"]: span["font"]
            for block in doc[0].get_text("dict")["blocks"]
            for line in block.get("lines", [])
            for span in line["spans"]
        }


@pytest.mark.parametrize(
    "page_prefix, form_matrix",
    [
        (b"", None),
        (b"", [1, 0, 0, 1, 10, -15]),
        # Unbalanced cm with no q, as written by the MediaBox normalizer
        (b"1 0 0 1 0 -40 cm\n", None),
        (b"1 0 0 1 0 -40 cm\n", [0.9, 0, 0, 1.1, 5, 5]),
    ],
)
def test_flatten_preserves_positions_and_fonts(enhancer, tmp_path, page_prefix, form_matrix):
    src = _make_ocr_layered(tmp_path / "layered.pdf", page_prefix, form_matrix)
    out = _enhance(enhancer, src, tmp_path / "out.pdf", ocr_performed=True)

    with pikepdf.open(out) as pdf:
        resources = pdf.pages[0].obj.Resources
        assert not any(str(n).startswith("/OCR-") for n in resources.XObject.keys())
        assert Name("/OCRf0") in resources.Font  # colliding /F1 was renamed
        assert pdf.check() == []

    assert words(out) == words(src)
    assert _fonts_by_word(out) == _fonts_by_word(src)
    assert renders_identically(src, out)


def test_flatten_puts_text_after_visible_content(enhancer, tmp_path):
    src = _make_ocr_layered(tmp_path / "layered.pdf")
    out = _enhance(enhancer, src, tmp_path / "out.pdf", ocr_performed=True)
    assert shown_strings(out) == [
        b"Visible text", b"Invisible OCR words", b"Second OCR line"
    ]


def test_flatten_runs_even_when_ocr_skipped(enhancer, tmp_path):
    """Inputs OCR'd earlier (e.g. by older versions of this tool) get flattened too."""
    src = _make_ocr_layered(tmp_path / "layered.pdf")
    out = _enhance(enhancer, src, tmp_path / "out.pdf", ocr_performed=False)
    with pikepdf.open(out) as pdf:
        assert "/OCR-testlayer" not in pdf.pages[0].obj.Resources.XObject


def test_flatten_skips_forms_with_non_font_resources(enhancer, tmp_path):
    src = _make_ocr_layered(
        tmp_path / "layered.pdf",
        form_extra_resources={"/ExtGState": Dictionary(GS0=Dictionary(CA=0.5))},
    )
    out = _enhance(enhancer, src, tmp_path / "out.pdf", ocr_performed=True)
    with pikepdf.open(out) as pdf:
        assert "/OCR-testlayer" in pdf.pages[0].obj.Resources.XObject
    assert words(out) == words(src)


def test_flatten_to_temp(enhancer, tmp_path):
    layered = _make_ocr_layered(tmp_path / "layered.pdf")
    flattened = enhancer.flatten_ocr_layers_to_temp(layered)
    try:
        assert flattened is not None and flattened.exists()
        assert words(flattened) == words(layered)
    finally:
        if flattened:
            flattened.unlink()

    plain = make_born_digital(tmp_path / "plain.pdf")
    assert enhancer.flatten_ocr_layers_to_temp(plain) is None


# ----------------------------------------------------------------------
# Detecting whether ocrmypdf actually added text
# ----------------------------------------------------------------------


def _with_ocr_form(path: Path, form_content: bytes) -> Path:
    pdf = pikepdf.new()
    form = pdf.make_stream(
        form_content, Type=Name.XObject, Subtype=Name.Form, BBox=Array([0, 0, 612, 792])
    )
    page = Dictionary(
        Type=Name.Page, MediaBox=Array([0, 0, 612, 792]),
        Resources=Dictionary(XObject=Dictionary({"/OCR-abc": form})),
    )
    pdf.pages.append(pikepdf.Page(page))
    pdf.pages[0].obj.Contents = pdf.make_stream(b"q /OCR-abc Do Q")
    pdf.save(path)
    return path


@pytest.mark.parametrize(
    "content, expected",
    [
        (b"q 612 0 0 792 0 0 cm Q\n", 0),  # empty layer redo_ocr grafts on text pages
        (b"BT 3 Tr /F1 10 Tf 72 700 Td (word) Tj ET", 1),
        (b"BT 3 Tr /F1 10 Tf 72 700 Td [(wo) 10 (rd)] TJ ET", 1),
    ],
)
def test_count_ocr_text_layers(tmp_path, content, expected):
    path = _with_ocr_form(tmp_path / "layer.pdf", content)
    assert SimpleOCREnhancer._count_ocr_text_layers(path) == expected


def test_count_ocr_text_layers_without_layer(tmp_path):
    assert SimpleOCREnhancer._count_ocr_text_layers(make_born_digital(tmp_path / "d.pdf")) == 0


def test_count_ocr_text_layers_unreadable_assumes_text(tmp_path):
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"not a pdf")
    assert SimpleOCREnhancer._count_ocr_text_layers(bad) == 1


def test_force_ocr_with_empty_layer_keeps_tags(tmp_path):
    """
    ocrmypdf's redo mode grafted an empty /OCR- layer (``q ... cm Q``) on a
    real Word export whose text was all real; the tag tree must survive.
    """
    import shutil

    import ocrmypdf

    def fake_ocr(input_file, output_file, **options):
        assert options["redo_ocr"] is True
        shutil.copy(input_file, output_file)
        with pikepdf.open(output_file, allow_overwriting_input=True) as pdf:
            page = pdf.pages[0].obj
            form = pdf.make_stream(
                b"q 612 0 0 792 0 0 cm Q\n",
                Type=Name.XObject, Subtype=Name.Form, BBox=Array([0, 0, 612, 792]),
            )
            if Name.XObject not in page.Resources:
                page.Resources.XObject = Dictionary()
            page.Resources.XObject["/OCR-empty"] = form
            page.Contents = pdf.make_stream(b"q /OCR-empty Do Q\n" + page.Contents.read_bytes())
            pdf.save(output_file)

    src = make_tagged(tmp_path / "tagged.pdf", body_lines=0)
    out = tmp_path / "out.pdf"
    with patch.object(ocrmypdf, "ocr", side_effect=fake_ocr):
        status = SimpleOCREnhancer().enhance_file_with_status(src, tmp_path / "ocr.pdf", force_ocr=True)
        assert status == (True, False)
        assert SimpleEnhancementService().enhance_document(src, out, force_ocr=True)

    assert marked_content_tags(out) == marked_content_tags(src)
    assert renders_identically(src, out)
    with pikepdf.open(out) as pdf:
        assert Name.StructTreeRoot in pdf.Root


# ----------------------------------------------------------------------
# Document language
# ----------------------------------------------------------------------


def _with_lang(path: Path, lang) -> Path:
    make_born_digital(path)
    if lang is not None:
        with pikepdf.open(path, allow_overwriting_input=True) as pdf:
            pdf.Root.Lang = pikepdf.String(lang)
            pdf.save(path)
    return path


def _lang(path: Path):
    with pikepdf.open(path) as pdf:
        with pdf.open_metadata() as meta:
            return str(pdf.Root.Lang), meta.get("dc:language")


@pytest.mark.parametrize(
    "existing, requested, expected",
    [
        ("en", None, "en"),          # Word export: keep the document's own
        ("fr-CA", None, "fr-CA"),
        (None, None, "en-US"),       # nothing declared: default
        ("  ", None, "en-US"),       # blank counts as nothing
        ("en", "de-DE", "de-DE"),    # explicit --language wins
    ],
)
def test_document_language_resolution(enhancer, tmp_path, existing, requested, expected):
    src = _with_lang(tmp_path / "in.pdf", existing)
    out = tmp_path / "out.pdf"
    assert enhancer.enhance_file(src, out, language=requested)
    lang, dc_language = _lang(out)
    assert lang == expected
    assert expected in str(dc_language)


def test_cli_keeps_document_language_by_default(tmp_path):
    from typer.testing import CliRunner

    from src.processor.main_simple import app

    src = _with_lang(tmp_path / "in.pdf", "en")
    out = tmp_path / "out.pdf"
    result = CliRunner().invoke(app, ["process", str(src), str(out), "--skip-ocr"])
    assert result.exit_code == 0, result.output
    assert _lang(out)[0] == "en"
