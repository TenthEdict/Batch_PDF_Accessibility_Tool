#!/usr/bin/env python3
"""
Simplified PDF/UA enhancer with orphan tag stripping and basic metadata.

This enhancer provides essential PDF/UA-1 compliance features:
- Orphan tag stripping (critical for Adobe Acrobat workflow)
- Basic PDF/UA-1 metadata
- Document properties (title, author, language)
- No mathematical notation detection
- No ML-based accessibility features
"""

import logging
import re
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
    - PDF/UA-1 metadata and compliance flags
    - Basic document properties (title, author, language)
    - Clean structure tree for manual Acrobat tagging
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
            # After OCR, remove any incomplete StructTreeRoot that ocrmypdf might have created
            # This allows Acrobat to create a complete tag structure from scratch
            self._remove_incomplete_struct_tree(document)
        else:
            # For non-OCR documents, strip orphan tags
            pages_cleaned = self._strip_orphan_tags(document)
            if pages_cleaned > 0:
                logger.info(f"Stripped orphan tags from {pages_cleaned} pages")

        # Step 2: Determine title if not provided
        if not title:
            title = self._extract_title(document, input_path)

        # Step 3: Update document metadata
        self._update_metadata(document, title, author, language)

        # Step 4: Add PDF/UA-1 compliance
        self._add_pdfua_compliance(document, language)

        logger.info("Applied PDF/UA-1 enhancements")

    def _remove_incomplete_struct_tree(self, document: pikepdf.Pdf) -> None:
        """
        Remove incomplete StructTreeRoot but PRESERVE marked content after OCR.

        ocrmypdf creates marked content operators (BDC/EMC with <P> containers)
        that Acrobat uses as "hooks" to link text when manually creating tags.

        We remove:
        - StructTreeRoot (incomplete structure)
        - StructParents (orphan page references)

        We KEEP:
        - Marked content operators (BDC/EMC) - Acrobat needs these!

        This allows Acrobat to link the invisible OCR text to tags when the
        user manually creates structure elements.

        Args:
            document: The PDF document to clean
        """
        logger.info("Removing incomplete StructTreeRoot but preserving marked content...")

        # Remove StructTreeRoot if present
        if Name.StructTreeRoot in document.Root:
            del document.Root[Name.StructTreeRoot]
            logger.info("Removed StructTreeRoot")

        # Remove StructParents from all pages
        pages_cleaned = 0
        for page in document.pages:
            if Name.StructParents in page:
                del page[Name.StructParents]
                pages_cleaned += 1

        if pages_cleaned > 0:
            logger.info(f"Removed StructParents from {pages_cleaned} pages")

        # DO NOT strip marked content - Acrobat needs it for manual tagging!
        logger.info("Preserved marked content operators for Acrobat tagging")

        # Move ocrmypdf's text layer out of its Form XObject into the page
        flattened = self._flatten_ocr_text_layers(document)
        if flattened > 0:
            logger.info(f"Flattened OCR text layer into page content on {flattened} pages")

    # ------------------------------------------------------------------
    # OCR text layer flattening
    # ------------------------------------------------------------------

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

    def _strip_orphan_tags(self, document: pikepdf.Pdf) -> int:
        """
        Strip orphan tagged content that interferes with proper tag tree creation.

        Some PDFs have malformed tagging where:
        - Pages have StructParents entries but no StructTreeRoot exists
        - Content streams have BDC/BMC/EMC marked content operators without structure
        - This creates "orphan tags" that confuse Acrobat's tagging system

        This function intelligently cleans orphan tags while preserving valid OCR content.

        Args:
            document: The PDF document to clean

        Returns:
            int: Number of pages cleaned
        """
        logger.info("Starting orphan tag cleanup...")
        pages_cleaned = 0
        streams_cleaned = 0

        try:
            # Check if document already has a StructTreeRoot (valid tag structure)
            has_struct_tree = Name.StructTreeRoot in document.Root

            if has_struct_tree:
                logger.info("Document has StructTreeRoot - preserving existing tag structure")
                # Don't strip anything if there's already a valid structure
                # This preserves OCR-generated marked content from ocrmypdf
                return 0

            # Only strip if we have orphan tags (StructParents without StructTreeRoot)
            logger.info("No StructTreeRoot found - stripping orphan tags")

            # Remove StructParents from all pages (these are orphan references)
            for page in document.pages:
                if Name.StructParents in page:
                    del page[Name.StructParents]
                    pages_cleaned += 1

                # Strip marked content operators from content streams
                try:
                    if Name.Contents in page:
                        contents = page.Contents

                        # Handle both single stream and array of streams
                        if isinstance(contents, pikepdf.Array):
                            for stream in contents:
                                if self._strip_marked_content_from_stream(stream):
                                    streams_cleaned += 1
                        else:
                            if self._strip_marked_content_from_stream(contents):
                                streams_cleaned += 1

                except Exception as e:
                    logger.debug(f"Could not clean content stream: {e}")
                    continue

            if pages_cleaned > 0:
                logger.info(f"Removed orphan StructParents from {pages_cleaned} pages")
            if streams_cleaned > 0:
                logger.info(f"Stripped marked content from {streams_cleaned} streams")

        except Exception as e:
            logger.warning(f"Error stripping orphan tags: {e}")

        return pages_cleaned

    def _strip_marked_content_from_stream(self, stream) -> bool:
        """
        Strip marked content operators (BMC, BDC, EMC) from a content stream.

        Args:
            stream: PDF content stream object

        Returns:
            bool: True if stream was modified, False otherwise
        """
        try:
            # Read stream content
            content_bytes = stream.read_raw_bytes()

            # Try to decode
            try:
                content_str = content_bytes.decode('utf-8', errors='ignore')
            except:
                try:
                    content_str = content_bytes.decode('latin-1', errors='ignore')
                except:
                    return False

            # Check if there are any marked content operators
            if not any(op in content_str for op in [' BMC', ' BDC', ' EMC', '\nBMC', '\nBDC', '\nEMC']):
                return False

            # Count operators before stripping
            bdc_before = len(re.findall(r'/\w+\s+(?:<<[^>]*>>\s+)?BDC', content_str))
            bmc_before = len(re.findall(r'/\w+\s+BMC', content_str))
            emc_before = len(re.findall(r'EMC', content_str))

            # Remove BDC operations (Begin Marked Content with Dictionary)
            content_str = re.sub(r'/\w+\s+(?:<<[^>]*>>\s+)?BDC\s*', '', content_str)

            # Remove BMC operations (Begin Marked Content)
            content_str = re.sub(r'/\w+\s+BMC\s*', '', content_str)

            # Remove EMC operations (End Marked Content)
            content_str = re.sub(r'EMC\s*', '', content_str)

            # Write cleaned content back
            new_content_bytes = content_str.encode('latin-1', errors='ignore')
            stream.write(new_content_bytes, filter=pikepdf.Name.FlateDecode)

            total_removed = bdc_before + bmc_before + emc_before
            if total_removed > 0:
                logger.debug(f"Stripped {total_removed} marked content operators")

            return True

        except Exception as e:
            logger.debug(f"Could not strip marked content: {e}")
            return False

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

    def _add_pdfua_compliance(self, document: pikepdf.Pdf, language: str) -> None:
        """
        Add PDF/UA-1 compliance metadata for manual tagging workflow.

        We DON'T create a StructTreeRoot. This allows Acrobat's auto-tagging
        system to create the tag structure from scratch and properly associate
        it with the OCR text layer.

        Args:
            document: PDF document
            language: Document language
        """
        # 1. Mark document as ready for tagging
        if Name.MarkInfo not in document.Root:
            document.Root.MarkInfo = Dictionary()

        # Only claim the document is tagged if a structure tree actually exists.
        # Marked=True / Suspects=True with no StructTreeRoot tells Acrobat the
        # file has (suspect) tags it can't find, which can derail auto-tagging.
        has_struct_tree = Name.StructTreeRoot in document.Root
        document.Root.MarkInfo[Name.Marked] = has_struct_tree
        if Name.Suspects in document.Root.MarkInfo:
            del document.Root.MarkInfo[Name.Suspects]
        logger.info(f"MarkInfo Marked={has_struct_tree} (untagged files are left for Acrobat to tag)")

        # 2. Set document language (required for PDF/UA)
        document.Root[Name.Lang] = String(language)

        # 4. Add PDF/UA-1 OutputIntent
        output_intent = Dictionary(
            Type=Name.OutputIntent,
            S=Name.GTS_PDFUA1,
            OutputConditionIdentifier=String("PDF/UA-1"),
            Info=String("PDF for Universal Accessibility"),
            RegistryName=String("http://www.color.org")
        )

        if Name.OutputIntents not in document.Root:
            document.Root.OutputIntents = Array()

        # Avoid duplicates
        pdfua_exists = any(
            intent.get(Name.S) == Name.GTS_PDFUA1
            for intent in document.Root.OutputIntents
            if isinstance(intent, Dictionary)
        )

        if not pdfua_exists:
            document.Root.OutputIntents.append(output_intent)
            logger.info("Added PDF/UA-1 OutputIntent")

        # 5. Add PDF/UA XMP metadata
        try:
            with document.open_metadata() as meta:
                meta["pdfuaid:part"] = "1"
                logger.info("Added PDF/UA-1 XMP metadata")
        except Exception as e:
            logger.warning(f"Error adding XMP metadata: {e}")

    def get_capabilities(self):
        """Get list of capabilities."""
        return [
            "pdfua.orphan_tag_stripping",
            "pdfua.basic_compliance",
            "pdfua.metadata",
            "pdfua.structure_tree",
        ]
