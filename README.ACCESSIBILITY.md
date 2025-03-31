# PDF Accessibility Project

This project provides tools for enhancing PDF accessibility, particularly focusing on historical documents that need searchable text.

## Structure

- `accessibility_tools/`: Primary tools for enhancing PDF accessibility
- `brodie_code/`: Code for OCR and text recognition with a focus on historical documents
- `acrobat_scripts/`: JavaScript tools for Adobe Acrobat
- `fix_searchable_text_invisible.py`: Main script for adding invisible, searchable text to PDFs

## Usage

To make a PDF searchable with invisible text:

```bash
source /Users/broderickschipp/work/ePubs_AccProj/pdf_venv/bin/activate
python /Users/broderickschipp/work/ePubs_AccProj/fix_searchable_text_invisible.py \
    "/path/to/input.pdf" \
    "/path/to/output.pdf" \
    --historical
```

This script:
1. Creates a searchable PDF with invisible text
2. Uses OCR to recognize text in the document
3. Places each word precisely where it appears in the original document
4. Applies specialized processing for historical documents

## Archive

The `archive/` directory contains intermediate files created during development:
- Previous script versions
- Test PDFs
- Experimental code

Refer to `archive/README.md` for details about archived files.
