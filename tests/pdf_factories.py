"""
Builders and inspectors for PDFs used by the tagging/OCR tests.

Everything is generated in code so no binary fixtures are checked in.
"""

import shutil
from pathlib import Path
from typing import List, Optional

import fitz  # PyMuPDF
import pikepdf
from pikepdf import Array, Dictionary, Name, String

TESSERACT_AVAILABLE = shutil.which("tesseract") is not None

BODY_LINES = 12  # comfortably above the 100 chars/page OCR threshold


# ----------------------------------------------------------------------
# Builders
# ----------------------------------------------------------------------


def make_born_digital(path: Path, pages: int = 2) -> Path:
    """Text PDF with a real (non-OCR) text layer and no tags."""
    doc = fitz.open()
    for page_num in range(pages):
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


def make_scanned(path: Path, pages: int = 1, dpi: int = 200) -> Path:
    """Image-only PDF: a born-digital page rasterized to grayscale."""
    source = fitz.open(make_born_digital(path.with_suffix(".src.pdf"), pages))
    scanned = fitz.open()
    for page in source:
        pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
        new_page = scanned.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, pixmap=pix)
    scanned.save(path)
    scanned.close()
    source.close()
    path.with_suffix(".src.pdf").unlink()
    return path


def _marked_content_stream(body_lines: int = BODY_LINES) -> bytes:
    """
    Content mixing every kind of marked content the stripper must handle.

    - /P and /Span with MCIDs (structure, strip when orphaned)
    - /OC optional content on a hidden layer (keep: controls visibility)
    - /Artifact pagination (keep: meaningful without a tag tree)
    - strings containing "EMC" (must survive untouched)
    """
    body = b"".join(
        b"BT /F1 11 Tf 72 %d Td (Body line %d of the marked content fixture.) Tj ET\n"
        % (640 - i * 16, i)
        for i in range(body_lines)
    )
    return (
        b"/P <</MCID 0>> BDC BT /F1 18 Tf 72 700 Td (Heading EMC test) Tj ET EMC\n"
        b"/Span <</ActualText <FEFF0041> /MCID 1>> BDC\n"
        b"BT /F1 12 Tf 72 670 Td (Text with EMCEE inside) Tj ET EMC\n" + body +
        b"/OC /MC0 BDC BT /F1 12 Tf 72 400 Td (Secret hidden layer) Tj ET EMC\n"
        b"/Artifact <</Type /Pagination>> BDC BT /F1 9 Tf 300 40 Td (Page 1) Tj ET EMC\n"
    )


def _base_marked_pdf(content: bytes) -> pikepdf.Pdf:
    pdf = pikepdf.new()
    font = pdf.make_indirect(
        Dictionary(Type=Name.Font, Subtype=Name.Type1, BaseFont=Name.Helvetica)
    )
    ocg = pdf.make_indirect(Dictionary(Type=Name.OCG, Name=String("Hidden layer")))
    pdf.Root.OCProperties = Dictionary(
        OCGs=Array([ocg]), D=Dictionary(OFF=Array([ocg]), Order=Array([ocg]))
    )
    page = Dictionary(
        Type=Name.Page,
        MediaBox=Array([0, 0, 612, 792]),
        Resources=Dictionary(
            Font=Dictionary(F1=font), Properties=Dictionary(MC0=ocg)
        ),
    )
    pdf.pages.append(pikepdf.Page(page))
    # Deliberately uncompressed: the old regex stripper corrupted these
    pdf.pages[0].obj.Contents = pdf.make_stream(content)
    pdf.pages[0].obj.StructParents = 0
    return pdf


def make_orphan_tagged(path: Path, legacy_claims: bool = True) -> Path:
    """
    MCIDs and StructParents, but no StructTreeRoot.

    With legacy_claims, also carries the PDF/UA claims older versions of
    this tool wrote (GTS_PDFUA1 OutputIntent, pdfuaid:part).
    """
    pdf = _base_marked_pdf(_marked_content_stream())
    annot = pdf.make_indirect(
        Dictionary(
            Type=Name.Annot,
            Subtype=Name.Link,
            Rect=Array([72, 700, 200, 720]),
            StructParent=1,
        )
    )
    pdf.pages[0].obj.Annots = Array([annot])
    if legacy_claims:
        pdf.Root.OutputIntents = Array(
            [Dictionary(Type=Name.OutputIntent, S=Name.GTS_PDFUA1)]
        )
        with pdf.open_metadata() as meta:
            meta["pdfuaid:part"] = "1"
    pdf.save(path)
    return path


