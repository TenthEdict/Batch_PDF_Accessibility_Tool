#!/usr/bin/env python3
"""
Simplified PDF/UA enhancer with orphan tag stripping and basic metadata.

This enhancer prepares files for tagging in Acrobat (it does not tag them,
so output does not claim PDF/UA-1 conformance):
- Orphan tag stripping (critical for Adobe Acrobat workflow)
- OCR text layer flattening (keeps Acrobat autotag from tagging pages as Figures)
- Document properties (title, author, language)
- No mathematical notation detection
- No ML-based accessibility features
"""

import logging
from pathlib import Path
from typing import Union, Optional
from datetime import datetime

try:
    import pikepdf
    from pikepdf import Pdf, Name, String, Dictionary, Array
except ImportError:
    raise ImportError(
        "pikepdf is required for SimplePDFUAEnhancer. "
        "Install it with: pip install pikepdf"
    )

logger = logging.getLogger(__name__)


class SimplePDFUAEnhancer:
    """
    Simplified PDF/UA enhancer for basic compliance and orphan tag stripping.

    Features:
    - Orphan tag stripping (removes malformed marked content operators)
    - Accurate MarkInfo / no false PDF/UA-1 claims
    - Basic document properties (title, author, language)
    - Clean, untagged structure for Acrobat tagging
    """

    def __init__(self):
        """Initialize the simple PDF/UA enhancer."""
        self.name = "simple_pdfua_enhancer"
        logger.info("SimplePDFUAEnhancer initialized")

    def enhance_file(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        title: Optional[str] = None,
        author: Optional[str] = None,
        language: str = "en-US",
        ocr_performed: bool = False,
        **kwargs
    ) -> bool:
        """
        Apply PDF/UA-1 compliance enhancements to a PDF file.

        Args:
            input_path: Path to the input PDF
            output_path: Path where the enhanced PDF should be saved
            title: Document title (default: extracted from filename)
            author: Document author (default: None)
            language: Document language (default: "en-US")
            ocr_performed: Whether OCR was just performed (default: False)
            **kwargs: Additional parameters (ignored for simplicity)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)

            if not input_path.exists():
                logger.error(f"Input file not found: {input_path}")
                return False

            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Load PDF
            logger.info(f"Loading PDF: {input_path}")
            document = pikepdf.open(input_path)

            # Apply enhancements
            self._enhance(document, input_path, title, author, language, ocr_performed)

            # Save enhanced PDF
            logger.info(f"Saving enhanced PDF: {output_path}")
            document.save(output_path)
            document.close()

            logger.info(f"PDF/UA enhancement complete: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error in PDF/UA enhancement: {e}")
            return False

    def _enhance(
        self,
        document: pikepdf.Pdf,
        input_path: Path,
        title: Optional[str],
        author: Optional[str],
        language: str,
        ocr_performed: bool = False
    ) -> None:
        """
        Apply PDF/UA-1 enhancements to document.

        Args:
            document: The PDF document to enhance
            input_path: Path to original PDF (for title extraction)
            title: Document title
            author: Document author
            language: Document language
            ocr_performed: Whether OCR was just performed
        """
        # Step 1: Clean up tag structure
        if ocr_performed:
            # OCR added untagged text, so any existing tag tree is now incomplete.
            # Remove it so Acrobat builds a complete tag structure from scratch.
            self._remove_incomplete_struct_tree(document)

        # Without a StructTreeRoot, any structure-linked marked content (MCIDs)
        # is orphaned. Strip it. Valid tagged files (no OCR) are left untouched.
        pages_cleaned = self._strip_orphan_tags(document)
        if pages_cleaned > 0:
            logger.info(f"Stripped orphan tags from {pages_cleaned} pages")

        # Move ocrmypdf's text layer out of its Form XObject into the page.
        # Runs even when OCR was skipped: inputs OCR'd earlier by ocrmypdf
        # (or by older versions of this tool) have the same layout.
        flattened = self._flatten_ocr_text_layers(document)
        if flattened > 0:
            logger.info(f"Flattened OCR text layer into page content on {flattened} pages")

        # Step 2: Determine title if not provided
        if not title:
            title = self._extract_title(document, input_path)

        # Step 3: Update document metadata
        self._update_metadata(document, title, author, language)

        # Step 4: Set tagging state and language (no compliance claims)
        self._set_tagging_state(document, language)

        logger.info("Applied PDF/UA-1 enhancements")

    def _remove_incomplete_struct_tree(self, document: pikepdf.Pdf) -> None:
        """
        Remove the StructTreeRoot and the page-level references into it.

        Called after OCR: the new text layer is untagged, so any existing tag
        tree is incomplete. Marked content operators left in the content
        streams are cleaned up afterwards by _strip_orphan_tags().
        (ocrmypdf 16 emits no marked content of its own.)

        Args:
            document: The PDF document to clean
        """
        if Name.StructTreeRoot in document.Root:
            del document.Root[Name.StructTreeRoot]
            logger.info("Removed StructTreeRoot")

    # ------------------------------------------------------------------
    # OCR text layer flattening
    # ------------------------------------------------------------------

    def flatten_ocr_layers_to_temp(self, input_path: Union[str, Path]) -> Optional[Path]:
        """
        Write a copy of input_path with ocrmypdf text layers flattened.

        Used before --force-ocr: ocrmypdf's redo_ocr can find and replace
        invisible text in page content, but not text inside the Form XObjects
        it creates itself, so re-OCRing old output would duplicate the text.

        Returns:
            Path to a temporary PDF (caller deletes it), or None if the input
            had no ocrmypdf text layers.
        """
        import os
        import tempfile

        with pikepdf.open(input_path) as document:
            if self._flatten_ocr_text_layers(document) == 0:
                return None
            fd, temp_path = tempfile.mkstemp(suffix=".pdf", prefix="flattened_")
            os.close(fd)
            document.save(temp_path)
        logger.info("Flattened existing OCR text layer before re-running OCR")
        return Path(temp_path)

    @staticmethod
    def _matmul(m, n):
        """Multiply two PDF matrices (a b c d e f): result = m x n."""
        a1, b1, c1, d1, e1, f1 = m
        a2, b2, c2, d2, e2, f2 = n
        return (
            a1 * a2 + b1 * c2,
            a1 * b2 + b1 * d2,
            c1 * a2 + d1 * c2,
            c1 * b2 + d1 * d2,
            e1 * a2 + f1 * c2 + e2,
            e1 * b2 + f1 * d2 + f2,
        )

    def _flatten_ocr_text_layers(self, document: pikepdf.Pdf) -> int:
        """
        Inline ocrmypdf's invisible text layer into each page's content stream.

        ocrmypdf grafts its OCR text as a Form XObject (named ``/OCR-...``) that
        is painted *underneath* the scanned image. Acrobat's auto-tagger
        (Accessibility > Autotag / "Tagged PDF" fix) frequently treats such
        pages as "difficult pages" and tags everything on them as a Figure.

        Acrobat's own OCR output instead writes invisible text (3 Tr) directly
        in the page content, after the image. This method rewrites pages into
        that layout. The page looks identical; only the paint order and
        location of the invisible text change.

        Returns:
            int: Number of pages flattened
        """
        flattened = 0
        for page_num, page in enumerate(document.pages):
            try:
                if self._flatten_page_ocr_layer(document, page):
                    flattened += 1
            except Exception as e:
                logger.warning(f"Could not flatten OCR layer on page {page_num + 1}: {e}")
        return flattened

    def _flatten_page_ocr_layer(self, document: pikepdf.Pdf, page) -> bool:
        resources = page.obj.get(Name.Resources)
        if resources is None or Name.XObject not in resources:
            return False
        xobjects = resources[Name.XObject]

        ocr_forms = {
            str(name): xobjects[name]
            for name in list(xobjects.keys())
            if str(name).startswith("/OCR-")
            and xobjects[name].get(Name.Subtype) == Name.Form
        }
        if not ocr_forms:
            return False

        # Only handle forms whose resources are fonts alone (what ocrmypdf emits)
        for form in ocr_forms.values():
            form_res = form.get(Name.Resources, Dictionary())
            if any(key != Name.Font for key in form_res.keys()):
                logger.debug("OCR form has non-font resources; leaving page unchanged")
                return False

        identity = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        ctm = identity
        stack = []
        kept = []
        text_blocks = []

        for instr in pikepdf.parse_content_stream(page):
            op = str(instr.operator) if not isinstance(
                instr, pikepdf.ContentStreamInlineImage
            ) else "INLINE IMAGE"
            if op == "q":
                stack.append(ctm)
            elif op == "Q":
                ctm = stack.pop() if stack else identity
            elif op == "cm":
                ctm = self._matmul(tuple(float(x) for x in instr.operands), ctm)
            elif op == "Do" and str(instr.operands[0]) in ocr_forms:
                text_blocks.append((ctm, ocr_forms[str(instr.operands[0])]))
                continue  # drop the Do; text is re-emitted below
            kept.append(instr)

        if not text_blocks:
            return False

        page_fonts = resources.get(Name.Font)
        if page_fonts is None:
            resources[Name.Font] = Dictionary()
            page_fonts = resources[Name.Font]

        new_ops = [pikepdf.ContentStreamInstruction([], pikepdf.Operator("q"))]
        new_ops.extend(kept)
        new_ops.append(pikepdf.ContentStreamInstruction([], pikepdf.Operator("Q")))

        for block_ctm, form in text_blocks:
            # Merge form fonts into page fonts, renaming on collision
            rename = {}
            form_fonts = form.get(Name.Resources, Dictionary()).get(Name.Font, Dictionary())
            for fname in list(form_fonts.keys()):
                font = form_fonts[fname]
                existing = page_fonts.get(fname)
                if existing is not None and existing.objgen == font.objgen and font.objgen != (0, 0):
                    continue
                if existing is None:
                    page_fonts[fname] = font
                    continue
                i = 0
                while Name(f"/OCRf{i}") in page_fonts:
                    i += 1
                page_fonts[Name(f"/OCRf{i}")] = font
                rename[str(fname)] = Name(f"/OCRf{i}")

            matrix = form.get(Name.Matrix)
            full = block_ctm
            if matrix is not None:
                full = self._matmul(tuple(float(x) for x in matrix), block_ctm)

            new_ops.append(pikepdf.ContentStreamInstruction([], pikepdf.Operator("q")))
            new_ops.append(
                pikepdf.ContentStreamInstruction(list(full), pikepdf.Operator("cm"))
            )
            for instr in pikepdf.parse_content_stream(form):
                if (
                    not isinstance(instr, pikepdf.ContentStreamInlineImage)
                    and str(instr.operator) == "Tf"
                    and str(instr.operands[0]) in rename
                ):
                    instr = pikepdf.ContentStreamInstruction(
                        [rename[str(instr.operands[0])], instr.operands[1]],
                        instr.operator,
                    )
                new_ops.append(instr)
            new_ops.append(pikepdf.ContentStreamInstruction([], pikepdf.Operator("Q")))

        page.obj[Name.Contents] = document.make_stream(
            pikepdf.unparse_content_stream(new_ops)
        )
        for name in ocr_forms:
            del xobjects[Name(name)]
        return True

    # Marked content that stays meaningful without a structure tree:
    # /OC controls optional-content (layer) visibility, /Artifact marks
    # headers/footers/decoration that assistive tech should skip.
    _KEEP_MARKED_CONTENT = frozenset({"/OC", "/Artifact"})

    def _strip_orphan_tags(self, document: pikepdf.Pdf) -> int:
        """
        Strip structure references that have no StructTreeRoot to point to.

        Some PDFs (and every PDF whose tree we removed after OCR) have:
        - /StructParents on pages, /StructParent on annotations and forms
        - BDC/BMC ... EMC marked content (e.g. /P <</MCID 3>> BDC) in content
        These "orphan tags" confuse Acrobat's tagging. Files that still have a
        StructTreeRoot are treated as validly tagged and left untouched.

        Returns:
            int: Number of pages cleaned
        """
        if Name.StructTreeRoot in document.Root:
            logger.info("Document has StructTreeRoot - preserving existing tag structure")
            return 0

        logger.info("No StructTreeRoot found - stripping orphan tags")
        pages_cleaned = 0
        visited_forms = set()

        for page_num, page in enumerate(document.pages):
            changed = False
            try:
                for key in (Name.StructParents, Name.StructParent):
                    if key in page.obj:
                        del page.obj[key]
                        changed = True

                for annot in page.obj.get(Name.Annots, Array()):
                    if isinstance(annot, Dictionary) and Name.StructParent in annot:
                        del annot[Name.StructParent]
                        changed = True

                new_ops = self._strip_marked_content(pikepdf.parse_content_stream(page))
                if new_ops is not None:
                    page.obj[Name.Contents] = document.make_stream(
                        pikepdf.unparse_content_stream(new_ops)
                    )
                    changed = True

                resources = page.obj.get(Name.Resources)
                if resources is not None and self._strip_forms(resources, visited_forms):
                    changed = True
            except Exception as e:
                logger.warning(f"Could not strip orphan tags on page {page_num + 1}: {e}")

            if changed:
                pages_cleaned += 1

        return pages_cleaned

    def _strip_forms(self, resources, visited: set) -> bool:
        """Recursively strip orphan marked content from Form XObjects."""
        changed = False
        xobjects = resources.get(Name.XObject)
        if not isinstance(xobjects, Dictionary):
            return False

        for name in list(xobjects.keys()):
            form = xobjects[name]
            if not isinstance(form, pikepdf.Stream) or form.get(Name.Subtype) != Name.Form:
                continue
            if form.objgen != (0, 0):
                if form.objgen in visited:
                    continue
                visited.add(form.objgen)

            for key in (Name.StructParents, Name.StructParent):
                if key in form:
                    del form[key]
                    changed = True

            new_ops = self._strip_marked_content(pikepdf.parse_content_stream(form))
            if new_ops is not None:
                form.write(pikepdf.unparse_content_stream(new_ops))
                changed = True

            form_res = form.get(Name.Resources)
            if form_res is not None and self._strip_forms(form_res, visited):
                changed = True

        return changed

    def _strip_marked_content(self, instructions):
        """
        Drop structure marked content (BMC/BDC/EMC) from parsed instructions.

        Works on parsed operators, so strings, inline images and operands are
        never touched. EMCs are matched to their BMC/BDC with a stack so only
        the pairs we remove are removed; /OC and /Artifact pairs are kept.

        Returns:
            New instruction list, or None if nothing needed removing.
        """
        out = []
        stack = []
        changed = False

        for instr in instructions:
            if isinstance(instr, pikepdf.ContentStreamInlineImage):
                out.append(instr)
                continue

            op = str(instr.operator)
            if op in ("BMC", "BDC"):
                keep = bool(instr.operands) and str(instr.operands[0]) in self._KEEP_MARKED_CONTENT
                stack.append(keep)
                if keep:
                    out.append(instr)
                else:
                    changed = True
            elif op == "EMC":
                # An EMC with no matching BMC/BDC is malformed; drop it.
                keep = stack.pop() if stack else False
                if keep:
                    out.append(instr)
                else:
                    changed = True
            else:
                out.append(instr)

        return out if changed else None

    def _extract_title(self, document: pikepdf.Pdf, input_path: Path) -> str:
        """
        Extract or generate document title.

        Args:
            document: PDF document
            input_path: Path to PDF file

        Returns:
            str: Document title
        """
        try:
            # Try existing PDF metadata first
            with document.open_metadata() as meta:
                title = meta.get("dc:title")
                if title and title.strip():
                    logger.info(f"Using existing title: {title}")
                    return str(title).strip()
        except Exception as e:
            logger.debug(f"Could not read metadata title: {e}")

        # Fallback to cleaned filename
        title = input_path.stem.replace("_", " ").replace("-", " ")
        title = title.replace(" final", "").replace(" draft", "")
        title = title.title().strip()
        logger.info(f"Using filename as title: {title}")
        return title

    def _update_metadata(
        self,
        document: pikepdf.Pdf,
        title: str,
        author: Optional[str],
        language: str
    ) -> None:
        """
        Update document metadata.

        Args:
            document: PDF document
            title: Document title
            author: Document author
            language: Document language
        """
        try:
            with document.open_metadata(set_pikepdf_as_editor=False) as meta:
                if title:
                    meta["dc:title"] = title
                    logger.info(f"Set title: {title}")
                if author:
                    meta["dc:creator"] = author
                    logger.info(f"Set author: {author}")
                meta["dc:language"] = language
                meta["xmp:CreateDate"] = datetime.now().isoformat()
                meta["pdf:Producer"] = "ePubs Accessibility Enhancement (Simplified)"

        except Exception as e:
            logger.warning(f"Error updating metadata: {e}")

    def _set_tagging_state(self, document: pikepdf.Pdf, language: str) -> None:
        """
        Set MarkInfo and language, and remove PDF/UA claims the file can't back up.

        We don't create a StructTreeRoot. Acrobat's auto-tagging builds the
        tag structure, so until then the file is untagged and must not claim
        to be tagged or PDF/UA-1 conformant (pdfuaid:part). A claim on an
        untagged file makes validators judge it as a failed PDF/UA document.

        Args:
            document: PDF document
            language: Document language
        """
        has_struct_tree = Name.StructTreeRoot in document.Root

        # 1. MarkInfo reflects whether a structure tree actually exists.
        # Marked=True / Suspects=True with no StructTreeRoot tells Acrobat the
        # file has (suspect) tags it can't find, which can derail auto-tagging.
        if Name.MarkInfo not in document.Root:
            document.Root.MarkInfo = Dictionary()
        document.Root.MarkInfo[Name.Marked] = has_struct_tree
        if Name.Suspects in document.Root.MarkInfo:
            del document.Root.MarkInfo[Name.Suspects]
        logger.info(f"MarkInfo Marked={has_struct_tree} (untagged files are left for Acrobat to tag)")

        # 2. Document language (needed for accessibility, tagged or not)
        document.Root[Name.Lang] = String(language)

        # 3. Remove the /GTS_PDFUA1 OutputIntent earlier versions of this tool
        # added. It isn't part of PDF/UA (OutputIntents describe color output).
        if Name.OutputIntents in document.Root:
            intents = document.Root.OutputIntents
            kept = [
                intent for intent in intents
                if not (isinstance(intent, Dictionary) and intent.get(Name.S) == Name.GTS_PDFUA1)
            ]
            if len(kept) != len(intents):
                if kept:
                    document.Root.OutputIntents = Array(kept)
                else:
                    del document.Root[Name.OutputIntents]
                logger.info("Removed non-standard GTS_PDFUA1 OutputIntent")

        # 4. An untagged file cannot conform to PDF/UA-1: drop any claim.
        # Tagged files that we left untouched keep whatever they declared.
        if not has_struct_tree:
            try:
                with document.open_metadata(set_pikepdf_as_editor=False) as meta:
                    if "pdfuaid:part" in meta:
                        del meta["pdfuaid:part"]
                        logger.info("Removed PDF/UA-1 identifier from untagged document")
            except Exception as e:
                logger.warning(f"Error updating XMP metadata: {e}")

    def get_capabilities(self):
        """Get list of capabilities."""
        return [
            "pdfua.orphan_tag_stripping",
            "pdfua.metadata",
            "pdfua.ocr_text_layer_flattening",
        ]
