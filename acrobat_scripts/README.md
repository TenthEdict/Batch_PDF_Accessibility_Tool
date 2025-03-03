# Adobe Acrobat JavaScript Tools for Accessibility

This directory contains JavaScript tools for Adobe Acrobat Pro that enhance and automate accessibility-related tasks for PDF documents, with a focus on academic publications.

## Installation

1. Open Adobe Acrobat Pro
2. Go to Tools > JavaScript > JavaScript Editor
3. Copy the entire content of the desired script file
4. Paste it into the JavaScript Editor
5. Save the script (File > Save As...)
6. Add the script to the menu using the provided code in each script's header

## Available Scripts

### 1. BatchPreflightAndOptimize.js

Automates Preflight operations and optimization for multiple open documents.

**Features:**
- Fixes potential font problems
- Fixes problems in PDF tagging structure 
- Optimizes documents with compatible settings
- Batch processes all open documents

**Usage:**
- Open multiple PDFs in Acrobat Pro
- Run the script from the menu (File > Batch Preflight and Optimize)

### 2. TaggingUtilities.js

Provides comprehensive tools for fixing and enhancing document tags.

**Features:**
- Analyze document structure and tag statistics
- Fix heading hierarchy issues
- Fix empty table cells
- Apply academic document templates
- Add placeholder alt text to figures

**Usage:**
- Open a PDF in Acrobat Pro
- Run the script from the menu (Advanced > Tagging Utilities)

### 3. AcademicPDFToolbox.js

Tools specifically designed for academic publications.

**Features:**
- Detect and mark document sections (abstract, methods, results, etc.)
- Create bookmarks based on document structure
- Tag mathematical equations for accessibility
- Create table of contents when missing
- Enhance citation accessibility

**Usage:**
- Open an academic PDF in Acrobat Pro
- Run the script from the menu (Document > Academic PDF Toolbox)

## Tips for Academic Document Tagging

1. **Heading Order**: Ensure headings follow a logical hierarchy (H1, H2, H3...) without skipping levels
2. **Table Cells**: All table cells should have content (even if just a non-breaking space)
3. **Alt Text**: All figures should have descriptive alt text
4. **Citations**: Citations should be properly tagged for accessibility
5. **Equations**: Mathematical equations need special tagging as Formula elements

## Additional Resources

- [Adobe Acrobat JavaScript API Reference](https://opensource.adobe.com/dc-acrobat-sdk-docs/acrobatsdk/)
- [PDF/UA Standard Information](https://www.pdfa.org/resource/pdfua-in-a-nutshell/)
- [Creating Accessible PDFs with Adobe Acrobat Pro](https://www.adobe.com/accessibility/products/acrobat.html)