def make_tagged(path: Path, body_lines: int = BODY_LINES) -> Path:
    """
    A minimal but valid tagged PDF (StructTreeRoot + ParentTree) claiming PDF/UA.

    body_lines=0 gives a short document (under the 100 chars/page OCR
    threshold), like a one-page Word export with a heading and a table.
    """
    pdf = _base_marked_pdf(_marked_content_stream(body_lines))
    page = pdf.pages[0].obj
    document = pdf.make_indirect(Dictionary(Type=Name.StructElem, S=Name.Document))
    heading = pdf.make_indirect(
        Dictionary(Type=Name.StructElem, S=Name.H1, P=document, Pg=page, K=0)
    )
    para = pdf.make_indirect(
        Dictionary(Type=Name.StructElem, S=Name.P, P=document, Pg=page, K=1)
    )
    document.K = Array([heading, para])
    root = pdf.make_indirect(
        Dictionary(
            Type=Name.StructTreeRoot,
            K=document,
            ParentTree=Dictionary(Nums=Array([0, Array([heading, para])])),
        )
    )
    document.P = root
    pdf.Root.StructTreeRoot = root
    pdf.Root.MarkInfo = Dictionary(Marked=True)
    with pdf.open_metadata() as meta:
        meta["pdfuaid:part"] = "1"
    pdf.save(path)
    return path


# ----------------------------------------------------------------------
# Inspectors
# ----------------------------------------------------------------------


def ocr_form_count(path: Path) -> int:
    """Number of ocrmypdf text-layer Form XObjects (/OCR-...) on page level."""
    with pikepdf.open(path) as pdf:
        return sum(
            1
            for page in pdf.pages
            for name in page.obj.get(Name.Resources, {}).get(Name.XObject, {}).keys()
            if str(name).startswith("/OCR-")
        )


def marked_content_tags(path: Path, page_index: int = 0) -> List[str]:
    """Tags of every BMC/BDC on a page, in order."""
    with pikepdf.open(path) as pdf:
        return [
            str(instr.operands[0])
            for instr in pikepdf.parse_content_stream(pdf.pages[page_index])
            if not isinstance(instr, pikepdf.ContentStreamInlineImage)
            and str(instr.operator) in ("BMC", "BDC")
        ]


def shown_strings(path: Path, page_index: int = 0) -> List[bytes]:
    """Operands of every Tj on a page."""
    with pikepdf.open(path) as pdf:
        return [
            bytes(instr.operands[0])
            for instr in pikepdf.parse_content_stream(pdf.pages[page_index])
            if not isinstance(instr, pikepdf.ContentStreamInlineImage)
            and str(instr.operator) == "Tj"
        ]


def words(path: Path) -> List[list]:
    """
    Per-page word boxes and text, rounded to absorb float noise.

    Sorted, because flattening intentionally changes paint order (OCR text
    moves after the image) and extraction order follows paint order.
    """
    with fitz.open(path) as doc:
        return [
            sorted(
                [round(v, 2) for v in w[:4]] + [w[4]] for w in page.get_text("words")
            )
            for page in doc
        ]


def renders_identically(a: Path, b: Path, dpi: int = 72) -> bool:
    with fitz.open(a) as doc_a, fitz.open(b) as doc_b:
        if len(doc_a) != len(doc_b):
            return False
        return all(
            pa.get_pixmap(dpi=dpi).samples == pb.get_pixmap(dpi=dpi).samples
            for pa, pb in zip(doc_a, doc_b)
        )


def pdfua_claim(path: Path) -> Optional[str]:
    with pikepdf.open(path) as pdf:
        with pdf.open_metadata() as meta:
            return meta.get("pdfuaid:part")
